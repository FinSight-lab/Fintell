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


# ============================================
# 3. 替换第1节 - 核心观点（使用字符串替换）
# ============================================
print("\n开始第二阶段...")

with open('templates/weekly_report.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 直接字符串替换
old_section1 = '''                <div class="summary-card">
                    <div class="summary-card-title">Professional Summary / 专业总结</div>
                    <div class="summary-card-text">
                        当前组合呈现典型的"防御性消费配置"，但在消费复苏乏力的背景下，进攻性不足。
                        核心问题在于 <span class="highlight">茅台仓位过重</span> 及 <span class="highlight">ETF与个股重复配置</span>。
                        下周策略关键词：<span class="highlight">"去弱留强、去重叠"</span>。利用可能的超跌反弹优化仓位，保护既有利润。
                    </div>
                    <div class="summary-bullets">
                        <ul>
                            <li>本周组合小幅回撤，整体波动仍主要由贵州茅台驱动。</li>
                            <li>消费个股 + 行业 ETF 高度重叠，资金利用效率偏低。</li>
                            <li>缺乏科技成长或高股息等风格配置，对单一行业过度暴露。</li>
                        </ul>
                    </div>
                </div>'''

new_section1 = '''                <div class="summary-card">
                    <div class="summary-card-title">Professional Summary / 专业总结</div>
                    <div class="summary-card-text">
                        {{ analysis.core_viewpoint|safe }}
                    </div>
                    {% if analysis.core_highlights %}
                    <div class="summary-bullets">
                        <ul>
                            {% for highlight in analysis.core_highlights %}
                            <li>{{ highlight }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endif %}
                </div>'''

if old_section1 in content:
    content = content.replace(old_section1, new_section1)
    print("✓ 第1节核心观点已替换")
else:
    print("✗ 第1节未找到匹配，检查空白字符...")
    # 尝试查找关键词
    idx = content.find('Professional Summary')
    if idx > 0:
        print(f"  找到 Professional Summary 在位置 {idx}")
        # 打印周围内容的 repr
        snippet = content[idx-50:idx+200]
        print(f"  内容片段: {repr(snippet[:100])}")

with open('templates/weekly_report.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ 模板已保存，当前大小: {len(content)} 字符")
