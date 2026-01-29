from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.citation import Citation, CitationCheck, CitationPlatform
from app.schemas.citation import (
    CitationResponse,
    CitationCheckResponse,
    CitationStats,
    CitationTrend,
    CitationHeatmap,
    PlatformCitationStats,
)

router = APIRouter()


@router.get("/{client_id}", response_model=List[CitationResponse])
async def list_citations(
    client_id: int,
    platform: Optional[str] = None,
    mention_type: Optional[str] = None,
    is_visible: Optional[bool] = True,
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    List all citations for a client.
    """
    query = select(Citation).where(Citation.client_id == client_id)

    if platform:
        query = query.join(CitationPlatform).where(CitationPlatform.slug == platform)
    if mention_type:
        query = query.where(Citation.mention_type == mention_type)
    if is_visible is not None:
        query = query.where(Citation.is_currently_visible == is_visible)

    query = query.order_by(Citation.last_seen_at.desc()).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{client_id}/stats", response_model=CitationStats)
async def get_citation_stats(
    client_id: int,
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """
    Get citation statistics for a client.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Get citations
    result = await db.execute(
        select(Citation).where(
            Citation.client_id == client_id,
            Citation.first_seen_at >= cutoff_date,
        )
    )
    citations = result.scalars().all()

    total = len(citations)
    active = sum(1 for c in citations if c.is_currently_visible)
    linked = sum(1 for c in citations if c.mention_type == "linked")
    unlinked = sum(1 for c in citations if c.mention_type == "unlinked")
    brand = sum(1 for c in citations if c.mention_type == "brand_mention")

    # Platform breakdown
    by_platform = {}
    for c in citations:
        platform = str(c.platform_id)  # Would join to get name
        by_platform[platform] = by_platform.get(platform, 0) + 1

    # Position breakdown
    by_position = {"1st": 0, "2nd": 0, "3rd": 0, "4th+": 0}
    for c in citations:
        if c.position == 1:
            by_position["1st"] += 1
        elif c.position == 2:
            by_position["2nd"] += 1
        elif c.position == 3:
            by_position["3rd"] += 1
        elif c.position:
            by_position["4th+"] += 1

    # Calculate stability from checks
    checks_result = await db.execute(
        select(CitationCheck).where(
            CitationCheck.prompt_id.in_([c.prompt_id for c in citations])
        ).order_by(CitationCheck.created_at.desc()).limit(1000)
    )
    checks = checks_result.scalars().all()

    if checks:
        cited_checks = sum(1 for c in checks if c.was_cited)
        stability = (cited_checks / len(checks)) * 100
    else:
        stability = 0

    avg_position = sum(c.position for c in citations if c.position) / max(total, 1)

    return CitationStats(
        total_citations=total,
        active_citations=active,
        linked_mentions=linked,
        unlinked_mentions=unlinked,
        brand_mentions=brand,
        by_platform=by_platform,
        by_position=by_position,
        avg_position=avg_position,
        citation_stability_score=stability,
    )


@router.get("/{client_id}/trend", response_model=CitationTrend)
async def get_citation_trend(
    client_id: int,
    period: str = Query(default="30d", regex="^(7d|30d|60d|90d)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get citation trend over time.
    """
    days = int(period.replace("d", ""))
    cutoff = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(Citation).where(
            Citation.client_id == client_id,
            Citation.first_seen_at >= cutoff,
        ).order_by(Citation.first_seen_at)
    )
    citations = result.scalars().all()

    # Group by day
    daily_data = {}
    for c in citations:
        day = c.first_seen_at.strftime("%Y-%m-%d")
        if day not in daily_data:
            daily_data[day] = {"new": 0, "total": 0}
        daily_data[day]["new"] += 1

    # Build data points
    data_points = []
    running_total = 0
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
        new_count = daily_data.get(date, {}).get("new", 0)
        running_total += new_count
        data_points.append({
            "date": date,
            "citations": running_total,
            "stability": 75 + (i % 10),  # Would calculate actual stability
        })

    start_total = data_points[0]["citations"] if data_points else 0
    end_total = data_points[-1]["citations"] if data_points else 0

    return CitationTrend(
        period=period,
        data_points=data_points,
        total_start=start_total,
        total_end=end_total,
        net_change=end_total - start_total,
    )


@router.get("/{client_id}/heatmap", response_model=CitationHeatmap)
async def get_citation_heatmap(
    client_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get citation heatmap by prompt category and platform.
    """
    # This would aggregate citations by category and platform
    # Placeholder response
    return CitationHeatmap(
        categories=["Product", "Pricing", "Reviews", "Comparison", "How-to"],
        platforms=["ChatGPT", "Perplexity", "Claude", "Google AI"],
        cells=[
            {"prompt_category": "Product", "platform": "ChatGPT", "citation_count": 15, "stability_score": 85, "avg_position": 1.5},
            {"prompt_category": "Product", "platform": "Perplexity", "citation_count": 12, "stability_score": 78, "avg_position": 2.0},
            {"prompt_category": "Reviews", "platform": "ChatGPT", "citation_count": 8, "stability_score": 72, "avg_position": 2.2},
            # ... more cells
        ],
    )


@router.get("/{client_id}/platforms", response_model=List[PlatformCitationStats])
async def get_platform_stats(
    client_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get citation statistics by platform.
    """
    platforms_result = await db.execute(select(CitationPlatform))
    platforms = platforms_result.scalars().all()

    stats = []
    for platform in platforms:
        citations_result = await db.execute(
            select(Citation).where(
                Citation.client_id == client_id,
                Citation.platform_id == platform.id,
            )
        )
        citations = citations_result.scalars().all()

        total = len(citations)
        active = sum(1 for c in citations if c.is_currently_visible)
        positions = [c.position for c in citations if c.position]
        avg_pos = sum(positions) / len(positions) if positions else 0

        stats.append(PlatformCitationStats(
            platform_name=platform.name,
            platform_slug=platform.slug,
            total_citations=total,
            active_citations=active,
            avg_position=avg_pos,
            stability_score=80.0,  # Would calculate
            trend="up",
            trend_percentage=5.0,
        ))

    return stats
