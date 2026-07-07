from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class CitationPolicyResult:
    is_allowed: bool
    citation_count: int
    reason: str


def validate_citation_policy(answer: str, citation_markers: list[str] | None = None) -> CitationPolicyResult:
    markers = citation_markers or []

    inline_marker_count = answer.count("[citation:") + answer.count("source:")
    citation_count = len(markers) + inline_marker_count

    if citation_count <= 0:
        return CitationPolicyResult(
            is_allowed=False,
            citation_count=0,
            reason="missing_citations",
        )

    return CitationPolicyResult(
        is_allowed=True,
        citation_count=citation_count,
        reason="allowed",
    )


def validate_citation_policy_dict(answer: str, citation_markers: list[str] | None = None) -> dict[str, object]:
    return asdict(validate_citation_policy(answer, citation_markers))
