"""Data Integration Service - 数据整合服务"""

from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.logging import get_logger, ProgressTracker
from app.core.exceptions import (
    PortfolioNotFoundError,
    EmptyPortfolioError,
    DataError
)
from app.services.wind_service import WindService
from app.services.portfolio_service import PortfolioService

logger = get_logger(__name__)


class DataService:
    """数据整合服务类 - 整合持仓、行情、技术指标等所有数据"""
    
    def __init__(self, db: Session):
        """
        初始化数据服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.wind_service = WindService()
        self.portfolio_service = PortfolioService(db)
    
    def get_weekly_report_data(self, portfolio_id: int) -> Dict:
        """
        获取周报所需的完整数据
        
        Args:
            portfolio_id: 持仓组合ID
            
        Returns:
            Dict: 包含所有周报所需数据的字典
            
        Raises:
            PortfolioNotFoundError: 持仓组合不存在
            EmptyPortfolioError: 持仓组合为空
        """
        # 创建进度跟踪器
        progress = ProgressTracker(logger, total_steps=4, task_name="周报数据获取")
        progress.start()
        
        try:
            # 步骤 1: 获取持仓组合信息
            progress.step("获取持仓组合信息")
            portfolio = self.portfolio_service.get_portfolio(portfolio_id)
            if not portfolio:
                raise PortfolioNotFoundError(portfolio_id)
            
            # 步骤 2: 获取持仓列表
            progress.step("获取持仓列表")
            positions = self.portfolio_service.get_positions(portfolio_id)
            if not positions:
                raise EmptyPortfolioError(portfolio_id)
            
            logger.info(f"   📊 持仓组合: {portfolio.name}")
            logger.info(f"   💰 总资产: ¥{portfolio.total_assets:,.2f}")
            logger.info(f"   📋 持仓数量: {len(positions)} 只股票")
            
            # 步骤 3: 获取每只股票的完整数据
            progress.step("获取股票行情和技术指标")
            holdings_data = []
            success_count = 0
            fail_count = 0
            
            for i, position in enumerate(positions, 1):
                progress.sub_progress(i, len(positions), position.stock_code)
                
                try:
                    # 获取 Wind 数据
                    wind_data = self.wind_service.get_stock_complete_data(position.stock_code)
                    
                    if not wind_data or wind_data.get("data") is None:
                        logger.warning(f"   ⚠️  跳过 {position.stock_code}（无数据）")
                        fail_count += 1
                        continue
                    
                    # 提取数据
                    df = wind_data["data"]
                    
                    # 获取技术指标（Wind API 已经计算好了）
                    indicators = wind_data.get("indicators", {})
                    
                    # 计算盈亏
                    current_price = wind_data["latest_price"]
                    position_metrics = self.portfolio_service.calculate_position_metrics(
                        position, 
                        current_price
                    )
                    
                    # 整合数据
                    holding_data = {
                        # 基本信息
                        "stock_code": position.stock_code,
                        "stock_name": wind_data["name"] or position.stock_name,
                        
                        # 持仓信息
                        "quantity": position.quantity,
                        "cost_price": float(position.cost_price),
                        
                        # 当前行情
                        "current_price": current_price,
                        "volume": wind_data["volume"],
                        "pe_ttm": wind_data["pe_ttm"],
                        "turnover": wind_data["turnover"],
                        
                        # 盈亏情况
                        "market_value": position_metrics["market_value"],
                        "cost_value": position_metrics["cost_value"],
                        "profit_loss": position_metrics["profit_loss"],
                        "profit_loss_pct": position_metrics["profit_loss_pct"],
                        
                        # 技术指标
                        "indicators": indicators,
                        
                        # 原始数据（用于进一步分析）
                        "historical_data": df.to_dict('records')  # 转为字典列表
                    }
                    
                    holdings_data.append(holding_data)
                    success_count += 1
                
                except Exception as e:
                    logger.error(f"   ✗ 处理 {position.stock_code} 失败: {e}")
                    fail_count += 1
                    continue
            
            logger.info(f"   📊 数据获取完成: 成功 {success_count}, 失败 {fail_count}")
            
            if not holdings_data:
                raise DataError(
                    message="没有成功获取任何股票数据",
                    error_code="NO_STOCK_DATA"
                )
            
            # 步骤 4: 计算组合级别指标
            progress.step("计算组合指标")
            portfolio_metrics = self.portfolio_service.calculate_portfolio_metrics(
                portfolio_id, 
                holdings_data
            )
            
            # 5. 生成报告元数据
            report_date = datetime.now().date()
            period_start = report_date - timedelta(days=7)  # 最近一周
            
            # 6. 组装完整数据
            complete_data = {
                # 报告元数据
                "report_date": report_date.strftime("%Y-%m-%d"),
                "period_start": period_start.strftime("%Y-%m-%d"),
                "period_end": report_date.strftime("%Y-%m-%d"),
                "period": f"{period_start.strftime('%Y年%m月%d日')} - {report_date.strftime('%Y年%m月%d日')}",
                "generated_at": datetime.now().isoformat(),
                
                # 组合信息
                "portfolio": {
                    "id": portfolio.id,
                    "name": portfolio.name,
                    "total_assets": portfolio_metrics["total_assets"],
                    "description": portfolio.description
                },
                
                # 组合指标
                "metrics": {
                    "total_market_value": portfolio_metrics["total_market_value"],
                    "total_cost_value": portfolio_metrics["total_cost_value"],
                    "total_profit_loss": portfolio_metrics["total_profit_loss"],
                    "total_return_pct": portfolio_metrics["total_return_pct"],
                    "position_ratio": portfolio_metrics["position_ratio"],
                    "cash": portfolio_metrics["cash"],
                    "cash_ratio": portfolio_metrics["cash_ratio"],
                    "position_count": portfolio_metrics["position_count"]
                },
                
                # KPI 指标（用于周报顶部展示）
                "kpis": {
                    "weekly_return": 0,  # TODO: 需要历史数据计算
                    "ytd_return": portfolio_metrics["total_return_pct"],  # 暂用总收益率
                    "position_ratio": portfolio_metrics["position_ratio"],
                    "action_count": 0  # TODO: 由 LLM 生成
                },
                
                # 持仓明细
                "holdings": holdings_data
            }
            
            # 完成
            summary = (
                f"持仓 {len(holdings_data)} 只, "
                f"总市值 ¥{portfolio_metrics['total_market_value']:,.2f}, "
                f"盈亏 {portfolio_metrics['total_return_pct']:+.2f}%"
            )
            progress.complete(success=True, message=summary)
            
            return complete_data
        
        except (PortfolioNotFoundError, EmptyPortfolioError, DataError) as e:
            progress.complete(success=False, message=str(e))
            raise
        except Exception as e:
            progress.complete(success=False, message=str(e))
            logger.error(f"获取周报数据失败: {e}", exc_info=True)
            raise DataError(
                message=f"获取周报数据失败: {str(e)}",
                error_code="DATA_FETCH_ERROR"
            )
    
    def close(self):
        """关闭服务"""
        try:
            self.wind_service.close()
        except Exception as e:
            logger.error(f"关闭服务失败: {e}")
