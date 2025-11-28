"""Step by Step Test - 分步测试每个环节"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
import json
from app.core.database import SessionLocal
from app.core.config import settings
from app.services.data_service import DataService
from app.services.llm_service import LLMService
from app.services.template_service import TemplateService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_step1_data_collection():
    """步骤1: 测试数据采集"""
    print("\n" + "=" * 80)
    print("步骤 1: 测试数据采集")
    print("=" * 80)
    
    db = SessionLocal()
    try:
        data_service = DataService(db)
        report_data = data_service.get_weekly_report_data(portfolio_id=1)
        
        if report_data:
            print("\n✓ 数据采集成功！")
            print(f"  - 持仓数量: {len(report_data.get('holdings', []))}")
            print(f"  - 总资产: ¥{report_data['metrics']['total_market_value'] + report_data['metrics']['cash']:,.2f}")
            print(f"  - 总盈亏: ¥{report_data['metrics']['total_profit_loss']:+,.2f}")
            
            # 保存数据到文件供调试
            output_file = "test_data_output.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                # 移除 historical_data 以减小文件大小
                output_data = report_data.copy()
                for holding in output_data.get('holdings', []):
                    holding.pop('historical_data', None)
                json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
            print(f"\n✓ 数据已保存到: {output_file}")
            
            data_service.close()
            return report_data
        else:
            print("\n✗ 数据采集失败")
            data_service.close()
            return None
    finally:
        db.close()


def test_step2_llm_analysis(report_data):
    """步骤2: 测试 LLM 分析"""
    print("\n" + "=" * 80)
    print("步骤 2: 测试 LLM 分析")
    print("=" * 80)
    
    if not report_data:
        print("✗ 跳过（数据采集失败）")
        return None
    
    llm_service = LLMService(
        api_url=settings.LLM_API_URL,
        api_key=settings.LLM_API_KEY,
        model=settings.LLM_MODEL
    )
    
    print(f"\nLLM 配置:")
    print(f"  - API URL: {settings.LLM_API_URL}")
    print(f"  - Model: {settings.LLM_MODEL}")
    print(f"\n正在调用 LLM...")
    
    analysis = llm_service.generate_weekly_analysis(report_data)
    
    if analysis:
        print("\n✓ LLM 分析成功！")
        print(f"  - 核心观点: {analysis.get('core_viewpoint', '')[:100]}...")
        print(f"  - 个股分析数: {len(analysis.get('stock_analysis', []))}")
        print(f"  - 操作建议数: {len(analysis.get('action_plan', []))}")
        
        # 保存分析结果
        output_file = "test_llm_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 分析结果已保存到: {output_file}")
        
        return analysis
    else:
        print("\n✗ LLM 分析失败")
        return None


def test_step3_template_render(report_data, analysis):
    """步骤3: 测试模板渲染"""
    print("\n" + "=" * 80)
    print("步骤 3: 测试模板渲染")
    print("=" * 80)
    
    if not report_data or not analysis:
        print("✗ 跳过（前置步骤失败）")
        return None
    
    template_service = TemplateService()
    
    complete_data = {
        **report_data,
        'analysis': analysis
    }
    
    print("\n正在渲染 HTML...")
    html = template_service.render_weekly_report(complete_data)
    
    if html:
        print(f"\n✓ HTML 渲染成功！")
        print(f"  - HTML 长度: {len(html)} 字符")
        
        # 保存 HTML
        output_file = "test_weekly_report.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\n✓ HTML 已保存到: {output_file}")
        print(f"  可以在浏览器中打开查看")
        
        return html
    else:
        print("\n✗ HTML 渲染失败")
        return None


def main():
    print("\n" + "=" * 80)
    print("周报生成流程 - 分步测试")
    print("=" * 80)
    
    # 步骤 1: 数据采集
    report_data = test_step1_data_collection()
    
    # 步骤 2: LLM 分析
    analysis = test_step2_llm_analysis(report_data)
    
    # 步骤 3: 模板渲染
    html = test_step3_template_render(report_data, analysis)
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"步骤 1 - 数据采集: {'✓ 成功' if report_data else '✗ 失败'}")
    print(f"步骤 2 - LLM 分析: {'✓ 成功' if analysis else '✗ 失败'}")
    print(f"步骤 3 - 模板渲染: {'✓ 成功' if html else '✗ 失败'}")
    print("=" * 80)
    
    if report_data and analysis and html:
        print("\n🎉 所有步骤测试通过！")
    else:
        print("\n⚠️  部分步骤失败，请检查日志")


if __name__ == "__main__":
    main()
