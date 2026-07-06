from __future__ import annotations
from ragops.sentinel.failure_classifier import Diagnosis


def choose_repair(diagnosis: Diagnosis) -> str:
    """Transparent Milestone-5 repair policy.

    This is deliberately rule-based. The purpose is not to claim a learned repair
    policy yet; it creates a measurable baseline for targeted repair experiments.
    """
    if not diagnosis.failure_detected:
        return "NO_REPAIR"
    return diagnosis.recommended_repair or "FULL_RERUN"
