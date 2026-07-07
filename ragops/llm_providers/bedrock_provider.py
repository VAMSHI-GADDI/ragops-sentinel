from __future__ import annotations

import json
from typing import Any

from ragops.llm_providers.base import LLMResponse


class BedrockLLMProvider:
    provider_name = "bedrock"

    def __init__(
        self,
        *,
        model_id: str,
        aws_region: str = "us-east-1",
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> None:
        if not model_id:
            raise ValueError("Bedrock model_id is required.")

        self.model_id = model_id
        self.aws_region = aws_region
        self.max_tokens = max_tokens
        self.temperature = temperature

    def _client(self) -> Any:
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError(
                "boto3 is required for AWS Bedrock provider. Install optional cloud dependencies first."
            ) from exc

        return boto3.client("bedrock-runtime", region_name=self.aws_region)

    def _build_body(self, prompt: str, system_prompt: str | None = None) -> dict[str, Any]:
        full_prompt = prompt if not system_prompt else f"{system_prompt}\n\nUser: {prompt}"

        return {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": full_prompt}],
                }
            ],
            "inferenceConfig": {
                "maxTokens": self.max_tokens,
                "temperature": self.temperature,
            },
        }

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> LLMResponse:
        client = self._client()
        body = self._build_body(prompt, system_prompt)

        response = client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        payload = json.loads(response["body"].read())

        text = ""
        output = payload.get("output", {})
        message = output.get("message", {})
        content = message.get("content", [])

        if content and isinstance(content, list):
            first = content[0]
            if isinstance(first, dict):
                text = str(first.get("text", ""))

        usage = payload.get("usage", {})

        return LLMResponse(
            provider=self.provider_name,
            model=self.model_id,
            text=text,
            input_tokens=usage.get("inputTokens"),
            output_tokens=usage.get("outputTokens"),
            raw_response=payload,
        )
