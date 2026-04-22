"""Reports endpoints — list, generate, download (PDF/CSV), schedule."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_for_user
from app.core.database import get_db
from app.models.campaign import Campaign, CampaignAsset
from app.models.citation import Citation
from app.models.client import Client
from app.models.competitor import Competitor
from app.models.content import ContentFreshness, TrackedContent
from app.models.keyword import Keyword, RRFScore
from app.models.prompt import Prompt
from app.models.report import Report, ReportSchedule
from app.services.report_generator import ReportGeneratorService

router = APIRouter()
_report_service = ReportGeneratorService()


async def _build_client_data(db: AsyncSession, client_id: int, period_start: datetime) -> dict:
    """Assemble aggregated data dict consumed by ReportGeneratorService."""
    client = (
        await db.execute(select(Client).where(Client.id == client_id))
    ).scalar_one()
    total_cites = (
        await db.execute(
            select(func.count(Citation.id)).where(
                Citation.client_id == client_id,
                Citation.first_seen_at >= period_start,
            )
        )
    ).scalar() or 0

    rrf_rows = (
        await db.execute(
            select(RRFScore.raw_score, RRFScore.meets_threshold)
            .join(Keyword, RRFScore.keyword_id == Keyword.id)
            .where(Keyword.client_id == client_id)
        )
    ).all()

    freshness_rows = (
        await db.execute(
            select(ContentFreshness.freshness_grade, ContentFreshness.freshness_score)
            .join(TrackedContent, ContentFreshness.content_id == TrackedContent.id)
            .where(TrackedContent.client_id == client_id)
        )
    ).all()

    campaigns = (
        await db.execute(select(Campaign).where(Campaign.client_id == client_id))
    ).scalars().all()
    total_assets = (
        await db.execute(
            select(func.count(CampaignAsset.id))
            .join(Campaign, CampaignAsset.campaign_id == Campaign.id)
            .where(Campaign.client_id == client_id)
        )
    ).scalar() or 0
    competitors_rows = (
        await db.execute(select(Competitor).where(Competitor.client_id == client_id))
    ).scalars().all()

    grade_distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for grade, _ in freshness_rows:
        grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
    avg_fresh = (
        sum(s for _, s in freshness_rows) / len(freshness_rows) if freshness_rows else 0
    )

    return {
        "client_name": client.name,
        "citations": {
            "total": total_cites,
            "net_change": total_cites,
            "growth_rate": 0,
            "by_type": {},
            "trend_data": [],
        },
        "platforms": {"list": [], "best_performing": None, "needs_attention": []},
        "rrf": {
            "avg_score": (sum(s for s, _ in rrf_rows) / len(rrf_rows)) if rrf_rows else 0,
            "meeting_threshold": sum(1 for _, meets in rrf_rows if meets),
            "total_keywords": len(rrf_rows),
            "threshold_rate": round(
                (sum(1 for _, meets in rrf_rows if meets) / len(rrf_rows) * 100), 1
            ) if rrf_rows else 0,
            "top_keywords": [],
            "needs_improvement": [],
        },
        "freshness": {
            "overall_grade": _grade_from_score(avg_fresh),
            "avg_score": round(avg_fresh, 1),
            "grade_distribution": grade_distribution,
            "needs_refresh": [],
            "recently_refreshed": [],
        },
        "campaigns": {
            "active_count": sum(1 for c in campaigns if c.status == "active"),
            "total_assets": total_assets,
            "citing_assets": 0,
            "conversion_rate": 0,
            "by_type": {},
            "top_campaigns": [],
        },
        "competitive": {
            "client_position": 1,
            "share_of_voice": 0,
            "rankings": [
                {"name": c.name, "citations": c.total_citations} for c in competitors_rows
            ],
            "overlap_analysis": {},
            "recent_activity": [],
        },
        "prompts": {
            "coverage_rate": (
                await db.execute(
                    select(func.count(Prompt.id)).where(
                        Prompt.client_id == client_id, Prompt.is_visible == True  # noqa: E712
                    )
                )
            ).scalar() or 0
        },
        "all_recommendations": [],
        "quick_wins": [],
    }


def _grade_from_score(score: float) -> str:
    if score >= 80:
        return "A"
    if score >= 60:
        return "B"
    if score >= 40:
        return "C"
    if score >= 20:
        return "D"
    return "F"


@router.get("/{client_id}", response_model=List[dict])
async def list_reports(
    client_id: int,
    report_type: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    client: Client = Depends(get_client_for_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Report).where(Report.client_id == client.id)
    if report_type:
        query = query.where(Report.report_type == report_type)
    query = query.order_by(Report.generated_at.desc()).limit(limit)
    result = await db.execute(query)
    reports = result.scalars().all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "report_type": r.report_type,
            "period_start": r.period_start,
            "period_end": r.period_end,
            "generated_at": r.generated_at,
            "status": r.status,
            "pdf_url": r.pdf_url,
        }
        for r in reports
    ]


@router.post("/{client_id}/generate")
async def generate_report(
    client_id: int,
    report_type: str = Query(default="monthly", regex="^(weekly|monthly|quarterly)$"),
    period_start: Optional[datetime] = None,
    period_end: Optional[datetime] = None,
    client: Client = Depends(get_client_for_user),
    db: AsyncSession = Depends(get_db),
):
    if not period_end:
        period_end = datetime.utcnow()
    if not period_start:
        if report_type == "weekly":
            period_start = period_end - timedelta(days=7)
        elif report_type == "monthly":
            period_start = period_end - timedelta(days=30)
        else:
            period_start = period_end - timedelta(days=90)

    client_data = await _build_client_data(db, client.id, period_start)
    report = await _report_service.generate_report(
        client_id=client.id,
        period_start=period_start,
        period_end=period_end,
        report_type=report_type,
        client_data=client_data,
    )
    record = Report(
        title=report.title,
        report_type=report_type,
        period_start=period_start,
        period_end=period_end,
        summary_metrics=report.key_metrics,
        citation_data=client_data["citations"],
        rrf_data=client_data["rrf"],
        freshness_data=client_data["freshness"],
        campaign_data=client_data["campaigns"],
        competitor_data=client_data["competitive"],
        recommendations=[],
        generated_at=datetime.utcnow(),
        status="published",
        client_id=client.id,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {
        "id": record.id,
        "title": report.title,
        "executive_summary": report.executive_summary,
        "key_metrics": report.key_metrics,
        "sections": [
            {"title": s.title, "recommendations": s.recommendations} for s in report.sections
        ],
        "generated_at": report.generated_at.isoformat(),
    }


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    format: str = Query(default="pdf", regex="^(pdf|csv)$"),
    db: AsyncSession = Depends(get_db),
):
    record = (
        await db.execute(select(Report).where(Report.id == report_id))
    ).scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Report not found")

    # Rehydrate a GeneratedReport for export.
    client_data = await _build_client_data(
        db, record.client_id, record.period_start or datetime.utcnow() - timedelta(days=30)
    )
    report = await _report_service.generate_report(
        client_id=record.client_id,
        period_start=record.period_start or datetime.utcnow() - timedelta(days=30),
        period_end=record.period_end or datetime.utcnow(),
        report_type=record.report_type or "monthly",
        client_data=client_data,
    )

    if format == "csv":
        content = _report_service.export_to_csv(report)
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="report_{report_id}.csv"'},
        )

    try:
        pdf_bytes = await _report_service.export_to_pdf(report)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {exc}")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="report_{report_id}.pdf"'},
    )


@router.get("/{report_id}/slides")
async def get_slides_outline(
    report_id: int,
    db: AsyncSession = Depends(get_db),
):
    record = (
        await db.execute(select(Report).where(Report.id == report_id))
    ).scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Report not found")
    client_data = await _build_client_data(
        db, record.client_id, record.period_start or datetime.utcnow() - timedelta(days=30)
    )
    report = await _report_service.generate_report(
        client_id=record.client_id,
        period_start=record.period_start or datetime.utcnow() - timedelta(days=30),
        period_end=record.period_end or datetime.utcnow(),
        report_type=record.report_type or "monthly",
        client_data=client_data,
    )
    return _report_service.generate_slides_outline(report)


@router.get("/{client_id}/schedules")
async def list_report_schedules(
    client_id: int,
    client: Client = Depends(get_client_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ReportSchedule).where(ReportSchedule.client_id == client.id)
    )
    return [
        {
            "id": s.id,
            "frequency": s.frequency,
            "recipients": s.recipients,
            "is_active": s.is_active,
            "last_run_at": s.last_run_at,
            "next_run_at": s.next_run_at,
        }
        for s in result.scalars().all()
    ]


@router.post("/{client_id}/schedules")
async def create_report_schedule(
    client_id: int,
    frequency: str = Query(..., regex="^(weekly|monthly)$"),
    recipients: List[str] = Query(...),
    day_of_week: Optional[int] = Query(default=1, ge=0, le=6),
    day_of_month: Optional[int] = Query(default=1, ge=1, le=28),
    hour: int = Query(default=9, ge=0, le=23),
    client: Client = Depends(get_client_for_user),
    db: AsyncSession = Depends(get_db),
):
    schedule = ReportSchedule(
        frequency=frequency,
        day_of_week=day_of_week if frequency == "weekly" else None,
        day_of_month=day_of_month if frequency == "monthly" else None,
        hour=hour,
        recipients=recipients,
        is_active=True,
        client_id=client.id,
    )
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return {
        "id": schedule.id,
        "frequency": schedule.frequency,
        "recipients": schedule.recipients,
        "is_active": schedule.is_active,
        "message": f"Schedule created. Reports will be sent {frequency}.",
    }
