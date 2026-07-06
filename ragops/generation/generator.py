from __future__ import annotations
from ragops.retrieval.types import RetrievedEvidence


class ExtractiveBaselineGenerator:
    """Citation-preserving baseline answer generator.

    This avoids paid API dependencies for Milestone 1. Later milestones can swap in
    a stronger LLM while keeping the same evidence/citation interface.
    """

    def generate(self, query: str, evidence: list[RetrievedEvidence]) -> str:
        if not evidence:
            return "I do not have enough indexed evidence to answer this question."

        snippets = []
        for idx, ev in enumerate(evidence[:3], start=1):
            compact = " ".join(ev.text.split())
            snippets.append(f"[{idx}] {compact[:450]}")

        return (
            "Baseline answer generated from retrieved evidence. "
            "The most relevant indexed evidence suggests:\n\n"
            + "\n\n".join(snippets)
            + "\n\nThis baseline does not claim full semantic reasoning yet; use the citations and diagnosis fields for validation."
        )
