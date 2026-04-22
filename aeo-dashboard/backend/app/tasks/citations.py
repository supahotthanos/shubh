"""Celery tasks for citation checking."""
from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import async_session_factory
from app.models.prompt import Prompt
from app.services.citation_orchestrator import run_prompt_check


async def _check_one(prompt_id: int, platforms: list[str] | None, check_count: int) -> int:
    async with async_session_factory() as db:
        result = await db.execute(select(Prompt).where(Prompt.id == prompt_id))
        prompt = result.scalar_one_or_none()
        if prompt is None:
            return 0
        outcomes = await run_prompt_check(db, prompt, platforms=platforms, check_count=check_count)
        return sum(len(v) for v in outcomes.values())


@celery_app.task(name="app.tasks.citations.check_prompt_visibility")
def check_prompt_visibility(prompt_id: int, platforms: list[str] | None = None, check_count: int = 1) -> int:
    return asyncio.run(_check_one(prompt_id, platforms, check_count))


async def _refresh_all() -> int:
    async with async_session_factory() as db:
        result = await db.execute(select(Prompt).where(Prompt.check_frequency_hours <= 24))
        prompts = result.scalars().all()
        total = 0
        for prompt in prompts:
            try:
                outcomes = await run_prompt_check(db, prompt, check_count=1)
                total += sum(len(v) for v in outcomes.values())
            except Exception:
                continue
        return total


@celery_app.task(name="app.tasks.citations.refresh_all_active_prompts")
def refresh_all_active_prompts() -> int:
    return asyncio.run(_refresh_all())
