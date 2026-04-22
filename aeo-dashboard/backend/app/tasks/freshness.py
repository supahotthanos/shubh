"""Celery tasks for content freshness."""
from __future__ import annotations

import asyncio
from datetime import datetime

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import async_session_factory
from app.models.content import ContentFreshness, TrackedContent
from app.services.freshness_analyzer import FreshnessAnalyzerService

_service = FreshnessAnalyzerService()


async def _analyze(content_id: int) -> bool:
    async with async_session_factory() as db:
        result = await db.execute(select(TrackedContent).where(TrackedContent.id == content_id))
        content = result.scalar_one_or_none()
        if content is None:
            return False
        analysis = await _service.analyze_url(content.url)
        db.add(
            ContentFreshness(
                content_id=content_id,
                last_modified_header=analysis.last_modified,
                detected_publish_date=analysis.publish_date,
                detected_update_date=analysis.update_date,
                content_hash=analysis.content_hash,
                freshness_score=analysis.freshness_score,
                freshness_grade=analysis.freshness_grade.value,
                days_since_update=analysis.days_since_update,
                refresh_priority=analysis.refresh_priority,
                refresh_recommendation=(
                    analysis.recommendations[0] if analysis.recommendations else None
                ),
                estimated_position_loss=analysis.estimated_position_loss,
                checked_at=datetime.utcnow(),
            )
        )
        await db.commit()
        return True


@celery_app.task(name="app.tasks.freshness.analyze_content")
def analyze_content(content_id: int) -> bool:
    return asyncio.run(_analyze(content_id))


async def _scan_all() -> int:
    async with async_session_factory() as db:
        result = await db.execute(select(TrackedContent).where(TrackedContent.is_active == True))  # noqa: E712
        items = result.scalars().all()
    count = 0
    for item in items:
        try:
            await _analyze(item.id)
            count += 1
        except Exception:
            continue
    return count


@celery_app.task(name="app.tasks.freshness.scan_all_content")
def scan_all_content() -> int:
    return asyncio.run(_scan_all())
