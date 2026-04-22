"""Celery tasks for competitor tracking."""
from __future__ import annotations

import asyncio
from datetime import datetime

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import async_session_factory
from app.models.competitor import Competitor
from app.providers import get_authority_provider


async def _refresh(competitor_id: int) -> bool:
    provider = get_authority_provider()
    async with async_session_factory() as db:
        result = await db.execute(select(Competitor).where(Competitor.id == competitor_id))
        competitor = result.scalar_one_or_none()
        if competitor is None:
            return False
        data = await provider.authority_for(competitor.domain)
        competitor.harmonic_centrality_rank = data.hc_rank
        competitor.domain_rating = data.domain_rating
        competitor.last_analyzed_at = datetime.utcnow()
        await db.commit()
        return True


@celery_app.task(name="app.tasks.competitors.refresh_competitor")
def refresh_competitor(competitor_id: int) -> bool:
    return asyncio.run(_refresh(competitor_id))


async def _refresh_all() -> int:
    async with async_session_factory() as db:
        result = await db.execute(select(Competitor).where(Competitor.is_active == True))  # noqa: E712
        competitors = result.scalars().all()
    count = 0
    for competitor in competitors:
        try:
            await _refresh(competitor.id)
            count += 1
        except Exception:
            continue
    return count


@celery_app.task(name="app.tasks.competitors.refresh_all_competitors")
def refresh_all_competitors() -> int:
    return asyncio.run(_refresh_all())
