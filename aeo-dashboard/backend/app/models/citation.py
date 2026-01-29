from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Float, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class Platform(str, enum.Enum):
    CHATGPT = "chatgpt"
    PERPLEXITY = "perplexity"
    CLAUDE = "claude"
    GOOGLE_AI = "google_ai"
    GROK = "grok"
    BING_COPILOT = "bing_copilot"
    GEMINI = "gemini"


class CitationPlatform(Base, TimestampMixin):
    __tablename__ = "citation_platforms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    icon_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    scraper_config = Column(JSON)  # Platform-specific scraper settings

    citations = relationship("Citation", back_populates="platform")
    citation_checks = relationship("CitationCheck", back_populates="platform")


class Citation(Base, TimestampMixin):
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)

    # Citation details
    cited_url = Column(String(2000))  # The URL that was cited (if linked)
    cited_text = Column(Text)  # The exact text that mentioned the brand
    mention_type = Column(String(50))  # "linked", "unlinked", "brand_mention"

    # Position tracking
    position = Column(Integer)  # 1 = first mention, 2 = second, etc.
    is_primary = Column(Boolean, default=False)  # First/prominent mention
    context_snippet = Column(Text)  # Surrounding context

    # Confidence
    confidence_score = Column(Float)  # How confident we are this is a real citation
    sentiment = Column(String(20))  # positive, neutral, negative

    # Timing
    first_seen_at = Column(DateTime(timezone=True))
    last_seen_at = Column(DateTime(timezone=True))
    is_currently_visible = Column(Boolean, default=True)

    # Relationships
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="citations")

    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    prompt = relationship("Prompt", back_populates="citations")

    platform_id = Column(Integer, ForeignKey("citation_platforms.id"), nullable=False)
    platform = relationship("CitationPlatform", back_populates="citations")


class CitationCheck(Base, TimestampMixin):
    """Individual check event - for tracking history and stability"""
    __tablename__ = "citation_checks"

    id = Column(Integer, primary_key=True, index=True)

    # Check results
    was_cited = Column(Boolean, nullable=False)
    position = Column(Integer)
    response_text = Column(Text)  # Full AI response for debugging
    response_hash = Column(String(64))  # For detecting response changes

    # Technical details
    model_version = Column(String(100))  # e.g., "gpt-4-turbo", "claude-3-opus"
    temperature = Column(Float)
    check_duration_ms = Column(Integer)

    # Relationships
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    prompt = relationship("Prompt", back_populates="citation_checks")

    platform_id = Column(Integer, ForeignKey("citation_platforms.id"), nullable=False)
    platform = relationship("CitationPlatform", back_populates="citation_checks")
