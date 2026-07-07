from __future__ import annotations

from typing import Any

from langchain.tools import tool


@tool
def ragops_retrieval_tool(query: str, top_k: int = 5, latest_only: bool = False) -> dict[str, Any]:
    """Describe a RAGOps retrieval action for agent planning.

    This tool is intentionally metadata-only. The actual retrieval call is executed
    inside the LangGraph workflow so the system can keep SQLAlchemy/Qdrant objects
    outside the LLM-facing tool boundary.
    """
    return {
        "tool": "ragops_retrieval_tool",
        "query": query,
        "top_k": top_k,
        "latest_only": latest_only,
    }


@tool
def ragops_diagnosis_tool(failure_code: str | None, confidence: float) -> dict[str, Any]:
    """Describe a RAGOps diagnosis action for agent planning."""
    return {
        "tool": "ragops_diagnosis_tool",
        "failure_code": failure_code,
        "confidence": confidence,
    }


@tool
def ragops_repair_tool(recommended_repair: str | None) -> dict[str, Any]:
    """Describe a RAGOps repair action for agent planning."""
    return {
        "tool": "ragops_repair_tool",
        "recommended_repair": recommended_repair,
    }
