from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from app.schemas.base import BaseSchema


class CitationResponse(BaseSchema):
    id: int
    prompt_id: int
    prompt_text: Optional[str] = None
    platform_id: int
    platform_name: Optional[str] = None

    cited_url: Optional[str]
    cited_text: Optional[str]
    mention_type: str
    position: Optional[int]
    is_primary: bool
    context_snippet: Optional[str]

    confidence_score: Optional[float]
    sentiment: Optional[str]

    first_seen_at: Optional[datetime]
    last_seen_at: Optional[datetime]
    is_currently_visible: bool

    created_at: datetime


class CitationCheckResponse(BaseSchema):
    id: int
    prompt_id: int
    platform_id: int
    was_cited: bool
    position: Optional[int]
    model_version: Optional[str]
    check_duration_ms: Optional[int]
    created_at: datetime


class CitationStats(BaseModel):
    total_citations: int
    active_citations: int
    linked_mentions: int
    unlinked_mentions: int
    brand_mentions: int

    by_platform: Dict[str, int]
    by_position: Dict[str, int]  # "1st mention", "2nd mention", etc.

    avg_position: float
    citation_stability_score: float  # % consistency across checks


class CitationTrendPoint(BaseModel):
    date: str
    total_citations: int
    new_citations: int
    lost_citations: int
    stability_score: float


class CitationTrend(BaseModel):
    period: str  # "30d", "60d", "90d"
    data_points: List[CitationTrendPoint]
    total_change: int
    change_percentage: float
    avg_velocity: float  # citations gained per day


class CitationHeatmapCell(BaseModel):
    prompt_category: str
    platform: str
    citation_count: int
    stability_score: float
    avg_position: float


class CitationHeatmap(BaseModel):
    categories: List[str]
    platforms: List[str]
    cells: List[CitationHeatmapCell]


class PlatformCitationStats(BaseModel):
    platform_name: str
    platform_slug: str
    total_citations: int
    active_citations: int
    avg_position: float
    stability_score: float
    trend: str  # "up", "down", "stable"
    trend_percentage: float
