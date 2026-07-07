from __future__ import annotations

from ragops.llm_providers.base import LLMResponse


class MockLLMProvider:
    provider_name = "mock"

    def __init__(self, model_id: str = "mock-ragops-local") -> None:
        self.model_id = model_id

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> LLMResponse:
        prefix = "RAGOps mock response"
        if system_prompt:
            prefix += " with system context"

        return LLMResponse(
            provider=self.provider_name,
            model=self.model_id,
            text=f"{prefix}: {prompt[:160]}",
            input_tokens=len(prompt.split()) + len((system_prompt or "").split()),
            output_tokens=min(32, max(1, len(prompt.split()) // 2)),
            raw_response={"mock": True},
        )
