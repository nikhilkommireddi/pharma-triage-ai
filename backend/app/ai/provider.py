from abc import ABC, abstractmethod

from app.ai.schemas import ExtractedCase


class LLMProvider(ABC):
    """Abstraction over the LLM used for extraction, so the system isn't
    hardwired to one vendor (see CLAUDE.md: configuration over hardcoding).
    Swapping providers means implementing this interface, not touching
    callers."""

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @property
    @abstractmethod
    def model_version(self) -> str: ...

    @abstractmethod
    def extract_case_fields(self, text: str) -> ExtractedCase: ...
