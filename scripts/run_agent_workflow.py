from __future__ import annotations

import argparse
import json
from typing import Any

from ragops.agents.langgraph_workflow import run_ragops_agent
from ragops.db import get_session, init_db
from ragops.retrieval.vector_qdrant import QdrantRetriever


def _json_default(value: Any) -> Any:
    if hasattr(value, "__dict__"):
        return value.__dict__
    return str(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the M10 LangGraph RAGOps agent workflow.")
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--latest-only", action="store_true")
    args = parser.parse_args()

    init_db()
    retriever = QdrantRetriever()
    retriever.ensure_collection()

    session = next(get_session())
    result = run_ragops_agent(
        session=session,
        retriever=retriever,
        query=args.query,
        top_k=args.top_k,
        latest_only=args.latest_only,
    )

    payload = {
        "milestone": "M10_LANGGRAPH_AGENT_WORKFLOW",
        "query": result.get("query"),
        "agent_path": result.get("agent_path"),
        "repair_applied": result.get("repair_applied"),
        "human_review_required": result.get("human_review_required"),
        "diagnosis": result.get("diagnosis"),
        "final_answer": result.get("final_answer"),
    }

    print(json.dumps(payload, indent=2, default=_json_default))


if __name__ == "__main__":
    main()
