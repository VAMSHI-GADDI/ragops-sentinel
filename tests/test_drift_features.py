from ragops.retrieval.types import RetrievedEvidence
from ragops.sentinel.drift import compute_evidence_drift_features


def test_evidence_drift_features_detect_stale_and_multi_version_evidence():
    evidence = [
        RetrievedEvidence(
            chunk_id="doc:v1:c0",
            text="old",
            score=0.9,
            document_id="doc",
            version_id="doc:v1",
            section_title="old",
            freshness_score=0.25,
        ),
        RetrievedEvidence(
            chunk_id="doc:v2:c0",
            text="new",
            score=0.8,
            document_id="doc",
            version_id="doc:v2",
            section_title="new",
            freshness_score=1.0,
        ),
    ]
    features = compute_evidence_drift_features(evidence)
    assert features.stale_chunks == 1
    assert features.latest_chunks == 1
    assert features.stale_evidence_rate == 0.5
    assert features.wrong_version_detected is True
    assert features.conflicting_versions_detected is True
