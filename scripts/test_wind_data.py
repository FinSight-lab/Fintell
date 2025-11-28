"""Test Wind API and Data Integration"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from app.core.database import SessionLocal
from app.services.data_service import DataService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_wind_connection():
    """测试 Wind API 连接"""
    logger.info("\n" + "=" * 80)
    logger.info("测试 1: Wind API 连接")
    logger.info("=" * 80)
    
    try:
        from wind_linker import w
        # wind-linker 不需要显式 start
        logger.info("✓ Wind API 连接成功")
        return True
    except Exception as e:
        logger.error(f"✗ Wind API 连接失败: {e}")
        return False


def test_single_stock():
    """测试获取单只股票数据"""
    logger.info("\n" + "=" * 80)
    logger.info("测试 2: 获取单只股票数据")
    logger.info("=" * 80)
    
    try:
        from app.services.wind_service import WindService
        
        wind_service = WindService()
        
        # 测试股票：贵州茅台
        test_stock = "600519.SH"
        logger.info(f"\n测试股票: {test_stock}")
        
        # 获取完整数据
        data = wind_service.get_stock_complete_data(test_stock)
        
        if data and data.get("data") is not None:
            logger.info(f"\n✓ 数据获取成功:")
            logger.info(f"  - 股票名称: {data['name']}")
            logger.info(f"  - 最新价格: ¥{data['latest_price']:.2f}")
            logger.info(f"  - 成交量: {data['volume']:,.0f}")
            logger.info(f"  - PE(TTM): {data['pe_ttm']:.2f}" if data['pe_ttm'] else "  - PE(TTM): N/A")
            logger.info(f"  - 换手率: {data['turnover']:.2f}%" if data['turnover'] else "  - 换手率: N/A")
            logger.info(f"  - 数据条数: {len(data['data'])}")
            
            # 技术指标（Wind API 已计算）
            indicators = data.get("indicators", {})
            
            logger.info(f"\n✓ 技术指标获取成功:")
            logger.info(f"  - MA5: ¥{indicators.get('MA5'):.2f}" if indicators.get('MA5') else "  - MA5: N/A")
            logger.info(f"  - MA10: ¥{indicators.get('MA10'):.2f}" if indicators.get('MA10') else "  - MA10: N/A")
            logger.info(f"  - MA20: ¥{indicators.get('MA20'):.2f}" if indicators.get('MA20') else "  - MA20: N/A")
            logger.info(f"  - RSI6: {indicators.get('RSI6'):.2f}" if indicators.get('RSI6') else "  - RSI6: N/A")
            logger.info(f"  - RSI12: {indicators.get('RSI12'):.2f}" if indicators.get('RSI12') else "  - RSI12: N/A")
            logger.info(f"  - MACD_DIF: {indicators.get('MACD_DIF'):.4f}" if indicators.get('MACD_DIF') else "  - MACD_DIF: N/A")
            logger.info(f"  - BOLL_mid: ¥{indicators.get('BOLL_mid'):.2f}" if indicators.get('BOLL_mid') else "  - BOLL_mid: N/A")
            
            wind_service.close()
            return True
        else:
            logger.error("✗ 数据获取失败")
            wind_service.close()
            return False
    
    except Exception as e:
        logger.error(f"✗ 测试失败: {e}", exc_info=True)
        return False


def test_portfolio_data():
    """测试获取组合完整数据"""
    logger.info("\n" + "=" * 80)
    logger.info("测试 3: 获取组合完整数据")
    logger.info("=" * 80)
    
    db = SessionLocal()
    
    try:
        data_service = DataService(db)
        
        # 获取组合 ID=1 的数据
        portfolio_id = 1
        logger.info(f"\n获取组合数据: Portfolio ID={portfolio_id}")
        
        complete_data = data_service.get_weekly_report_data(portfolio_id)
        
        if complete_data:
            logger.info("\n" + "=" * 80)
            logger.info("✓ 组合数据获取成功")
            logger.info("=" * 80)
            
            # 显示汇总信息
            logger.info(f"\n📊 组合信息:")
            logger.info(f"  - 组合名称: {complete_data['portfolio']['name']}")
            logger.info(f"  - 报告日期: {complete_data['report_date']}")
            logger.info(f"  - 统计周期: {complete_data['period']}")
            
            logger.info(f"\n💰 资产情况:")
            metrics = complete_data['metrics']
            logger.info(f"  - 总资产: ¥{metrics['total_market_value'] + metrics['cash']:,.2f}")
            logger.info(f"  - 持仓市值: ¥{metrics['total_market_value']:,.2f}")
            logger.info(f"  - 现金: ¥{metrics['cash']:,.2f}")
            logger.info(f"  - 仓位占比: {metrics['position_ratio']:.1f}%")
            
            logger.info(f"\n📈 盈亏情况:")
            logger.info(f"  - 总盈亏: ¥{metrics['total_profit_loss']:+,.2f}")
            logger.info(f"  - 收益率: {metrics['total_return_pct']:+.2f}%")
            
            logger.info(f"\n📋 持仓明细: ({len(complete_data['holdings'])} 只股票)")
            for i, holding in enumerate(complete_data['holdings'], 1):
                logger.info(f"  {i}. {holding['stock_code']} {holding['stock_name']}")
                logger.info(f"     价格: ¥{holding['current_price']:.2f}, "
                          f"盈亏: ¥{holding['profit_loss']:+,.2f} "
                          f"({holding['profit_loss_pct']:+.2f}%)")
            
            # 保存到文件（用于调试）
            output_file = Path(__file__).parent.parent / "test_output_data.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                # 移除 historical_data 以减小文件大小
                output_data = complete_data.copy()
                for holding in output_data['holdings']:
                    holding.pop('historical_data', None)
                json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"\n✓ 数据已保存到: {output_file}")
            
            data_service.close()
            return True
        else:
            logger.error("✗ 组合数据获取失败")
            data_service.close()
            return False
    
    except Exception as e:
        logger.error(f"✗ 测试失败: {e}", exc_info=True)
        return False
    finally:
        db.close()


def main():
    """运行所有测试"""
    logger.info("\n" + "=" * 80)
    logger.info("Wind 接口和数据整合测试")
    logger.info("=" * 80)
    
    results = []
    
    # 测试 1: Wind 连接
    results.append(("Wind API 连接", test_wind_connection()))
    
    # 测试 2: 单只股票
    results.append(("单只股票数据", test_single_stock()))
    
    # 测试 3: 组合数据
    results.append(("组合完整数据", test_portfolio_data()))
    
    # 显示测试结果
    logger.info("\n" + "=" * 80)
    logger.info("测试结果汇总")
    logger.info("=" * 80)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        logger.info("\n🎉 所有测试通过！")
    else:
        logger.info("\n⚠️  部分测试失败，请检查日志")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
