import uuid

from sqlalchemy.orm import Session

from app.models.audit import ActorType, AuditEvent


def record_event(
    db: Session,
    *,
    case_id: uuid.UUID,
    action: str,
    actor_type: ActorType = ActorType.SYSTEM,
    actor_id: str = "system",
    previous_value: dict | None = None,
    new_value: dict | None = None,
    reason: str | None = None,
    model_version: str | None = None,
    rules_version: str | None = None,
) -> AuditEvent:
    event = AuditEvent(
        case_id=case_id,
        action=action,
        actor_type=actor_type,
        actor_id=actor_id,
        previous_value=previous_value,
        new_value=new_value,
        reason=reason,
        model_version=model_version,
        rules_version=rules_version,
    )
    db.add(event)
    return event
