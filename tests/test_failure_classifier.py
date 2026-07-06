from ragops.sentinel.failure_classifier import RuleBasedFailureClassifier


def test_missing_evidence_failure():
    clf = RuleBasedFailureClassifier()
    diagnosis = clf.diagnose("test query", [], "no answer")
    assert diagnosis.failure_detected is True
    assert diagnosis.failure_code == "F1_MISSING_EVIDENCE"
