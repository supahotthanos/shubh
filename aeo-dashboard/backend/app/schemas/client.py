from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.base import BaseSchema


class ClientDomainCreate(BaseModel):
    domain: str
    is_primary: bool = False
    gsc_property_url: Optional[str] = None


class ClientDomainResponse(BaseSchema):
    id: int
    domain: str
    is_primary: bool
    is_verified: bool
    gsc_connected: bool
    gsc_property_url: Optional[str]


class ClientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    industry: Optional[str] = None
    logo_url: Optional[str] = None
    brand_names: List[str] = []
    brand_keywords: List[str] = []
    domains: List[ClientDomainCreate] = []


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    industry: Optional[str] = None
    logo_url: Optional[str] = None
    brand_names: Optional[List[str]] = None
    brand_keywords: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ClientResponse(BaseSchema):
    id: int
    name: str
    slug: str
    description: Optional[str]
    industry: Optional[str]
    logo_url: Optional[str]
    brand_names: List[str]
    brand_keywords: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    domains: List[ClientDomainResponse] = []


class ClientSummary(BaseSchema):
    id: int
    name: str
    slug: str
    industry: Optional[str]
    is_active: bool
    total_citations: int = 0
    total_prompts: int = 0
    citation_stability_score: float = 0.0
