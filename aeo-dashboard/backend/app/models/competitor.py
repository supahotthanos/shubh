from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Float, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Competitor(Base, TimestampMixin):
    """Competitor tracking for AI visibility"""
    __tablename__ = "competitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=False, index=True)

    # Brand identifiers
    brand_names = Column(JSON, default=list)  # Alternative names for matching

    # Current metrics
    total_citations = Column(Integer, default=0)
    citation_share = Column(Float)  # % of prompts where they're cited
    avg_position = Column(Float)  # Average citation position

    # Authority metrics
    harmonic_centrality_rank = Column(Integer)
    domain_rating = Column(Float)

    # Tracking
    is_active = Column(Boolean, default=True)
    last_analyzed_at = Column(DateTime(timezone=True))

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="competitors")

    citations = relationship("CompetitorCitation", back_populates="competitor", cascade="all, delete-orphan")


class CompetitorCitation(Base, TimestampMixin):
    """Track competitor citations for specific prompts"""
    __tablename__ = "competitor_citations"

    id = Column(Integer, primary_key=True, index=True)

    # Citation details
    prompt_text = Column(Text, nullable=False)
    platform = Column(String(50))
    position = Column(Integer)
    cited_url = Column(String(2000))
    mention_type = Column(String(50))  # linked, unlinked, brand_mention

    # Overlap tracking
    client_also_cited = Column(Boolean, default=False)  # Was client cited too?
    client_position = Column(Integer)  # If yes, what position?

    first_seen_at = Column(DateTime(timezone=True))
    last_seen_at = Column(DateTime(timezone=True))
    is_currently_visible = Column(Boolean, default=True)

    competitor_id = Column(Integer, ForeignKey("competitors.id"), nullable=False)
    competitor = relationship("Competitor", back_populates="citations")
