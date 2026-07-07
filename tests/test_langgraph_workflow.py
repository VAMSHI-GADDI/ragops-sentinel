from __future__ import annotations

from ragops.agents.langchain_tools import (
    ragops_diagnosis_tool,
    ragops_repair_tool,
    ragops_retrieval_tool,
)
from ragops.agents.langgraph_workflow import run_ragops_agent
from ragops.retrieval.types import RetrievedEvidence


class FakeRetriever:
    def search(self, session, query: str, top_k: int = 5, latest_only: bool = False):
        if latest_only:
            return [
                RetrievedEvidence(
                    chunk_id="fresh_chunk_1",
                    text="Qdrant latest policy: use current indexed vectors and version-aware metadata.",
                    score=0.91,
                    document_id="qdrant_policy",
                    version_id="qdrant_policy:v2",
                    section_title="Latest policy",
                    freshness_score=1.0,
                )
            ]

        return [
            RetrievedEvidence(
                chunk_id="stale_chunk_1",
                text="Old Qdrant policy from a superseded document version.",
                score=0.88,
                document_id="qdrant_policy",
                version_id="qdrant_policy:v1",
                section_title="Old policy",
                freshness_score=0.25,
            )
        ]


def test_langgraph_agent_repairs_stale_evidence_path():
    result = run_ragops_agent(
        session=None,
        retriever=FakeRetriever(),
        query="What is the current Qdrant retrieval policy?",
        top_k=1,
    )

    assert result["repair_applied"] is True
    assert result["latest_only"] is True
    assert result["diagnosis"]["failure_detected"] is False
    assert result["agent_path"] == [
        "retrieve",
        "generate",
        "diagnose",
        "repair_temporal_filter",
        "finalize",
    ]
    assert "final_answer" in result
    assert result["final_answer"]


def test_langchain_tools_are_registered_and_callable():
    retrieval_result = ragops_retrieval_tool.invoke(
        {"query": "test query", "top_k": 3, "latest_only": True}
    )
    diagnosis_result = ragops_diagnosis_tool.invoke(
        {"failure_code": "F2_STALE_DOCUMENT", "confidence": 0.8}
    )
    repair_result = ragops_repair_tool.invoke(
        {"recommended_repair": "TEMPORAL_FILTER_RETRIEVAL"}
    )

    assert retrieval_result["tool"] == "ragops_retrieval_tool"
    assert retrieval_result["latest_only"] is True
    assert diagnosis_result["failure_code"] == "F2_STALE_DOCUMENT"
    assert repair_result["recommended_repair"] == "TEMPORAL_FILTER_RETRIEVAL"
