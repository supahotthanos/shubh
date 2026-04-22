"""Celery tasks for authority metrics."""
from __future__ import annotations

import asyncio
from datetime import datetime

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import async_session_factory
from app.models.authority import AuthoritySignal
from app.models.client import ClientDomain
from app.providers import get_authority_provider, get_wikipedia_provider
from app.services.authority_tracker import AUTHORITY_DILUTION_DOMAINS


async def _refresh(domain: str) -> int:
    auth = get_authority_provider()
    wiki = get_wikipedia_provider()
    data = await auth.authority_for(domain)
    has_wiki, wiki_url = await wiki.has_citation(domain)
    dilution = AUTHORITY_DILUTION_DOMAINS.get(domain.lower())
    async with async_session_factory() as db:
        result = await db.execute(select(AuthoritySignal).where(AuthoritySignal.domain == domain))
        signal = result.scalar_one_or_none()
        if signal is None:
            signal = AuthoritySignal(domain=domain)
            db.add(signal)
        signal.harmonic_centrality_rank = data.hc_rank
        signal.harmonic_centrality_score = data.hc_score
        signal.pagerank_rank = data.pagerank_rank
        signal.pagerank_score = data.pagerank_score
        signal.domain_rating = data.domain_rating
        signal.domain_authority = data.domain_authority
        signal.referring_domains = data.referring_domains
        signal.total_backlinks = data.total_backlinks
        signal.dofollow_backlinks = data.dofollow_backlinks
        signal.has_wikipedia_citation = has_wiki
        signal.wikipedia_citation_url = wiki_url
        signal.authority_dilution_warning = dilution is not None
        signal.dilution_explanation = dilution
        signal.measured_at = datetime.utcnow()
        await db.commit()
        return signal.id


@celery_app.task(name="app.tasks.authority.refresh_authority")
def refresh_authority(domain: str) -> int:
    return asyncio.run(_refresh(domain))


async def _refresh_all() -> int:
    async with async_session_factory() as db:
        result = await db.execute(select(ClientDomain))
        domains = [d.domain for d in result.scalars().all() if d.domain]
    count = 0
    for domain in set(domains):
        try:
            await _refresh(domain)
            count += 1
        except Exception:
            continue
    return count


@celery_app.task(name="app.tasks.authority.refresh_all_authority")
def refresh_all_authority() -> int:
    return asyncio.run(_refresh_all())
