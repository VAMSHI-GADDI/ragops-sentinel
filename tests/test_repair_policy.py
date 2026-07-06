from ragops.retrieval.types import RetrievedEvidence
from ragops.sentinel.failure_classifier import RuleBasedFailureClassifier
from ragops.sentinel.repair import make_repair_decision


def test_stale_evidence_maps_to_temporal_repair():
    evidence = [
        RetrievedEvidence(
            chunk_id="c1",
            text="Old policy text says retention is 7 days.",
            score=0.5,
            document_id="policy",
            version_id="policy:old",
            section_title="Retention",
            freshness_score=0.25,
        )
    ]
    diagnosis = RuleBasedFailureClassifier().diagnose("retention policy", evidence, "retention is 7 days")
    decision = make_repair_decision(diagnosis)
    assert diagnosis.failure_code == "F2_STALE_DOCUMENT"
    assert decision.action == "TEMPORAL_FILTER_RETRIEVAL"
    assert decision.should_retrieve_again is True
    assert decision.latest_only is True
    assert decision.should_regenerate is True


def test_no_failure_maps_to_no_repair():
    evidence = [
        RetrievedEvidence(
            chunk_id="c2",
            text="Current policy says retention is 90 days.",
            score=0.5,
            document_id="policy",
            version_id="policy:current",
            section_title="Retention",
            freshness_score=1.0,
        )
    ]
    diagnosis = RuleBasedFailureClassifier().diagnose("retention policy", evidence, "retention is 90 days")
    decision = make_repair_decision(diagnosis)
    assert diagnosis.failure_detected is False
    assert decision.action == "NO_REPAIR"
    assert decision.should_retrieve_again is False
