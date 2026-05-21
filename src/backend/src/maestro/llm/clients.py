"""Thin wrappers around Anthropic and OpenAI SDKs.

Each client returns a uniform RawLLMResponse used by the gateway.
"""

import time
from dataclasses import dataclass

import anthropic
import openai

from maestro.config import settings


@dataclass
class RawLLMResponse:
    """Uniform response from any LLM provider."""

    content: str
    model_id: str
    input_tokens: int
    output_tokens: int
    latency_ms: int


class AnthropicClient:
    """Wrapper for Anthropic API (Claude models)."""

    def __init__(self) -> None:
        # Allow startup without keys; calls will fail at runtime if missing.
        self._client = anthropic.AsyncAnthropic(
            api_key=settings.anthropic_api_key or "sk-not-configured"
        )

    async def generate(
        self,
        *,
        system_prompt: str,
        user_message: str,
        model: str | None = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> RawLLMResponse:
        model = model or settings.llm_primary_model
        start = time.monotonic()
        response = await self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        latency_ms = int((time.monotonic() - start) * 1000)
        return RawLLMResponse(
            content=response.content[0].text,
            model_id=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_ms=latency_ms,
        )


class OpenAIClient:
    """Wrapper for OpenAI API (GPT models)."""

    def __init__(self) -> None:
        # Allow startup without keys; calls will fail at runtime if missing.
        self._client = openai.AsyncOpenAI(
            api_key=settings.openai_api_key or "sk-not-configured"
        )

    async def generate(
        self,
        *,
        system_prompt: str,
        user_message: str,
        model: str | None = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> RawLLMResponse:
        model = model or settings.llm_batch_model
        start = time.monotonic()
        response = await self._client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        latency_ms = int((time.monotonic() - start) * 1000)
        choice = response.choices[0]
        usage = response.usage
        return RawLLMResponse(
            content=choice.message.content or "",
            model_id=response.model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            latency_ms=latency_ms,
        )
