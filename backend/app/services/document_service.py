import hashlib
import io
import json
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.audit import ActorType
from app.models.document import Document, DocumentContentType
from app.services import audit_service
from app.services.case_service import get_case
from app.storage import get_storage

_ALLOWED_CONTENT_TYPES = {ct.value for ct in DocumentContentType}


def _sniff_and_validate(content_type: str, data: bytes) -> None:
    """Reject files whose actual bytes don't match the declared content
    type, before we persist anything or attempt extraction."""
    if content_type == DocumentContentType.APPLICATION_PDF.value:
        if not data.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="File content does not match declared type application/pdf",
            )
    elif content_type == DocumentContentType.APPLICATION_JSON.value:
        try:
            json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="File content is not valid JSON",
            ) from exc
    elif content_type == DocumentContentType.TEXT_PLAIN.value:
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="File content is not valid UTF-8 text",
            ) from exc


def _extract_text(content_type: str, data: bytes) -> tuple[str | None, str | None]:
    """Returns (extracted_text, extraction_error). Never raises — a file
    that passed content-type validation but can't be parsed is a normal,
    expected outcome to record, not a server error."""
    if content_type in (
        DocumentContentType.TEXT_PLAIN.value,
        DocumentContentType.APPLICATION_JSON.value,
    ):
        return data.decode("utf-8"), None

    if content_type == DocumentContentType.APPLICATION_PDF.value:
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(data))
            text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        except Exception as exc:  # noqa: BLE001 — any parser failure is an extraction error, not a bug
            return None, f"Failed to extract text: {exc}"

        if not text:
            return None, "No extractable text found (the PDF may be a scanned image)"
        return text, None

    return None, f"Unsupported content type: {content_type}"


def upload_document(
    db: Session,
    case_id: uuid.UUID,
    *,
    upload: UploadFile,
    actor_id: str = "system",
) -> Document:
    get_case(db, case_id)  # raises 404 if the case doesn't exist

    content_type = upload.content_type
    if content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content type: {content_type}",
        )

    data = upload.file.read()
    if len(data) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Uploaded file is empty"
        )
    if len(data) > get_settings().max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds maximum upload size",
        )

    _sniff_and_validate(content_type, data)

    document = Document(
        case_id=case_id,
        filename=upload.filename or "unnamed",
        content_type=DocumentContentType(content_type),
        size_bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
        storage_key=str(uuid.uuid4()),
    )
    db.add(document)
    db.flush()

    get_storage().save(document.storage_key, data)

    audit_service.record_event(
        db,
        case_id=case_id,
        action="DOCUMENT_UPLOADED",
        actor_type=ActorType.HUMAN,
        actor_id=actor_id,
        new_value={
            "document_id": str(document.id),
            "filename": document.filename,
            "content_type": content_type,
            "size_bytes": document.size_bytes,
            "sha256": document.sha256,
        },
    )

    extracted_text, extraction_error = _extract_text(content_type, data)
    document.extracted_text = extracted_text
    document.extraction_error = extraction_error

    audit_service.record_event(
        db,
        case_id=case_id,
        action="DOCUMENT_PARSED" if extraction_error is None else "DOCUMENT_PARSE_FAILED",
        actor_type=ActorType.SYSTEM,
        actor_id="document-ingestion",
        new_value={"document_id": str(document.id)},
        reason=extraction_error,
    )

    db.commit()
    db.refresh(document)
    return document


def list_documents(db: Session, case_id: uuid.UUID) -> list[Document]:
    get_case(db, case_id)
    return (
        db.query(Document)
        .filter(Document.case_id == case_id)
        .order_by(Document.created_at.asc())
        .all()
    )


def get_document(db: Session, case_id: uuid.UUID, document_id: uuid.UUID) -> Document:
    get_case(db, case_id)
    document = (
        db.query(Document)
        .filter(Document.case_id == case_id, Document.id == document_id)
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document
