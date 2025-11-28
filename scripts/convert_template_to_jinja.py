"""
将静态 HTML 模板转换为 Jinja2 动态模板
"""

import re

# 读取原始模板
with open('templates/weekly_template.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 替换报告元数据
content = re.sub(
    r'<span><strong>报告区间：</strong><span class="font-num">.*?</span></span>',
    '<span><strong>报告区间：</strong><span class="font-num">{{ period }}</span></span>',
    content
)

content = re.sub(
    r'<span><strong>报告日期：</strong><span class="font-num">.*?</span></span>',
    '<span><strong>报告日期：</strong><span class="font-num">{{ report_date }}</span></span>',
    content
)

content = re.sub(
    r'<span><strong>客户总资产：</strong><span class="font-num">.*?</span></span>',
    '<span><strong>客户总资产：</strong><span class="font-num">{{ "{:,.2f}".format(metrics.total_market_value + metrics.cash) }} 元</span></span>',
    content
)

# 2. 替换 KPI 卡片
kpi_pattern = r'<div class="header-kpis">.*?</div>\s*</div>\s*</div>\s*</div>'
kpi_replacement = '''<div class="header-kpis">
                <div class="kpi-card">
                    <div class="kpi-label">本周组合收益率</div>
                    <div class="kpi-value {% if analysis.kpis.weekly_return >= 0 %}kpi-up{% else %}kpi-down{% endif %} font-num">{{ "%+.2f"|format(analysis.kpis.weekly_return) }}%</div>
                    <div class="kpi-sub">沪深300：{{ "%+.2f"|format(analysis.kpis.get('benchmark_return', 0)) }}%</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">今年以来收益率</div>
                    <div class="kpi-value font-num">{{ "%+.2f"|format(analysis.kpis.ytd_return) }}%</div>
                    <div class="kpi-sub">{{ analysis.kpis.get('ytd_comment', '波动可控') }}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">当前整体仓位</div>
                    <div class="kpi-value font-num">{{ "%.0f"|format(analysis.kpis.position_ratio) }}%</div>
                    <div class="kpi-sub">{{ analysis.kpis.get('position_comment', '偏高') }}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">本周建议调仓</div>
                    <div class="kpi-value font-num">{{ analysis.kpis.action_count }} 笔</div>
                    <div class="kpi-sub">{{ analysis.kpis.get('action_summary', '核心：去弱留强') }}</div>
                </div>
            </div>
        </div>'''

content = re.sub(kpi_pattern, kpi_replacement, content, flags=re.DOTALL)

print("✓ 模板转换完成")
print(f"输出长度: {len(content)} 字符")

# 保存转换后的模板
with open('templates/weekly_report_dynamic.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ 已保存到: templates/weekly_report_dynamic.html")
