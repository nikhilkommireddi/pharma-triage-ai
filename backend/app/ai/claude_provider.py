import anthropic

from app.ai.prompts import load_prompt
from app.ai.provider import LLMProvider
from app.ai.schemas import ExtractedCase

_TOOL_NAME = "record_extracted_case"


class ClaudeExtractionProvider(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    @property
    def provider_name(self) -> str:
        return "claude"

    @property
    def model_version(self) -> str:
        return self._model

    def extract_case_fields(self, text: str) -> ExtractedCase:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=2048,
            system=load_prompt("extraction_v1"),
            tools=[
                {
                    "name": _TOOL_NAME,
                    "description": (
                        "Record structured fields extracted from a "
                        "pharmaceutical case document."
                    ),
                    "input_schema": ExtractedCase.model_json_schema(),
                }
            ],
            tool_choice={"type": "tool", "name": _TOOL_NAME},
            messages=[{"role": "user", "content": text}],
        )

        for block in response.content:
            if block.type == "tool_use" and block.name == _TOOL_NAME:
                return ExtractedCase.model_validate(block.input)

        raise RuntimeError(
            f"Claude response did not include the expected '{_TOOL_NAME}' tool call"
        )
