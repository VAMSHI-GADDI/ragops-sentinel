from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean
import json
from typing import Any


@dataclass
class SLOCheck:
    name: str
    value: float
    threshold: float
    comparator: str
    passed: bool
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _leq(value: float, threshold: float) -> bool:
    return value <= threshold


def _geq(value: float, threshold: float) -> bool:
    return value >= threshold


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_observability_snapshot(repair_result_path: Path, output_path: Path | None = None) -> dict[str, Any]:
    """Build an auditable observability snapshot from a repair benchmark result.

    Milestone 6 keeps this offline and deterministic so the dashboard logic can
    be tested without requiring Grafana/Prometheus in CI. The API still exposes
    live Prometheus metrics through /metrics.
    """
    payload = _load_json(repair_result_path)
    summary = payload.get("summary", {})
    examples = payload.get("examples", [])

    before_stale = float(summary.get("before_mean_stale_evidence_rate", 0.0))
    after_stale = float(summary.get("after_mean_stale_evidence_rate", 0.0))
    repair_success_rate = float(summary.get("repair_success_rate", 0.0))
    after_unsupported = float(summary.get("after_mean_unsupported_claim_rate", 0.0))
    after_recall = float(summary.get("after_mean_context_recall", 0.0))
    mean_latency_ms = float(summary.get("mean_latency_ms", 0.0))

    stale_reduction = before_stale - after_stale
    repair_latencies = [float(ex.get("latency_ms", 0.0)) for ex in examples]
    p95_latency_ms = max(repair_latencies) if len(repair_latencies) <= 2 else sorted(repair_latencies)[int(0.95 * (len(repair_latencies) - 1))]
    mean_graph_or_repair_latency = mean(repair_latencies) if repair_latencies else mean_latency_ms

    slo_checks = [
        SLOCheck(
            name="post_repair_stale_evidence_rate",
            value=round(after_stale, 4),
            threshold=0.05,
            comparator="<=",
            passed=_leq(after_stale, 0.05),
            rationale="After repair, stale evidence should be close to zero in the controlled drift benchmark.",
        ),
        SLOCheck(
            name="repair_success_rate",
            value=round(repair_success_rate, 4),
            threshold=0.80,
            comparator=">=",
            passed=_geq(repair_success_rate, 0.80),
            rationale="Targeted repair should succeed for most labeled stale-evidence failures.",
        ),
        SLOCheck(
            name="post_repair_context_recall",
            value=round(after_recall, 4),
            threshold=0.90,
            comparator=">=",
            passed=_geq(after_recall, 0.90),
            rationale="Repair should not remove required supporting context.",
        ),
        SLOCheck(
            name="post_repair_unsupported_claim_rate",
            value=round(after_unsupported, 4),
            threshold=0.25,
            comparator="<=",
            passed=_leq(after_unsupported, 0.25),
            rationale="Repair should not increase unsupported claims beyond a conservative baseline threshold.",
        ),
        SLOCheck(
            name="mean_repair_latency_ms",
            value=round(mean_graph_or_repair_latency, 2),
            threshold=5000.0,
            comparator="<=",
            passed=_leq(mean_graph_or_repair_latency, 5000.0),
            rationale="Local repair should stay within an interactive debugging budget on a small benchmark.",
        ),
    ]

    snapshot = {
        "milestone": "M6_OBSERVABILITY",
        "source_result": str(repair_result_path),
        "summary": {
            "examples": int(summary.get("num_examples", len(examples))),
            "before_mean_stale_evidence_rate": round(before_stale, 4),
            "after_mean_stale_evidence_rate": round(after_stale, 4),
            "stale_evidence_rate_reduction": round(stale_reduction, 4),
            "repair_success_rate": round(repair_success_rate, 4),
            "after_mean_context_recall": round(after_recall, 4),
            "after_mean_unsupported_claim_rate": round(after_unsupported, 4),
            "mean_repair_latency_ms": round(mean_graph_or_repair_latency, 2),
            "p95_repair_latency_ms": round(p95_latency_ms, 2),
        },
        "slo_checks": [check.to_dict() for check in slo_checks],
        "passed": all(check.passed for check in slo_checks),
        "dashboard_panels": [
            "RAG query latency",
            "Retrieval latency",
            "Stale evidence rate",
            "Failure count by code",
            "Repair attempts by action/success",
            "Repair latency",
            "Unsupported claim rate",
            "Context precision/recall",
        ],
    }
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return snapshot
