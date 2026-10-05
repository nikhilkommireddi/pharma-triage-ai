from app.ai.claude_provider import ClaudeExtractionProvider
from app.ai.provider import LLMProvider
from app.core.config import get_settings


def get_llm_provider() -> LLMProvider:
    """FastAPI dependency. Not cached — tests override it entirely via
    `app.dependency_overrides`, and constructing the Anthropic client is
    cheap (no network call)."""
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not configured; extraction requires an LLM provider."
        )
    return ClaudeExtractionProvider(
        api_key=settings.anthropic_api_key, model=settings.extraction_model
    )
