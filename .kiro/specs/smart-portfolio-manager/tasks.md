# 实施计划

## 🎯 第一里程碑：周报推送 MVP（简化版）

### 目标
快速实现周报生成和推送的核心功能，基于现有模板和参考代码。

### 技术方案
- **后端**: FastAPI + Wind API
- **数据源**: Wind API（复用 stock_query.py）+ stock_position.json
- **LLM**: Gemini API（参考 reference_llm_service.py）
- **模板**: Jinja2 渲染 HTML（使用 templates/weekly_template.html）
- **推送**: ServerChan（微信）
- **数据库**: 可选使用，优先快速实现功能

### 核心原则
- **快速迭代**：先实现核心功能，后续再优化
- **复用代码**：充分利用现有的 stock_query.py 和 reference_llm_service.py
- **灵活存储**：数据可以暂时不入库，优先保证功能可用

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

- [ ] 2. 实现 Wind 数据采集服务
  - [ ] 2.1 封装 Wind API 客户端
    - 复用 stock_query.py 中的 Wind API 调用逻辑
    - 封装为 app/services/wind_service.py 中的 WindService 类
    - 实现获取股票基本信息、最新行情、历史数据的方法
    - 添加错误处理和日志记录
    - _需求: 2.1, 2.6_
    - _参考: stock_query.py 中的 wind_to_df() 和相关函数_
  
  - [ ] 2.2 实现技术指标计算服务
    - 创建 app/services/indicators.py
    - 迁移 calc_ma、calc_rsi、calc_macd、calc_boll 函数
    - 保持与 stock_query.py 完全一致的计算逻辑
    - 添加输入验证
    - _需求: 2.2, 2.3, 2.4, 2.5_
    - _参考: stock_query.py 中的技术指标计算函数_
  
  - [ ] 2.3 实现持仓数据服务
    - 创建 app/services/portfolio_service.py
    - 实现从 stock_position.json 加载持仓数据
    - 实现获取持仓列表、计算持仓市值、盈亏等方法
    - 支持持仓数据的增删改查（暂时基于文件，后续可迁移到数据库）
    - _需求: 1.1, 1.2_
  
  - [ ] 2.4 实现数据整合服务
    - 创建 app/services/data_service.py
    - 整合持仓数据 + Wind 行情数据 + 技术指标
    - 生成周报所需的完整数据结构
    - 计算组合级别的指标（总资产、总盈亏、仓位占比等）
    - _需求: 1.1, 2.1-2.7_

