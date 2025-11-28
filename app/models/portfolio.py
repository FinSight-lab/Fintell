"""Portfolio and Position models"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Portfolio(Base):
    """持仓组合模型"""
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, comment="用户ID（预留多用户支持）")
    name = Column(String(100), nullable=False, default="默认组合", comment="组合名称")
    total_assets = Column(Numeric(15, 2), nullable=False, default=0, comment="总资产")
    description = Column(Text, nullable=True, comment="组合描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    positions = relationship("Position", back_populates="portfolio", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="portfolio", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Portfolio(id={self.id}, name='{self.name}', total_assets={self.total_assets})>"


class Position(Base):
    """个股持仓模型"""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, comment="所属组合ID")
    stock_code = Column(String(20), nullable=False, index=True, comment="股票代码（如 600519.SH）")
    stock_name = Column(String(100), nullable=True, comment="股票名称")
    quantity = Column(Integer, nullable=False, default=0, comment="持仓数量（股）")
    cost_price = Column(Numeric(10, 3), nullable=False, comment="成本价")
    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    portfolio = relationship("Portfolio", back_populates="positions")

    def __repr__(self):
        return f"<Position(stock_code='{self.stock_code}', quantity={self.quantity}, cost_price={self.cost_price})>"

    @property
    def market_value(self):
        """计算市值（需要传入当前价格）"""
        # 这个方法需要在服务层调用时传入当前价格
        pass

    def calculate_profit_loss(self, current_price: float):
        """计算盈亏"""
        market_value = self.quantity * current_price
        cost_value = self.quantity * float(self.cost_price)
        profit_loss = market_value - cost_value
        profit_loss_pct = (profit_loss / cost_value * 100) if cost_value > 0 else 0
        
        return {
            "market_value": market_value,
            "cost_value": cost_value,
            "profit_loss": profit_loss,
            "profit_loss_pct": profit_loss_pct
        }
