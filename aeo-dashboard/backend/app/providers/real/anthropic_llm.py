"""Real Anthropic (Claude) LLM provider."""
from __future__ import annotations

import time

from app.providers.base import LLMResponse


class AnthropicLLMProvider:
    platform = "claude"

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6") -> None:
        import anthropic  # noqa: WPS433

        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self._model = model

    async def complete(self, prompt: str, *, temperature: float = 0.7) -> LLMResponse:
        start = time.time()
        msg = await self._client.messages.create(
            model=self._model,
            max_tokens=800,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        text_parts = []
        for block in msg.content:
            if getattr(block, "type", "") == "text":
                text_parts.append(block.text)
        return LLMResponse(
            text="".join(text_parts),
            model=self._model,
            duration_ms=int((time.time() - start) * 1000),
        )
