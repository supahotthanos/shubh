from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.report import Report, ReportSchedule
from app.services.report_generator import ReportGeneratorService

router = APIRouter()
report_service = ReportGeneratorService()


@router.get("/{client_id}", response_model=List[dict])
async def list_reports(
    client_id: int,
    report_type: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    List generated reports for a client.
    """
    query = select(Report).where(Report.client_id == client_id)

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
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a new report for a client.

    Report types: weekly, monthly, quarterly
    """
    # Set default period based on report type
    if not period_end:
        period_end = datetime.utcnow()
    if not period_start:
        if report_type == "weekly":
            period_start = period_end - timedelta(days=7)
        elif report_type == "monthly":
            period_start = period_end - timedelta(days=30)
        else:  # quarterly
            period_start = period_end - timedelta(days=90)

    # In production, gather all client data
    client_data = {
        "client_name": "Client Name",  # Would fetch from DB
        "citations": {
            "total": 142,
            "new_this_period": 23,
            "lost_this_period": 5,
            "net_change": 18,
            "growth_rate": 12.5,
            "by_type": {"linked": 45, "unlinked": 67, "brand_mention": 30},
            "trend_data": [],
        },
        "platforms": {
            "list": [
                {"name": "ChatGPT", "citations": 58, "avg_position": 1.8, "stability_score": 82},
                {"name": "Perplexity", "citations": 42, "avg_position": 2.1, "stability_score": 76},
            ],
            "best_performing": "ChatGPT",
            "needs_attention": [],
        },
        "rrf": {
            "avg_score": 0.024,
            "meeting_threshold": 18,
            "total_keywords": 25,
            "threshold_rate": 72,
            "top_keywords": [],
            "needs_improvement": [],
        },
        "freshness": {
            "overall_grade": "B",
            "avg_score": 72,
            "grade_distribution": {"A": 10, "B": 15, "C": 8, "D": 3, "F": 1},
            "needs_refresh": [],
            "recently_refreshed": [],
        },
        "campaigns": {
            "active_count": 3,
            "total_assets": 25,
            "citing_assets": 12,
            "conversion_rate": 48,
            "by_type": {},
            "top_campaigns": [],
        },
        "competitive": {
            "client_position": 2,
            "share_of_voice": 34.5,
            "rankings": [],
            "overlap_analysis": {},
            "recent_activity": [],
        },
        "prompts": {
            "coverage_rate": 55.3,
        },
        "all_recommendations": [],
        "quick_wins": [],
    }

    # Generate report
    report = await report_service.generate_report(
        client_id=client_id,
        period_start=period_start,
        period_end=period_end,
        report_type=report_type,
        client_data=client_data,
    )

    # Store report
    report_record = Report(
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
        client_id=client_id,
    )

    db.add(report_record)
    await db.commit()
    await db.refresh(report_record)

    return {
        "id": report_record.id,
        "title": report.title,
        "executive_summary": report.executive_summary,
        "key_metrics": report.key_metrics,
        "sections": [
            {
                "title": s.title,
                "recommendations": s.recommendations,
            }
            for s in report.sections
        ],
        "generated_at": report.generated_at.isoformat(),
    }


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    format: str = Query(default="pdf", regex="^(pdf|csv)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Download a report in PDF or CSV format.
    """
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if format == "csv":
        # Generate CSV
        csv_data = f"Report: {report.title}\n"
        csv_data += f"Period: {report.period_start} to {report.period_end}\n\n"
        csv_data += "Metric,Value\n"
        for key, value in (report.summary_metrics or {}).items():
            csv_data += f"{key},{value}\n"

        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="report_{report_id}.csv"'
            },
        )
    else:
        # PDF would be generated with WeasyPrint
        raise HTTPException(status_code=501, detail="PDF export not yet implemented")


@router.get("/{report_id}/slides")
async def get_slides_outline(
    report_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get Google Slides outline for a report.
    """
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Generate slides outline
    slides = [
        {
            "type": "title",
            "title": report.title,
            "subtitle": f"Period: {report.period_start.strftime('%B %d')} - {report.period_end.strftime('%B %d, %Y')}",
        },
        {
            "type": "metrics",
            "title": "Key Metrics",
            "metrics": report.summary_metrics,
        },
        {
            "type": "section",
            "title": "Citation Performance",
            "data": report.citation_data,
        },
        {
            "type": "section",
            "title": "RRF Visibility",
            "data": report.rrf_data,
        },
        {
            "type": "section",
            "title": "Content Freshness",
            "data": report.freshness_data,
        },
        {
            "type": "section",
            "title": "Competitive Position",
            "data": report.competitor_data,
        },
        {
            "type": "recommendations",
            "title": "Next Steps",
            "recommendations": report.recommendations,
        },
    ]

    return {
        "report_id": report_id,
        "slides": slides,
        "total_slides": len(slides),
    }


# Report scheduling
@router.get("/{client_id}/schedules")
async def list_report_schedules(
    client_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    List report schedules for a client.
    """
    result = await db.execute(
        select(ReportSchedule).where(ReportSchedule.client_id == client_id)
    )
    schedules = result.scalars().all()

    return [
        {
            "id": s.id,
            "frequency": s.frequency,
            "recipients": s.recipients,
            "is_active": s.is_active,
            "last_run_at": s.last_run_at,
            "next_run_at": s.next_run_at,
        }
        for s in schedules
    ]


@router.post("/{client_id}/schedules")
async def create_report_schedule(
    client_id: int,
    frequency: str = Query(..., regex="^(weekly|monthly)$"),
    recipients: List[str] = Query(...),
    day_of_week: Optional[int] = Query(default=1, ge=0, le=6),  # Monday default
    day_of_month: Optional[int] = Query(default=1, ge=1, le=28),
    hour: int = Query(default=9, ge=0, le=23),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a scheduled report.
    """
    schedule = ReportSchedule(
        frequency=frequency,
        day_of_week=day_of_week if frequency == "weekly" else None,
        day_of_month=day_of_month if frequency == "monthly" else None,
        hour=hour,
        recipients=recipients,
        is_active=True,
        client_id=client_id,
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
