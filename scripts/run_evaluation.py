from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from statistics import mean

# Make the script runnable from a fresh checkout on Windows without requiring
# users to set PYTHONPATH manually.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ragops.db import SessionLocal, init_db
from ragops.evaluation.rag_metrics import evaluate_example
from ragops.evaluation.types import EvaluationExample
from ragops.generation.generator import ExtractiveBaselineGenerator
from ragops.observability.mlflow_logger import log_query_run
from ragops.retrieval.vector_qdrant import QdrantRetriever
from ragops.sentinel.failure_classifier import RuleBasedFailureClassifier


def load_examples(path: Path) -> list[EvaluationExample]:
    examples: list[EvaluationExample] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            examples.append(EvaluationExample(**row))
    return examples


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic baseline RAG evaluation.")
    parser.add_argument("--eval-set", default="data/eval/baseline_eval_set.jsonl")
    parser.add_argument("--output", default="experiments/results/m2_baseline_eval.json")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--latest-only", action="store_true")
    args = parser.parse_args()

    init_db()
    retriever = QdrantRetriever()
    retriever.ensure_collection()
    generator = ExtractiveBaselineGenerator()
    classifier = RuleBasedFailureClassifier()
    examples = load_examples(Path(args.eval_set))

    results = []
    with SessionLocal() as session:
        for example in examples:
            evidence = retriever.search(session, example.query, top_k=args.top_k, latest_only=args.latest_only)
            answer = generator.generate(example.query, evidence)
            diagnosis = classifier.diagnose(example.query, evidence, answer)
            scores = evaluate_example(example, evidence, answer, diagnosis)
            results.append(scores.to_dict())
            print(json.dumps(scores.to_dict(), indent=2))

    labeled = [r for r in results if r.get("diagnosis_correct") is not None]
    aggregate = {
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

    payload = {"aggregate": aggregate, "examples": results}
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("\nAggregate:")
    print(json.dumps(aggregate, indent=2))
    print(f"Wrote {output_path}")

    log_query_run(aggregate, params={"phase": "m2_evaluation", "top_k": args.top_k, "latest_only": args.latest_only})


if __name__ == "__main__":
    main()
