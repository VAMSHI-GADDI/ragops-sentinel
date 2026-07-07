from __future__ import annotations

import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from ragops.llm_providers.bedrock_provider import BedrockLLMProvider
from ragops.llm_providers.config import LLMProviderConfig, load_llm_provider_config
from ragops.llm_providers.factory import create_llm_provider
from ragops.llm_providers.mock_provider import MockLLMProvider
from ragops.llm_providers.openai_provider import OpenAICompatibleProvider


def validate_llm_providers() -> dict[str, object]:
    errors: list[str] = []

    mock = MockLLMProvider()
    mock_response = mock.generate("Validate provider abstraction.")

    if mock_response.provider != "mock":
        errors.append("Mock provider did not return provider='mock'.")

    if "Validate provider abstraction" not in mock_response.text:
        errors.append("Mock provider response text did not include prompt excerpt.")

    bedrock = BedrockLLMProvider(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        aws_region="us-east-1",
    )
    bedrock_body = bedrock._build_body("Hello", "System context")

    if "messages" not in bedrock_body:
        errors.append("Bedrock request body missing messages.")

    if bedrock_body["inferenceConfig"]["maxTokens"] != 512:
        errors.append("Bedrock default maxTokens mismatch.")

    openai_provider = OpenAICompatibleProvider(model_id="gpt-4o-mini")

    if openai_provider.provider_name != "openai":
        errors.append("OpenAI-compatible provider name mismatch.")

    previous_provider = os.environ.get("LLM_PROVIDER")
    previous_model = os.environ.get("LLM_MODEL_ID")

    try:
        os.environ["LLM_PROVIDER"] = "mock"
        os.environ.pop("LLM_MODEL_ID", None)

        config = load_llm_provider_config()
        provider = create_llm_provider(config)

        if config.provider != "mock":
            errors.append("Environment config did not default to mock provider.")

        if provider.provider_name != "mock":
            errors.append("Factory did not create mock provider from config.")
    finally:
        if previous_provider is None:
            os.environ.pop("LLM_PROVIDER", None)
        else:
            os.environ["LLM_PROVIDER"] = previous_provider

        if previous_model is None:
            os.environ.pop("LLM_MODEL_ID", None)
        else:
            os.environ["LLM_MODEL_ID"] = previous_model

    return {
        "milestone": "M14_MANAGED_CLOUD_AI_SERVICES",
        "providers": ["mock", "bedrock", "openai"],
        "cloud_dependencies_required_for_live_calls": ["boto3", "openai"],
        "live_cloud_calls_executed": False,
        "passed": not errors,
        "errors": errors,
    }


def main() -> None:
    result = validate_llm_providers()
    print(json.dumps(result, indent=2))

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
