# 实施指南

## 📚 现有资源说明

### 1. templates/weekly_template.html
**用途**：周报的 HTML 模板（完整样式）

**关键特点**：
- 完整的 CSS 样式（内联，适配微信）
- 包含所有周报章节：
  - 顶部 KPI 仪表盘
  - 组合总览
  - 持仓盈亏分析
  - 个股与 ETF 分析
  - 操作清单
  - 风险评估
  - 板块视角

**需要做的**：
- 将静态数据替换为 Jinja2 变量
- 添加循环逻辑（{% for %}）
- 添加条件逻辑（{% if %}）

**示例改造**：
```html
<!-- 原始静态数据 -->
<span class="font-num">2025年11月24日 - 2025年11月28日</span>

<!-- 改为 Jinja2 变量 -->
<span class="font-num">{{ period }}</span>

<!-- 原始静态列表 -->
<tr>
    <td>贵州茅台</td>
    <td>1,447.30</td>
    ...
</tr>

<!-- 改为 Jinja2 循环 -->
{% for holding in holdings %}
<tr>
    <td>{{ holding.name }}</td>
    <td class="font-num">{{ holding.current_price|format_price }}</td>
    ...
</tr>
{% endfor %}
```

### 2. reference_llm_service.py
**用途**：LLM 服务的完整参考实现（大宗商品场景）

**关键特点**：
- 完整的 LLMService 类
- 流式响应处理（SSE）
- 重试逻辑
- 详细的 system_prompt 设计
- 结构化 JSON 输出

**需要做的**：
- 复制整个类结构
- 调整 system_prompt（从大宗商品改为股票）
- 调整 user_prompt（传入股票数据）
- 调整 JSON 输出结构（适配周报模板）

**Prompt 调整要点**：
```python
# 原始（大宗商品）
"""你是一位专业的{product_name}品种研究分析师，服务于石油化工产业链大宗商品研究"""

# 调整为（股票）
"""你是一位专业的股票投资分析师，擅长 A 股市场分析和持仓管理"""

# 原始输出结构
{
    "core_viewpoint": "...",
    "sections": [...]
}

# 调整为周报结构
{
    "core_viewpoint": "...",
    "holdings_analysis": {...},
    "stock_analysis": [...],
    "action_plan": [...],
    "risk_assessment": {...},
    "sector_view": {...}
}
```

### 3. stock_query.py
**用途**：Wind API 调用和技术指标计算

**关键函数**：
- `wind_to_df()`: Wind API 响应转 DataFrame
- `calc_ma()`: 计算移动平均线
- `calc_rsi()`: 计算 RSI
- `calc_macd()`: 计算 MACD
- `calc_boll()`: 计算布林带
- `get_stock_recent_info()`: 获取股票完整信息

**需要做的**：
- 提取这些函数到 `app/services/indicators.py`
- 封装 Wind API 调用到 `app/services/wind_service.py`
- 保持计算逻辑完全一致

**示例封装**：
```python
# app/services/wind_service.py
class WindService:
    def __init__(self):
        from WindPy import w
        w.start()
        self.w = w
    
    def get_stock_info(self, stock_code: str, days: int = 90):
        """获取股票信息（复用 stock_query.py 逻辑）"""
        # 复制 get_stock_recent_info 的逻辑
        pass

# app/services/indicators.py
def calc_ma(df, periods=[5, 10, 20, 30, 250]):
    """计算移动平均线（完全复制 stock_query.py）"""
    # 复制原有逻辑
    pass
```

### 4. vx_notice_push.py
**用途**：ServerChan 推送参考

**关键函数**：
- `push_wechat()`: 推送到微信

**需要做的**：
- 提取推送逻辑到 `app/services/notification_service.py`
- 添加重试机制
- 添加日志记录

**示例封装**：
```python
# app/services/notification_service.py
class NotificationService:
    def __init__(self, serverchan_key: str):
        self.serverchan_key = serverchan_key
        self.base_url = "https://sctapi.ftqq.com"
    
    def send_serverchan(self, title: str, content: str, max_retries: int = 3):
        """发送 ServerChan 通知（复用 vx_notice_push.py 逻辑）"""
        # 复制 push_wechat 的逻辑
        pass
```

### 5. stock_position.json
**用途**：持仓数据

**数据结构**：
```json
{
  "stocks": ["000651.SZ", "600519.SH", ...],
  "positions": {
    "000651.SZ": 4000,
    "600519.SH": 100,
    ...
  },
  "cost_prices": {
    "000651.SZ": 40.745,
    "600519.SH": 1458.961,
    ...
  },
  "total_assets": 422157.20
}
```

**需要做的**：
- 创建 `PortfolioService` 读取这个文件
- 提供持仓查询、计算市值、盈亏等方法

## 🔧 实施步骤

### Step 1: 创建服务层（Task 2）

#### 1.1 Wind 数据服务
```python
# app/services/wind_service.py
from WindPy import w
import pandas as pd

class WindService:
    def __init__(self):
        w.start()
        self.w = w
    
    def get_stock_basic_info(self, stock_code: str):
        """获取股票基本信息"""
        pass
    
    def get_latest_price(self, stock_code: str):
        """获取最新价格"""
        pass
    
    def get_historical_data(self, stock_code: str, days: int = 90):
        """获取历史数据"""
        pass
```

#### 1.2 技术指标服务
```python
# app/services/indicators.py
import pandas as pd
import numpy as np

def calc_ma(df: pd.DataFrame, periods=[5, 10, 20, 30, 250]):
    """计算移动平均线"""
    # 复制 stock_query.py 的逻辑
    pass

def calc_rsi(df: pd.DataFrame, periods=[6, 12, 24]):
    """计算 RSI"""
    pass

def calc_macd(df: pd.DataFrame):
    """计算 MACD"""
    pass

def calc_boll(df: pd.DataFrame, period=20, std_num=2):
    """计算布林带"""
    pass
```

