from __future__ import annotations

from dataclasses import dataclass, asdict
import re


@dataclass(frozen=True)
class PIIRedactionResult:
    redacted_text: str
    findings: list[str]
    redaction_count: int


PII_PATTERNS: dict[str, tuple[str, str]] = {
    "email": (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[REDACTED_EMAIL]"),
    "us_phone": (r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]"),
    "ssn": (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]"),
    "credit_card_like": (r"\b(?:\d[ -]*?){13,16}\b", "[REDACTED_CARD]"),
    "api_key_like": (r"\b(?:sk|pk|api|key|token)[-_]?[A-Za-z0-9]{16,}\b", "[REDACTED_SECRET]"),
}


def redact_pii(text: str) -> PIIRedactionResult:
    redacted = text
    findings: list[str] = []
    count = 0

    for label, (pattern, replacement) in PII_PATTERNS.items():
        redacted, replacements = re.subn(pattern, replacement, redacted)
        if replacements:
            findings.append(label)
            count += replacements

    return PIIRedactionResult(
        redacted_text=redacted,
        findings=findings,
        redaction_count=count,
    )


def redact_pii_dict(text: str) -> dict[str, object]:
    return asdict(redact_pii(text))
