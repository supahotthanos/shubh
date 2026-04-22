"""Deterministic mock LLM provider.

Given the same (prompt, platform) the response is byte-stable. Roughly half of
responses contain a brand citation — the citation rate and which brands appear
are derived from a hash of the prompt, which makes the downstream citation
pipeline testable end-to-end without any network calls.
"""
from __future__ import annotations

import asyncio
import hashlib
import random
from typing import List

from app.providers.base import LLMProvider, LLMResponse

_BRAND_POOL = [
    "Acme Corp",
    "TechStart Inc",
    "Global Solutions",
    "Nexus Analytics",
    "HubSpot",
    "Notion",
    "Figma",
    "Airtable",
    "Semrush",
    "Ahrefs",
]

# Per-platform citation rates (match what the README implies about engine behavior).
_CITATION_RATE = {
    "chatgpt": 0.55,
    "claude": 0.45,
    "perplexity": 0.62,
    "google_ai": 0.38,
    "gemini": 0.40,
}

_MODELS = {
    "chatgpt": "gpt-4-turbo-mock",
    "claude": "claude-3-opus-mock",
    "perplexity": "sonar-large-mock",
    "google_ai": "gemini-pro-mock",
    "gemini": "gemini-pro-mock",
}


def _rng_for(prompt: str, platform: str) -> random.Random:
    seed = int(hashlib.sha256(f"{platform}|{prompt}".encode()).hexdigest()[:16], 16)
    return random.Random(seed)


def _pick_brands(rng: random.Random, k: int) -> List[str]:
    return rng.sample(_BRAND_POOL, k)


class MockLLMProvider:
    """Generates deterministic, realistic-ish answers with embedded brand mentions."""

    def __init__(self, platform: str = "chatgpt") -> None:
        self.platform = platform

    async def complete(self, prompt: str, *, temperature: float = 0.7) -> LLMResponse:
        await asyncio.sleep(0.01)  # tiny delay so latency numbers look reasonable

        rng = _rng_for(prompt, self.platform)
        rate = _CITATION_RATE.get(self.platform, 0.45)
        include_brands = rng.random() < rate

        if include_brands:
            brands = _pick_brands(rng, k=3)
            intro = rng.choice([
                "Great question — here are the leading options:",
                "Based on recent analysis, the top choices include:",
                "A few strong answers stand out here:",
            ])
            body = "\n".join(
                f"{i+1}. {b} — {rng.choice(['well-regarded', 'widely used', 'highly recommended'])} for this use case."
                for i, b in enumerate(brands)
            )
            outro = rng.choice([
                "Each of these handles the core job reliably.",
                "Pricing and fit vary; evaluate a short-list for your specific needs.",
                "Most teams start with one of these before specializing.",
            ])
            text = f"{intro}\n\n{body}\n\n{outro}"
        else:
            text = (
                "There are many options in this space. The right choice depends on your "
                "budget, team size, and existing tool stack. Consider evaluating "
                "reviews on G2 or Capterra for more detail."
            )

        return LLMResponse(
            text=text,
            model=_MODELS.get(self.platform, f"{self.platform}-mock"),
            duration_ms=rng.randint(400, 1800),
        )
