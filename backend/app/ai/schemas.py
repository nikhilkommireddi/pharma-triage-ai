from pydantic import BaseModel, Field


class ExtractedProduct(BaseModel):
    name: str | None = None
    strength: str | None = None
    dosage_form: str | None = None
    lot_number: str | None = None
    expiration_date: str | None = None


class ExtractedPatient(BaseModel):
    age: int | None = None
    sex: str | None = None


class ExtractedEvent(BaseModel):
    description: str | None = None
    onset_date: str | None = None
    seriousness: str | None = None


class ExtractedReporter(BaseModel):
    name: str | None = None
    organization: str | None = None
    contact_available: bool | None = None


class ExtractedSignals(BaseModel):
    """Candidate routing signals. These are hints for the (not-yet-built)
    deterministic rules engine to act on — the model's say on them is
    advisory, never authoritative."""

    adverse_event_detected: bool = False
    quality_issue_detected: bool = False
    medical_information_request_detected: bool = False


class EvidenceItem(BaseModel):
    field: str = Field(description="Dot-path of the extracted field this evidence supports, e.g. 'product.lot_number'.")
    quote: str = Field(description="Verbatim quote from the source text supporting that field.")


class ExtractedCase(BaseModel):
    """Structured output of the extraction model. Every field is optional
    and must be null/empty when the source text doesn't state it — the
    model must never fill in a plausible-sounding guess."""

    product: ExtractedProduct = ExtractedProduct()
    patient: ExtractedPatient = ExtractedPatient()
    event: ExtractedEvent = ExtractedEvent()
    reporter: ExtractedReporter = ExtractedReporter()
    signals: ExtractedSignals = ExtractedSignals()
    evidence: list[EvidenceItem] = []
