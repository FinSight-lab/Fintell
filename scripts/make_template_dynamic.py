"""
将 weekly_template.html 转换为完全动态的 Jinja2 模板
只保留样式和结构，所有内容都来自 LLM
"""

import re

# 读取原始模板
with open('templates/weekly_template.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("开始转换模板...")

# 1. 替换核心观点部分（第1节）
content = re.sub(
    r'<div class="summary-card-text">\s*当前组合.*?</div>\s*<div class="summary-bullets">\s*<ul>.*?</ul>\s*</div>',
    '''<div class="summary-card-text">
                        {{ analysis.core_viewpoint|safe }}
                    </div>
                    {% if analysis.holdings_analysis and analysis.holdings_analysis.highlights %}
                    <div class="summary-bullets">
                        <ul>
                            {% for highlight in analysis.holdings_analysis.highlights %}
                            <li>{{ highlight }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endif %}''',
    content,
    flags=re.DOTALL
)
print("✓ 已替换第1节：核心观点")

# 2. 替换持仓表格（第2节）- 将所有静态行替换为循环
# 查找表格 tbody 部分
tbody_pattern = r'(<table class="holdings-table align-center">.*?<tbody>)(.*?)(</tbody>)'
def replace_holdings_table(match):
    before = match.group(1)
    after = match.group(3)
    
    new_tbody = '''
                            {% for holding in holdings %}
                            <tr>
                                <td class="col-text-left">
                                    <div class="stock-name">{{ holding.stock_name }}</div>
                                    <div class="stock-code font-num">{{ holding.stock_code }}</div>
                                </td>
                                <td class="font-num">{{ "%.2f"|format(holding.current_price) }}</td>
                                <td class="font-num">{{ "%.2f"|format(holding.cost_price) }}</td>
                                <td class="font-num">{{ "{:,.2f}".format(holding.market_value) }}</td>
                                <td class="font-num">{{ "%.1f"|format(holding.position_ratio) }}%</td>
                                <td class="font-num {% if holding.profit_loss >= 0 %}text-up{% else %}text-down{% endif %}">{{ "%+,.2f"|format(holding.profit_loss) }}</td>
                                <td>
                                    <span class="status-capsule {% if holding.profit_loss_pct >= 0 %}capsule-positive{% else %}capsule-negative{% endif %} font-num">{% if holding.profit_loss_pct >= 0 %}▲{% else %}▼{% endif %} {{ "%+.2f"|format(holding.profit_loss_pct) }}%</span>
                                </td>
                                <td><span class="position-role {{ holding.get('role_class', 'role-core') }}">{{ holding.get('role', '核心持仓') }}</span></td>
                            </tr>
                            {% endfor %}'''
    
    return before + new_tbody + after

content = re.sub(tbody_pattern, replace_holdings_table, content, flags=re.DOTALL)
print("✓ 已替换第2节：持仓表格")

# 3. 替换个股分析卡片（第3节）- 将所有静态卡片替换为循环
analysis_grid_pattern = r'(<div class="analysis-grid">)(.*?)(</div>\s*</section>)'
def replace_analysis_grid(match):
    before = match.group(1)
    after = match.group(3)
    
    new_grid = '''
                    {% for stock in analysis.stock_analysis %}
                    <div class="stock-card">
                        <div class="stock-card-header">
                            <div>
                                <div class="stock-card-title">{{ stock.stock_name }}</div>
                                <div class="stock-card-subtitle font-num">{{ stock.stock_code }} · {{ stock.get('subtitle', '') }}</div>
                            </div>
                            <span class="status-capsule capsule-{{ stock.status_class }}">{{ stock.status }}</span>
                        </div>
                        <ul class="stock-card-list">
                            <li><strong>技术面：</strong>{{ stock.technical }}</li>
                            <li><strong>基本面：</strong>{{ stock.fundamental }}</li>
                            <li><strong>题材逻辑：</strong>{{ stock.theme }}</li>
                            <li><strong>风险点：</strong>{{ stock.risk }}</li>
                            <li><strong>操作建议：</strong>{{ stock.suggestion|safe }}</li>
                        </ul>
                    </div>
                    {% endfor %}'''
    
    return before + new_grid + after

# 找到第3节的 analysis-grid
sections = content.split('<!-- 3. 个股与 ETF 分析')
if len(sections) > 1:
    section3_and_after = sections[1]
    section3_parts = section3_and_after.split('<!-- 4. 本周建议操作清单')
    section3_content = section3_parts[0]
    
    section3_content = re.sub(analysis_grid_pattern, replace_analysis_grid, section3_content, flags=re.DOTALL)
    
    content = sections[0] + '<!-- 3. 个股与 ETF 分析' + section3_content + '<!-- 4. 本周建议操作清单' + section3_parts[1]
    print("✓ 已替换第3节：个股分析")

# 4. 替换操作清单表格（第4节）
action_table_pattern = r'(<table class="action-table align-center">.*?<tbody>)(.*?)(</tbody>)'
def replace_action_table(match):
    before = match.group(1)
    after = match.group(3)
    
    new_tbody = '''
                            {% for action in analysis.action_plan %}
                            <tr>
                                <td class="font-num">{{ action.stock_code }}</td>
                                <td class="col-text-left">{{ action.stock_name }}</td>
                                <td><span class="badge-action badge-{{ action.action_class }}">{{ action.action }}</span></td>
                                <td class="font-num">{{ action.price_range }}</td>
                                <td class="font-num">{{ action.current_position }}</td>
                                <td class="font-num">{{ action.target_position }}</td>
                                <td>{{ action.plan }}</td>
                                <td>{{ action.reason }}</td>
                            </tr>
                            {% endfor %}'''
    
    return before + new_tbody + after

content = re.sub(action_table_pattern, replace_action_table, content, flags=re.DOTALL)
print("✓ 已替换第4节：操作清单")

# 5. 替换目标仓位分布（第4节）
allocation_pattern = r'<div class="allocation-bar">\s*<div class="allocation-segment.*?</div>\s*</div>\s*<div class="allocation-legend">.*?</div>\s*</div>'
allocation_replacement = '''<div class="allocation-bar">
                        {% for segment in analysis.target_allocation_segments %}
                        <div class="allocation-segment {{ segment.css_class }}" style="width:{{ segment.percentage }}%;">{{ segment.label }} {{ segment.percentage }}%</div>
                        {% endfor %}
                    </div>
                    <div class="allocation-legend">
                        {% for segment in analysis.target_allocation_segments %}
                        <div class="allocation-legend-item">
                            <span class="allocation-legend-dot" style="background:{{ segment.color }};"></span> {{ segment.legend_label }}
                        </div>
                        {% endfor %}
                    </div>'''

content = re.sub(allocation_pattern, allocation_replacement, content, flags=re.DOTALL)
print("✓ 已替换第4节：目标仓位分布")

# 6. 替换风险评估（第5节）
risk_grid_pattern = r'(<div class="analysis-grid">)(.*?)(</div>\s*</section>\s*<!-- 6\. 板块)'
def replace_risk_grid(match):
    before = match.group(1)
    after = match.group(3)
    
    new_grid = '''
                    <!-- 当前风险 -->
                    <div class="stock-card">
                        <div class="stock-card-header">
                            <span class="stock-card-title">当前风险拆解</span>
                        </div>
                        <ul class="stock-card-list">
                            {% for risk in analysis.risk_assessment.current_risks %}
                            <li>{{ risk|safe }}</li>
                            {% endfor %}
                        </ul>
                    </div>

                    <!-- 优化建议 -->
                    <div class="stock-card">
                        <div class="stock-card-header">
                            <span class="stock-card-title">结构优化建议</span>
                        </div>
                        <ul class="stock-card-list recommendation-list">
                            {% for suggestion in analysis.risk_assessment.optimization_suggestions %}
                            <li>{{ suggestion|safe }}</li>
                            {% endfor %}
                        </ul>
                    </div>'''
    
    return before + new_grid + after

# 找到第5节
sections = content.split('<!-- 5. 组合风险与优化建议')
if len(sections) > 1:
    section5_and_after = sections[1]
    section5_parts = section5_and_after.split('<!-- 6. 板块')
    section5_content = section5_parts[0]
    
    section5_content = re.sub(risk_grid_pattern, replace_risk_grid, section5_content, flags=re.DOTALL)
    
    content = sections[0] + '<!-- 5. 组合风险与优化建议' + section5_content + '<!-- 6. 板块' + section5_parts[1]
    print("✓ 已替换第5节：风险评估")

# 7. 替换板块视角（第6节）
sector_pattern = r'(<div class="summary-card">\s*<div class="summary-card-text">)\s*从当前市场.*?(</div>\s*<div class="summary-bullets">\s*<ul>).*?(</ul>\s*</div>\s*</div>)'
sector_replacement = r'''\1
                        {{ analysis.sector_view.summary|safe }}
                    \2
                            <li><strong>主线判断：</strong>{{ analysis.sector_view.main_theme }}</li>
                            <li><strong>消费位置：</strong>{{ analysis.sector_view.consumer_position }}</li>
                            <li><strong>组合定位：</strong>{{ analysis.sector_view.portfolio_position }}</li>
                            <li><strong>调仓方向：</strong>{{ analysis.sector_view.adjustment_direction }}</li>
                        \3'''

content = re.sub(sector_pattern, sector_replacement, content, flags=re.DOTALL)
print("✓ 已替换第6节：板块视角")

# 8. 替换风险等级条的动态宽度
content = re.sub(
    r'<div class="risk-bar-fill" style="width: 65%;"></div>',
    '<div class="risk-bar-fill" style="width:{{ analysis.risk_assessment.level_score }}%;"></div>',
    content
)
content = re.sub(
    r'<span class="risk-label">中等偏高</span>',
    '<span class="risk-label">{{ analysis.risk_assessment.level }}</span>',
    content
)
print("✓ 已替换风险等级条")

# 保存转换后的模板
with open('templates/weekly_report.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ 模板转换完成！")
print(f"输出文件: templates/weekly_report.html")
print(f"文件大小: {len(content)} 字符")
