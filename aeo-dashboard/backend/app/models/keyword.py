from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Float, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Keyword(Base, TimestampMixin):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(500), nullable=False, index=True)
    normalized_keyword = Column(String(500), index=True)

    # Search volume and competition
    monthly_search_volume = Column(Integer)
    keyword_difficulty = Column(Float)
    cpc = Column(Float)  # Cost per click for value calculation
    search_intent = Column(String(50))  # informational, transactional, etc.

    # Tracking settings
    is_priority = Column(Boolean, default=False)
    track_rankings = Column(Boolean, default=True)

    # Relationships
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="keywords")

    rankings = relationship("KeywordRanking", back_populates="keyword", cascade="all, delete-orphan")
    rrf_scores = relationship("RRFScore", back_populates="keyword", cascade="all, delete-orphan")


class KeywordRanking(Base, TimestampMixin):
    """Track SERP rankings over time"""
    __tablename__ = "keyword_rankings"

    id = Column(Integer, primary_key=True, index=True)

    # Ranking data
    search_engine = Column(String(50), default="google")  # google, bing
    position = Column(Integer)
    url = Column(String(2000))  # Which URL is ranking
    is_featured_snippet = Column(Boolean, default=False)
    is_ai_overview = Column(Boolean, default=False)

    # SERP features
    serp_features = Column(JSON)  # List of features present (PAA, local pack, etc.)

    checked_at = Column(DateTime(timezone=True))

    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)
    keyword = relationship("Keyword", back_populates="rankings")


class RRFScore(Base, TimestampMixin):
    """Reciprocal Rank Fusion score calculations"""
    __tablename__ = "rrf_scores"

    id = Column(Integer, primary_key=True, index=True)

    # Sub-query appearances
    sub_queries = Column(JSON)  # List of sub-queries and their ranks
    # Example: [{"query": "best seo tools", "rank": 5}, {"query": "top seo software", "rank": 12}]

    # RRF Calculation
    k_constant = Column(Float, default=60.0)
    raw_score = Column(Float)  # Sum of 1/(k + rank) for all appearances
    normalized_score = Column(Float)  # Normalized to 0-1 scale
    meets_threshold = Column(Boolean)  # Whether score >= 0.020

    # Appearance metrics
    total_appearances = Column(Integer, default=0)
    avg_rank = Column(Float)
    best_rank = Column(Integer)
    worst_rank = Column(Integer)

    # Recommendations
    appearances_needed = Column(Integer)  # How many more appearances to meet threshold
    target_rank_each = Column(Integer)  # What rank needed if X more appearances

    calculated_at = Column(DateTime(timezone=True))

    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)
    keyword = relationship("Keyword", back_populates="rrf_scores")
