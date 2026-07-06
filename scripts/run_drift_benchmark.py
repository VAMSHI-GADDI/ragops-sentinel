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
from ragops.evaluation.rag_metrics import evaluate_example
from ragops.evaluation.types import EvaluationExample
from ragops.generation.generator import ExtractiveBaselineGenerator
from ragops.retrieval.vector_qdrant import QdrantRetriever
from ragops.sentinel.failure_classifier import RuleBasedFailureClassifier


def load_examples(path: Path) -> list[EvaluationExample]:
    examples: list[EvaluationExample] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(EvaluationExample(**json.loads(line)))
    return examples


def summarize(results: list[dict]) -> dict:
    labeled = [r for r in results if r.get("diagnosis_correct") is not None]
    return {
        "num_examples": len(results),
        "mean_context_precision": round(mean(r["context_precision"] for r in results), 4) if results else 0.0,
        "mean_context_recall": round(mean(r["context_recall"] for r in results), 4) if results else 0.0,
        "mean_answer_relevance": round(mean(r["answer_relevance"] for r in results), 4) if results else 0.0,
        "mean_faithfulness": round(mean(r["faithfulness"] for r in results), 4) if results else 0.0,
        "mean_unsupported_claim_rate": round(mean(r["unsupported_claim_rate"] for r in results), 4) if results else 0.0,
        "mean_stale_evidence_rate": round(mean(r["stale_evidence_rate"] for r in results), 4) if results else 0.0,
        "total_stale_chunks": sum(int(r.get("stale_chunks", 0)) for r in results),
        "diagnosis_accuracy_on_labeled_failures": round(mean(1.0 if r["diagnosis_correct"] else 0.0 for r in labeled), 4) if labeled else None,
    }


def evaluate_mode(examples: list[EvaluationExample], latest_only: bool, top_k: int) -> tuple[dict, list[dict]]:
    retriever = QdrantRetriever()
    generator = ExtractiveBaselineGenerator()
    classifier = RuleBasedFailureClassifier()
    results: list[dict] = []
    with SessionLocal() as session:
        for example in examples:
            evidence = retriever.search(session, example.query, top_k=top_k, latest_only=latest_only)
            answer = generator.generate(example.query, evidence)
            diagnosis = classifier.diagnose(example.query, evidence, answer)
            scores = evaluate_example(example, evidence, answer, diagnosis).to_dict()
            scores["latest_only"] = latest_only
            scores["retrieved_version_ids"] = [ev.version_id for ev in evidence]
            scores["retrieved_freshness_scores"] = [ev.freshness_score for ev in evidence]
            results.append(scores)
    return summarize(results), results


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare stale-prone retrieval against temporal latest-only retrieval.")
    parser.add_argument("--eval-set", default="data/eval/evidence_drift_eval_set.jsonl")
    parser.add_argument("--output", default="experiments/results/m3_evidence_drift_benchmark.json")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    init_db()
    examples = load_examples(Path(args.eval_set))
    baseline_summary, baseline_results = evaluate_mode(examples, latest_only=False, top_k=args.top_k)
    temporal_summary, temporal_results = evaluate_mode(examples, latest_only=True, top_k=args.top_k)

    payload = {
        "baseline_no_temporal_filter": baseline_summary,
        "temporal_latest_only_filter": temporal_summary,
        "delta": {
            "stale_evidence_rate_reduction": round(
                baseline_summary["mean_stale_evidence_rate"] - temporal_summary["mean_stale_evidence_rate"], 4
            ),
            "stale_chunk_reduction": baseline_summary["total_stale_chunks"] - temporal_summary["total_stale_chunks"],
        },
        "examples": {
            "baseline_no_temporal_filter": baseline_results,
            "temporal_latest_only_filter": temporal_results,
        },
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["baseline_no_temporal_filter"], indent=2))
    print(json.dumps(payload["temporal_latest_only_filter"], indent=2))
    print("Delta:")
    print(json.dumps(payload["delta"], indent=2))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
