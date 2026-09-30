import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DocumentContentType(str, enum.Enum):
    TEXT_PLAIN = "text/plain"
    APPLICATION_JSON = "application/json"
    APPLICATION_PDF = "application/pdf"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cases.id"), index=True)

    filename: Mapped[str] = mapped_column(String)
    content_type: Mapped[DocumentContentType] = mapped_column(
        Enum(DocumentContentType, name="documentcontenttype")
    )
    size_bytes: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String, index=True)

    # Server-generated key into the storage backend. Never derived from the
    # client-supplied filename — see app/storage/local.py.
    storage_key: Mapped[str] = mapped_column(String)

    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    case: Mapped["Case"] = relationship()  # noqa: F821
