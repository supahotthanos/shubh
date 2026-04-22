"""Multi-platform citation checking orchestrator.

Uses the provider factory to fan out a single prompt across all configured
platforms, scans the resulting LLM text for brand mentions, and persists
`Citation` + `CitationCheck` rows.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.citation import Citation, CitationCheck, CitationPlatform
from app.models.client import Client, ClientDomain
from app.models.prompt import Prompt
from app.providers import get_llm_provider
from app.services.citation_checker import BasePlatformChecker

SUPPORTED_PLATFORMS = ["chatgpt", "perplexity", "claude", "google_ai"]


class _Scanner(BasePlatformChecker):
    """Reuse the mention-detection helpers on `BasePlatformChecker`."""

    async def check_citation(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError


_scanner = _Scanner()


@dataclass
class PlatformCheckOutcome:
    platform: str
    was_cited: bool
    position: Optional[int]
    mention_type: str
    cited_text: Optional[str]
    context_snippet: Optional[str]
    response_text: str
    response_hash: str
    model_version: str
    duration_ms: int


async def _ensure_platform(db: AsyncSession, slug: str) -> CitationPlatform:
    result = await db.execute(select(CitationPlatform).where(CitationPlatform.slug == slug))
    platform = result.scalar_one_or_none()
    if platform:
        return platform
    name_map = {
        "chatgpt": "ChatGPT",
        "perplexity": "Perplexity",
        "claude": "Claude",
        "google_ai": "Google AI Overview",
        "gemini": "Gemini",
        "grok": "Grok",
        "bing_copilot": "Bing Copilot",
    }
    platform = CitationPlatform(slug=slug, name=name_map.get(slug, slug.title()), is_active=True)
    db.add(platform)
    await db.flush()
    return platform


async def run_prompt_check(
    db: AsyncSession,
    prompt: Prompt,
    platforms: Optional[List[str]] = None,
    check_count: int = 1,
) -> Dict[str, List[PlatformCheckOutcome]]:
    """Run N checks per platform for a prompt, persist results."""
    client_result = await db.execute(select(Client).where(Client.id == prompt.client_id))
    client = client_result.scalar_one()
    brand_names: List[str] = list(client.brand_names or []) or [client.name]
    domain_result = await db.execute(
        select(ClientDomain).where(ClientDomain.client_id == client.id)
    )
    brand_urls: List[str] = [
        d.domain for d in domain_result.scalars().all() if d.domain
    ]

    platforms = platforms or SUPPORTED_PLATFORMS
    outcomes: Dict[str, List[PlatformCheckOutcome]] = {p: [] for p in platforms}
    citation_rate_counts: Dict[str, int] = {p: 0 for p in platforms}
    positions: Dict[str, List[int]] = {p: [] for p in platforms}

    for platform_slug in platforms:
        provider = get_llm_provider(platform_slug)
        db_platform = await _ensure_platform(db, platform_slug)

        for _ in range(max(1, check_count)):
            resp = await provider.complete(prompt.text)
            was_cited, position, mention_type, cited_text = _scanner._find_brand_mentions(
                resp.text, brand_names, brand_urls
            )
            context = _scanner._get_context_snippet(resp.text, cited_text) if cited_text else None
            response_hash = hashlib.sha256(resp.text.encode()).hexdigest()[:16]

            # Persist the check event
            check = CitationCheck(
                prompt_id=prompt.id,
                platform_id=db_platform.id,
                was_cited=was_cited,
                position=position,
                response_text=resp.text,
                response_hash=response_hash,
                model_version=resp.model,
                temperature=0.7,
                check_duration_ms=resp.duration_ms,
            )
            db.add(check)

            if was_cited:
                citation_rate_counts[platform_slug] += 1
                if position is not None:
                    positions[platform_slug].append(position)

                # Upsert a live Citation row (client, prompt, platform)
                existing_q = await db.execute(
                    select(Citation).where(
                        Citation.client_id == prompt.client_id,
                        Citation.prompt_id == prompt.id,
                        Citation.platform_id == db_platform.id,
                    )
                )
                cite = existing_q.scalar_one_or_none()
                now = datetime.utcnow()
                if cite is None:
                    cite = Citation(
                        client_id=prompt.client_id,
                        prompt_id=prompt.id,
                        platform_id=db_platform.id,
                        cited_url=brand_urls[0] if mention_type == "linked" and brand_urls else None,
                        cited_text=cited_text,
                        mention_type=mention_type,
                        position=position,
                        is_primary=position == 1,
                        context_snippet=context,
                        confidence_score=0.95 if mention_type == "linked" else 0.85,
                        sentiment="neutral",
                        first_seen_at=now,
                        last_seen_at=now,
                        is_currently_visible=True,
                    )
                    db.add(cite)
                else:
                    cite.mention_type = mention_type
                    cite.position = position
                    cite.context_snippet = context
                    cite.last_seen_at = now
                    cite.is_currently_visible = True
            outcomes[platform_slug].append(
                PlatformCheckOutcome(
                    platform=platform_slug,
                    was_cited=was_cited,
                    position=position,
                    mention_type=mention_type,
                    cited_text=cited_text,
                    context_snippet=context,
                    response_text=resp.text,
                    response_hash=response_hash,
                    model_version=resp.model,
                    duration_ms=resp.duration_ms,
                )
            )

    # Update prompt visibility summary
    total_checks = sum(len(v) for v in outcomes.values()) or 1
    total_cited = sum(citation_rate_counts.values())
    prompt.is_visible = total_cited > 0
    prompt.visibility_score = round((total_cited / total_checks) * 100, 2)
    prompt.last_checked_at = datetime.utcnow().isoformat()

    await db.commit()
    return outcomes
