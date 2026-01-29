from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Float, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class TrackedContent(Base, TimestampMixin):
    """Content pages being tracked for AI optimization"""
    __tablename__ = "tracked_content"

    id = Column(Integer, primary_key=True, index=True)

    # URL and metadata
    url = Column(String(2000), nullable=False, index=True)
    title = Column(String(500))
    meta_description = Column(Text)
    canonical_url = Column(String(2000))

    # Content analysis
    word_count = Column(Integer)
    avg_chunk_size_tokens = Column(Integer)  # Target ~500 tokens
    has_schema_markup = Column(Boolean, default=False)
    schema_types = Column(JSON)  # List of schema types found

    # Content structure
    heading_structure = Column(JSON)  # H1, H2, H3 hierarchy
    has_paa_style_sections = Column(Boolean)  # Question/answer format
    has_negation_content = Column(Boolean)  # "what it is" AND "what it isn't"

    # Tracking settings
    is_active = Column(Boolean, default=True)
    check_frequency_hours = Column(Integer, default=168)  # Weekly

    # Relationships
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="tracked_content")

    freshness_records = relationship("ContentFreshness", back_populates="content", cascade="all, delete-orphan")


class ContentFreshness(Base, TimestampMixin):
    """Track content freshness over time"""
    __tablename__ = "content_freshness"

    id = Column(Integer, primary_key=True, index=True)

    # Freshness detection
    last_modified_header = Column(DateTime(timezone=True))
    detected_publish_date = Column(DateTime(timezone=True))
    detected_update_date = Column(DateTime(timezone=True))
    content_hash = Column(String(64))  # For detecting actual content changes

    # Freshness scoring
    freshness_score = Column(Float)  # 0-100
    freshness_grade = Column(String(2))  # A, B, C, D, F
    days_since_update = Column(Integer)

    # Model-specific impact
    gpt_impact_score = Column(Float)  # Estimated impact on GPT citation
    llama_impact_score = Column(Float)
    gemini_impact_score = Column(Float)

    # Recommendations
    refresh_priority = Column(String(20))  # critical, high, medium, low
    refresh_recommendation = Column(Text)
    estimated_position_loss = Column(Integer)  # "Losing up to X positions"

    checked_at = Column(DateTime(timezone=True))

    content_id = Column(Integer, ForeignKey("tracked_content.id"), nullable=False)
    content = relationship("TrackedContent", back_populates="freshness_records")