#### 1.3 持仓数据服务
```python
# app/services/portfolio_service.py
import json
from typing import Dict, List

class PortfolioService:
    def __init__(self, json_path: str = "stock_position.json"):
        self.json_path = json_path
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """加载持仓数据"""
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_positions(self) -> List[Dict]:
        """获取持仓列表"""
        pass
    
    def calculate_market_value(self, stock_code: str, current_price: float) -> float:
        """计算持仓市值"""
        pass
    
    def calculate_profit_loss(self, stock_code: str, current_price: float) -> Dict:
        """计算盈亏"""
        pass
```

#### 1.4 数据整合服务
```python
# app/services/data_service.py
from .wind_service import WindService
from .indicators import calc_ma, calc_rsi, calc_macd, calc_boll
from .portfolio_service import PortfolioService

class DataService:
    def __init__(self):
        self.wind = WindService()
        self.portfolio = PortfolioService()
    
    def get_weekly_report_data(self) -> Dict:
        """获取周报所需的完整数据"""
        # 1. 加载持仓
        positions = self.portfolio.get_positions()
        
        # 2. 获取每只股票的行情和技术指标
        holdings_data = []
        for pos in positions:
            stock_code = pos['code']
            # 获取 Wind 数据
            price_data = self.wind.get_latest_price(stock_code)
            hist_data = self.wind.get_historical_data(stock_code)
            
            # 计算技术指标
            indicators = {
                'ma': calc_ma(hist_data),
                'rsi': calc_rsi(hist_data),
                'macd': calc_macd(hist_data),
                'boll': calc_boll(hist_data)
            }
            
            # 计算盈亏
            profit_loss = self.portfolio.calculate_profit_loss(
                stock_code, 
                price_data['current_price']
            )
            
            holdings_data.append({
                'position': pos,
                'price': price_data,
                'indicators': indicators,
                'profit_loss': profit_loss
            })
        
        # 3. 计算组合级别指标
        portfolio_metrics = self._calculate_portfolio_metrics(holdings_data)
        
        return {
            'holdings': holdings_data,
            'portfolio_metrics': portfolio_metrics
        }
```

### Step 2: 创建 LLM 服务（Task 3）

```python
# app/services/llm_service.py
# 完全参考 reference_llm_service.py
# 调整 prompt 为股票场景
# 调整输出结构为周报格式
```

### Step 3: 创建模板服务（Task 4）

```python
# app/services/template_service.py
from jinja2 import Environment, FileSystemLoader
from typing import Dict

class TemplateService:
    def __init__(self, template_dir: str = "templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self._register_filters()
    
    def _register_filters(self):
        """注册自定义过滤器"""
        self.env.filters['format_price'] = lambda x: f"{x:,.2f}"
        self.env.filters['format_percent'] = lambda x: f"{x:+.2f}%"
        self.env.filters['format_date'] = lambda x: x.strftime('%Y年%m月%d日')
    
    def render_weekly_report(self, data: Dict) -> str:
        """渲染周报 HTML"""
        template = self.env.get_template('weekly_report.html')
        return template.render(**data)
```

### Step 4: 创建推送服务（Task 5）

```python
# app/services/notification_service.py
# 参考 vx_notice_push.py
# 添加重试逻辑
```

### Step 5: 创建 API 接口（Task 6）

```python
# app/api/reports.py
from fastapi import APIRouter, HTTPException
from app.services.data_service import DataService
from app.services.llm_service import LLMService
from app.services.template_service import TemplateService
from app.services.notification_service import NotificationService

router = APIRouter()

@router.post("/weekly")
async def generate_weekly_report(skip_push: bool = False):
    """生成周报并推送"""
    try:
        # 1. 获取数据
        data_service = DataService()
        report_data = data_service.get_weekly_report_data()
        
        # 2. LLM 分析
        llm_service = LLMService()
        analysis = llm_service.generate_weekly_analysis(report_data)
        
        # 3. 合并数据
        full_data = {**report_data, 'analysis': analysis}
        
        # 4. 渲染 HTML
        template_service = TemplateService()
        html = template_service.render_weekly_report(full_data)
        
        # 5. 推送（可选）
        if not skip_push:
            notification_service = NotificationService()
            notification_service.send_serverchan(
                title="📊 每周投资分析报告",
                content=html
            )
        
        return {
            "success": True,
            "html": html,
            "pushed": not skip_push
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 🎯 关键注意事项

### 1. Wind API 调用
- 确保 Wind 终端已启动
- 处理 Wind API 的错误码
- 添加重试逻辑

### 2. LLM Prompt 设计
- 参考 reference_llm_service.py 的详细 prompt
- 明确 JSON 输出格式
- 包含数据解读规则（如价差不用百分比）

### 3. Jinja2 模板
- 保持 weekly_template.html 的完整样式
- 添加自定义过滤器（格式化金额、日期等）
- 处理空值和异常情况

### 4. 数据格式化
- 金额：千分位分隔，保留2位小数
- 百分比：带符号，保留2位小数
- 日期：中文格式（2025年11月28日）

### 5. 错误处理
- Wind API 调用失败
- LLM API 调用失败
- 模板渲染失败
- 推送失败

## 📝 测试清单

- [ ] Wind API 能正常获取数据
- [ ] 技术指标计算正确
- [ ] 持仓数据加载正确
- [ ] LLM 返回结构化 JSON
- [ ] HTML 渲染美观且数据正确
- [ ] ServerChan 推送成功
- [ ] 完整流程在 2 分钟内完成

---

**下一步**：开始实施 Task 2.1 - 封装 Wind API 客户端
