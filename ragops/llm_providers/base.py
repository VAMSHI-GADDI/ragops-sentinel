from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMResponse:
    provider: str
    model: str
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    raw_response: dict[str, object] | None = None


class LLMProvider(Protocol):
    provider_name: str

    def generate(self, prompt: str, *, system_prompt: str | None = None) -> LLMResponse:
        ...


def response_to_dict(response: LLMResponse) -> dict[str, object]:
    return asdict(response)
