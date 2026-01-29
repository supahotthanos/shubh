from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Float, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class CampaignType(str, enum.Enum):
    CONTENT_PUBLISH = "content_publish"  # Original content creation
    GUEST_POST = "guest_post"  # Guest posting on high-authority sites
    PRESS_RELEASE = "press_release"  # Press release distribution
    RESEARCH_REPORT = "research_report"  # Original research/data
    LISTICLE = "listicle"  # "Best X" style content
    THOUGHT_LEADERSHIP = "thought_leadership"  # Expert content
    COMMUNITY_ENGAGEMENT = "community_engagement"  # Forum/community participation


class Campaign(Base, TimestampMixin):
    """Content marketing campaign tracking"""
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    campaign_type = Column(String(50), nullable=False)
    description = Column(Text)

    # Status
    status = Column(String(50), default="active")  # draft, active, paused, completed
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))

    # Goals
    target_citations = Column(Integer)
    target_domains = Column(Integer)
    target_prompts = Column(JSON)  # List of prompts we want to be cited for

    # Budget tracking
    budget = Column(Float)
    spent = Column(Float, default=0)

    # Relationships
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="campaigns")

    assets = relationship("CampaignAsset", back_populates="campaign", cascade="all, delete-orphan")
    metrics = relationship("CampaignMetric", back_populates="campaign", cascade="all, delete-orphan")


class CampaignAsset(Base, TimestampMixin):
    """Individual assets within a campaign"""
    __tablename__ = "campaign_assets"

    id = Column(Integer, primary_key=True, index=True)

    # Asset details
    asset_type = Column(String(50))  # article, press_release, guest_post, etc.
    title = Column(String(500))
    url = Column(String(2000))
    hosting_domain = Column(String(255))
    hosting_domain_authority = Column(Float)

    # Placement details (for listicles)
    client_position = Column(Integer)  # Position in the listicle (1 = first)
    total_items = Column(Integer)  # Total items in listicle

    # Status tracking
    status = Column(String(50), default="pending")  # pending, live, indexed, cited
    published_at = Column(DateTime(timezone=True))
    indexed_at = Column(DateTime(timezone=True))
    first_citation_at = Column(DateTime(timezone=True))

    # Performance
    citation_count = Column(Integer, default=0)
    prompts_cited_for = Column(JSON)  # List of prompts this asset gets cited for

    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    campaign = relationship("Campaign", back_populates="assets")


class CampaignMetric(Base, TimestampMixin):
    """Campaign performance metrics over time"""
    __tablename__ = "campaign_metrics"

    id = Column(Integer, primary_key=True, index=True)

    # Metrics
    total_assets = Column(Integer, default=0)
    live_assets = Column(Integer, default=0)
    indexed_assets = Column(Integer, default=0)
    citing_assets = Column(Integer, default=0)

    # Citation metrics
    total_citations_gained = Column(Integer, default=0)
    new_prompts_visible = Column(Integer, default=0)
    citation_velocity = Column(Float)  # Citations gained per day

    # Domain metrics
    unique_domains = Column(Integer, default=0)
    avg_domain_authority = Column(Float)

    # Time tracking
    avg_time_to_index_days = Column(Float)
    avg_time_to_citation_days = Column(Float)

    measured_at = Column(DateTime(timezone=True))

    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    campaign = relationship("Campaign", back_populates="metrics")
