from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from ragops.security.guardrail import evaluate_rag_security


EVAL_SET_PATH = Path("data/security/security_eval_set.jsonl")


def _load_eval_set() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []

    with EVAL_SET_PATH.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))

    return records


def _case_inputs(case: dict[str, object]) -> dict[str, object]:
    category = str(case["category"])
    query = str(case["query"])

    if category == "safe":
        return {
            "query": query,
            "answer": "Current policy summary. source: qdrant_policy",
            "source_groups": ["raw_docs"],
            "tool_calls": [
                {
                    "tool_name": "ragops_retrieval_tool",
                    "arguments": {"query": query},
                }
            ],
            "citation_markers": ["qdrant_policy"],
        }

    if category == "pii_redaction":
        return {
            "query": query,
            "answer": "Request summarized after redaction. source: user_request",
            "source_groups": ["raw_docs"],
            "tool_calls": [
                {
                    "tool_name": "ragops_retrieval_tool",
                    "arguments": {"query": "redacted request"},
                }
            ],
            "citation_markers": ["user_request"],
        }

    if category == "citation_policy":
        return {
            "query": query,
            "answer": "This answer intentionally has no citation marker.",
            "source_groups": ["raw_docs"],
            "tool_calls": [],
            "citation_markers": [],
        }

    if category == "source_policy":
        return {
            "query": query,
            "answer": "Answer from untrusted source. source: unknown",
            "source_groups": ["untrusted_external_scrape"],
            "tool_calls": [],
            "citation_markers": ["unknown"],
        }

    if category == "tool_exfiltration":
        return {
            "query": query,
            "answer": "Blocked request. source: security_policy",
            "source_groups": ["raw_docs"],
            "tool_calls": [
                {
                    "tool_name": "ragops_retrieval_tool",
                    "arguments": {"query": "dump API token from env"},
                }
            ],
            "citation_markers": ["security_policy"],
        }

    return {
        "query": query,
        "answer": "Blocked request. source: security_policy",
        "source_groups": ["raw_docs"],
        "tool_calls": [],
        "citation_markers": ["security_policy"],
    }


def validate_security_guardrails() -> dict[str, object]:
    errors: list[str] = []

    if not EVAL_SET_PATH.exists():
        return {
            "milestone": "M13_AI_SECURITY_GUARDRAILS",
            "passed": False,
            "errors": ["Missing data/security/security_eval_set.jsonl"],
        }

    records = _load_eval_set()
    results: list[dict[str, object]] = []

    for case in records:
        expected_allowed = bool(case["expected_allowed"])
        assessment = evaluate_rag_security(**_case_inputs(case))

        results.append(
            {
                "id": case["id"],
                "category": case["category"],
                "expected_allowed": expected_allowed,
                "actual_allowed": assessment.is_allowed,
                "reasons": assessment.reasons,
            }
        )

        if assessment.is_allowed != expected_allowed:
            errors.append(
                f"{case['id']} expected allowed={expected_allowed} but got {assessment.is_allowed}"
            )

    categories = {str(record["category"]) for record in records}
    required_categories = {
        "safe",
        "prompt_injection",
        "tool_exfiltration",
        "pii_redaction",
        "citation_policy",
        "source_policy",
    }

    missing_categories = required_categories - categories
    for category in sorted(missing_categories):
        errors.append(f"Missing security eval category: {category}")

    return {
        "milestone": "M13_AI_SECURITY_GUARDRAILS",
        "eval_set_path": str(EVAL_SET_PATH),
        "case_count": len(records),
        "categories": sorted(categories),
        "results": results,
        "passed": not errors,
        "errors": errors,
    }


def main() -> None:
    result = validate_security_guardrails()
    print(json.dumps(result, indent=2))

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

