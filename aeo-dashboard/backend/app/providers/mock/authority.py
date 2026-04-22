"""Deterministic mock authority + Wikipedia providers."""
from __future__ import annotations

import hashlib
import random
from typing import Optional

from app.providers.base import AuthorityData, AuthorityProvider, WikipediaProvider


def _rng_for(domain: str) -> random.Random:
    seed = int(hashlib.sha256(domain.encode()).hexdigest()[:16], 16)
    return random.Random(seed)


class MockAuthorityProvider:
    async def authority_for(self, domain: str) -> AuthorityData:
        rng = _rng_for(domain)
        dr = round(rng.uniform(20, 92), 1)
        da = round(rng.uniform(15, 90), 1)
        ref = rng.randint(50, 150000)
        return AuthorityData(
            hc_rank=rng.randint(1000, 5_000_000),
            hc_score=round(rng.uniform(0.001, 0.9), 4),
            pagerank_rank=rng.randint(1000, 5_000_000),
            pagerank_score=round(rng.uniform(0.0001, 0.1), 6),
            domain_rating=dr,
            domain_authority=da,
            referring_domains=ref,
            total_backlinks=ref * rng.randint(5, 40),
            dofollow_backlinks=int(ref * rng.randint(3, 25)),
        )


class MockWikipediaProvider:
    async def has_citation(self, domain: str) -> tuple[bool, Optional[str]]:
        rng = _rng_for(domain)
        present = rng.random() < 0.35
        if present:
            return True, f"https://en.wikipedia.org/wiki/Special:Search/{domain}"
        return False, None
