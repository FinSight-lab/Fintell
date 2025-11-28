"""修复第1节的内容"""
import re

with open('templates/weekly_report.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 更简单的方式：直接替换整个 summary-card 内容
old_text = '''                    <div class="summary-card-text">
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
                    </div>'''

new_text = '''                    <div class="summary-card-text">
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
                    {% endif %}'''

if old_text in content:
    content = content.replace(old_text, new_text)
    print("✓ 第1节已修复")
else:
    print("✗ 未找到匹配内容，尝试打印前后内容...")
    # 查找位置
    idx = content.find('summary-card-text')
    if idx > 0:
        print(f"找到 summary-card-text 在位置 {idx}")
        print("内容片段:")
        print(repr(content[idx:idx+500]))

with open('templates/weekly_report.html', 'w', encoding='utf-8') as f:
    f.write(content)
