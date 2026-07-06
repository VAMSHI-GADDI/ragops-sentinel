from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from statistics import mean

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ragops.db import SessionLocal, init_db
from ragops.evaluation.types import EvaluationExample
from ragops.sentinel.repair import apply_repair_for_example


def load_examples(path: Path) -> list[EvaluationExample]:
    examples: list[EvaluationExample] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(EvaluationExample(**json.loads(line)))
    return examples


def summarize(results: list[dict]) -> dict:
    if not results:
        return {"num_examples": 0}

    before = [r["before_metrics"] for r in results]
    after = [r["after_metrics"] for r in results]
    deltas = [r["deltas"] for r in results]

    return {
        "num_examples": len(results),
        "repairs_applied": sum(1 for r in results if r["repair_applied"]),
        "repair_successes": sum(1 for r in results if r["repair_success"]),
        "repair_success_rate": round(mean(1.0 if r["repair_success"] else 0.0 for r in results), 4),
        "before_mean_stale_evidence_rate": round(mean(float(r["stale_evidence_rate"]) for r in before), 4),
        "after_mean_stale_evidence_rate": round(mean(float(r["stale_evidence_rate"]) for r in after), 4),
        "before_total_stale_chunks": sum(int(r.get("stale_chunks", 0)) for r in before),
        "after_total_stale_chunks": sum(int(r.get("stale_chunks", 0)) for r in after),
        "mean_stale_evidence_rate_delta": round(mean(float(r["stale_evidence_rate_delta"]) for r in deltas), 4),
        "stale_chunk_reduction": sum(int(r.get("stale_chunks", 0)) for r in before) - sum(int(r.get("stale_chunks", 0)) for r in after),
        "before_mean_context_precision": round(mean(float(r["context_precision"]) for r in before), 4),
        "after_mean_context_precision": round(mean(float(r["context_precision"]) for r in after), 4),
        "before_mean_context_recall": round(mean(float(r["context_recall"]) for r in before), 4),
        "after_mean_context_recall": round(mean(float(r["context_recall"]) for r in after), 4),
        "before_mean_faithfulness": round(mean(float(r["faithfulness"]) for r in before), 4),
        "after_mean_faithfulness": round(mean(float(r["faithfulness"]) for r in after), 4),
        "before_mean_unsupported_claim_rate": round(mean(float(r["unsupported_claim_rate"]) for r in before), 4),
        "after_mean_unsupported_claim_rate": round(mean(float(r["unsupported_claim_rate"]) for r in after), 4),
        "mean_latency_ms": round(mean(float(r["latency_ms"]) for r in results), 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Milestone-5 targeted repair benchmark.")
    parser.add_argument("--eval-set", default="data/eval/evidence_drift_eval_set.jsonl")
    parser.add_argument("--output", default="experiments/results/m5_repair_benchmark.json")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    init_db()
    examples = load_examples(Path(args.eval_set))
    results: list[dict] = []
    with SessionLocal() as session:
        for example in examples:
            result = apply_repair_for_example(session, example, top_k=args.top_k).to_dict()
            results.append(result)
            print(json.dumps({
                "example_id": example.example_id,
                "action": result["action"],
                "repair_applied": result["repair_applied"],
                "repair_success": result["repair_success"],
                "before_stale_evidence_rate": result["before_metrics"]["stale_evidence_rate"],
                "after_stale_evidence_rate": result["after_metrics"]["stale_evidence_rate"],
                "stale_chunk_delta": result["deltas"]["stale_chunk_delta"],
                "before_failure_code": result["before_diagnosis"]["failure_code"],
                "after_failure_code": result["after_diagnosis"]["failure_code"],
            }, indent=2))

    payload = {"summary": summarize(results), "examples": results}
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("Aggregate:")
    print(json.dumps(payload["summary"], indent=2))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
