from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentContentType


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    filename: str
    content_type: DocumentContentType
    size_bytes: int
    sha256: str
    extracted_text: str | None
    extraction_error: str | None
    created_at: datetime
