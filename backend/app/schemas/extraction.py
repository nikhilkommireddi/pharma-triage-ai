from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExtractionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: UUID
    case_id: UUID
    document_id: UUID
    extracted_data: dict
    model_provider: str
    model_version: str
    prompt_version: str
    created_at: datetime
