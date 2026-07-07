from __future__ import annotations

from dataclasses import dataclass, asdict


DEFAULT_ALLOWED_SOURCE_GROUPS = {
    "raw_docs",
    "drift_fixture",
    "evaluation_data",
    "research_artifacts",
}


@dataclass(frozen=True)
class SourcePolicyResult:
    is_allowed: bool
    source_group: str | None
    reason: str


def validate_source_group(
    source_group: str | None,
    *,
    allowed_source_groups: set[str] | None = None,
) -> SourcePolicyResult:
    allowed = allowed_source_groups or DEFAULT_ALLOWED_SOURCE_GROUPS

    if not source_group:
        return SourcePolicyResult(
            is_allowed=False,
            source_group=source_group,
            reason="missing_source_group",
        )

    if source_group not in allowed:
        return SourcePolicyResult(
            is_allowed=False,
            source_group=source_group,
            reason="source_group_not_allowlisted",
        )

    return SourcePolicyResult(
        is_allowed=True,
        source_group=source_group,
        reason="allowed",
    )


def validate_source_group_dict(source_group: str | None) -> dict[str, object]:
    return asdict(validate_source_group(source_group))
