from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Float, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class AuthoritySignal(Base, TimestampMixin):
    """Track various authority signals for a domain"""
    __tablename__ = "authority_signals"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, index=True)

    # Common Crawl WebGraph metrics
    harmonic_centrality_rank = Column(Integer)
    harmonic_centrality_score = Column(Float)
    pagerank_score = Column(Float)
    pagerank_rank = Column(Integer)

    # Traditional SEO metrics
    domain_rating = Column(Float)  # Ahrefs DR
    domain_authority = Column(Float)  # Moz DA
    trust_flow = Column(Float)  # Majestic
    citation_flow = Column(Float)

    # Link profile
    referring_domains = Column(Integer)
    total_backlinks = Column(Integer)
    dofollow_backlinks = Column(Integer)

    # Trust indicators
    has_wikipedia_citation = Column(Boolean, default=False)
    wikipedia_citation_url = Column(String(2000))
    reddit_mention_count = Column(Integer)
    forum_mention_count = Column(Integer)
    press_release_count = Column(Integer)

    # Schema implementation
    schema_implementation_score = Column(Float)  # 0-100
    schema_types_implemented = Column(JSON)

    # PSL (Public Suffix List) analysis
    is_subdomain = Column(Boolean, default=False)
    root_domain = Column(String(255))
    authority_dilution_warning = Column(Boolean, default=False)  # For Medium, LinkedIn, etc.
    dilution_explanation = Column(Text)

    measured_at = Column(DateTime(timezone=True))


class WebGraphMetric(Base, TimestampMixin):
    """Historical WebGraph metrics for trend tracking"""
    __tablename__ = "webgraph_metrics"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, index=True)

    # Metric type and value
    metric_type = Column(String(50))  # harmonic_centrality, pagerank, etc.
    metric_value = Column(Float)
    metric_rank = Column(Integer)

    # Source
    source = Column(String(50))  # common_crawl, ahrefs, etc.
    crawl_date = Column(String(20))  # e.g., "2024-01" for Common Crawl

    measured_at = Column(DateTime(timezone=True))
