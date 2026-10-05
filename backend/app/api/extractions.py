import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai import get_llm_provider
from app.ai.provider import LLMProvider
from app.db.session import get_db
from app.schemas.extraction import ExtractionRead
from app.services import extraction_service

router = APIRouter(
    prefix="/cases/{case_id}/documents/{document_id}/extractions", tags=["extraction"]
)


@router.post("", response_model=ExtractionRead, status_code=201)
def create_extraction(
    case_id: uuid.UUID,
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    provider: LLMProvider = Depends(get_llm_provider),
) -> ExtractionRead:
    return extraction_service.run_extraction(db, case_id, document_id, provider=provider)


@router.get("", response_model=list[ExtractionRead])
def list_extractions(
    case_id: uuid.UUID, document_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[ExtractionRead]:
    return extraction_service.list_extractions(db, case_id, document_id)
