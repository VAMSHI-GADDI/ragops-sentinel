from __future__ import annotations

from dataclasses import dataclass, asdict
import re


@dataclass(frozen=True)
class PromptInjectionResult:
    is_suspicious: bool
    risk_score: float
    matched_patterns: list[str]
    recommended_action: str


PROMPT_INJECTION_PATTERNS: dict[str, str] = {
    "ignore_previous_instructions": r"\b(ignore|forget|disregard)\b.{0,40}\b(previous|prior|above|system)\b.{0,30}\b(instructions|rules|prompt)\b",
    "reveal_system_prompt": r"\b(reveal|show|print|dump|leak)\b.{0,40}\b(system prompt|developer message|hidden instructions|internal rules)\b",
    "jailbreak_roleplay": r"\b(DAN|do anything now|jailbreak|developer mode|god mode)\b",
    "disable_safety": r"\b(disable|bypass|turn off|remove)\b.{0,40}\b(safety|guardrails|filters|policy|security)\b",
    "tool_exfiltration": r"\b(call|use|invoke|run)\b.{0,40}\b(tool|function|shell|terminal|powershell|bash)\b.{0,40}\b(secret|token|key|credential|env)\b",
    "instruction_override": r"\b(new instruction|override instruction|you must obey|highest priority)\b",
    "data_exfiltration": r"\b(exfiltrate|steal|leak|dump)\b.{0,40}\b(data|database|emails|files|secrets|credentials)\b",
}


def detect_prompt_injection(text: str) -> PromptInjectionResult:
    normalized = " ".join(text.lower().split())
    matched: list[str] = []

    for label, pattern in PROMPT_INJECTION_PATTERNS.items():
        if re.search(pattern, normalized, flags=re.IGNORECASE):
            matched.append(label)

    risk_score = min(1.0, 0.25 * len(matched))

    if risk_score >= 0.50:
        action = "block_or_human_review"
    elif risk_score > 0:
        action = "allow_with_caution"
    else:
        action = "allow"

    return PromptInjectionResult(
        is_suspicious=bool(matched),
        risk_score=risk_score,
        matched_patterns=matched,
        recommended_action=action,
    )


def detect_prompt_injection_dict(text: str) -> dict[str, object]:
    return asdict(detect_prompt_injection(text))