- [ ] 3. 实现 LLM 分析服务
  - [ ] 3.1 创建 LLM 客户端
    - 创建 app/services/llm_service.py
    - 参考 reference_llm_service.py 实现 LLMService 类
    - 连接到 Gemini API (http://frp3.ccszxc.site:14266/v1/chat/completions)
    - 实现流式响应处理（SSE 格式）
    - 添加重试逻辑和错误处理
    - _需求: 4.7_
    - _参考: reference_llm_service.py 的完整实现_
  
  - [ ] 3.2 设计周报分析提示词
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
  
  - [ ] 3.3 实现周报分析生成
    - 在 LLMService 中实现 generate_weekly_analysis() 方法
    - 接收整合后的数据（持仓、行情、技术指标）
    - 调用 LLM API 生成结构化分析
    - 解析 JSON 响应并验证格式
    - 添加流式输出的进度回调（可选）
    - _需求: 4.1-4.8_

- [ ] 4. 实现 Jinja2 模板渲染服务
  - [ ] 4.1 复制并调整 HTML 模板
    - 将 templates/weekly_template.html 复制为工作模板
    - 识别所有需要动态填充的数据点
    - 添加 Jinja2 变量标记（{{ variable }}）
    - 添加循环和条件逻辑（{% for %}, {% if %}）
    - 确保样式完整且适配微信显示
    - _需求: 4.6_
    - _参考: templates/weekly_template.html 的完整结构_
  
  - [ ] 4.2 实现模板渲染服务
    - 创建 app/services/template_service.py
    - 实现 TemplateService 类
    - 实现 render_weekly_report(data) 方法
    - 将 LLM 生成的 JSON 数据映射到模板变量
    - 处理数据格式化（日期、金额、百分比等）
    - 生成最终的 HTML 字符串
    - _需求: 4.6_

- [ ] 5. 实现推送服务
  - [ ] 5.1 实现 ServerChan 推送
    - 创建 app/services/notification_service.py
    - 参考 vx_notice_push.py 实现 ServerChan 推送
    - 实现 send_serverchan(title, content) 方法
    - 支持 HTML 格式内容
    - 添加重试逻辑（3次）
    - 添加推送日志记录
    - _需求: 3.6, 8.1_
    - _参考: vx_notice_push.py 的 push_wechat 函数_

- [ ] 6. 创建周报生成 API 接口
  - [ ] 6.1 实现周报生成接口
    - 创建 app/api/reports.py
    - 实现 POST /api/reports/weekly 接口
    - 接口功能：
      1. 加载持仓数据（stock_position.json）
      2. 调用 Wind API 获取最新行情和历史数据
      3. 计算技术指标
      4. 调用 LLM 生成分析
      5. 渲染 HTML 模板
      6. 推送到微信（可选参数控制）
      7. 返回生成的 HTML 和推送状态
    - 添加请求参数：skip_push（是否跳过推送）、date（指定日期）
    - 添加详细的日志输出
    - _需求: 4.1, 4.6, 4.7_
  
  - [ ] 6.2 注册路由并测试
    - 在 app/main.py 中注册 reports 路由
    - 使用 FastAPI 自动文档测试接口
    - 验证完整流程可用
    - _需求: 所有 MVP 需求_

- [ ] 7. 端到端测试和优化
  - [ ] 7.1 完整流程测试
    - 使用 stock_position.json 中的真实持仓测试
    - 验证 Wind API 数据获取正确
    - 验证技术指标计算准确
    - 验证 LLM 输出格式和内容质量
    - 验证 HTML 渲染效果（在浏览器和微信中查看）
    - 验证微信推送成功
    - _需求: 所有 MVP 需求_
  
  - [ ] 7.2 错误处理和日志优化
    - 添加完善的错误处理
    - 优化日志输出（INFO、WARNING、ERROR 级别）
    - 添加关键步骤的进度提示
    - _需求: 所有需求_

---

## 🚀 第二里程碑：数据库持久化和定时任务（可选）

- [ ] 8. 数据库模型和持久化（可选）
  - [ ] 8.1 创建数据库模型
    - 定义 Portfolio 模型（持仓组合）
    - 定义 Position 模型（个股持仓）
    - 定义 StockDataCache 模型（行情数据缓存）
    - 定义 Report 模型（周报记录）
    - _需求: 1.1, 2.7, 4.6_
  
  - [ ] 8.2 配置数据库迁移
    - 配置 Alembic
    - 创建初始迁移脚本
    - 执行迁移创建表结构
    - _需求: 1.3, 9.2_
  
  - [ ] 8.3 迁移持仓数据到数据库
    - 实现从 stock_position.json 导入到数据库
    - 修改 PortfolioService 使用数据库
    - 保留 JSON 文件作为备份
    - _需求: 1.1_
  
  - [ ] 8.4 实现数据缓存
    - 实现 Wind 数据缓存到数据库
    - 避免重复调用 Wind API
    - 设置缓存过期策略
    - _需求: 2.1, 2.7_

- [ ] 9. 实现定时任务系统
  - [ ] 9.1 配置 APScheduler
    - 配置 AsyncIOScheduler
    - 创建任务执行日志
    - _需求: 10.1, 10.2, 10.3_
  
  - [ ] 9.2 实现每周自动生成任务
    - 创建定时作业（周五 16:00）
    - 自动调用周报生成接口
    - 自动推送到微信
    - _需求: 4.1, 10.3, 10.6_
  
  - [ ] 9.3 实现每日数据采集任务（可选）
    - 创建定时作业（交易日 15:30）
    - 自动获取最新行情
    - 缓存到数据库
    - _需求: 2.1, 10.1, 10.6_

- [ ] 10. 扩展 API 接口
  - [ ] 10.1 实现持仓管理 API
    - GET /api/portfolio - 查询持仓列表
    - POST /api/portfolio/positions - 添加持仓
    - PUT /api/portfolio/positions/{code} - 更新持仓
    - DELETE /api/portfolio/positions/{code} - 删除持仓
    - _需求: 1.1, 1.2, 1.3_
  
  - [ ] 10.2 实现报告查询 API
    - GET /api/reports - 查询历史报告列表
    - GET /api/reports/{id} - 查询报告详情
    - GET /api/reports/latest - 查询最新报告
    - _需求: 4.6_

---

## 🎨 第三里程碑：前端界面（后续）

- [ ] 11. 搭建 Next.js 前端项目
  - 使用 TypeScript 和 Tailwind CSS 初始化 Next.js 14 项目
  - 配置 API 路由和环境变量
  - 设置项目目录结构
  - _需求: 前端需求_

- [ ] 12. 构建持仓管理页面
  - 创建持仓录入表单
  - 创建持仓列表展示
  - 实现 CSV/JSON 导入功能
  - 连接到后端 API
  - _需求: 1.1, 1.2, 1.3_

- [ ] 13. 构建报告查看页面
  - 创建报告列表页面（历史周报）
  - 创建报告详情页面（展示 HTML 周报）
  - 添加日期筛选和搜索功能
  - _需求: 4.6_

- [ ] 14. 构建仪表板页面
  - 创建资产概览卡片
  - 创建持仓列表表格
  - 创建净值曲线图表
  - _需求: 6.1, 6.2, 6.3_

---

## 📦 后续功能（按需实现）

- [ ] 15. 实现用户认证系统
  - 用户注册和登录
  - JWT token 管理
  - 权限控制
  - _需求: 9.1, 9.3_

- [ ] 16. 实现调仓工作流
  - 调仓建议展示
  - 调仓确认界面
  - 调仓历史记录
  - _需求: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [ ] 17. 实现回测功能
  - 回测计算引擎
  - 回测结果可视化
  - 风险指标计算
  - _需求: 7.1, 7.2, 7.3_

- [ ] 18. 实现用户偏好管理
  - 风险偏好配置
  - 通知设置
  - 调仓频率设置
  - _需求: 1.4, 1.5, 8.1, 8.2, 8.3, 8.4_

---

## 🧪 可选任务

- [ ]* 19. 编写测试
  - 单元测试（服务层）
  - 集成测试（API 接口）
  - 端到端测试
  - _需求: 所有需求_

- [ ]* 20. 性能优化
  - 数据库查询优化
  - API 响应缓存
  - Wind API 调用优化
  - _需求: 6.5, 7.4_

- [ ]* 21. 错误处理和监控
  - 全局错误处理器
  - 日志中间件
  - 性能监控
  - _需求: 所有需求_

- [ ]* 22. 部署和运维
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
- ✅ LLM 生成结构化的周报分析
- ✅ 渲染出美观的 HTML 周报
- ✅ 成功推送到微信
- ✅ 整个流程在 2 分钟内完成
