from __future__ import annotations

from ragops.llm_providers.base import LLMProvider
from ragops.llm_providers.bedrock_provider import BedrockLLMProvider
from ragops.llm_providers.config import LLMProviderConfig, load_llm_provider_config
from ragops.llm_providers.mock_provider import MockLLMProvider
from ragops.llm_providers.openai_provider import OpenAICompatibleProvider


def create_llm_provider(config: LLMProviderConfig | None = None) -> LLMProvider:
    resolved = config or load_llm_provider_config()

    if resolved.provider == "mock":
        return MockLLMProvider(model_id=resolved.model_id)

    if resolved.provider == "bedrock":
        return BedrockLLMProvider(
            model_id=resolved.model_id,
            aws_region=resolved.aws_region,
            max_tokens=resolved.max_tokens,
            temperature=resolved.temperature,
        )

    if resolved.provider == "openai":
        return OpenAICompatibleProvider(
            model_id=resolved.model_id,
            max_tokens=resolved.max_tokens,
            temperature=resolved.temperature,
        )

    raise ValueError(f"Unsupported provider: {resolved.provider}")
