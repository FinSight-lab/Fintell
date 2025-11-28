"""
Report model for storing generated analysis reports.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from app.models.base import Base


class Report(Base):
    """
    Report model stores generated analysis reports (daily and weekly).
    
    Attributes:
        id: Primary key
        portfolio_id: Foreign key to the portfolio
        report_type: Type of report ('daily' or 'weekly')
        report_date: Date of the report
        content: JSON field storing structured report data
        html_content: HTML-rendered version of the report
        created_at: Timestamp when the report was created
    """
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    report_type = Column(String(20), nullable=False, comment="'daily' or 'weekly'")
    report_date = Column(Date, nullable=False)
    content = Column(JSON, nullable=False, comment="Structured report data")
    html_content = Column(Text, comment="HTML-rendered report content")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="reports")

    # Indexes
    __table_args__ = (
        Index("idx_reports_portfolio_date", "portfolio_id", report_date.desc()),
    )

    def __repr__(self):
        return f"<Report(id={self.id}, portfolio_id={self.portfolio_id}, report_type={self.report_type}, report_date={self.report_date})>"
