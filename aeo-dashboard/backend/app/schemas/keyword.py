from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from app.schemas.base import BaseSchema


class KeywordCreate(BaseModel):
    keyword: str = Field(..., min_length=1)
    monthly_search_volume: Optional[int] = None
    keyword_difficulty: Optional[float] = None
    cpc: Optional[float] = None
    search_intent: Optional[str] = None
    is_priority: bool = False


class KeywordUpdate(BaseModel):
    monthly_search_volume: Optional[int] = None
    keyword_difficulty: Optional[float] = None
    cpc: Optional[float] = None
    search_intent: Optional[str] = None
    is_priority: Optional[bool] = None
    track_rankings: Optional[bool] = None


class KeywordResponse(BaseSchema):
    id: int
    keyword: str
    normalized_keyword: Optional[str]
    monthly_search_volume: Optional[int]
    keyword_difficulty: Optional[float]
    cpc: Optional[float]
    search_intent: Optional[str]
    is_priority: bool
    track_rankings: bool
    created_at: datetime
    updated_at: datetime

    # Latest RRF score
    rrf_score: Optional[float] = None
    rrf_meets_threshold: Optional[bool] = None


class SubQueryRank(BaseModel):
    query: str
    rank: int
    url: str
    search_engine: str = "google"


class RRFCalculation(BaseModel):
    keyword_id: int
    sub_queries: List[SubQueryRank]


class RRFScoreResponse(BaseSchema):
    id: int
    keyword_id: int
    keyword_text: Optional[str] = None

    sub_queries: List[Dict]
    k_constant: float
    raw_score: float
    normalized_score: float
    meets_threshold: bool

    total_appearances: int
    avg_rank: float
    best_rank: int
    worst_rank: int

    appearances_needed: int
    target_rank_each: int

    calculated_at: datetime


class RRFQuickReference(BaseModel):
    """Quick reference table for RRF thresholds"""
    appearances: int
    max_rank_each: int
    guaranteed_score: float
    meets_threshold: bool


class RRFRecommendation(BaseModel):
    keyword: str
    current_score: float
    target_score: float = 0.020
    gap: float
    recommendation: str
    priority: str  # "high", "medium", "low"
    action_items: List[str]
