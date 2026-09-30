import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ActorType(str, enum.Enum):
    SYSTEM = "SYSTEM"
    HUMAN = "HUMAN"
    AI = "AI"


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cases.id"), index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    actor_type: Mapped[ActorType] = mapped_column(Enum(ActorType, name="actortype"))
    actor_id: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String)

    previous_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String, nullable=True)
    rules_version: Mapped[str | None] = mapped_column(String, nullable=True)

    case: Mapped["Case"] = relationship(back_populates="audit_events")  # noqa: F821
