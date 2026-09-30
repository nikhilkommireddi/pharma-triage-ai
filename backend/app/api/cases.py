import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.audit import AuditEventRead
from app.schemas.case import CaseCreate, CaseRead, CaseUpdate
from app.services import case_service

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("", response_model=CaseRead, status_code=201)
def create_case(payload: CaseCreate, db: Session = Depends(get_db)) -> CaseRead:
    return case_service.create_case(db, payload)


@router.get("", response_model=list[CaseRead])
def list_cases(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[CaseRead]:
    return case_service.list_cases(db, limit=limit, offset=offset)


@router.get("/{case_id}", response_model=CaseRead)
def get_case(case_id: uuid.UUID, db: Session = Depends(get_db)) -> CaseRead:
    return case_service.get_case(db, case_id)


@router.patch("/{case_id}", response_model=CaseRead)
def update_case(
    case_id: uuid.UUID, payload: CaseUpdate, db: Session = Depends(get_db)
) -> CaseRead:
    return case_service.update_case(db, case_id, payload)


@router.get("/{case_id}/audit", response_model=list[AuditEventRead])
def get_case_audit(case_id: uuid.UUID, db: Session = Depends(get_db)) -> list[AuditEventRead]:
    return case_service.list_audit_events(db, case_id)
