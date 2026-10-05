from functools import lru_cache
from pathlib import Path

# backend/app/ai/prompts.py -> parents[2] is backend/ -> parents[3] is the repo root.
_PROMPTS_DIR = Path(__file__).resolve().parents[3] / "prompts"

EXTRACTION_PROMPT_VERSION = "extraction-v1"


@lru_cache
def load_prompt(name: str) -> str:
    return (_PROMPTS_DIR / f"{name}.txt").read_text(encoding="utf-8")
