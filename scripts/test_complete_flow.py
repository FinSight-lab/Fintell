"""
完整流程测试脚本 - 测试数据获取、技术指标、LLM分析、推送
"""

import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logging import setup_logging, get_logger
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.wind_service import WindService
from app.services.data_service import DataService
from app.services.llm_service import LLMService
from app.services.template_service import TemplateService
from app.services.notification_service import NotificationService

# 配置日志
setup_logging(level="INFO")
logger = get_logger(__name__)


def test_indicators():
    """测试技术指标计算"""
    logger.info("=" * 60)
    logger.info("测试技术指标计算")
    logger.info("=" * 60)
    
    wind = WindService()
    
    # 测试一只股票
    test_code = "600519.SH"
    logger.info(f"\n测试股票: {test_code}")
    
    data = wind.get_stock_complete_data(test_code)
    
    if data:
        indicators = data.get('indicators', {})
        
        # 检查所有指标
        all_keys = ['MA5', 'MA10', 'MA20', 'MA30', 'MA250', 
                    'RSI6', 'RSI12', 'RSI24',
                    'MACD_DIF', 'MACD_DEA', 'MACD',
                    'BOLL_upper', 'BOLL_mid', 'BOLL_lower']
        
        valid_count = 0
        for key in all_keys:
            value = indicators.get(key)
            if value is not None:
                valid_count += 1
                logger.info(f"  ✓ {key}: {value:.4f}")
            else:
                logger.warning(f"  ✗ {key}: None")
        
        logger.info(f"\n指标统计: {valid_count}/{len(all_keys)} 有效")
        
        return valid_count == len(all_keys)
    else:
        logger.error("获取数据失败")
        return False


def test_data_service():
    """测试数据整合服务"""
    logger.info("\n" + "=" * 60)
    logger.info("测试数据整合服务")
    logger.info("=" * 60)
    
    db = SessionLocal()
    try:
        data_service = DataService(db)
        report_data = data_service.get_weekly_report_data(portfolio_id=1)
        
        if report_data:
            holdings = report_data.get('holdings', [])
            logger.info(f"\n持仓数量: {len(holdings)}")
            
            # 检查每只股票的技术指标
            all_valid = True
            for h in holdings:
                indicators = h.get('indicators', {})
                valid_count = sum(1 for v in indicators.values() if v is not None)
                total_count = len(indicators)
                
                if valid_count < total_count:
                    all_valid = False
                    missing = [k for k, v in indicators.items() if v is None]
                    logger.warning(f"  ⚠️ {h['stock_name']}: {valid_count}/{total_count} 有效, 缺失: {missing}")
                else:
                    logger.info(f"  ✓ {h['stock_name']}: {valid_count}/{total_count} 有效")
            
            # 保存数据
            output_file = "output/test_report_data.json"
            os.makedirs("output", exist_ok=True)
            
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
            
            data_service.close()
            return report_data, all_valid
        else:
            data_service.close()
            return None, False
    finally:
        db.close()


def test_notification():
    """测试推送服务"""
    logger.info("\n" + "=" * 60)
    logger.info("测试推送服务")
    logger.info("=" * 60)
    
    if not settings.SERVERCHAN_KEY:
        logger.warning("未配置 SERVERCHAN_KEY，跳过推送测试")
        return False
    
    notification = NotificationService(settings.SERVERCHAN_KEY)
    
    # 发送测试消息
    test_content = """
## 测试消息

这是一条来自 Smart Portfolio Manager 的测试消息。

### 测试内容
- 时间: 测试时间
- 状态: 正常

---
*此消息用于测试推送功能*
"""
    
    result = notification.send_serverchan(
        title="🧪 推送测试",
        content=test_content,
        short="测试推送功能"
    )
    
    return result


def main():
    """主函数"""
    logger.info("开始完整流程测试")
    logger.info("=" * 60)
    
    results = {}
    
    # 1. 测试技术指标
    results['indicators'] = test_indicators()
    
    # 2. 测试数据服务
    report_data, indicators_valid = test_data_service()
    results['data_service'] = report_data is not None
    results['all_indicators_valid'] = indicators_valid
    
    # 3. 测试推送（可选）
    # results['notification'] = test_notification()
    
    # 总结
    logger.info("\n" + "=" * 60)
    logger.info("测试总结")
    logger.info("=" * 60)
    
    for name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        logger.info(f"  {name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        logger.info("\n🎉 所有测试通过！")
    else:
        logger.warning("\n⚠️ 部分测试失败")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
