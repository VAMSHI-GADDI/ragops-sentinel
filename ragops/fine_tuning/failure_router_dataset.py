from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any


REQUIRED_FIELDS = {
    "id",
    "query",
    "evidence_summary",
    "metrics",
    "failure_code",
    "repair_action",
    "target",
}


@dataclass(frozen=True)
class FailureRouterExample:
    id: str
    query: str
    evidence_summary: str
    metrics: dict[str, Any]
    failure_code: str
    repair_action: str
    target: str


def load_failure_router_dataset(path: str | Path) -> list[FailureRouterExample]:
    dataset_path = Path(path)
    examples: list[FailureRouterExample] = []

    with dataset_path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue

            payload = json.loads(line)
            missing = REQUIRED_FIELDS - set(payload)

            if missing:
                raise ValueError(
                    f"Line {line_number} is missing required fields: {sorted(missing)}"
                )

            examples.append(
                FailureRouterExample(
                    id=str(payload["id"]),
                    query=str(payload["query"]),
                    evidence_summary=str(payload["evidence_summary"]),
                    metrics=dict(payload["metrics"]),
                    failure_code=str(payload["failure_code"]),
                    repair_action=str(payload["repair_action"]),
                    target=str(payload["target"]),
                )
            )

    return examples


def format_failure_router_prompt(example: FailureRouterExample) -> str:
    metrics_json = json.dumps(example.metrics, sort_keys=True)

    return (
        "You are a RAG failure router. Given a user query, evidence summary, "
        "and evaluation metrics, predict the failure code and repair action.\n\n"
        f"Query: {example.query}\n"
        f"Evidence Summary: {example.evidence_summary}\n"
        f"Metrics: {metrics_json}\n\n"
        "Return format: FAILURE_CODE -> REPAIR_ACTION"
    )


def to_instruction_tuning_record(example: FailureRouterExample) -> dict[str, str]:
    return {
        "instruction": format_failure_router_prompt(example),
        "response": example.target,
    }


def validate_failure_router_dataset(path: str | Path) -> dict[str, object]:
    errors: list[str] = []
    examples = load_failure_router_dataset(path)

    if len(examples) < 10:
        errors.append("Dataset should contain at least 10 examples for this milestone.")

    ids = [example.id for example in examples]
    if len(ids) != len(set(ids)):
        errors.append("Dataset contains duplicate IDs.")

    failure_codes = {example.failure_code for example in examples}
    repair_actions = {example.repair_action for example in examples}

    required_failure_codes = {
        "NO_FAILURE",
        "F2_STALE_DOCUMENT",
        "F12_MISSING_CITATION",
        "F20_PROMPT_INJECTION",
        "F21_UNSAFE_TOOL_CALL",
        "F22_UNTRUSTED_SOURCE",
        "F23_PII_DETECTED",
    }

    required_repair_actions = {
        "NO_REPAIR",
        "TEMPORAL_FILTER_RETRIEVAL",
        "REQUIRE_CITATIONS",
        "BLOCK_OR_HUMAN_REVIEW",
        "BLOCK_TOOL_CALL",
        "RETRIEVE_ALLOWLISTED_SOURCES",
        "REDACT_PII",
    }

    missing_codes = required_failure_codes - failure_codes
    missing_actions = required_repair_actions - repair_actions

    if missing_codes:
        errors.append(f"Missing failure codes: {sorted(missing_codes)}")

    if missing_actions:
        errors.append(f"Missing repair actions: {sorted(missing_actions)}")

    for example in examples:
        expected_target = f"{example.failure_code} -> {example.repair_action}"
        if example.target != expected_target:
            errors.append(
                f"{example.id} target mismatch: expected {expected_target!r}, got {example.target!r}"
            )

    return {
        "milestone": "M15_LORA_PEFT_FINE_TUNING_READY_WORKFLOW",
        "dataset_path": str(Path(path)),
        "example_count": len(examples),
        "failure_codes": sorted(failure_codes),
        "repair_actions": sorted(repair_actions),
        "instruction_record_preview": to_instruction_tuning_record(examples[0]) if examples else None,
        "passed": not errors,
        "errors": errors,
    }
