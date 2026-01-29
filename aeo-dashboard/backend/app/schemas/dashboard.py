from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class TrendIndicator(BaseModel):
    value: float
    change: float
    change_percentage: float
    trend: str  # "up", "down", "stable"
    period: str  # "day", "week", "month"


class DashboardMetrics(BaseModel):
    """Main dashboard KPIs"""
    # Total AI Citations This Month
    total_citations: int
    citations_trend: TrendIndicator

    # Citation Stability Score
    citation_stability_score: float  # 0-100
    stability_trend: TrendIndicator

    # RRF Visibility Score
    rrf_visibility_score: float  # 0.000 - 0.100
    rrf_trend: TrendIndicator
    keywords_meeting_threshold: int
    keywords_total: int

    # Content Freshness Grade
    content_freshness_grade: str  # A-F
    content_freshness_score: float  # 0-100
    pages_needing_refresh: int

    # Active Campaigns
    active_campaigns: int
    campaign_breakdown: Dict[str, int]  # By type

    # Competitive Position
    competitive_position: int  # 1st, 2nd, 3rd in category
    share_of_voice: float  # 0-100

    # Prompt Coverage
    prompts_visible: int
    prompts_total: int
    prompt_coverage_percentage: float


class PlatformBreakdown(BaseModel):
    platform_name: str
    platform_slug: str
    icon_url: Optional[str]
    total_citations: int
    active_citations: int
    avg_position: float
    stability_score: float
    trend: str
    trend_value: float


class CitationTrendPoint(BaseModel):
    date: str
    citations: int
    stability: float


class CitationTrend(BaseModel):
    period: str  # "30d", "60d", "90d"
    data_points: List[CitationTrendPoint]
    total_start: int
    total_end: int
    net_change: int


class PromptVisibilitySummary(BaseModel):
    already_visible: List[Dict]  # Prompts where client is cited
    high_potential: List[Dict]  # Strong GSC, not yet visible in AI
    at_risk: List[Dict]  # Recently lost visibility


class CompetitorComparison(BaseModel):
    client_name: str
    client_citations: int
    client_share: float
    competitors: List[Dict]  # Name, citations, share


class AlertItem(BaseModel):
    id: str
    type: str  # "citation_drop", "freshness_warning", "rrf_alert", etc.
    severity: str  # "critical", "warning", "info"
    title: str
    description: str
    action_url: Optional[str]
    created_at: datetime


class DashboardAlerts(BaseModel):
    critical: List[AlertItem]
    warnings: List[AlertItem]
    info: List[AlertItem]
    total_unread: int


class QuickAction(BaseModel):
    id: str
    title: str
    description: str
    action_type: str
    priority: int
    estimated_impact: str


class DashboardQuickActions(BaseModel):
    """Prioritized actions for the user"""
    actions: List[QuickAction]
