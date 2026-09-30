from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.case import CaseStatus


class SourceInfo(BaseModel):
    channel: str | None = None
    reporter_type: str | None = None


class ProductInfo(BaseModel):
    name: str | None = None
    strength: str | None = None
    dosage_form: str | None = None
    lot_number: str | None = None
    expiration_date: str | None = None


class PatientInfo(BaseModel):
    age: int | None = None
    sex: str | None = None


class EventInfo(BaseModel):
    description: str | None = None
    onset_date: str | None = None
    seriousness: str | None = None


class ReporterInfo(BaseModel):
    name: str | None = None
    organization: str | None = None
    contact_available: bool | None = None


class CaseCreate(BaseModel):
    source: SourceInfo = SourceInfo()
    product: ProductInfo = ProductInfo()
    patient: PatientInfo = PatientInfo()
    event: EventInfo = EventInfo()
    reporter: ReporterInfo = ReporterInfo()


class CaseUpdate(BaseModel):
    """Partial update. Only fields provided are changed; each changed field
    is recorded as a separate audit event. `reason` is stored on every audit
    event this update produces and should explain why the change was made."""

    source: SourceInfo | None = None
    product: ProductInfo | None = None
    patient: PatientInfo | None = None
    event: EventInfo | None = None
    reporter: ReporterInfo | None = None
    status: CaseStatus | None = None
    reason: str | None = None


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_number: str
    status: CaseStatus
    source: dict
    product: dict
    patient: dict
    event: dict
    reporter: dict
    created_at: datetime
    updated_at: datetime
