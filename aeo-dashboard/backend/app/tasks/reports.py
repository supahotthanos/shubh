"""Celery tasks for scheduled report generation."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import async_session_factory
from app.models.report import Report, ReportSchedule
from app.services.report_generator import ReportGeneratorService

_service = ReportGeneratorService()


def _next_run_from(now: datetime, schedule: ReportSchedule) -> datetime:
    if schedule.frequency == "weekly":
        days_ahead = (schedule.day_of_week or 1) - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return now.replace(hour=schedule.hour or 9, minute=0, second=0, microsecond=0) + timedelta(
            days=days_ahead
        )
    # monthly
    day = schedule.day_of_month or 1
    target = now.replace(day=1) + timedelta(days=32)
    return target.replace(day=min(day, 28), hour=schedule.hour or 9, minute=0, second=0, microsecond=0)


async def _run_due() -> int:
    now = datetime.utcnow()
    async with async_session_factory() as db:
        result = await db.execute(select(ReportSchedule).where(ReportSchedule.is_active == True))  # noqa: E712
        schedules = result.scalars().all()
        generated = 0
        for sched in schedules:
            if sched.next_run_at and sched.next_run_at > now:
                continue
            # Generate a report for this schedule's client.
            period_end = now
            period_start = period_end - timedelta(days=7 if sched.frequency == "weekly" else 30)
            report = await _service.generate_report(
                client_id=sched.client_id,
                period_start=period_start,
                period_end=period_end,
                report_type=sched.frequency or "monthly",
                client_data={"client_name": "Scheduled", "citations": {}, "rrf": {}, "freshness": {},
                             "campaigns": {}, "competitive": {}, "prompts": {}, "all_recommendations": []},
            )
            db.add(
                Report(
                    title=report.title,
                    report_type=sched.frequency or "monthly",
                    period_start=period_start,
                    period_end=period_end,
                    summary_metrics=report.key_metrics,
                    generated_at=datetime.utcnow(),
                    status="published",
                    client_id=sched.client_id,
                )
            )
            sched.last_run_at = now
            sched.next_run_at = _next_run_from(now, sched)
            generated += 1
        await db.commit()
        return generated


@celery_app.task(name="app.tasks.reports.run_scheduled_reports")
def run_scheduled_reports() -> int:
    return asyncio.run(_run_due())
