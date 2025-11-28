# 最终实施计划

## 📋 项目概述

**智能持仓管理系统** - 一个"省心型"股票持仓智能管家

### 核心功能
1. **周报生成**：基于 Wind 数据 + LLM 分析，生成专业的 HTML 周报
2. **持仓管理**：数据库存储持仓数据，支持增删改查
3. **微信推送**：自动推送周报到微信
4. **Admin 后台**：Next.js 管理界面，可视化操作

### 技术栈
- **后端**: FastAPI + SQLAlchemy + MySQL + Wind API
- **前端**: Next.js 14 + TypeScript + Tailwind CSS
- **LLM**: Gemini API
- **推送**: ServerChan

---

## 🎯 第一里程碑：纯后端 API（当前重点）

### 目标
实现周报生成和推送的完整后端 API，调用接口即可生成并推送周报。

### 核心流程
```
数据库持仓数据
        ↓
    Wind API 获取行情
        ↓
    计算技术指标
        ↓
    LLM 生成分析（JSON）
        ↓
    Jinja2 渲染 HTML
        ↓
    保存到数据库
        ↓
    ServerChan 推送微信
```

### 任务清单

#### ✅ Task 1: 搭建后端项目基础结构（已完成）
- FastAPI 项目初始化
- 依赖安装和配置
- 目录结构创建

#### 🔄 Task 1.5: 创建数据库和初始化表结构（新增）
- **1.5.1** 创建数据库模型
  - Portfolio 模型（持仓组合）
  - Position 模型（个股持仓）
  - Report 模型（周报记录）
  - StockDataCache 模型（可选）
- **1.5.2** 配置 Alembic 并执行迁移
  - 创建迁移脚本
  - 执行迁移
  - 从 stock_position.json 导入初始数据

#### Task 2: 实现 Wind 数据采集服务
- **2.1** 封装 Wind API 客户端
- **2.2** 实现技术指标计算服务
- **2.3** 实现持仓数据服务（从数据库读取）
- **2.4** 实现数据整合服务

#### Task 3: 实现 LLM 分析服务
- **3.1** 创建 LLM 客户端（参考 reference_llm_service.py）
- **3.2** 设计周报分析提示词（调整为股票场景）
- **3.3** 实现周报分析生成

#### Task 4: 实现 Jinja2 模板渲染服务
- **4.1** 复制并调整 HTML 模板（添加 Jinja2 标记）
- **4.2** 实现模板渲染服务

#### Task 5: 实现推送服务
- **5.1** 实现 ServerChan 推送

#### Task 6: 创建周报生成 API 接口
- **6.1** 实现 POST /api/reports/weekly 接口
- **6.2** 注册路由并测试

#### Task 7: 端到端测试和优化
- **7.1** 完整流程测试
- **7.2** 错误处理和日志优化

### 成功标准
- ✅ 调用 `POST /api/reports/weekly?portfolio_id=1` 接口
- ✅ 从数据库读取持仓数据
- ✅ 成功获取 Wind 数据并计算技术指标
- ✅ LLM 生成结构化的周报分析（JSON 格式）
- ✅ 渲染出美观的 HTML 周报
- ✅ 保存周报到数据库
- ✅ 成功推送到微信
- ✅ 整个流程在 2 分钟内完成

---

## 🚀 第二里程碑：Admin 管理系统（前端）

### 目标
基于 free-nextjs-admin-dashboard-main 搭建管理后台。

### 核心功能
1. **仪表盘**：资产概览、持仓分布图表
2. **持仓管理**：增删改查、批量导入
3. **周报管理**：查看历史周报、生成新周报、重新推送

### 任务清单

#### Task 8: 搭建前端项目
- **8.1** 初始化 Next.js 项目（frontend/ 目录）
- **8.2** 配置基础布局和路由

#### Task 9: 实现持仓管理页面
- **9.1** 持仓列表页面
- **9.2** 持仓编辑功能
- **9.3** 批量导入功能

#### Task 10: 实现仪表盘页面
- **10.1** 资产概览卡片
- **10.2** 持仓分布图表
- **10.3** 快捷操作

#### Task 11: 实现周报管理页面
- **11.1** 周报列表页面
- **11.2** 周报详情页面
- **11.3** 周报生成功能

#### Task 12: 扩展后端 API（支持前端）
- **12.1** 持仓管理 API
- **12.2** 仪表盘数据 API
- **12.3** 报告查询 API

#### Task 13: 实现定时任务系统（可选）
- **13.1** 配置 APScheduler
- **13.2** 实现每周自动生成任务

---

## 📦 数据库设计

