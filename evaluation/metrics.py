"""Field comparison helpers for the extraction evaluation harness.

Grading only covers fields the dataset makes a claim about (i.e. keys
present in `expected`) — a case that doesn't mention patient age says
nothing about what the model should predict for fields it wasn't asked
about, so those aren't scored.
"""
from collections import defaultdict


def _flatten(d: dict, prefix: str = "") -> dict:
    flat = {}
    for key, value in d.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(_flatten(value, path))
        else:
            flat[path] = value
    return flat


def _values_match(expected, predicted) -> bool:
    if expected is None and predicted is None:
        return True
    if expected is None or predicted is None:
        return False
    if isinstance(expected, str) and isinstance(predicted, str):
        e, p = expected.strip().lower(), predicted.strip().lower()
        return e == p or e in p or p in e
    return expected == predicted


def compare_fields(expected: dict, predicted: dict) -> dict:
    expected_flat = _flatten(expected)
    predicted_flat = _flatten(predicted)

    results = {}
    for field, expected_value in expected_flat.items():
        predicted_value = predicted_flat.get(field)
        results[field] = {
            "expected": expected_value,
            "predicted": predicted_value,
            "match": _values_match(expected_value, predicted_value),
        }
    return results


def summarize(all_field_results: list[dict]) -> dict:
    field_totals: dict[str, dict[str, int]] = defaultdict(lambda: {"correct": 0, "total": 0})
    for field_results in all_field_results:
        for field, result in field_results.items():
            field_totals[field]["total"] += 1
            if result["match"]:
                field_totals[field]["correct"] += 1

    per_field_accuracy = {
        field: totals["correct"] / totals["total"] for field, totals in field_totals.items()
    }
    overall_correct = sum(t["correct"] for t in field_totals.values())
    overall_total = sum(t["total"] for t in field_totals.values())
    return {
        "per_field_accuracy": per_field_accuracy,
        "overall_accuracy": overall_correct / overall_total if overall_total else 0.0,
    }
