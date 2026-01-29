from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Float, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Report(Base, TimestampMixin):
    """Generated reports for clients"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    report_type = Column(String(50))  # weekly, monthly, quarterly, custom

    # Date range
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))

    # Report data (JSON snapshot)
    summary_metrics = Column(JSON)  # Key metrics at time of report
    citation_data = Column(JSON)
    rrf_data = Column(JSON)
    freshness_data = Column(JSON)
    campaign_data = Column(JSON)
    competitor_data = Column(JSON)
    recommendations = Column(JSON)  # List of prioritized recommendations

    # Generation
    generated_at = Column(DateTime(timezone=True))
    generated_by_id = Column(Integer)  # User who generated it

    # Files
    pdf_url = Column(String(500))
    slides_url = Column(String(500))

    # Status
    status = Column(String(50), default="draft")  # draft, published, sent

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="reports")


class ReportSchedule(Base, TimestampMixin):
    """Automated report scheduling"""
    __tablename__ = "report_schedules"

    id = Column(Integer, primary_key=True, index=True)

    # Schedule
    frequency = Column(String(20))  # weekly, monthly
    day_of_week = Column(Integer)  # 0-6 for weekly
    day_of_month = Column(Integer)  # 1-28 for monthly
    hour = Column(Integer, default=9)  # Hour to generate (UTC)

    # Recipients
    recipients = Column(JSON)  # List of email addresses
    include_pdf = Column(Boolean, default=True)
    include_slides = Column(Boolean, default=False)

    # Status
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True))
    next_run_at = Column(DateTime(timezone=True))

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
