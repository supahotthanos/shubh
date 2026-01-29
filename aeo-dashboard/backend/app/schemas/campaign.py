from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from app.schemas.base import BaseSchema


class CampaignAssetCreate(BaseModel):
    asset_type: str
    title: str
    url: Optional[str] = None
    hosting_domain: Optional[str] = None
    hosting_domain_authority: Optional[float] = None
    client_position: Optional[int] = None
    total_items: Optional[int] = None


class CampaignAssetResponse(BaseSchema):
    id: int
    asset_type: str
    title: str
    url: Optional[str]
    hosting_domain: Optional[str]
    hosting_domain_authority: Optional[float]
    client_position: Optional[int]
    total_items: Optional[int]
    status: str
    published_at: Optional[datetime]
    indexed_at: Optional[datetime]
    first_citation_at: Optional[datetime]
    citation_count: int
    prompts_cited_for: Optional[List[str]]
    created_at: datetime


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    campaign_type: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_citations: Optional[int] = None
    target_domains: Optional[int] = None
    target_prompts: Optional[List[str]] = None
    budget: Optional[float] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_citations: Optional[int] = None
    target_domains: Optional[int] = None
    target_prompts: Optional[List[str]] = None
    budget: Optional[float] = None
    spent: Optional[float] = None


class CampaignResponse(BaseSchema):
    id: int
    name: str
    campaign_type: str
    description: Optional[str]
    status: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    target_citations: Optional[int]
    target_domains: Optional[int]
    target_prompts: Optional[List[str]]
    budget: Optional[float]
    spent: float
    created_at: datetime
    updated_at: datetime

    # Computed metrics
    total_assets: int = 0
    live_assets: int = 0
    citing_assets: int = 0
    total_citations_gained: int = 0


class CampaignMetricResponse(BaseSchema):
    id: int
    campaign_id: int

    total_assets: int
    live_assets: int
    indexed_assets: int
    citing_assets: int

    total_citations_gained: int
    new_prompts_visible: int
    citation_velocity: Optional[float]

    unique_domains: int
    avg_domain_authority: Optional[float]

    avg_time_to_index_days: Optional[float]
    avg_time_to_citation_days: Optional[float]

    measured_at: datetime


class CampaignTypeSummary(BaseModel):
    campaign_type: str
    total_campaigns: int
    active_campaigns: int
    total_assets: int
    total_citations_gained: int
    avg_time_to_citation_days: Optional[float]
