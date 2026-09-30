from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.audit import ActorType


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: UUID
    case_id: UUID
    timestamp: datetime
    actor_type: ActorType
    actor_id: str
    action: str
    previous_value: dict | None = None
    new_value: dict | None = None
    reason: str | None = None
    model_version: str | None = None
    rules_version: str | None = None
