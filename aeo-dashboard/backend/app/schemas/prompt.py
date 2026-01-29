from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.base import BaseSchema


class PromptCreate(BaseModel):
    text: str = Field(..., min_length=3)
    category_id: Optional[int] = None
    intent_type: Optional[str] = None
    is_branded: bool = False
    check_frequency_hours: int = 24


class PromptUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=3)
    category_id: Optional[int] = None
    intent_type: Optional[str] = None
    is_branded: Optional[bool] = None
    check_frequency_hours: Optional[int] = None


class PromptBulkImport(BaseModel):
    prompts: List[str]
    category_id: Optional[int] = None
    source: str = "manual"


class PromptGSCImport(BaseModel):
    min_impressions: int = 1000
    min_clicks: int = 10
    max_position: float = 50.0
    days_back: int = 90


class PromptResponse(BaseSchema):
    id: int
    text: str
    normalized_text: Optional[str]
    source: str
    intent_type: Optional[str]
    is_branded: bool

    # GSC data
    gsc_impressions: Optional[int]
    gsc_clicks: Optional[int]
    gsc_avg_position: Optional[float]

    # Visibility
    is_visible: Optional[bool]
    visibility_score: Optional[float]
    last_checked_at: Optional[str]
    check_frequency_hours: int

    # Category
    category_id: Optional[int]
    category_name: Optional[str] = None

    created_at: datetime
    updated_at: datetime


class PromptVisibilityCheck(BaseModel):
    prompt_id: int
    platforms: List[str] = ["chatgpt", "perplexity", "claude", "google_ai"]
    check_count: int = 3  # Number of times to check for variance


class PromptCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    color: str = "#6366f1"


class PromptCategoryResponse(BaseSchema):
    id: int
    name: str
    slug: str
    description: Optional[str]
    color: str
    prompt_count: int = 0
