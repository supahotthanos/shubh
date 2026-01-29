from app.schemas.base import BaseSchema, PaginatedResponse
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse, ClientDomainCreate
from app.schemas.prompt import PromptCreate, PromptUpdate, PromptResponse, PromptBulkImport
from app.schemas.citation import CitationResponse, CitationCheckResponse, CitationStats
from app.schemas.keyword import KeywordCreate, KeywordResponse, RRFScoreResponse, RRFCalculation
from app.schemas.content import TrackedContentCreate, TrackedContentResponse, FreshnessResponse
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignAssetCreate
from app.schemas.dashboard import DashboardMetrics, CitationTrend, PlatformBreakdown

__all__ = [
    "BaseSchema",
    "PaginatedResponse",
    "ClientCreate",
    "ClientUpdate",
    "ClientResponse",
    "ClientDomainCreate",
    "PromptCreate",
    "PromptUpdate",
    "PromptResponse",
    "PromptBulkImport",
    "CitationResponse",
    "CitationCheckResponse",
    "CitationStats",
    "KeywordCreate",
    "KeywordResponse",
    "RRFScoreResponse",
    "RRFCalculation",
    "TrackedContentCreate",
    "TrackedContentResponse",
    "FreshnessResponse",
    "CampaignCreate",
    "CampaignResponse",
    "CampaignAssetCreate",
    "DashboardMetrics",
    "CitationTrend",
    "PlatformBreakdown",
]
