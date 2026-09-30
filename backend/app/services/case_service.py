import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.audit import ActorType, AuditEvent
from app.models.case import Case
from app.schemas.case import CaseCreate, CaseUpdate
from app.services import audit_service

_STRUCTURED_FIELDS = ("source", "product", "patient", "event", "reporter")


def _generate_case_number() -> str:
    # Short unique code rather than a sequential counter, to avoid a
    # contended shared-sequence write on every case creation. Switch to a
    # DB sequence if a sequential, human-assigned number becomes a
    # requirement.
    return f"CASE-{uuid.uuid4().hex[:8].upper()}"


def create_case(db: Session, payload: CaseCreate, *, actor_id: str = "system") -> Case:
    case = Case(
        case_number=_generate_case_number(),
        source=payload.source.model_dump(),
        product=payload.product.model_dump(),
        patient=payload.patient.model_dump(),
        event=payload.event.model_dump(),
        reporter=payload.reporter.model_dump(),
    )
    db.add(case)
    db.flush()

    audit_service.record_event(
        db,
        case_id=case.id,
        action="CASE_CREATED",
        actor_type=ActorType.HUMAN,
        actor_id=actor_id,
        new_value={field: getattr(case, field) for field in _STRUCTURED_FIELDS},
    )

    db.commit()
    db.refresh(case)
    return case


def get_case(db: Session, case_id: uuid.UUID) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


def list_cases(db: Session, *, limit: int = 50, offset: int = 0) -> list[Case]:
    return (
        db.query(Case)
        .order_by(Case.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def update_case(
    db: Session, case_id: uuid.UUID, payload: CaseUpdate, *, actor_id: str = "system"
) -> Case:
    case = get_case(db, case_id)

    for field in _STRUCTURED_FIELDS:
        new_value = getattr(payload, field)
        if new_value is None:
            continue
        previous = getattr(case, field)
        updated = new_value.model_dump()
        if updated == previous:
            continue
        setattr(case, field, updated)
        audit_service.record_event(
            db,
            case_id=case.id,
            action=f"CASE_{field.upper()}_UPDATED",
            actor_type=ActorType.HUMAN,
            actor_id=actor_id,
            previous_value=previous,
            new_value=updated,
            reason=payload.reason,
        )

    if payload.status is not None and payload.status != case.status:
        previous_status = case.status.value
        case.status = payload.status
        audit_service.record_event(
            db,
            case_id=case.id,
            action="CASE_STATUS_CHANGED",
            actor_type=ActorType.HUMAN,
            actor_id=actor_id,
            previous_value={"status": previous_status},
            new_value={"status": payload.status.value},
            reason=payload.reason,
        )

    db.commit()
    db.refresh(case)
    return case


def list_audit_events(db: Session, case_id: uuid.UUID) -> list[AuditEvent]:
    get_case(db, case_id)  # raises 404 if the case doesn't exist
    return (
        db.query(AuditEvent)
        .filter(AuditEvent.case_id == case_id)
        .order_by(AuditEvent.timestamp.asc())
        .all()
    )
