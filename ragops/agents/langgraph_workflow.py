from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from ragops.generation.generator import ExtractiveBaselineGenerator
from ragops.retrieval.types import RetrievedEvidence
from ragops.sentinel.failure_classifier import RuleBasedFailureClassifier


class RAGOpsAgentState(TypedDict, total=False):
    query: str
    top_k: int
    latest_only: bool
    evidence: list[RetrievedEvidence]
    answer: str
    diagnosis: dict[str, Any]
    repair_applied: bool
    repair_action: str | None
    human_review_required: bool
    final_answer: str
    agent_path: list[str]


class RAGOpsAgentDependencies:
    def __init__(
        self,
        session: Any,
        retriever: Any,
        generator: ExtractiveBaselineGenerator | None = None,
        classifier: RuleBasedFailureClassifier | None = None,
    ) -> None:
        self.session = session
        self.retriever = retriever
        self.generator = generator or ExtractiveBaselineGenerator()
        self.classifier = classifier or RuleBasedFailureClassifier()


def _append_path(state: RAGOpsAgentState, node_name: str) -> list[str]:
    return [*state.get("agent_path", []), node_name]


def _diagnosis_to_dict(diagnosis: Any) -> dict[str, Any]:
    if is_dataclass(diagnosis):
        return asdict(diagnosis)

    return {
        "failure_detected": getattr(diagnosis, "failure_detected", False),
        "failure_code": getattr(diagnosis, "failure_code", None),
        "root_component": getattr(diagnosis, "root_component", None),
        "confidence": getattr(diagnosis, "confidence", 0.0),
        "recommended_repair": getattr(diagnosis, "recommended_repair", None),
        "evidence": getattr(diagnosis, "evidence", []),
    }


def build_ragops_agent_graph(deps: RAGOpsAgentDependencies):
    """Build a LangGraph workflow for RAGOps query diagnosis and repair.

    The workflow keeps the original deterministic RAGOps components intact:
    retrieval, extractive answer generation, rule-based diagnosis, and temporal
    repair. LangGraph is used as the orchestration layer rather than as a
    replacement for the existing reliability logic.
    """

    def retrieve_node(state: RAGOpsAgentState) -> RAGOpsAgentState:
        evidence = deps.retriever.search(
            deps.session,
            state["query"],
            top_k=int(state.get("top_k", 5)),
            latest_only=bool(state.get("latest_only", False)),
        )
        return {
            **state,
            "evidence": evidence,
            "agent_path": _append_path(state, "retrieve"),
        }

    def generate_node(state: RAGOpsAgentState) -> RAGOpsAgentState:
        answer = deps.generator.generate(state["query"], state.get("evidence", []))
        return {
            **state,
            "answer": answer,
            "agent_path": _append_path(state, "generate"),
        }

    def diagnose_node(state: RAGOpsAgentState) -> RAGOpsAgentState:
        diagnosis = deps.classifier.diagnose(
            state["query"],
            state.get("evidence", []),
            state.get("answer", ""),
        )
        diagnosis_payload = _diagnosis_to_dict(diagnosis)
        return {
            **state,
            "diagnosis": diagnosis_payload,
            "repair_action": diagnosis_payload.get("recommended_repair"),
            "agent_path": _append_path(state, "diagnose"),
        }

    def repair_node(state: RAGOpsAgentState) -> RAGOpsAgentState:
        evidence = deps.retriever.search(
            deps.session,
            state["query"],
            top_k=int(state.get("top_k", 5)),
            latest_only=True,
        )
        answer = deps.generator.generate(state["query"], evidence)
        diagnosis = deps.classifier.diagnose(state["query"], evidence, answer)
        return {
            **state,
            "latest_only": True,
            "evidence": evidence,
            "answer": answer,
            "diagnosis": _diagnosis_to_dict(diagnosis),
            "repair_applied": True,
            "agent_path": _append_path(state, "repair_temporal_filter"),
        }

    def human_review_node(state: RAGOpsAgentState) -> RAGOpsAgentState:
        return {
            **state,
            "human_review_required": True,
            "agent_path": _append_path(state, "human_review"),
        }

    def finalize_node(state: RAGOpsAgentState) -> RAGOpsAgentState:
        return {
            **state,
            "final_answer": state.get("answer", ""),
            "agent_path": _append_path(state, "finalize"),
        }

    def route_after_diagnosis(state: RAGOpsAgentState) -> str:
        diagnosis = state.get("diagnosis", {})
        failure_detected = bool(diagnosis.get("failure_detected", False))
        repair_action = diagnosis.get("recommended_repair")
        confidence = float(diagnosis.get("confidence", 0.0))

        if failure_detected and repair_action == "TEMPORAL_FILTER_RETRIEVAL" and not state.get("latest_only", False):
            return "repair"

        if failure_detected and confidence >= 0.90:
            return "review"

        return "final"

    graph = StateGraph(RAGOpsAgentState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_node("diagnose", diagnose_node)
    graph.add_node("repair", repair_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "diagnose")
    graph.add_conditional_edges(
        "diagnose",
        route_after_diagnosis,
        {
            "repair": "repair",
            "review": "human_review",
            "final": "finalize",
        },
    )
    graph.add_edge("repair", "finalize")
    graph.add_edge("human_review", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()


def run_ragops_agent(
    *,
    session: Any,
    retriever: Any,
    query: str,
    top_k: int = 5,
    latest_only: bool = False,
    generator: ExtractiveBaselineGenerator | None = None,
    classifier: RuleBasedFailureClassifier | None = None,
) -> dict[str, Any]:
    deps = RAGOpsAgentDependencies(
        session=session,
        retriever=retriever,
        generator=generator,
        classifier=classifier,
    )
    graph = build_ragops_agent_graph(deps)
    result = graph.invoke(
        {
            "query": query,
            "top_k": top_k,
            "latest_only": latest_only,
            "repair_applied": False,
            "human_review_required": False,
            "agent_path": [],
        }
    )
    return dict(result)
