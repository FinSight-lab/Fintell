"""
测试新的 Jinja2 模板和 JSON 正则提取功能
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import json
import logging
from app.services.template_service import TemplateService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_template_rendering():
    """测试模板渲染"""
    logger.info("=" * 60)
    logger.info("测试 1: 模板渲染")
    logger.info("=" * 60)
    
    # 加载测试数据
    with open('test_data_output.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # 创建模拟的 LLM 分析结果
    mock_analysis = {
        "core_viewpoint": "当前组合呈现典型的<span class='highlight'>防御性消费配置</span>，但在消费复苏乏力的背景下，进攻性不足。",
        "kpis": {
            "weekly_return": -0.42,
            "ytd_return": test_data['metrics']['total_return_pct'],
            "position_ratio": test_data['metrics']['position_ratio'],
            "action_count": 3,
            "benchmark_return": -0.35,
            "ytd_comment": "波动可控",
            "position_comment": "偏高（建议 70%–80%）",
            "action_summary": "核心：去弱留强、去重叠"
        },
        "holdings_analysis": {
            "summary": "本周组合小幅回撤，整体波动仍主要由贵州茅台驱动。",
            "highlights": [
                "本周组合小幅回撤，整体波动仍主要由贵州茅台驱动。",
                "消费个股 + 行业 ETF 高度重叠，资金利用效率偏低。",
                "缺乏科技成长或高股息等风格配置，对单一行业过度暴露。"
            ]
        },
        "stock_analysis": [
            {
                "stock_code": "600519.SH",
                "stock_name": "贵州茅台",
                "status": "超卖反弹",
                "status_class": "warning",
                "technical": "均线空头排列，但 RSI(6) 跌至 43.6，短期存在技术反弹需求。",
                "fundamental": "现金流稳健、品牌力极强，长期逻辑未改变。",
                "theme": "属于白酒板块核心资产，当前不在 A 股主线中。",
                "risk": "估值仍处高位，一旦消费恢复不及预期，可能面临估值中枢下移风险。",
                "suggestion": "<strong>持有为主，逢高减仓</strong>。反弹至 1460–1480 区间可考虑减仓 5% 左右。"
            }
        ],
        "action_plan": [
            {
                "stock_code": "600519.SH",
                "stock_name": "贵州茅台",
                "action": "逢高减仓",
                "action_class": "reduce",
                "price_range": "1460-1480元",
                "current_position": "34.4%",
                "target_position": "30%",
                "plan": "触及区间上沿分两次各减2.5%",
                "reason": "单票仓位过重，利用超跌反弹优化集中度"
            }
        ],
        "risk_assessment": {
            "level": "中等偏高",
            "level_score": 65,
            "current_risks": [
                "<strong>行业集中度：</strong><span class='text-down'>近 100% 集中在泛消费领域</span>",
                "<strong>个股集中度：</strong>贵州茅台单只仓位约 <span class='text-down'>34%</span>"
            ],
            "optimization_suggestions": [
                "<strong>去重叠：</strong>建议逐步减仓食品ETF和消费LOF",
                "<strong>止损弱势：</strong>对珀莱雅等趋势破位标的减仓"
            ]
        },
        "sector_view": {
            "summary": "从当前市场结构看，消费并非绝对主线，更偏向于"防御+修复"方向。",
            "main_theme": "科技成长（如半导体、算力）、高股息红利",
            "consumer_position": "消费处于深跌后震荡修复阶段",
            "portfolio_position": "当前组合更接近'进可攻能力有限、退可守尚可'的状态",
            "adjustment_direction": "释放部分消费仓位，引入科技成长 & 高股息"
        },
        "target_allocation": {
            "consumer": 55,
            "tech_growth": 20,
            "dividend": 15,
            "cash": 10
        }
    }
    
    # 准备模板数据
    template_data = {
        "period": test_data['period'],
        "report_date": test_data['report_date'],
        "portfolio": test_data['portfolio'],
        "metrics": test_data['metrics'],
        "holdings": test_data['holdings'],
        "analysis": mock_analysis
    }
    
    # 渲染模板
    template_service = TemplateService()
    html = template_service.render_weekly_report(template_data)
    
    if html:
        # 保存 HTML
        output_path = "output/test_weekly_report.html"
        if template_service.save_html(html, output_path):
            logger.info(f"✓ 测试成功！HTML 已保存到: {output_path}")
            logger.info(f"  HTML 长度: {len(html)} 字符")
            return True
        else:
            logger.error("✗ 保存 HTML 失败")
            return False
    else:
        logger.error("✗ 模板渲染失败")
        return False


def test_json_extraction():
    """测试 JSON 正则提取"""
    logger.info("\n" + "=" * 60)
    logger.info("测试 2: JSON 正则提取")
    logger.info("=" * 60)
    
    import re
    
    # 模拟各种 LLM 输出格式
    test_cases = [
        {
            "name": "标准 JSON",
            "content": '{"core_viewpoint": "测试内容", "kpis": {"weekly_return": 1.5}}'
        },
        {
            "name": "带 markdown 代码块",
            "content": '```json\n{"core_viewpoint": "测试内容", "kpis": {"weekly_return": 1.5}}\n```'
        },
        {
            "name": "带前缀文本",
            "content": '这是分析结果：\n{"core_viewpoint": "测试内容", "kpis": {"weekly_return": 1.5}}'
        },
        {
            "name": "带 <think> 标签",
            "content": '<think>思考过程...</think>\n{"core_viewpoint": "测试内容", "kpis": {"weekly_return": 1.5}}'
        },
        {
            "name": "嵌套 JSON",
            "content": '外层文本 {"core_viewpoint": "测试", "nested": {"data": {"value": 123}}} 后续文本'
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n测试用例 {i}: {test_case['name']}")
        logger.info(f"原始内容: {test_case['content'][:100]}...")
        
        content = test_case['content']
        
        # 1. 过滤 <think> 标签
        if '<think>' in content:
            think_end = content.find('</think>')
            if think_end != -1:
                content = content[think_end + 8:].strip()
                logger.info("  ✓ 已过滤 <think> 标签")
        
        # 2. 提取 markdown 代码块
        if '```json' in content:
            start = content.find('```json') + 7
            end = content.find('```', start)
            if end != -1:
                content = content[start:end].strip()
                logger.info("  ✓ 从 markdown 代码块中提取")
        elif '```' in content:
            start = content.find('```') + 3
            end = content.find('```', start)
            if end != -1:
                content = content[start:end].strip()
                logger.info("  ✓ 从代码块中提取")
        
        # 3. 查找 JSON 对象
        if not content.strip().startswith('{'):
            json_start = content.find('{')
            if json_start != -1:
                content = content[json_start:]
                logger.info("  ✓ 找到 JSON 起始位置")
        
        # 4. 尝试解析
        try:
            parsed = json.loads(content)
            logger.info(f"  ✓ JSON 解析成功: {list(parsed.keys())}")
            success_count += 1
        except json.JSONDecodeError as e:
            logger.warning(f"  ✗ 直接解析失败: {e}")
            
            # 5. 使用正则表达式提取
            json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'
            matches = re.findall(json_pattern, content, re.DOTALL)
            
            if matches:
                logger.info(f"  找到 {len(matches)} 个 JSON 对象")
                for j, match in enumerate(matches):
                    try:
                        parsed = json.loads(match)
                        if 'core_viewpoint' in parsed or 'kpis' in parsed:
                            logger.info(f"  ✓ 正则提取成功 (匹配 {j+1}): {list(parsed.keys())}")
                            success_count += 1
                            break
                    except json.JSONDecodeError:
                        continue
            else:
                logger.error("  ✗ 正则提取也失败")
    
    logger.info(f"\n总结: {success_count}/{len(test_cases)} 个测试用例成功")
    return success_count == len(test_cases)


if __name__ == "__main__":
    logger.info("开始测试新模板和 JSON 提取功能\n")
    
    # 测试 1: 模板渲染
    test1_passed = test_template_rendering()
    
    # 测试 2: JSON 提取
    test2_passed = test_json_extraction()
    
    # 总结
    logger.info("\n" + "=" * 60)
    logger.info("测试总结")
    logger.info("=" * 60)
    logger.info(f"模板渲染: {'✓ 通过' if test1_passed else '✗ 失败'}")
    logger.info(f"JSON 提取: {'✓ 通过' if test2_passed else '✗ 失败'}")
    
    if test1_passed and test2_passed:
        logger.info("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        logger.error("\n❌ 部分测试失败")
        sys.exit(1)
