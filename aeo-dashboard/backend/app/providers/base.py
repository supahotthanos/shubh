"""Provider protocols — everything external speaks one of these."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable


@dataclass
class LLMResponse:
    text: str
    model: str
    duration_ms: int


@dataclass
class GSCRow:
    query: str
    clicks: int
    impressions: int
    ctr: float
    position: float


@dataclass
class AuthorityData:
    hc_rank: Optional[int] = None
    hc_score: Optional[float] = None
    pagerank_rank: Optional[int] = None
    pagerank_score: Optional[float] = None
    domain_rating: Optional[float] = None
    domain_authority: Optional[float] = None
    referring_domains: Optional[int] = None
    total_backlinks: Optional[int] = None
    dofollow_backlinks: Optional[int] = None


@runtime_checkable
class LLMProvider(Protocol):
    platform: str

    async def complete(self, prompt: str, *, temperature: float = 0.7) -> LLMResponse:
        ...


@runtime_checkable
class GSCProvider(Protocol):
    async def fetch_queries(
        self,
        property_url: str,
        days_back: int = 90,
        row_limit: int = 500,
    ) -> list[GSCRow]:
        ...


@runtime_checkable
class AuthorityProvider(Protocol):
    async def authority_for(self, domain: str) -> AuthorityData:
        ...


@runtime_checkable
class WikipediaProvider(Protocol):
    async def has_citation(self, domain: str) -> tuple[bool, Optional[str]]:
        ...
