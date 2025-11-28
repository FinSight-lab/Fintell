"""
Portfolio model representing a user's investment portfolio.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base


class Portfolio(Base):
    """
    Portfolio model stores the user's portfolio information.
    
    Attributes:
        id: Primary key
        user_id: Reference to the user who owns this portfolio
        total_assets: Total asset value in the portfolio
        created_at: Timestamp when the portfolio was created
        updated_at: Timestamp when the portfolio was last updated
    """
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    total_assets = Column(DECIMAL(15, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    positions = relationship("Position", back_populates="portfolio", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="portfolio", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Portfolio(id={self.id}, user_id={self.user_id}, total_assets={self.total_assets})>"
