"""
完整测试：LLM 服务 + 模板渲染
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import json
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_full_report():
    """测试完整的周报生成流程"""
    
    # 1. 加载测试数据
    logger.info("=" * 60)
    logger.info("步骤 1: 加载测试数据")
    logger.info("=" * 60)
    
    with open('test_data_output.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    logger.info(f"✓ 加载了 {len(test_data['holdings'])} 只持仓数据")
    
    # 2. 调用 LLM 服务
    logger.info("\n" + "=" * 60)
    logger.info("步骤 2: 调用 LLM 生成分析")
    logger.info("=" * 60)
    
    from app.services.llm_service import LLMService
    
    api_url = os.getenv('GEMINI_API_URL', 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions')
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        logger.error("✗ 未设置 GEMINI_API_KEY 环境变量")
        return False
    
    llm_service = LLMService(api_url=api_url, api_key=api_key)
    
    # 添加基准数据
    test_data['benchmark_name'] = '沪深300'
    test_data['benchmark_return'] = -0.35
    
    analysis = llm_service.generate_weekly_analysis(test_data)
    
    if not analysis:
        logger.error("✗ LLM 分析生成失败")
        return False
    
    logger.info("✓ LLM 分析生成成功")
    logger.info(f"  - 核心观点: {analysis.get('core_viewpoint', '')[:50]}...")
    logger.info(f"  - 个股分析数量: {len(analysis.get('stock_analysis', []))}")
    logger.info(f"  - 操作建议数量: {len(analysis.get('action_plan', []))}")
    
    # 保存 LLM 输出用于调试
    with open('output/llm_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    logger.info("✓ LLM 分析结果已保存到 output/llm_analysis.json")
    
    # 3. 渲染模板
    logger.info("\n" + "=" * 60)
    logger.info("步骤 3: 渲染 HTML 模板")
    logger.info("=" * 60)
    
    from app.services.template_service import TemplateService
    
    template_service = TemplateService()
    
    # 准备模板数据
    template_data = {
        'period': test_data['period'],
        'report_date': test_data['report_date'],
        'portfolio': test_data['portfolio'],
        'metrics': test_data['metrics'],
        'holdings': test_data['holdings'],
        'analysis': analysis
    }
    
    html = template_service.render_weekly_report(template_data)
    
    if not html:
        logger.error("✗ 模板渲染失败")
        return False
    
    logger.info(f"✓ 模板渲染成功，HTML 长度: {len(html)} 字符")
    
    # 4. 保存 HTML
    output_path = 'output/weekly_report.html'
    if template_service.save_html(html, output_path):
        logger.info(f"✓ HTML 已保存到: {output_path}")
    else:
        logger.error("✗ 保存 HTML 失败")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("🎉 完整测试通过！")
    logger.info("=" * 60)
    logger.info(f"请在浏览器中打开 {output_path} 查看报告")
    
    return True


if __name__ == "__main__":
    # 确保输出目录存在
    os.makedirs('output', exist_ok=True)
    
    success = test_full_report()
    sys.exit(0 if success else 1)
