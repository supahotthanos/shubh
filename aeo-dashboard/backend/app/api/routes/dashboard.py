from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.schemas.dashboard import (
    DashboardMetrics,
    PlatformBreakdown,
    CitationTrend,
    DashboardAlerts,
    DashboardQuickActions,
)

router = APIRouter()


@router.get("/metrics/{client_id}", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    client_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get main dashboard KPIs for a client.

    Returns:
    - Total AI Citations This Month (with trend)
    - Citation Stability Score
    - RRF Visibility Score
    - Content Freshness Grade
    - Active Campaigns
    - Competitive Position
    - Prompt Coverage
    """
    # In production, this would fetch from database
    # Placeholder response structure
    return DashboardMetrics(
        total_citations=142,
        citations_trend={
            "value": 142,
            "change": 23,
            "change_percentage": 19.3,
            "trend": "up",
            "period": "month",
        },
        citation_stability_score=78.5,
        stability_trend={
            "value": 78.5,
            "change": 2.3,
            "change_percentage": 3.0,
            "trend": "up",
            "period": "month",
        },
        rrf_visibility_score=0.024,
        rrf_trend={
            "value": 0.024,
            "change": 0.003,
            "change_percentage": 14.3,
            "trend": "up",
            "period": "month",
        },
        keywords_meeting_threshold=18,
        keywords_total=25,
        content_freshness_grade="B",
        content_freshness_score=72.0,
        pages_needing_refresh=4,
        active_campaigns=3,
        campaign_breakdown={
            "content_publish": 1,
            "guest_post": 1,
            "press_release": 1,
        },
        competitive_position=2,
        share_of_voice=34.5,
        prompts_visible=47,
        prompts_total=85,
        prompt_coverage_percentage=55.3,
    )


@router.get("/platforms/{client_id}", response_model=list[PlatformBreakdown])
async def get_platform_breakdown(
    client_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get citation breakdown by AI platform.

    Platforms: ChatGPT, Perplexity, Claude, Google AI, Grok, etc.
    """
    return [
        PlatformBreakdown(
            platform_name="ChatGPT",
            platform_slug="chatgpt",
            icon_url="/icons/chatgpt.svg",
            total_citations=58,
            active_citations=52,
            avg_position=1.8,
            stability_score=82.0,
            trend="up",
            trend_value=12.5,
        ),
        PlatformBreakdown(
            platform_name="Perplexity",
            platform_slug="perplexity",
            icon_url="/icons/perplexity.svg",
            total_citations=42,
            active_citations=38,
            avg_position=2.1,
            stability_score=76.0,
            trend="stable",
            trend_value=2.1,
        ),
        PlatformBreakdown(
            platform_name="Claude",
            platform_slug="claude",
            icon_url="/icons/claude.svg",
            total_citations=28,
            active_citations=26,
            avg_position=1.5,
            stability_score=88.0,
            trend="up",
            trend_value=18.2,
        ),
        PlatformBreakdown(
            platform_name="Google AI Overview",
            platform_slug="google_ai",
            icon_url="/icons/google-ai.svg",
            total_citations=14,
            active_citations=12,
            avg_position=2.4,
            stability_score=65.0,
            trend="down",
            trend_value=-8.3,
        ),
    ]


@router.get("/citations/trend/{client_id}", response_model=CitationTrend)
async def get_citation_trend(
    client_id: int,
    period: str = Query(default="30d", regex="^(7d|30d|60d|90d)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get citation trend over time.

    Periods: 7d, 30d, 60d, 90d
    """
    # Generate sample trend data
    days = int(period.replace("d", ""))
    data_points = []

    base_citations = 100
    for i in range(days):
        date = datetime.now() - timedelta(days=days - i - 1)
        citations = base_citations + (i * 1.5) + (i % 7) * 2
        data_points.append({
            "date": date.strftime("%Y-%m-%d"),
            "citations": int(citations),
            "stability": 75 + (i % 10),
        })

    return CitationTrend(
        period=period,
        data_points=data_points,
        total_start=100,
        total_end=142,
        net_change=42,
    )


@router.get("/alerts/{client_id}", response_model=DashboardAlerts)
async def get_dashboard_alerts(
    client_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get active alerts and notifications.

    Alert types:
    - citation_drop: Lost citation on important prompt
    - freshness_warning: Content needs refresh
    - rrf_alert: RRF score dropped below threshold
    - competitor_activity: Competitor gained citations
    """
    return DashboardAlerts(
        critical=[
            {
                "id": "alert-1",
                "type": "freshness_warning",
                "severity": "critical",
                "title": "Content Critically Outdated",
                "description": "Page 'Best SEO Tools 2024' hasn't been updated in 14 months",
                "action_url": "/content/123",
                "created_at": datetime.now() - timedelta(hours=2),
            }
        ],
        warnings=[
            {
                "id": "alert-2",
                "type": "citation_drop",
                "severity": "warning",
                "title": "Lost Citation on High-Value Prompt",
                "description": "No longer cited for 'best project management software'",
                "action_url": "/prompts/456",
                "created_at": datetime.now() - timedelta(hours=6),
            },
            {
                "id": "alert-3",
                "type": "competitor_activity",
                "severity": "warning",
                "title": "Competitor Published New Listicle",
                "description": "CompetitorX published 'Top 10 Tools' featuring themselves at #1",
                "action_url": "/competitors/789",
                "created_at": datetime.now() - timedelta(days=1),
            },
        ],
        info=[
            {
                "id": "alert-4",
                "type": "rrf_improvement",
                "severity": "info",
                "title": "RRF Score Improved",
                "description": "Keyword 'crm software' now meets citation threshold",
                "action_url": "/keywords/101",
                "created_at": datetime.now() - timedelta(days=2),
            },
        ],
        total_unread=4,
    )


@router.get("/quick-actions/{client_id}", response_model=DashboardQuickActions)
async def get_quick_actions(
    client_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get prioritized quick actions for the user.
    """
    return DashboardQuickActions(
        actions=[
            {
                "id": "action-1",
                "title": "Refresh Outdated Content",
                "description": "4 pages need content updates to maintain freshness scores",
                "action_type": "content_refresh",
                "priority": 1,
                "estimated_impact": "high",
            },
            {
                "id": "action-2",
                "title": "Add Missing Schema Markup",
                "description": "3 high-traffic pages missing structured data",
                "action_type": "schema_optimization",
                "priority": 2,
                "estimated_impact": "medium",
            },
            {
                "id": "action-3",
                "title": "Target New Keywords",
                "description": "12 high-potential prompts identified from GSC data",
                "action_type": "keyword_expansion",
                "priority": 3,
                "estimated_impact": "high",
            },
        ]
    )
