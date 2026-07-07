from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from ragops.security.citation_policy import CitationPolicyResult, validate_citation_policy
from ragops.security.pii_redaction import PIIRedactionResult, redact_pii
from ragops.security.prompt_injection import PromptInjectionResult, detect_prompt_injection
from ragops.security.source_policy import SourcePolicyResult, validate_source_group
from ragops.security.tool_policy import ToolPolicyResult, validate_tool_call


@dataclass(frozen=True)
class SecurityAssessment:
    query_prompt_injection: PromptInjectionResult
    query_pii: PIIRedactionResult
    answer_pii: PIIRedactionResult
    citation_policy: CitationPolicyResult
    source_policy_results: list[SourcePolicyResult]
    tool_policy_results: list[ToolPolicyResult]
    is_allowed: bool
    requires_human_review: bool
    reasons: list[str]


def evaluate_rag_security(
    *,
    query: str,
    answer: str,
    source_groups: list[str | None] | None = None,
    tool_calls: list[dict[str, Any]] | None = None,
    citation_markers: list[str] | None = None,
) -> SecurityAssessment:
    injection = detect_prompt_injection(query)
    query_pii = redact_pii(query)
    answer_pii = redact_pii(answer)
    citation_policy = validate_citation_policy(answer, citation_markers)

    source_results = [
        validate_source_group(source_group) for source_group in (source_groups or [])
    ]

    tool_results = [
        validate_tool_call(
            tool_name=str(tool_call.get("tool_name", "")),
            arguments=tool_call.get("arguments", {}),
        )
        for tool_call in (tool_calls or [])
    ]

    reasons: list[str] = []

    if injection.recommended_action == "block_or_human_review":
        reasons.append("prompt_injection_risk")

    if query_pii.redaction_count > 0:
        reasons.append("query_contains_pii")

    if answer_pii.redaction_count > 0:
        reasons.append("answer_contains_pii")

    if not citation_policy.is_allowed:
        reasons.append("citation_policy_failed")

    for source_result in source_results:
        if not source_result.is_allowed:
            reasons.append(f"source_policy_failed:{source_result.reason}")

    for tool_result in tool_results:
        if not tool_result.is_allowed:
            reasons.append(f"tool_policy_failed:{tool_result.reason}")

    blocking_reasons = [
        reason
        for reason in reasons
        if reason.startswith("prompt_injection_risk")
        or reason.startswith("citation_policy_failed")
        or reason.startswith("source_policy_failed")
        or reason.startswith("tool_policy_failed")
    ]

    return SecurityAssessment(
        query_prompt_injection=injection,
        query_pii=query_pii,
        answer_pii=answer_pii,
        citation_policy=citation_policy,
        source_policy_results=source_results,
        tool_policy_results=tool_results,
        is_allowed=not blocking_reasons,
        requires_human_review=bool(reasons),
        reasons=reasons,
    )


def evaluate_rag_security_dict(**kwargs: Any) -> dict[str, Any]:
    return asdict(evaluate_rag_security(**kwargs))
