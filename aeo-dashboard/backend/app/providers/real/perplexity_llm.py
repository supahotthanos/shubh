"""Real Perplexity LLM provider (OpenAI-compatible API)."""
from __future__ import annotations

import time

import httpx

from app.providers.base import LLMResponse


class PerplexityLLMProvider:
    platform = "perplexity"

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-sonar-large-128k-online",
    ) -> None:
        self._api_key = api_key
        self._model = model

    async def complete(self, prompt: str, *, temperature: float = 0.7) -> LLMResponse:
        start = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self._model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                },
            )
            resp.raise_for_status()
            data = resp.json()
        text = data["choices"][0]["message"]["content"]
        return LLMResponse(
            text=text,
            model=self._model,
            duration_ms=int((time.time() - start) * 1000),
        )
