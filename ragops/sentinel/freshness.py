from __future__ import annotations
from ragops.retrieval.types import RetrievedEvidence


def stale_evidence_rate(evidence: list[RetrievedEvidence]) -> float:
    if not evidence:
        return 0.0
    stale = sum(1 for ev in evidence if ev.freshness_score < 1.0)
    return stale / len(evidence)
