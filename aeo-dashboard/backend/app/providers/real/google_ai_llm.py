"""Real Google Gemini LLM provider."""
from __future__ import annotations

import time

import httpx

from app.providers.base import LLMResponse


class GoogleAILLMProvider:
    platform = "google_ai"

    def __init__(self, api_key: str, model: str = "gemini-1.5-pro") -> None:
        self._api_key = api_key
        self._model = model

    async def complete(self, prompt: str, *, temperature: float = 0.7) -> LLMResponse:
        start = time.time()
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent?key={self._api_key}"
        )
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": temperature},
                },
            )
            resp.raise_for_status()
            data = resp.json()
        candidates = data.get("candidates") or []
        text = ""
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts)
        return LLMResponse(
            text=text,
            model=self._model,
            duration_ms=int((time.time() - start) * 1000),
        )
