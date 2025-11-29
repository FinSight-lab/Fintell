# 实施计划

## 🎯 第一里程碑：周报推送 MVP（简化版）

### 目标
快速实现周报生成和推送的核心功能，基于现有模板和参考代码。

### 技术方案
- **后端**: FastAPI + SQLAlchemy + MySQL + Wind API
- **数据源**: Wind API（复用 stock_query.py）+ 数据库持仓数据
- **LLM**: Gemini API（参考 reference_llm_service.py）
- **模板**: Jinja2 渲染 HTML（使用 templates/weekly_template.html）
- **推送**: ServerChan（微信）
- **数据库**: MySQL 存储持仓数据、周报记录等
- **前端**: Next.js 14 + TypeScript + Tailwind CSS（第二里程碑）

### 核心原则
- **前后端分离**：后端提供 RESTful API，前端独立部署
- **数据库优先**：持仓数据存储在数据库，支持多用户
- **复用代码**：充分利用现有的 stock_query.py 和 reference_llm_service.py
- **快速迭代**：先实现核心功能，后续再优化

### 项目结构
```
smart-portfolio-manager/
├── backend/              # 后端 FastAPI 项目
│   ├── app/
│   │   ├── models/      # 数据库模型
│   │   ├── services/    # 业务逻辑
│   │   ├── api/         # API 端点
│   │   └── core/        # 核心配置
│   ├── templates/       # Jinja2 模板
│   └── alembic/         # 数据库迁移
└── frontend/            # 前端 Next.js 项目（第二里程碑）
    ├── src/
    │   ├── app/         # Next.js 14 App Router
    │   ├── components/  # React 组件
    │   └── lib/         # 工具函数
    └── public/          # 静态资源
```

---

- [x] 1. 搭建后端项目基础结构
  - 使用 Poetry 初始化 FastAPI 项目
  - 安装核心依赖：fastapi, uvicorn, sqlalchemy, alembic, pandas, requests, jinja2, pymysql
  - 配置项目目录结构（app/models, app/services, app/api, templates/, prompts/）
  - 配置环境变量（.env 文件）：数据库连接、LLM API、ServerChan Key
  - 设置 Git 仓库，包含 .gitignore 和 README
  - _需求: 所有需求都依赖于正确的项目搭建_
  - _数据库: host=frp3.ccszxc.site, port=14269, user=root, password=zxc123_
  - _LLM API: http://frp3.ccszxc.site:14266/v1/chat/completions, model=gemini-3-pro-preview-thinking, key=zxc123_
  - _注意: 后续需要重组为 backend/ 和 frontend/ 目录结构_

- [ ] 1.5 创建数据库和初始化表结构



  - [x] 1.5.1 创建数据库模型


    - 创建 app/models/portfolio.py - Portfolio 和 Position 模型
    - 创建 app/models/report.py - Report 模型
    - 创建 app/models/stock_cache.py - StockDataCache 模型（可选）
    - _需求: 1.1, 2.7, 4.6_
  
  - [x] 1.5.2 配置 Alembic 并执行迁移


    - 创建初始迁移脚本
    - 执行迁移创建表结构
    - 从 stock_position.json 导入初始持仓数据
    - _需求: 1.3, 9.2_

