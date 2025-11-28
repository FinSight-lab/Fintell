# 任务规划总结

## 📋 调整说明

根据你的要求，我已经调整了 tasks.md，重点变化如下：

### 🎯 核心调整

1. **简化第一里程碑**
   - 专注于周报生成和推送的核心功能
   - 不强制使用数据库，优先快速实现
   - 充分复用现有代码（stock_query.py、reference_llm_service.py）

2. **明确技术路线**
   - 使用 templates/weekly_template.html 作为 Jinja2 模板
   - 参考 reference_llm_service.py 实现 LLM 服务
   - 从 stock_position.json 读取持仓数据
   - Wind API 获取行情和技术指标

3. **第一个接口：周报推送**
   - POST /api/reports/weekly
   - 完整流程：持仓加载 → Wind 数据 → 技术指标 → LLM 分析 → HTML 渲染 → 微信推送

## 🚀 第一里程碑任务清单（7个主任务）

### ✅ Task 1: 搭建后端项目基础结构（已完成）
- FastAPI 项目初始化
- 依赖安装和配置
- 目录结构创建
- 环境变量配置

### Task 2: 实现 Wind 数据采集服务
- **2.1** 封装 Wind API 客户端（复用 stock_query.py）
- **2.2** 实现技术指标计算服务（迁移 calc_ma、calc_rsi 等）
- **2.3** 实现持仓数据服务（读取 stock_position.json）
- **2.4** 实现数据整合服务（组合所有数据）

### Task 3: 实现 LLM 分析服务
- **3.1** 创建 LLM 客户端（参考 reference_llm_service.py）
- **3.2** 设计周报分析提示词（调整为股票场景）
- **3.3** 实现周报分析生成（调用 LLM 并解析 JSON）

### Task 4: 实现 Jinja2 模板渲染服务
- **4.1** 复制并调整 HTML 模板（添加 Jinja2 标记）
- **4.2** 实现模板渲染服务（映射数据到模板）

### Task 5: 实现推送服务
- **5.1** 实现 ServerChan 推送（参考 vx_notice_push.py）

### Task 6: 创建周报生成 API 接口
- **6.1** 实现周报生成接口（POST /api/reports/weekly）
- **6.2** 注册路由并测试

### Task 7: 端到端测试和优化
- **7.1** 完整流程测试
- **7.2** 错误处理和日志优化

## 📊 数据流程图

```
stock_position.json
        ↓
    持仓数据
        ↓
    Wind API ← stock_query.py 逻辑
        ↓
  行情 + 技术指标
        ↓
    数据整合
        ↓
    LLM 分析 ← reference_llm_service.py 逻辑
        ↓
   结构化 JSON
        ↓
  Jinja2 渲染 ← weekly_template.html
        ↓
    HTML 周报
        ↓
  ServerChan 推送
        ↓
      微信通知
```

## 🎯 成功标准

完成第一里程碑后，应该能够：

1. ✅ 调用 `POST /api/reports/weekly` 接口
2. ✅ 自动获取 Wind 数据并计算技术指标
3. ✅ LLM 生成结构化的周报分析（JSON 格式）
4. ✅ 渲染出美观的 HTML 周报（基于 weekly_template.html）
5. ✅ 成功推送到微信
6. ✅ 整个流程在 2 分钟内完成

## 📝 关键文件清单

### 需要创建的文件
```
app/services/
├── wind_service.py          # Wind API 客户端
├── indicators.py            # 技术指标计算
├── portfolio_service.py     # 持仓数据服务
├── data_service.py          # 数据整合服务
├── llm_service.py           # LLM 客户端（参考 reference_llm_service.py）
├── template_service.py      # Jinja2 模板渲染
└── notification_service.py  # ServerChan 推送

app/api/
└── reports.py               # 周报 API 接口

templates/
└── weekly_report.html       # Jinja2 模板（基于 weekly_template.html）
```

### 参考文件
```
stock_query.py               # Wind API 和技术指标参考
reference_llm_service.py     # LLM 服务参考
vx_notice_push.py           # ServerChan 推送参考
stock_position.json         # 持仓数据
templates/weekly_template.html  # HTML 模板参考
```

## 🔧 技术要点

### Wind API 调用
- 复用 stock_query.py 中的 `wind_to_df()` 逻辑
- 获取股票基本信息、最新行情、历史数据
- 计算 MA、RSI、MACD、BOLL 等技术指标

### LLM 提示词设计
- 参考 reference_llm_service.py 的 prompt 结构
- 调整为股票分析场景
- 定义清晰的 JSON 输出格式
- 包含：核心观点、持仓分析、个股分析、调仓建议、风险评估

### Jinja2 模板
- 基于 weekly_template.html 的完整样式
- 添加动态数据绑定
- 支持循环渲染（持仓列表、个股分析等）
- 支持条件渲染（涨跌颜色、风险等级等）

### 数据结构示例
```python
{
    "report_date": "2025-11-28",
    "period": "2025-11-24 - 2025-11-28",
    "total_assets": 322157.20,
    "kpis": {
        "weekly_return": -0.42,
        "ytd_return": 3.80,
        "position_ratio": 87,
        "action_count": 3
    },
    "holdings": [
        {
            "code": "600519.SH",
            "name": "贵州茅台",
            "current_price": 1447.30,
            "cost_price": 1458.96,
            "market_value": 145000.00,
            "position_ratio": 45.0,
            "profit_loss": -1166.10,
            "profit_loss_pct": -0.80,
            "role": "核心持仓"
        }
    ],
    "analysis": {
        "core_viewpoint": "...",
        "stock_analysis": [...],
        "action_plan": [...],
        "risk_assessment": {...}
    }
}
```

## 🚦 下一步行动

1. **开始 Task 2**：实现 Wind 数据采集服务
2. 从 stock_query.py 提取 Wind API 逻辑
3. 封装为独立的服务类
4. 测试数据获取和指标计算

---

**注意**：第二、第三里程碑（数据库持久化、定时任务、前端界面）都是可选的，可以在第一里程碑完成并验证后再决定是否实施。
