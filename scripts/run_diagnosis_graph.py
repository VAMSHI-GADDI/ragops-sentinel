from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ragops.db import SessionLocal, init_db
from ragops.evaluation.rag_metrics import evaluate_example
from ragops.evaluation.types import EvaluationExample
from ragops.generation.generator import ExtractiveBaselineGenerator
from ragops.retrieval.vector_qdrant import QdrantRetriever
from ragops.sentinel.diagnosis_graph import build_diagnosis_graph
from ragops.sentinel.failure_classifier import RuleBasedFailureClassifier


def load_examples(path: Path) -> list[EvaluationExample]:
    examples: list[EvaluationExample] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(EvaluationExample(**json.loads(line)))
    return examples


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Sentinel Diagnosis Graph artifacts for evaluation examples.")
    parser.add_argument("--eval-set", default="data/eval/evidence_drift_eval_set.jsonl")
    parser.add_argument("--output-dir", default="experiments/diagnosis_graphs")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--latest-only", action="store_true")
    args = parser.parse_args()

    init_db()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    retriever = QdrantRetriever()
    generator = ExtractiveBaselineGenerator()
    classifier = RuleBasedFailureClassifier()
    graphs = []

    with SessionLocal() as session:
        for idx, example in enumerate(load_examples(Path(args.eval_set)), start=1):
            evidence = retriever.search(session, example.query, top_k=args.top_k, latest_only=args.latest_only)
            answer = generator.generate(example.query, evidence)
            diagnosis = classifier.diagnose(example.query, evidence, answer)
            evaluation = evaluate_example(example, evidence, answer, diagnosis)
            query_id = f"eval_query_{idx:03d}_{example.example_id}"
            answer_id = f"eval_answer_{idx:03d}_{example.example_id}"
            graph = build_diagnosis_graph(
                query_id=query_id,
                answer_id=answer_id,
                query_text=example.query,
                answer_text=answer,
                evidence=evidence,
                diagnosis=diagnosis,
                retrieval_run_id=f"eval_retrieval_{idx:03d}_{example.example_id}",
                metrics={"top_k": float(args.top_k), "latest_only": float(bool(args.latest_only))},
                evaluation=evaluation,
            )
            graph_json_path = output_dir / f"{example.example_id}.json"
            graph_dot_path = output_dir / f"{example.example_id}.dot"
            graph_json_path.write_text(json.dumps(graph.to_dict(), indent=2), encoding="utf-8")
            graph_dot_path.write_text(graph.to_dot(), encoding="utf-8")
            graphs.append(graph.summary)
            print(json.dumps(graph.summary, indent=2))

    manifest = {
        "num_graphs": len(graphs),
        "latest_only": bool(args.latest_only),
        "graphs": graphs,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {manifest_path}")


if __name__ == "__main__":
    main()
