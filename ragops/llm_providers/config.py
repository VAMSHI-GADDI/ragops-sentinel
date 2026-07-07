from __future__ import annotations

from dataclasses import dataclass
import os


SUPPORTED_PROVIDERS = {"mock", "bedrock", "openai"}


@dataclass(frozen=True)
class LLMProviderConfig:
    provider: str
    model_id: str
    aws_region: str
    max_tokens: int
    temperature: float


def load_llm_provider_config() -> LLMProviderConfig:
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()

    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unsupported LLM_PROVIDER={provider!r}. Expected one of {sorted(SUPPORTED_PROVIDERS)}."
        )

    model_id = os.getenv("LLM_MODEL_ID", "").strip()

    if provider == "mock" and not model_id:
        model_id = "mock-ragops-local"

    if provider == "bedrock" and not model_id:
        model_id = os.getenv("BEDROCK_MODEL_ID", "").strip()

    if provider == "openai" and not model_id:
        model_id = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    return LLMProviderConfig(
        provider=provider,
        model_id=model_id,
        aws_region=os.getenv("AWS_REGION", "us-east-1").strip(),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "512")),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
    )
