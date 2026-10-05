import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.prompts import EXTRACTION_PROMPT_VERSION
from app.ai.provider import LLMProvider
from app.models.audit import ActorType
from app.models.extraction import Extraction
from app.services import audit_service
from app.services.document_service import get_document


def run_extraction(
    db: Session,
    case_id: uuid.UUID,
    document_id: uuid.UUID,
    *,
    provider: LLMProvider,
) -> Extraction:
    document = get_document(db, case_id, document_id)

    if not document.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Document has no extracted text to run AI extraction on",
        )

    extracted_case = provider.extract_case_fields(document.extracted_text)

    extraction = Extraction(
        case_id=case_id,
        document_id=document_id,
        extracted_data=extracted_case.model_dump(),
        model_provider=provider.provider_name,
        model_version=provider.model_version,
        prompt_version=EXTRACTION_PROMPT_VERSION,
    )
    db.add(extraction)
    db.flush()

    audit_service.record_event(
        db,
        case_id=case_id,
        action="EXTRACTION_COMPLETED",
        actor_type=ActorType.AI,
        actor_id=provider.provider_name,
        new_value={"extraction_id": str(extraction.id), "document_id": str(document_id)},
        model_version=provider.model_version,
    )

    db.commit()
    db.refresh(extraction)
    return extraction


def list_extractions(
    db: Session, case_id: uuid.UUID, document_id: uuid.UUID
) -> list[Extraction]:
    get_document(db, case_id, document_id)  # raises 404 if missing
    return (
        db.query(Extraction)
        .filter(Extraction.case_id == case_id, Extraction.document_id == document_id)
        .order_by(Extraction.created_at.asc())
        .all()
    )
