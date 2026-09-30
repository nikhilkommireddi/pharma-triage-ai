import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CaseStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    case_number: Mapped[str] = mapped_column(String, unique=True, index=True)
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus, name="casestatus"), default=CaseStatus.OPEN
    )

    # Structured case information. Kept as JSON rather than dedicated columns
    # because the field set is still evolving (extraction/triage phases will
    # add to it) — promote to relational columns if these need to be queried
    # or indexed individually.
    source: Mapped[dict] = mapped_column(JSON, default=dict)
    product: Mapped[dict] = mapped_column(JSON, default=dict)
    patient: Mapped[dict] = mapped_column(JSON, default=dict)
    event: Mapped[dict] = mapped_column(JSON, default=dict)
    reporter: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    audit_events: Mapped[list["AuditEvent"]] = relationship(  # noqa: F821
        back_populates="case", cascade="all, delete-orphan"
    )
