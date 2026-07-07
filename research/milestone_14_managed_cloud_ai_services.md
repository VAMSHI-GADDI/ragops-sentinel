# Milestone 14 - Managed Cloud AI Services

## Objective

Add managed cloud AI provider abstractions to RAGOps Sentinel without hardcoding credentials or requiring live cloud calls in CI.

## Added Capabilities

- Mock LLM provider for deterministic local testing
- AWS Bedrock provider abstraction
- OpenAI-compatible provider abstraction
- Environment-based provider configuration
- Provider factory for selecting mock, Bedrock, or OpenAI-compatible providers
- Optional cloud dependency file
- Provider validation script
- Unit tests for provider configuration and request construction

## Skills Demonstrated

- Managed cloud AI services
- AWS Bedrock integration pattern
- OpenAI-compatible LLM provider design
- LLM provider abstraction
- Environment-based cloud configuration
- Secret-safe provider setup
- CI-safe cloud integration testing

## Validation

Run:

python scripts/validate_llm_providers.py

Expected: passed true

Run tests:

python -m pytest

Expected result after M14: 42 passed

## Limitation

This milestone adds provider abstractions and CI-safe tests. It does not claim a live AWS Bedrock or OpenAI production deployment.
