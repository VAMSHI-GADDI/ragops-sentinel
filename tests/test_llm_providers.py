from __future__ import annotations

import os

import pytest

from ragops.llm_providers.bedrock_provider import BedrockLLMProvider
from ragops.llm_providers.config import load_llm_provider_config
from ragops.llm_providers.factory import create_llm_provider
from ragops.llm_providers.mock_provider import MockLLMProvider
from ragops.llm_providers.openai_provider import OpenAICompatibleProvider
from scripts.validate_llm_providers import validate_llm_providers


def test_mock_provider_generates_deterministic_response():
    provider = MockLLMProvider()

    response = provider.generate("Explain evidence drift.", system_prompt="Be concise.")

    assert response.provider == "mock"
    assert response.model == "mock-ragops-local"
    assert "RAGOps mock response" in response.text
    assert response.input_tokens is not None
    assert response.output_tokens is not None


def test_llm_provider_config_defaults_to_mock(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_MODEL_ID", raising=False)

    config = load_llm_provider_config()

    assert config.provider == "mock"
    assert config.model_id == "mock-ragops-local"


def test_provider_factory_creates_mock_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")

    provider = create_llm_provider()

    assert provider.provider_name == "mock"


def test_bedrock_provider_builds_request_body_without_live_aws_call():
    provider = BedrockLLMProvider(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        aws_region="us-east-1",
    )

    body = provider._build_body("Hello", "System instruction")

    assert "messages" in body
    assert body["messages"][0]["role"] == "user"
    assert body["inferenceConfig"]["maxTokens"] == 512
    assert body["inferenceConfig"]["temperature"] == 0.2


def test_bedrock_provider_requires_model_id():
    with pytest.raises(ValueError):
        BedrockLLMProvider(model_id="")


def test_openai_compatible_provider_initializes_without_live_call():
    provider = OpenAICompatibleProvider(model_id="gpt-4o-mini")

    assert provider.provider_name == "openai"
    assert provider.model_id == "gpt-4o-mini"


def test_validate_llm_providers_passes():
    result = validate_llm_providers()

    assert result["passed"] is True
    assert result["errors"] == []
    assert "bedrock" in result["providers"]
    assert result["live_cloud_calls_executed"] is False
