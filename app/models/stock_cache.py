"""Stock data cache model"""

from sqlalchemy import Column, Integer, String, Date, Numeric, BigInteger, DateTime, JSON, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class StockDataCache(Base):
    """股票数据缓存模型（可选使用）"""
    __tablename__ = "stock_data_cache"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(20), nullable=False, index=True, comment="股票代码")
    date = Column(Date, nullable=False, index=True, comment="日期")
    
    # 基础行情数据
    open_price = Column(Numeric(10, 3), nullable=True, comment="开盘价")
    high_price = Column(Numeric(10, 3), nullable=True, comment="最高价")
    low_price = Column(Numeric(10, 3), nullable=True, comment="最低价")
    close_price = Column(Numeric(10, 3), nullable=False, comment="收盘价")
    volume = Column(BigInteger, nullable=True, comment="成交量")
    amount = Column(Numeric(20, 2), nullable=True, comment="成交额")
    
    # 技术指标（JSON 格式存储）
    indicators = Column(JSON, nullable=True, comment="技术指标（MA, RSI, MACD, BOLL 等）")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # 唯一约束：同一股票同一天只能有一条记录
    __table_args__ = (
        UniqueConstraint('stock_code', 'date', name='uix_stock_date'),
    )

    def __repr__(self):
        return f"<StockDataCache(stock_code='{self.stock_code}', date={self.date}, close={self.close_price})>"
