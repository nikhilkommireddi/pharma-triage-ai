import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.document import DocumentRead
from app.services import document_service

router = APIRouter(prefix="/cases/{case_id}/documents", tags=["documents"])


@router.post("", response_model=DocumentRead, status_code=201)
def upload_document(
    case_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentRead:
    return document_service.upload_document(db, case_id, upload=file)


@router.get("", response_model=list[DocumentRead])
def list_documents(case_id: uuid.UUID, db: Session = Depends(get_db)) -> list[DocumentRead]:
    return document_service.list_documents(db, case_id)


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    case_id: uuid.UUID, document_id: uuid.UUID, db: Session = Depends(get_db)
) -> DocumentRead:
    return document_service.get_document(db, case_id, document_id)
