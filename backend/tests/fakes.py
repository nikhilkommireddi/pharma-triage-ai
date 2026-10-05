from app.ai.provider import LLMProvider
from app.ai.schemas import ExtractedCase


class FakeLLMProvider(LLMProvider):
    """Deterministic test double — returns a fixed, known extraction result
    instead of calling a real model, so extraction-pipeline tests don't
    need network access or an API key."""

    def __init__(self, result: ExtractedCase | None = None) -> None:
        self._result = result or ExtractedCase(
            product={"name": "Acme Tablet 50mg", "lot_number": "ABC123"},
            event={"description": "Patient experienced nausea"},
            signals={"adverse_event_detected": True, "quality_issue_detected": False},
            evidence=[
                {"field": "product.lot_number", "quote": "lot ABC123"},
                {"field": "event.description", "quote": "experienced nausea"},
            ],
        )
        self.calls: list[str] = []

    @property
    def provider_name(self) -> str:
        return "fake"

    @property
    def model_version(self) -> str:
        return "fake-v1"

    def extract_case_fields(self, text: str) -> ExtractedCase:
        self.calls.append(text)
        return self._result
