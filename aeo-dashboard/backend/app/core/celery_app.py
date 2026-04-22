"""Celery application + beat schedule.

Run a worker: `celery -A app.core.celery_app worker --loglevel=info`
Run the beat scheduler: `celery -A app.core.celery_app beat --loglevel=info`
"""
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "aeo",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
    include=[
        "app.tasks.citations",
        "app.tasks.freshness",
        "app.tasks.authority",
        "app.tasks.competitors",
        "app.tasks.reports",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_acks_late=True,
    worker_prefetch_multiplier=2,
    beat_schedule={
        "refresh-active-prompt-citations": {
            "task": "app.tasks.citations.refresh_all_active_prompts",
            "schedule": crontab(minute="0"),  # hourly
        },
        "daily-freshness-scan": {
            "task": "app.tasks.freshness.scan_all_content",
            "schedule": crontab(hour="2", minute="0"),  # 02:00 UTC daily
        },
        "daily-competitor-refresh": {
            "task": "app.tasks.competitors.refresh_all_competitors",
            "schedule": crontab(hour="4", minute="0"),
        },
        "weekly-authority-refresh": {
            "task": "app.tasks.authority.refresh_all_authority",
            "schedule": crontab(hour="3", minute="0", day_of_week="1"),
        },
        "hourly-report-scheduler": {
            "task": "app.tasks.reports.run_scheduled_reports",
            "schedule": crontab(minute="5"),
        },
    },
)
