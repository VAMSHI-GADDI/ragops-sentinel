from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

from ragops.retrieval.types import RetrievedEvidence


@dataclass
class EvidenceDriftFeatures:
    retrieved_chunks: int
    stale_chunks: int
    latest_chunks: int
    stale_evidence_rate: float
    wrong_version_detected: bool
    conflicting_versions_detected: bool
    retrieved_version_ids: list[str]
    retrieved_document_ids: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_evidence_drift_features(evidence: list[RetrievedEvidence]) -> EvidenceDriftFeatures:
    total = len(evidence)
    stale = sum(1 for ev in evidence if ev.freshness_score < 1.0)
    latest = total - stale
    version_ids = [ev.version_id for ev in evidence]
    document_ids = [ev.document_id for ev in evidence]

    # A lightweight baseline signal: if the same document appears through more
    # than one version in a single evidence set, the answer is at risk of mixing
    # stale/current claims even when one chunk is relevant.
    versions_by_doc: dict[str, set[str]] = {}
    for ev in evidence:
        versions_by_doc.setdefault(ev.document_id, set()).add(ev.version_id)

    conflicting_versions = any(len(versions) > 1 for versions in versions_by_doc.values())
    rate = stale / total if total else 0.0
    return EvidenceDriftFeatures(
        retrieved_chunks=total,
        stale_chunks=stale,
        latest_chunks=latest,
        stale_evidence_rate=rate,
        wrong_version_detected=stale > 0,
        conflicting_versions_detected=conflicting_versions,
        retrieved_version_ids=version_ids,
        retrieved_document_ids=document_ids,
    )