### Portfolio 表（持仓组合）
```sql
CREATE TABLE portfolios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    name VARCHAR(100),
    total_assets DECIMAL(15, 2),
    created_at DATETIME,
    updated_at DATETIME
);
```

### Position 表（个股持仓）
```sql
CREATE TABLE positions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    portfolio_id INT,
    stock_code VARCHAR(20),
    stock_name VARCHAR(100),
    quantity INT,
    cost_price DECIMAL(10, 3),
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);
```

### Report 表（周报记录）
```sql
CREATE TABLE reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    portfolio_id INT,
    report_type VARCHAR(20),
    report_date DATE,
    content JSON,
    html_content TEXT,
    pushed BOOLEAN,
    created_at DATETIME,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);
```

### StockDataCache 表（可选）
```sql
CREATE TABLE stock_data_cache (
    id INT PRIMARY KEY AUTO_INCREMENT,
    stock_code VARCHAR(20),
    date DATE,
    close_price DECIMAL(10, 3),
    volume BIGINT,
    indicators JSON,
    created_at DATETIME,
    UNIQUE KEY (stock_code, date)
);
```

---

## 🔧 API 接口设计

### 第一里程碑 API

#### 1. 生成周报
```
POST /api/reports/weekly
Body: {
    "portfolio_id": 1,
    "skip_push": false,
    "date": "2025-11-28"  // 可选
}
Response: {
    "success": true,
    "report_id": 123,
    "html": "<html>...</html>",
    "pushed": true
}
```

### 第二里程碑 API

#### 2. 持仓管理
```
GET /api/portfolios/{id}/positions
POST /api/portfolios/{id}/positions
PUT /api/portfolios/{id}/positions/{code}
DELETE /api/portfolios/{id}/positions/{code}
POST /api/portfolios/{id}/positions/import
```

#### 3. 仪表盘数据
```
GET /api/portfolios/{id}/metrics
GET /api/portfolios/{id}/distribution
```

#### 4. 报告查询
```
GET /api/reports
GET /api/reports/{id}
GET /api/reports/latest
POST /api/reports/{id}/push
```

---

## 📁 项目结构（最终）

```
smart-portfolio-manager/
├── backend/                    # 后端 FastAPI 项目
│   ├── app/
│   │   ├── models/            # 数据库模型
│   │   │   ├── portfolio.py
│   │   │   ├── report.py
│   │   │   └── stock_cache.py
│   │   ├── services/          # 业务逻辑
│   │   │   ├── wind_service.py
│   │   │   ├── indicators.py
│   │   │   ├── portfolio_service.py
│   │   │   ├── data_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── template_service.py
│   │   │   └── notification_service.py
│   │   ├── api/               # API 端点
│   │   │   └── reports.py
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   └── main.py
│   ├── templates/             # Jinja2 模板
│   │   └── weekly_report.html
│   ├── alembic/               # 数据库迁移
│   ├── .env
│   ├── pyproject.toml
│   └── README.md
│
├── frontend/                   # 前端 Next.js 项目（第二里程碑）
│   ├── src/
│   │   ├── app/               # Next.js 14 App Router
│   │   │   ├── dashboard/
│   │   │   ├── portfolio/
│   │   │   └── reports/
│   │   ├── components/        # React 组件
│   │   └── lib/               # 工具函数
│   ├── public/
│   ├── .env.local
│   ├── package.json
│   └── README.md
│
├── docs/                       # 文档
├── stock_position.json         # 初始持仓数据（用于导入）
├── stock_query.py              # 参考代码
├── reference_llm_service.py    # 参考代码
└── README.md
```

---

## 🚦 下一步行动

### 立即开始：Task 1.5 - 创建数据库和初始化表结构

1. **创建数据库模型**
   - 定义 Portfolio、Position、Report 模型
   - 使用 SQLAlchemy ORM

2. **配置 Alembic**
   - 创建迁移脚本
   - 执行迁移创建表

3. **导入初始数据**
   - 从 stock_position.json 读取数据
   - 插入到数据库

### 预期时间
- Task 1.5: 1-2 小时
- Task 2-7: 8-12 小时
- **第一里程碑总计**: 10-14 小时

---

## ✅ 确认清单

在开始开发前，请确认：

- [x] Tasks 规划已明确
- [x] 技术方案已确定（数据库 + 前后端分离）
- [x] 参考代码已准备（stock_query.py、reference_llm_service.py）
- [x] 模板文件已准备（weekly_template.html）
- [ ] Wind API 可用
- [ ] LLM API 可用
- [ ] 数据库可连接
- [ ] ServerChan Key 已配置

**准备好了吗？让我们开始 Task 1.5！** 🚀
