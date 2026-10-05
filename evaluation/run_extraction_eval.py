#!/usr/bin/env python
"""Extraction-quality evaluation harness.

Runs the configured LLM provider against a small, versioned set of
synthetic cases (extraction_cases.jsonl) and reports field-level accuracy
against known expected values.

This is a manual/CI-optional check, not part of the pytest suite — it
calls a real external model and costs money. The pytest suite instead
exercises the extraction *pipeline* (storage, audit, versioning, error
handling) against a deterministic fake provider; this script checks the
*model's* actual extraction quality.

This is a 5-case smoke check, not the full dev/validation/test evaluation
dataset described in the product plan (Phase: Evaluation) — that larger,
reviewer-validated dataset is future work.

Usage:
    export ANTHROPIC_API_KEY=sk-...
    cd backend && python ../evaluation/run_extraction_eval.py
"""
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from metrics import compare_fields, summarize  # noqa: E402

from app.ai import get_llm_provider  # noqa: E402
from app.core.config import get_settings  # noqa: E402

DATASET_PATH = Path(__file__).resolve().parent / "extraction_cases.jsonl"


def load_cases() -> list[dict]:
    with DATASET_PATH.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> None:
    settings = get_settings()
    if not settings.anthropic_api_key:
        print("ANTHROPIC_API_KEY is not set — cannot run a real-model evaluation.")
        sys.exit(1)

    provider = get_llm_provider()
    cases = load_cases()

    all_field_results = []
    per_case_reports = []

    for case in cases:
        predicted = provider.extract_case_fields(case["text"]).model_dump()
        field_results = compare_fields(case["expected"], predicted)
        all_field_results.append(field_results)
        per_case_reports.append(
            {
                "id": case["id"],
                "mismatches": {f: r for f, r in field_results.items() if not r["match"]},
            }
        )

    summary = summarize(all_field_results)

    print("=" * 50)
    print("PHARMATRIAGE EXTRACTION EVALUATION")
    print("=" * 50)
    print(f"Provider:          {provider.provider_name}")
    print(f"Model:             {provider.model_version}")
    print(f"Cases:             {len(cases)}")
    print(f"Overall accuracy:  {summary['overall_accuracy']:.1%}")
    print()
    print("Per-field accuracy:")
    for field, accuracy in sorted(summary["per_field_accuracy"].items()):
        print(f"  {field:35s} {accuracy:.1%}")
    print()
    for report in per_case_reports:
        if report["mismatches"]:
            print(f"Mismatches in {report['id']}:")
            for field, r in report["mismatches"].items():
                print(f"  {field}: expected={r['expected']!r} predicted={r['predicted']!r}")

    reports_dir = Path(__file__).resolve().parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    out_file = reports_dir / "latest_result.json"
    out_file.write_text(
        json.dumps({"summary": summary, "cases": per_case_reports}, indent=2),
        encoding="utf-8",
    )
    print(f"\nFull report written to {out_file}")


if __name__ == "__main__":
    main()