- [ ] 2. 实现 Wind 数据采集和技术指标计算



  - [x] 2.1 封装 Wind API 客户端


    - 创建 app/services/wind_service.py
    - 复用 stock_query.py 中的 Wind API 调用逻辑
    - 实现 WindService 类，包含以下方法：
      - `get_stock_info(stock_code)`: 获取股票基本信息（名称）
      - `get_stock_data(stock_code, days=90)`: 获取历史行情数据
      - `get_latest_price(stock_code)`: 获取最新价格
      - `wind_to_df(res)`: Wind 响应转 DataFrame
    - 添加错误处理和重试逻辑
    - 添加日志记录
    - _需求: 2.1, 2.6_
    - _参考: stock_query.py 的 wind_to_df() 和 get_stock_recent_info()_
  
  - [x] 2.2 实现技术指标计算服务


    - 创建 app/services/indicators.py
    - 完全复制 stock_query.py 中的技术指标函数：
      - `calc_ma(series)`: 计算 MA5, MA10, MA20, MA30, MA250
      - `calc_rsi(close)`: 计算 RSI6, RSI12, RSI24
      - `calc_macd(close)`: 计算 MACD_DIF, MACD_DEA, MACD
      - `calc_boll(close)`: 计算 BOLL_mid, BOLL_upper, BOLL_lower
    - 保持计算逻辑完全一致
    - 添加输入验证和异常处理
    - _需求: 2.2, 2.3, 2.4, 2.5_
    - _参考: stock_query.py 的技术指标函数_
  
  - [x] 2.3 实现持仓数据服务


    - 创建 app/services/portfolio_service.py
    - 实现 PortfolioService 类，包含以下方法：
      - `get_portfolio(portfolio_id)`: 获取持仓组合
      - `get_positions(portfolio_id)`: 获取持仓列表
      - `calculate_position_metrics(position, current_price)`: 计算单个持仓的市值、盈亏
      - `calculate_portfolio_metrics(portfolio_id, positions_data)`: 计算组合级别指标
    - 支持持仓数据的增删改查（基于数据库）
    - _需求: 1.1, 1.2_
  
  - [x] 2.4 实现数据整合服务


    - 创建 app/services/data_service.py
    - 实现 DataService 类，整合所有数据：
      - 从数据库加载持仓数据
      - 调用 Wind API 获取每只股票的行情数据
      - 计算每只股票的技术指标
      - 计算每只股票的盈亏情况
      - 计算组合级别的汇总指标
    - 生成周报所需的完整数据结构（JSON 格式）
    - 数据结构包含：
      - 基本信息：报告日期、统计周期、总资产
      - KPI 指标：周收益率、年初至今收益率、仓位占比、建议调仓数
      - 持仓明细：每只股票的代码、名称、价格、成本、市值、盈亏、技术指标
      - 组合汇总：总市值、总盈亏、持仓分布等
    - _需求: 1.1, 2.1-2.7_
  
  - [x] 2.5 测试 Wind 接口和数据整合



    - 创建测试脚本 scripts/test_wind_data.py
    - 测试 Wind API 连接
    - 测试获取单只股票的完整数据
    - 测试获取组合所有股票的数据
    - 验证技术指标计算正确性
    - 验证数据结构完整性
    - _需求: 2.1-2.7_

