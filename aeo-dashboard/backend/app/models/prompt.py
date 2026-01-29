from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Float, JSON, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class PromptSource(str, enum.Enum):
    MANUAL = "manual"
    GSC_IMPORT = "gsc_import"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    AI_SUGGESTED = "ai_suggested"


class PromptCategory(Base, TimestampMixin):
    __tablename__ = "prompt_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    color = Column(String(7), default="#6366f1")

    prompts = relationship("Prompt", back_populates="category")


class PromptCluster(Base, TimestampMixin):
    __tablename__ = "prompt_clusters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    centroid_embedding = Column(JSON)  # Stored embedding vector
    prompt_count = Column(Integer, default=0)

    prompts = relationship("Prompt", back_populates="cluster")


class Prompt(Base, TimestampMixin):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    normalized_text = Column(Text)  # Cleaned/normalized version for comparison

    # Classification
    source = Column(String(50), default=PromptSource.MANUAL.value)
    intent_type = Column(String(50))  # informational, transactional, navigational
    is_branded = Column(Boolean, default=False)

    # GSC data (if imported)
    gsc_impressions = Column(Integer)
    gsc_clicks = Column(Integer)
    gsc_avg_position = Column(Float)

    # Visibility tracking
    is_visible = Column(Boolean)  # Whether client is currently cited
    visibility_score = Column(Float)  # 0-100 confidence score
    last_checked_at = Column(String(50))  # ISO timestamp
    check_frequency_hours = Column(Integer, default=24)

    # Relationships
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="prompts")

    category_id = Column(Integer, ForeignKey("prompt_categories.id"))
    category = relationship("PromptCategory", back_populates="prompts")

    cluster_id = Column(Integer, ForeignKey("prompt_clusters.id"))
    cluster = relationship("PromptCluster", back_populates="prompts")

    citations = relationship("Citation", back_populates="prompt", cascade="all, delete-orphan")
    citation_checks = relationship("CitationCheck", back_populates="prompt", cascade="all, delete-orphan")
