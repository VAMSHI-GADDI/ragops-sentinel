# Milestone 13 - AI Security / Guardrails

## Objective

Add deterministic AI security and guardrail checks to RAGOps Sentinel.

## Added Capabilities

- Prompt-injection detection
- PII redaction
- Source allowlisting
- Safe tool-call policy
- Citation-required answer policy
- Combined RAG security assessment
- Security evaluation set
- Guardrail validation script
- Unit tests for security controls

## Skills Demonstrated

- AI security
- Prompt-injection defense
- PII redaction
- RAG guardrails
- Source allowlisting
- Safe tool-call policy
- Citation-required grounded answering

## Validation

Run:

python scripts/validate_security_guardrails.py

Expected: passed true

Run tests:

python -m pytest

Expected result after M13: 35 passed

## Limitation

This milestone adds deterministic guardrails and security tests. It does not claim full enterprise-grade security, formal red-team coverage, or compliance certification.
