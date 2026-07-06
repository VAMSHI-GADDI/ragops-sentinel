from pathlib import Path
import json

from ragops.observability.snapshot import build_observability_snapshot


def test_observability_snapshot_passes_for_good_repair_result(tmp_path: Path):
    result_path = tmp_path / "repair.json"
    result_path.write_text(json.dumps({
        "summary": {
            "num_examples": 2,
            "repair_success_rate": 1.0,
            "before_mean_stale_evidence_rate": 0.2,
            "after_mean_stale_evidence_rate": 0.0,
            "after_mean_context_recall": 1.0,
            "after_mean_unsupported_claim_rate": 0.1,
            "mean_latency_ms": 100.0,
        },
        "examples": [{"latency_ms": 90.0}, {"latency_ms": 110.0}],
    }), encoding="utf-8")

    snapshot = build_observability_snapshot(result_path)
    assert snapshot["passed"] is True
    assert snapshot["summary"]["stale_evidence_rate_reduction"] == 0.2
    assert len(snapshot["slo_checks"]) >= 5


def test_observability_snapshot_fails_for_high_stale_rate(tmp_path: Path):
    result_path = tmp_path / "repair.json"
    result_path.write_text(json.dumps({
        "summary": {
            "num_examples": 1,
            "repair_success_rate": 0.0,
            "before_mean_stale_evidence_rate": 0.2,
            "after_mean_stale_evidence_rate": 0.2,
            "after_mean_context_recall": 0.5,
            "after_mean_unsupported_claim_rate": 0.5,
            "mean_latency_ms": 9000.0,
        },
        "examples": [{"latency_ms": 9000.0}],
    }), encoding="utf-8")

    snapshot = build_observability_snapshot(result_path)
    assert snapshot["passed"] is False
    failed = [check for check in snapshot["slo_checks"] if not check["passed"]]
    assert failed
