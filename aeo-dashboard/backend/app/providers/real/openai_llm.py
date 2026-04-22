"""Real OpenAI LLM provider."""
from __future__ import annotations

import time
from typing import Optional

from app.providers.base import LLMProvider, LLMResponse


class OpenAILLMProvider:
    platform = "chatgpt"

    def __init__(self, api_key: str, model: str = "gpt-4-turbo") -> None:
        from openai import AsyncOpenAI  # noqa: WPS433

        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def complete(self, prompt: str, *, temperature: float = 0.7) -> LLMResponse:
        start = time.time()
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=800,
        )
        text = resp.choices[0].message.content or ""
        return LLMResponse(
            text=text,
            model=self._model,
            duration_ms=int((time.time() - start) * 1000),
        )
