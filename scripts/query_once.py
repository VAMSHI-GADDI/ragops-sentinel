from __future__ import annotations
import argparse
import json
from ragops.db import SessionLocal, init_db
from ragops.generation.generator import ExtractiveBaselineGenerator
from ragops.retrieval.vector_qdrant import QdrantRetriever
from ragops.sentinel.failure_classifier import RuleBasedFailureClassifier


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one local query without FastAPI.")
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    init_db()
    retriever = QdrantRetriever()
    generator = ExtractiveBaselineGenerator()
    classifier = RuleBasedFailureClassifier()
    with SessionLocal() as session:
        evidence = retriever.search(session, args.query, top_k=args.top_k)
        answer = generator.generate(args.query, evidence)
        diagnosis = classifier.diagnose(args.query, evidence, answer)
        print(json.dumps({
            "answer": answer,
            "citations": [ev.__dict__ for ev in evidence],
            "diagnosis": diagnosis.__dict__,
        }, indent=2))


if __name__ == "__main__":
    main()
