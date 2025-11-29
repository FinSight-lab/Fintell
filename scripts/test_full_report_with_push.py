"""
完整周报生成和推送测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['NO_PROXY'] = '*'

import json
from datetime import datetime

# 导入服务
from app.core.database import SessionLocal
from app.core.config import settings
from app.services.data_service import DataService
from app.services.llm_service import LLMService
from app.services.template_service import TemplateService
from app.services.notification_service import NotificationService

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始完整周报生成和推送测试")
    logger.info("=" * 60)
    
    db = SessionLocal()
    data_service = None
    
    try:
        # 步骤 1: 获取数据
        logger.info("\n📊 步骤 1/4: 获取数据...")
        data_service = DataService(db)
        report_data = data_service.get_weekly_report_data(portfolio_id=1)
        
        if not report_data:
            logger.error("获取数据失败")
            return False
        
        holdings = report_data.get('holdings', [])
        logger.info(f"✓ 数据获取完成，持仓数量: {len(holdings)}")
        
        # 检查技术指标
        logger.info("\n检查技术指标:")
        for h in holdings:
            indicators = h.get('indicators', {})
            valid_count = sum(1 for v in indicators.values() if v is not None)
            total_count = len(indicators)
            logger.info(f"  {h['stock_name']}: {valid_count}/{total_count} 有效")
        
        # 保存数据
        output_data = {
            **report_data,
            'holdings': [
                {k: v for k, v in h.items() if k != 'historical_data'}
                for h in holdings
            ]
        }
        with open('output/report_data_new.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
        logger.info("✓ 数据已保存到 output/report_data_new.json")
        
        # 步骤 2: LLM 分析
        logger.info("\n🤖 步骤 2/4: LLM 分析...")
        llm_service = LLMService(
            api_url=settings.LLM_API_URL,
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL
        )
        
        analysis = llm_service.generate_weekly_analysis(report_data)
        
        if not analysis:
            logger.error("LLM 分析失败")
            return False
        
        logger.info(f"✓ LLM 分析完成")
        logger.info(f"  - 核心观点: {analysis.get('core_viewpoint', '')[:50]}...")
        logger.info(f"  - 个股分析: {len(analysis.get('stock_analysis', []))} 只")
        logger.info(f"  - 操作建议: {len(analysis.get('action_plan', []))} 条")
        
        # 保存分析结果
        with open('output/llm_analysis_new.json', 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        logger.info("✓ 分析结果已保存到 output/llm_analysis_new.json")
        
        # 步骤 3: 渲染 HTML
        logger.info("\n🎨 步骤 3/4: 渲染 HTML...")
        template_service = TemplateService()
        
        complete_data = {
            **report_data,
            'analysis': analysis
        }
        
        html = template_service.render_weekly_report(complete_data)
        
        if not html:
            logger.error("HTML 渲染失败")
            return False
        
        logger.info(f"✓ HTML 渲染完成，长度: {len(html)} 字符")
        
        # 保存 HTML
        with open('output/weekly_report_new.html', 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info("✓ HTML 已保存到 output/weekly_report_new.html")
        
        # 步骤 4: 推送到微信
        logger.info("\n📱 步骤 4/4: 推送到微信...")
        
        if settings.SERVERCHAN_KEY:
            notification_service = NotificationService(settings.SERVERCHAN_KEY)
            pushed = notification_service.send_weekly_report(
                html_content=html,
                report_date=datetime.now()
            )
            
            if pushed:
                logger.info("✓ 微信推送成功！")
            else:
                logger.warning("⚠️ 微信推送失败")
        else:
            logger.warning("⚠️ 未配置 SERVERCHAN_KEY，跳过推送")
            pushed = False
        
        # 完成
        logger.info("\n" + "=" * 60)
        logger.info("✓ 完整流程测试完成！")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return False
    finally:
        if data_service:
            data_service.close()
        db.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
