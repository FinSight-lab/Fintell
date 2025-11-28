"""
Position model representing a stock position in a portfolio.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base


class Position(Base):
    """
    Position model stores individual stock positions within a portfolio.
    
    Attributes:
        id: Primary key
        portfolio_id: Foreign key to the portfolio
        stock_code: Stock code in Wind format (e.g., 600519.SH)
        stock_name: Name of the stock
        quantity: Number of shares held
        cost_price: Average cost price per share
        created_at: Timestamp when the position was created
        updated_at: Timestamp when the position was last updated
    """
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    stock_code = Column(String(20), nullable=False)
    stock_name = Column(String(100))
    quantity = Column(Integer, nullable=False)
    cost_price = Column(DECIMAL(10, 4), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")

    # Constraints
    __table_args__ = (
        UniqueConstraint("portfolio_id", "stock_code", name="uq_portfolio_stock"),
    )

    def __repr__(self):
        return f"<Position(id={self.id}, stock_code={self.stock_code}, quantity={self.quantity}, cost_price={self.cost_price})>"
