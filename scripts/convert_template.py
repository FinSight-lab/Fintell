"""
将 weekly_template.html 转换为完全动态的 Jinja2 模板
"""
import re

print("开始转换模板...")

# 读取原始模板
with open('templates/weekly_template.html', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"原始模板大小: {len(content)} 字符")

# ============================================
# 1. 替换 Header 元数据
# ============================================
content = content.replace(
    '<span><strong>报告区间：</strong><span class="font-num">2025年11月24日 - 2025年11月28日</span></span>',
    '<span><strong>报告区间：</strong><span class="font-num">{{ period }}</span></span>'
)
content = content.replace(
    '<span><strong>报告日期：</strong><span class="font-num">2025年11月28日</span></span>',
    '<span><strong>报告日期：</strong><span class="font-num">{{ report_date }}</span></span>'
)
content = content.replace(
    '<span><strong>客户总资产：</strong><span class="font-num">322,157.20 元</span></span>',
    '<span><strong>客户总资产：</strong><span class="font-num">{{ "{:,.2f}".format(metrics.total_market_value + metrics.cash) }} 元</span></span>'
)
print("✓ Header 元数据已替换")

# ============================================
# 2. 替换 KPI 卡片为动态循环
# ============================================
old_kpi = '''            <!-- 顶部 KPI 仪表盘 -->
            <div class="header-kpis">
                <div class="kpi-card">
                    <div class="kpi-label">本周组合收益率</div>
                    <div class="kpi-value kpi-down font-num">-0.42%</div>
                    <div class="kpi-sub">沪深300：-0.35%</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">今年以来收益率</div>
                    <div class="kpi-value font-num">+3.80%</div>
                    <div class="kpi-sub">波动可控，略跑输大盘</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">当前整体仓位</div>
                    <div class="kpi-value font-num">87%</div>
                    <div class="kpi-sub">偏高（建议 70%–80%）</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">本周建议调仓</div>
                    <div class="kpi-value font-num">3 笔</div>
                    <div class="kpi-sub">核心：去弱留强、去重叠</div>
                </div>
            </div>'''

new_kpi = '''            <!-- 顶部 KPI 仪表盘 - 所有内容来自 LLM -->
            <div class="header-kpis">
                {% for kpi in analysis.kpis.cards %}
                <div class="kpi-card">
                    <div class="kpi-label">{{ kpi.label }}</div>
                    <div class="kpi-value {{ kpi.value_class }} font-num">{{ kpi.value }}</div>
                    <div class="kpi-sub">{{ kpi.sub }}</div>
                </div>
                {% endfor %}
            </div>'''

content = content.replace(old_kpi, new_kpi)
print("✓ KPI 卡片已替换")

# 保存中间结果
with open('templates/weekly_report.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ 模板已保存，当前大小: {len(content)} 字符")
print("第一阶段完成！")
