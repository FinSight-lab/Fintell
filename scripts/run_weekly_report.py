#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
第一里程碑完整测试脚本 - 周报生成和推送

功能：
1. 从数据库获取持仓数据
2. 调用 Wind API 获取行情和技术指标
3. 调用 LLM 生成分析报告
4. 渲染 HTML 模板
5. 推送到微信

使用方法：
    python scripts/run_weekly_report.py [--skip-push] [--portfolio-id 1]

输出文件：
    output/report_data.json     - 原始数据
    output/llm_analysis.json    - LLM 分析结果
    output/weekly_report.html   - 渲染后的 HTML 报告
"""

import sys
import os
import json
import argparse
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置代理
os.environ['NO_PROXY'] = '*'

# 导入服务
from app.core.database import SessionLocal
from app.core.config import settings
from app.services.data_service import DataService
from app.services.llm_service import LLMService
from app.services.template_service import TemplateService
from app.services.notification_service import NotificationService

import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def ensure_output_dir():
    """确保输出目录存在"""
    os.makedirs('output', exist_ok=True)


def save_json(data, filename):
    """保存 JSON 数据"""
    filepath = f'output/{filename}'
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"   ✓ 已保存: {filepath}")
    return filepath


def save_html(html, filename):
    """保存 HTML 文件"""
    filepath = f'output/{filename}'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    logger.info(f"   ✓ 已保存: {filepath}")
    return filepath


def step1_get_data(db, portfolio_id):
    """步骤 1: 获取数据"""
    logger.info("=" * 60)
    logger.info("📊 步骤 1/5: 获取持仓和行情数据")
    logger.info("=" * 60)
    
    data_service = DataService(db)
    report_data = data_service.get_weekly_report_data(portfolio_id=portfolio_id)
    
    if not report_data:
        logger.error("✗ 获取数据失败")
        data_service.close()
        return None, None
    
    holdings = report_data.get('holdings', [])
    metrics = report_data.get('metrics', {})
    
    logger.info(f"\n   组合信息:")
    logger.info(f"   - 持仓数量: {len(holdings)} 只")
    logger.info(f"   - 总市值: ¥{metrics.get('total_market_value', 0):,.2f}")
    logger.info(f"   - 总盈亏: ¥{metrics.get('total_profit_loss', 0):+,.2f}")
    logger.info(f"   - 收益率: {metrics.get('total_return_pct', 0):+.2f}%")
    logger.info(f"   - 仓位: {metrics.get('position_ratio', 0):.1f}%")
    
    # 检查技术指标
    logger.info(f"\n   技术指标检查:")
    for h in holdings:
        indicators = h.get('indicators', {})
        valid_count = sum(1 for v in indicators.values() if v is not None)
        total_count = len(indicators)
        status = "✓" if valid_count == total_count else "⚠️"
        logger.info(f"   {status} {h['stock_name']}: {valid_count}/{total_count} 有效")
    
    # 保存数据（移除 historical_data）
    save_data = {
        **report_data,
        'holdings': [
            {k: v for k, v in h.items() if k != 'historical_data'}
            for h in holdings
        ]
    }
    save_json(save_data, 'report_data.json')
    
    return report_data, data_service


def step2_llm_analysis(report_data):
    """步骤 2: LLM 分析"""
    logger.info("\n" + "=" * 60)
    logger.info("🤖 步骤 2/5: LLM 智能分析")
    logger.info("=" * 60)
    
    logger.info(f"\n   LLM 配置:")
    logger.info(f"   - API: {settings.LLM_API_URL}")
    logger.info(f"   - 模型: {settings.LLM_MODEL}")
    
    llm_service = LLMService(
        api_url=settings.LLM_API_URL,
        api_key=settings.LLM_API_KEY,
        model=settings.LLM_MODEL
    )
    
    logger.info(f"\n   正在调用 LLM...")
    analysis = llm_service.generate_weekly_analysis(report_data)
    
    if not analysis:
        logger.error("✗ LLM 分析失败")
        return None
    
    logger.info(f"\n   分析结果:")
    logger.info(f"   - 核心观点: {analysis.get('core_viewpoint', '')[:60]}...")
    logger.info(f"   - 个股分析: {len(analysis.get('stock_analysis', []))} 只")
    logger.info(f"   - 操作建议: {len(analysis.get('action_plan', []))} 条")
    
    save_json(analysis, 'llm_analysis.json')
    
    return analysis


def step3_merge_data(report_data, analysis):
    """步骤 3: 合并数据"""
    logger.info("\n" + "=" * 60)
    logger.info("📦 步骤 3/5: 合并数据")
    logger.info("=" * 60)
    
    complete_data = {
        **report_data,
        'analysis': analysis
    }
    
    logger.info("   ✓ 数据合并完成")
    
    return complete_data


def step4_render_html(complete_data):
    """步骤 4: 渲染 HTML"""
    logger.info("\n" + "=" * 60)
    logger.info("🎨 步骤 4/5: 渲染 HTML 模板")
    logger.info("=" * 60)
    
    template_service = TemplateService()
    html = template_service.render_weekly_report(complete_data)
    
    if not html:
        logger.error("✗ HTML 渲染失败")
        return None
    
    logger.info(f"   ✓ HTML 渲染完成，长度: {len(html):,} 字符")
    
    save_html(html, 'weekly_report.html')
    
    return html


def step5_push_wechat(html, skip_push=False):
    """步骤 5: 推送到微信"""
    logger.info("\n" + "=" * 60)
    logger.info("📱 步骤 5/5: 推送到微信")
    logger.info("=" * 60)
    
    if skip_push:
        logger.info("   ⏭️ 跳过推送（--skip-push）")
        return False
    
    if not settings.SERVERCHAN_KEY:
        logger.warning("   ⚠️ 未配置 SERVERCHAN_KEY，跳过推送")
        return False
    
    notification_service = NotificationService(settings.SERVERCHAN_KEY)
    pushed = notification_service.send_weekly_report(
        html_content=html,
        report_date=datetime.now()
    )
    
    if pushed:
        logger.info("   ✓ 微信推送成功！")
    else:
        logger.warning("   ⚠️ 微信推送失败")
    
    return pushed


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='生成并推送周报')
    parser.add_argument('--skip-push', action='store_true', help='跳过微信推送')
    parser.add_argument('--portfolio-id', type=int, default=1, help='持仓组合ID')
    args = parser.parse_args()
    
    logger.info("\n" + "=" * 60)
    logger.info("🚀 第一里程碑完整测试 - 周报生成和推送")
    logger.info("=" * 60)
    logger.info(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"   组合ID: {args.portfolio_id}")
    logger.info(f"   推送: {'跳过' if args.skip_push else '启用'}")
    
    ensure_output_dir()
    
    db = SessionLocal()
    data_service = None
    
    try:
        start_time = datetime.now()
        
        # 步骤 1: 获取数据
        report_data, data_service = step1_get_data(db, args.portfolio_id)
        if not report_data:
            return False
        
        # 步骤 2: LLM 分析
        analysis = step2_llm_analysis(report_data)
        if not analysis:
            return False
        
        # 步骤 3: 合并数据
        complete_data = step3_merge_data(report_data, analysis)
        
        # 步骤 4: 渲染 HTML
        html = step4_render_html(complete_data)
        if not html:
            return False
        
        # 步骤 5: 推送到微信
        pushed = step5_push_wechat(html, args.skip_push)
        
        # 完成
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 周报生成完成！")
        logger.info("=" * 60)
        logger.info(f"   耗时: {elapsed:.1f} 秒")
        logger.info(f"   推送: {'成功' if pushed else '未推送'}")
        logger.info(f"\n   输出文件:")
        logger.info(f"   - output/report_data.json")
        logger.info(f"   - output/llm_analysis.json")
        logger.info(f"   - output/weekly_report.html")
        logger.info("=" * 60 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"\n✗ 执行失败: {e}", exc_info=True)
        return False
    finally:
        if data_service:
            data_service.close()
        db.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