- [x] 3. 实现 LLM 分析服务


  - [x] 3.1 创建 LLM 客户端



    - 创建 app/services/llm_service.py
    - 参考 reference_llm_service.py 实现 LLMService 类
    - 连接到 Gemini API (http://frp3.ccszxc.site:14266/v1/chat/completions)
    - 实现流式响应处理（SSE 格式）
    - 添加重试逻辑和错误处理
    - _需求: 4.7_
    - _参考: reference_llm_service.py 的完整实现_
  
  - [x] 3.2 设计周报分析提示词

    - 参考 reference_llm_service.py 中的 system_prompt 和 user_prompt
    - 调整为股票周报场景（从大宗商品改为股票）
    - 定义 JSON 输出结构，包含：
      - 核心观点 (core_viewpoint)
      - 持仓盈亏分析 (holdings_analysis)
      - 个股分析 (stock_analysis)：技术面、基本面、题材逻辑、风险点、操作建议
      - 调仓建议 (action_plan)：具体操作清单
      - 风险评估 (risk_assessment)
      - 板块视角 (sector_view)
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5_
    - _参考: reference_llm_service.py 的 prompt 设计思路_
  
  - [x] 3.3 实现周报分析生成

    - 在 LLMService 中实现 generate_weekly_analysis() 方法
    - 接收整合后的数据（持仓、行情、技术指标）
    - 调用 LLM API 生成结构化分析
    - 解析 JSON 响应并验证格式
    - 添加流式输出的进度回调（可选）
    - _需求: 4.1-4.8_

- [x] 4. 实现 Jinja2 模板渲染服务


  - [x] 4.1 复制并调整 HTML 模板


    - 将 templates/weekly_template.html 复制为工作模板
    - 识别所有需要动态填充的数据点
    - 添加 Jinja2 变量标记（{{ variable }}）
    - 添加循环和条件逻辑（{% for %}, {% if %}）
    - 确保样式完整且适配微信显示
    - _需求: 4.6_
    - _参考: templates/weekly_template.html 的完整结构_
  
  - [x] 4.2 实现模板渲染服务



    - 创建 app/services/template_service.py
    - 实现 TemplateService 类
    - 实现 render_weekly_report(data) 方法
    - 将 LLM 生成的 JSON 数据映射到模板变量
    - 处理数据格式化（日期、金额、百分比等）
    - 生成最终的 HTML 字符串
    - _需求: 4.6_

- [x] 5. 创建周报生成 API 接口



  - [x] 5.1 实现周报生成接口


    - 创建 app/api/reports.py
    - 实现 POST /api/reports/weekly 接口
    - 接口功能：
      1. 从数据库加载持仓数据 
      2. 调用 Wind API 获取最新行情和历史数据
      3. 计算技术指标
      4. 调用 LLM 生成结构化分析（JSON 格式）
      5. 使用 Jinja2 渲染 HTML 模板
      6. 保存周报到数据库
      7. 返回生成的 HTML
    - 添加请求参数：portfolio_id（持仓组合ID）、date（指定日期）
    - 添加详细的日志输出
    - _需求: 4.1, 4.6, 4.7_
  
  - [x] 5.2 注册路由并测试


    - 在 app/main.py 中注册 reports 路由
    - 使用 FastAPI 自动文档测试接口
    - 验证完整流程可用
    - _需求: 所有 MVP 需求_

- [x] 6. 端到端测试和优化




  - [x] 6.1 完整流程测试
    - 使用数据库中的真实持仓数据测试
    - 验证 Wind API 数据获取正确
    - 验证技术指标计算准确
    - 验证 LLM 输出格式和内容质量
    - 验证 HTML 渲染效果（在浏览器中查看）
    - _需求: 所有 MVP 需求_
  
  - [x] 6.2 错误处理和日志优化


    - 添加完善的错误处理
    - 优化日志输出（INFO、WARNING、ERROR 级别）
    - 添加关键步骤的进度提示
    - _需求: 所有需求_

- [ ] 7. 实现推送服务


  - [ ] 7.1 实现 ServerChan 推送



    - 创建 app/services/notification_service.py
    - 参考 vx_notice_push.py 实现 ServerChan 推送
    - 实现 send_serverchan(title, content) 方法
    - 支持 HTML 格式内容
    - 添加重试逻辑（3次）
    - 添加推送日志记录
    - _需求: 3.6, 8.1_
    - _参考: vx_notice_push.py 的 push_wechat 函数_
  
  - [ ] 7.2 集成推送到周报 API
    - 在 POST /api/reports/weekly 接口中添加推送功能
    - 添加 skip_push 参数控制是否推送
    - 验证微信推送成功
    - _需求: 3.6, 8.1_

---

## 🚀 第二里程碑：Admin 管理系统（前端）

### 目标
基于 free-nextjs-admin-dashboard-main 搭建管理后台，实现持仓管理、仪表盘、周报生成等功能。

### 技术方案
- **框架**: Next.js 14 + TypeScript + Tailwind CSS
- **UI 参考**: free-nextjs-admin-dashboard-main
- **状态管理**: React Hooks + Context API
- **数据可视化**: Recharts
- **API 调用**: Fetch API / Axios

---

- [ ] 8. 搭建前端项目（第二里程碑）
  - [ ] 8.1 初始化 Next.js 项目
    - 创建 frontend/ 目录
    - 使用 create-next-app 初始化项目（TypeScript + Tailwind CSS）
    - 参考 free-nextjs-admin-dashboard-main 的项目结构
    - 配置环境变量（后端 API 地址）
    - _需求: 前端需求_
  
  - [ ] 8.2 配置基础布局和路由
    - 创建 Admin 布局组件（侧边栏 + 顶部导航）
    - 配置路由结构（仪表盘、持仓管理、周报查看）
    - 实现响应式设计
    - _需求: 前端需求_

- [ ] 9. 实现持仓管理页面
  - [ ] 9.1 持仓列表页面
    - 展示持仓列表（表格形式）
    - 显示股票代码、名称、数量、成本价、当前价、盈亏等
    - 支持搜索和筛选
    - _需求: 1.1, 1.3_
  
  - [ ] 9.2 持仓编辑功能
    - 添加持仓表单（股票代码、数量、成本价）
    - 编辑持仓信息
    - 删除持仓
    - 连接后端 API
    - _需求: 1.2_
  
  - [ ] 9.3 批量导入功能
    - 支持 CSV/JSON 文件导入
    - 数据验证和错误提示
    - 导入预览
    - _需求: 1.2_

- [ ] 10. 实现仪表盘页面
  - [ ] 10.1 资产概览卡片
    - 总资产、总盈亏、持仓数量等关键指标
    - 使用卡片组件展示
    - 实时更新（可选）
    - _需求: 6.1_
  
  - [ ] 10.2 持仓分布图表
    - 饼图展示持仓占比
    - 柱状图展示盈亏情况
    - 使用 Recharts 实现
    - _需求: 6.2_
  
  - [ ] 10.3 快捷操作
    - "生成周报"按钮
    - "查看最新周报"按钮
    - 操作状态提示
    - _需求: 4.6_

- [ ] 11. 实现周报管理页面
  - [ ] 11.1 周报列表页面
    - 展示历史周报列表
    - 显示生成时间、状态等信息
    - 支持日期筛选
    - _需求: 4.6_
  
  - [ ] 11.2 周报详情页面
    - 展示 HTML 格式的周报
    - 支持打印和导出
    - 支持重新推送到微信
    - _需求: 4.6_
  
  - [ ] 11.3 周报生成功能
    - "生成周报"按钮
    - 生成进度提示（流式输出）
    - 生成完成后自动跳转到详情页
    - _需求: 4.6, 4.7_

- [ ] 12. 扩展后端 API（支持前端）
  - [ ] 12.1 持仓管理 API
    - GET /api/portfolios - 查询持仓组合列表
    - GET /api/portfolios/{id}/positions - 查询持仓列表
    - POST /api/portfolios/{id}/positions - 添加持仓
    - PUT /api/portfolios/{id}/positions/{code} - 更新持仓
    - DELETE /api/portfolios/{id}/positions/{code} - 删除持仓
    - POST /api/portfolios/{id}/positions/import - 批量导入
    - _需求: 1.1, 1.2, 1.3_
  
  - [ ] 12.2 仪表盘数据 API
    - GET /api/portfolios/{id}/metrics - 获取资产指标
    - GET /api/portfolios/{id}/distribution - 获取持仓分布
    - _需求: 6.1, 6.2_
  
  - [ ] 12.3 报告查询 API
    - GET /api/reports - 查询历史报告列表
    - GET /api/reports/{id} - 查询报告详情
    - GET /api/reports/latest - 查询最新报告
    - POST /api/reports/{id}/push - 重新推送报告
    - _需求: 4.6_

- [ ] 13. 实现定时任务系统（可选）
  - [ ] 13.1 配置 APScheduler
    - 配置 AsyncIOScheduler
    - 创建任务执行日志
    - _需求: 10.1, 10.2, 10.3_
  
  - [ ] 13.2 实现每周自动生成任务
    - 创建定时作业（周五 16:00）
    - 自动调用周报生成接口
    - 自动推送到微信
    - _需求: 4.1, 10.3, 10.6_

---

## 🎨 第三里程碑：高级功能（后续）

---

## 📦 后续功能（按需实现）

- [ ] 14. 实现用户认证系统
  - 用户注册和登录
  - JWT token 管理
  - 权限控制
  - _需求: 9.1, 9.3_

- [ ] 15. 实现调仓工作流
  - 调仓建议展示
  - 调仓确认界面
  - 调仓历史记录
  - _需求: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [ ] 16. 实现回测功能
  - 回测计算引擎
  - 回测结果可视化
  - 风险指标计算
  - _需求: 7.1, 7.2, 7.3_

- [ ] 17. 实现用户偏好管理
  - 风险偏好配置
  - 通知设置
  - 调仓频率设置
  - _需求: 1.4, 1.5, 8.1, 8.2, 8.3, 8.4_

---

## 🧪 可选任务

- [ ]* 18. 编写测试
  - 单元测试（服务层）
  - 集成测试（API 接口）
  - 端到端测试
  - _需求: 所有需求_

- [ ]* 19. 性能优化
  - 数据库查询优化
  - API 响应缓存
  - Wind API 调用优化
  - _需求: 6.5, 7.4_

- [ ]* 20. 错误处理和监控
  - 全局错误处理器
  - 日志中间件
  - 性能监控
  - _需求: 所有需求_

- [ ]* 21. 部署和运维
  - Docker 容器化
  - CI/CD 配置
  - 监控告警
  - _需求: 所有需求_

---

## 📝 实施说明

### 第一里程碑重点
1. **快速验证**：优先实现核心功能，验证技术方案可行性
2. **复用代码**：充分利用 stock_query.py 和 reference_llm_service.py
3. **灵活存储**：数据暂时不入库，使用 JSON 文件即可
4. **完整流程**：确保从数据采集到推送的完整链路打通

### 关键依赖
- **Wind API**：需要有效的 Wind 终端或 API 权限
- **LLM API**：Gemini API 需要稳定可用
- **ServerChan**：需要配置有效的 ServerChan Key

### 成功标准
- ✅ 调用 POST /api/reports/weekly 接口
- ✅ 成功获取 Wind 数据并计算技术指标
- ✅ LLM 生成结构化的周报分析（JSON 格式）
- ✅ 渲染出美观的 HTML 周报
- ✅ 整个流程在 2 分钟内完成
- ⏳ 成功推送到微信（待实现）
