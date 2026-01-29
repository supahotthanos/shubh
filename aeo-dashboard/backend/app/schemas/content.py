from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from app.schemas.base import BaseSchema


class TrackedContentCreate(BaseModel):
    url: str = Field(..., min_length=10)
    check_frequency_hours: int = 168  # Weekly default


class TrackedContentUpdate(BaseModel):
    is_active: Optional[bool] = None
    check_frequency_hours: Optional[int] = None


class TrackedContentResponse(BaseSchema):
    id: int
    url: str
    title: Optional[str]
    meta_description: Optional[str]

    word_count: Optional[int]
    avg_chunk_size_tokens: Optional[int]
    has_schema_markup: bool
    schema_types: Optional[List[str]]

    heading_structure: Optional[Dict]
    has_paa_style_sections: bool
    has_negation_content: bool

    is_active: bool
    check_frequency_hours: int

    # Latest freshness
    freshness_score: Optional[float] = None
    freshness_grade: Optional[str] = None
    days_since_update: Optional[int] = None

    created_at: datetime
    updated_at: datetime


class FreshnessResponse(BaseSchema):
    id: int
    content_id: int
    content_url: Optional[str] = None

    last_modified_header: Optional[datetime]
    detected_publish_date: Optional[datetime]
    detected_update_date: Optional[datetime]

    freshness_score: float
    freshness_grade: str
    days_since_update: int

    gpt_impact_score: Optional[float]
    llama_impact_score: Optional[float]
    gemini_impact_score: Optional[float]

    refresh_priority: str
    refresh_recommendation: Optional[str]
    estimated_position_loss: Optional[int]

    checked_at: datetime


class FreshnessTarget(BaseModel):
    """Model-specific freshness recommendations"""
    model_family: str
    recommended_update_frequency_months: int
    current_age_months: float
    is_fresh: bool
    impact_description: str


class ContentOptimizationRecommendation(BaseModel):
    url: str
    title: Optional[str]
    recommendations: List[Dict]  # List of specific recommendations
    priority_score: float  # 0-100
    estimated_impact: str  # "high", "medium", "low"


class ChunkAnalysis(BaseModel):
    """Analysis of content chunking for LLM retrieval"""
    url: str
    total_chunks: int
    avg_tokens_per_chunk: int
    optimal_chunks: int  # Chunks in 400-600 token range
    oversized_chunks: int
    undersized_chunks: int
    recommendation: Optional[str]
