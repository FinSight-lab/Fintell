"""
StockDataCache model for caching stock market data and technical indicators.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DECIMAL, BigInteger, DateTime, UniqueConstraint, Index
from sqlalchemy.dialects.mysql import JSON
from app.models.base import Base


class StockDataCache(Base):
    """
    StockDataCache model stores historical stock data and calculated technical indicators.
    
    Attributes:
        id: Primary key
        stock_code: Stock code in Wind format (e.g., 600519.SH)
        date: Trading date
        close_price: Closing price
        volume: Trading volume
        indicators: JSON field storing all technical indicators (MA, RSI, MACD, BOLL, etc.)
        created_at: Timestamp when the cache entry was created
    """
    __tablename__ = "stock_data_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    close_price = Column(DECIMAL(10, 4))
    volume = Column(BigInteger)
    indicators = Column(JSON, comment="Technical indicators stored as JSON")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Constraints
    __table_args__ = (
        UniqueConstraint("stock_code", "date", name="uq_stock_date"),
        Index("idx_stock_data_code_date", "stock_code", date.desc()),
    )

    def __repr__(self):
        return f"<StockDataCache(id={self.id}, stock_code={self.stock_code}, date={self.date}, close_price={self.close_price})>"
