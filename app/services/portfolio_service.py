"""Portfolio Service - 持仓数据服务"""

from typing import Dict, List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.exceptions import PortfolioNotFoundError, PositionNotFoundError
from app.models import Portfolio, Position

logger = get_logger(__name__)


class PortfolioService:
    """持仓数据服务类"""
    
    def __init__(self, db: Session):
        """
        初始化持仓服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def get_portfolio(self, portfolio_id: int) -> Optional[Portfolio]:
        """
        获取持仓组合
        
        Args:
            portfolio_id: 组合ID
            
        Returns:
            Portfolio: 持仓组合对象，不存在返回 None
        """
        try:
            portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if portfolio:
                logger.debug(f"✓ 获取持仓组合: {portfolio.name} (ID: {portfolio.id})")
            else:
                logger.warning(f"⚠️ 持仓组合不存在: ID={portfolio_id}")
            return portfolio
        except Exception as e:
            logger.error(f"✗ 获取持仓组合失败: {e}")
            return None
    
    def get_positions(self, portfolio_id: int) -> List[Position]:
        """
        获取持仓列表
        
        Args:
            portfolio_id: 组合ID
            
        Returns:
            List[Position]: 持仓列表
        """
        try:
            positions = self.db.query(Position).filter(
                Position.portfolio_id == portfolio_id
            ).all()
            logger.debug(f"✓ 获取持仓列表: {len(positions)} 只股票")
            return positions
        except Exception as e:
            logger.error(f"✗ 获取持仓列表失败: {e}")
            return []
    
    def calculate_position_metrics(
        self, 
        position: Position, 
        current_price: float
    ) -> Dict:
        """
        计算单个持仓的指标
        
        Args:
            position: 持仓对象
            current_price: 当前价格
            
        Returns:
            Dict: 包含市值、盈亏等指标
        """
        try:
            quantity = position.quantity
            cost_price = float(position.cost_price)
            
            # 计算市值
            market_value = quantity * current_price
            cost_value = quantity * cost_price
            
            # 计算盈亏
            profit_loss = market_value - cost_value
            profit_loss_pct = (profit_loss / cost_value * 100) if cost_value > 0 else 0
            
            return {
                "stock_code": position.stock_code,
                "stock_name": position.stock_name,
                "quantity": quantity,
                "cost_price": cost_price,
                "current_price": current_price,
                "market_value": market_value,
                "cost_value": cost_value,
                "profit_loss": profit_loss,
                "profit_loss_pct": profit_loss_pct
            }
        except Exception as e:
            logger.error(f"计算持仓指标失败: {position.stock_code}, {e}")
            return {}
    
    def calculate_portfolio_metrics(
        self, 
        portfolio_id: int, 
        positions_data: List[Dict]
    ) -> Dict:
        """
        计算组合级别的指标
        
        Args:
            portfolio_id: 组合ID
            positions_data: 持仓数据列表（包含市值、盈亏等）
            
        Returns:
            Dict: 组合级别的汇总指标
        """
        try:
            portfolio = self.get_portfolio(portfolio_id)
            if not portfolio:
                return {}
            
            # 计算总市值和总盈亏
            total_market_value = sum(p.get("market_value", 0) for p in positions_data)
            total_cost_value = sum(p.get("cost_value", 0) for p in positions_data)
            total_profit_loss = sum(p.get("profit_loss", 0) for p in positions_data)
            
            # 计算总收益率
            total_return_pct = (total_profit_loss / total_cost_value * 100) if total_cost_value > 0 else 0
            
            # 计算仓位占比（假设总资产包含现金）
            total_assets = float(portfolio.total_assets)
            position_ratio = (total_market_value / total_assets * 100) if total_assets > 0 else 0
            cash = total_assets - total_market_value
            
            # 计算每只股票的仓位占比
            for pos_data in positions_data:
                pos_data["position_ratio"] = (pos_data.get("market_value", 0) / total_assets * 100) if total_assets > 0 else 0
            
            metrics = {
                "portfolio_id": portfolio_id,
                "portfolio_name": portfolio.name,
                "total_assets": total_assets,
                "total_market_value": total_market_value,
                "total_cost_value": total_cost_value,
                "total_profit_loss": total_profit_loss,
                "total_return_pct": total_return_pct,
                "position_ratio": position_ratio,
                "cash": cash,
                "cash_ratio": 100 - position_ratio,
                "position_count": len(positions_data)
            }
            
            logger.info(f"   ✓ 组合指标: 总资产 ¥{total_assets:,.2f}, 市值 ¥{total_market_value:,.2f}, "
                        f"盈亏 {total_return_pct:+.2f}%, 仓位 {position_ratio:.1f}%")
            
            return metrics
        except Exception as e:
            logger.error(f"✗ 计算组合指标失败: {e}")
            return {}
    
    def add_position(
        self, 
        portfolio_id: int, 
        stock_code: str, 
        stock_name: str,
        quantity: int, 
        cost_price: float
    ) -> Optional[Position]:
        """
        添加持仓
        
        Args:
            portfolio_id: 组合ID
            stock_code: 股票代码
            stock_name: 股票名称
            quantity: 数量
            cost_price: 成本价
            
        Returns:
            Position: 新增的持仓对象
        """
        try:
            position = Position(
                portfolio_id=portfolio_id,
                stock_code=stock_code.upper(),
                stock_name=stock_name,
                quantity=quantity,
                cost_price=Decimal(str(cost_price))
            )
            self.db.add(position)
            self.db.commit()
            self.db.refresh(position)
            
            logger.info(f"✓ 添加持仓: {stock_code} {quantity}股 @ ¥{cost_price}")
            return position
        except Exception as e:
            self.db.rollback()
            logger.error(f"添加持仓失败: {e}")
            return None
    
    def update_position(
        self, 
        position_id: int, 
        quantity: Optional[int] = None,
        cost_price: Optional[float] = None
    ) -> bool:
        """
        更新持仓
        
        Args:
            position_id: 持仓ID
            quantity: 新数量（可选）
            cost_price: 新成本价（可选）
            
        Returns:
            bool: 是否成功
        """
        try:
            position = self.db.query(Position).filter(Position.id == position_id).first()
            if not position:
                logger.warning(f"持仓不存在: ID={position_id}")
                return False
            
            if quantity is not None:
                position.quantity = quantity
            if cost_price is not None:
                position.cost_price = Decimal(str(cost_price))
            
            self.db.commit()
            logger.info(f"✓ 更新持仓: {position.stock_code}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新持仓失败: {e}")
            return False
    
    def delete_position(self, position_id: int) -> bool:
        """
        删除持仓
        
        Args:
            position_id: 持仓ID
            
        Returns:
            bool: 是否成功
        """
        try:
            position = self.db.query(Position).filter(Position.id == position_id).first()
            if not position:
                logger.warning(f"持仓不存在: ID={position_id}")
                return False
            
            stock_code = position.stock_code
            self.db.delete(position)
            self.db.commit()
            
            logger.info(f"✓ 删除持仓: {stock_code}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除持仓失败: {e}")
            return False
