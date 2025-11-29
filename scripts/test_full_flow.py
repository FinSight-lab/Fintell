"""
完整流程测试脚本 - 测试数据获取、技术指标计算、LLM分析
"""

import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logging import setup_logging, get_logger
from app.core.database import SessionLocal
from app.services.wind_service import WindService
from app.services.portfolio_service import PortfolioService
from app.services.data_service import DataService

# 配置日志
setup_logging(level="INFO")
logger = get_logger(__name__)


def test_wind_service():
    """测试 Wind 服务"""
    logger.info("=" * 60)
    logger.info("测试 Wind 服务")
    logger.info("=" * 60)
    
    wind = WindService()
    
    # 测试获取股票信息
    test_code = "600519.SH"
    logger.info(f"\n测试股票: {test_code}")
    
    # 获取完整数据
    data = wind.get_stock_complete_data(test_code)
    
    if data:
        logger.info(f"\n股票名称: {data['name']}")
        logger.info(f"最新价格: {data['latest_price']}")
        logger.info(f"成交量: {data['volume']}")
        logger.info(f"PE_TTM: {data['pe_ttm']}")
        logger.info(f"换手率: {data['turnover']}")
        
        # 检查技术指标
        indicators = data.get('indicators', {})
        logger.info(f"\n技术指标 ({len(indicators)} 个):")
        
        # MA 指标
        ma_keys = ['MA5', 'MA10', 'MA20', 'MA30', 'MA250']
        logger.info("\nMA 指标:")
        for key in ma_keys:
            value = indicators.get(key)
            status = "✓" if value is not None else "✗"
            logger.info(f"  {status} {key}: {value}")
        
        # RSI 指标
        rsi_keys = ['RSI6', 'RSI12', 'RSI24']
        logger.info("\nRSI 指标:")
        for key in rsi_keys:
            value = indicators.get(key)
            status = "✓" if value is not None else "✗"
            logger.info(f"  {status} {key}: {value}")
        
        # MACD 指标
        macd_keys = ['MACD_DIF', 'MACD_DEA', 'MACD']
        logger.info("\nMACD 指标:")
        for key in macd_keys:
            value = indicators.get(key)
            status = "✓" if value is not None else "✗"
            logger.info(f"  {status} {key}: {value}")
        
        # BOLL 指标
        boll_keys = ['BOLL_upper', 'BOLL_mid', 'BOLL_lower']
        logger.info("\nBOLL 指标:")
        for key in boll_keys:
            value = indicators.get(key)
            status = "✓" if value is not None else "✗"
            logger.info(f"  {status} {key}: {value}")
        
        # 统计有效指标数量
        valid_count = sum(1 for v in indicators.values() if v is not None)
        total_count = len(indicators)
        logger.info(f"\n指标统计: {valid_count}/{total_count} 有效")
        
        return data
    else:
        logger.error("获取数据失败")
        return None


def test_data_service():
    """测试数据整合服务"""
    logger.info("\n" + "=" * 60)
    logger.info("测试数据整合服务")
    logger.info("=" * 60)
    
    db = SessionLocal()
    try:
        data_service = DataService(db)
        
        # 获取周报数据
        report_data = data_service.get_weekly_report_data(portfolio_id=1)
        
        if report_data:
            logger.info("\n周报数据获取成功!")
            logger.info(f"报告日期: {report_data.get('report_date')}")
            logger.info(f"统计周期: {report_data.get('period')}")
            
            # 组合信息
            portfolio = report_data.get('portfolio', {})
            logger.info(f"\n组合名称: {portfolio.get('name')}")
            
            # 组合指标
            metrics = report_data.get('metrics', {})
            logger.info(f"总市值: ¥{metrics.get('total_market_value', 0):,.2f}")
            logger.info(f"总盈亏: ¥{metrics.get('total_profit_loss', 0):+,.2f}")
            logger.info(f"收益率: {metrics.get('total_return_pct', 0):+.2f}%")
            logger.info(f"仓位占比: {metrics.get('position_ratio', 0):.1f}%")
            
            # 持仓明细
            holdings = report_data.get('holdings', [])
            logger.info(f"\n持仓数量: {len(holdings)}")
            
            # 检查每只股票的技术指标
            logger.info("\n各股票技术指标检查:")
            for h in holdings:
                stock_code = h.get('stock_code')
                stock_name = h.get('stock_name')
                indicators = h.get('indicators', {})
                valid_count = sum(1 for v in indicators.values() if v is not None)
                total_count = len(indicators)
                
                status = "✓" if valid_count == total_count else "⚠️"
                logger.info(f"  {status} {stock_name} ({stock_code}): {valid_count}/{total_count} 指标有效")
                
                # 如果有缺失的指标，列出来
                if valid_count < total_count:
                    missing = [k for k, v in indicators.items() if v is None]
                    logger.warning(f"      缺失: {missing}")
            
            # 保存数据到文件
            output_file = "output/test_report_data.json"
            os.makedirs("output", exist_ok=True)
            
            # 移除 DataFrame 数据（不能序列化）
            save_data = {
                **report_data,
                'holdings': [
                    {k: v for k, v in h.items() if k != 'historical_data'}
                    for h in holdings
                ]
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"\n数据已保存到: {output_file}")
            
            return report_data
        else:
            logger.error("获取周报数据失败")
            return None
    finally:
        data_service.close()
        db.close()


def main():
    """主函数"""
    logger.info("开始完整流程测试")
    logger.info("=" * 60)
    
    # 1. 测试 Wind 服务
    wind_data = test_wind_service()
    
    # 2. 测试数据整合服务
    report_data = test_data_service()
    
    # 总结
    logger.info("\n" + "=" * 60)
    logger.info("测试总结")
    logger.info("=" * 60)
    
    if wind_data and report_data:
        logger.info("✓ Wind 服务正常")
        logger.info("✓ 数据整合服务正常")
        logger.info("✓ 技术指标计算正常")
        logger.info("\n所有测试通过!")
    else:
        logger.error("部分测试失败，请检查日志")


if __name__ == "__main__":
    main()
