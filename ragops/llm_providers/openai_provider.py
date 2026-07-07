from __future__ import annotations

from typing import Any

from ragops.llm_providers.base import LLMResponse


class OpenAICompatibleProvider:
    provider_name = "openai"

    def __init__(
        self,
        *,
        model_id: str = "gpt-4o-mini",
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> None:
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.temperature = temperature

    def _client(self) -> Any:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "openai package is required for OpenAI-compatible provider. Install optional cloud dependencies first."
            ) from exc

        return OpenAI()

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> LLMResponse:
        client = self._client()

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        text = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)

        return LLMResponse(
            provider=self.provider_name,
            model=self.model_id,
            text=text,
            input_tokens=getattr(usage, "prompt_tokens", None) if usage else None,
            output_tokens=getattr(usage, "completion_tokens", None) if usage else None,
            raw_response=response.model_dump() if hasattr(response, "model_dump") else None,
        )
