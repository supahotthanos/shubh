from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Client(Base, TimestampMixin):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    industry = Column(String(100))
    logo_url = Column(String(500))
    is_active = Column(Boolean, default=True)

    # Brand information for citation matching
    brand_names = Column(JSON, default=list)  # ["Brand", "Brand.com", "Brand Inc"]
    brand_keywords = Column(JSON, default=list)  # Keywords that indicate brand mention

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="clients")

    # Relationships
    domains = relationship("ClientDomain", back_populates="client", cascade="all, delete-orphan")
    prompts = relationship("Prompt", back_populates="client", cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="client", cascade="all, delete-orphan")
    keywords = relationship("Keyword", back_populates="client", cascade="all, delete-orphan")
    tracked_content = relationship("TrackedContent", back_populates="client", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="client", cascade="all, delete-orphan")
    competitors = relationship("Competitor", back_populates="client", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="client", cascade="all, delete-orphan")


class ClientDomain(Base, TimestampMixin):
    __tablename__ = "client_domains"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, index=True)
    is_primary = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

    # GSC Integration
    gsc_property_url = Column(String(500))
    gsc_connected = Column(Boolean, default=False)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="domains")
