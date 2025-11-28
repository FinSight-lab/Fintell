# Smart Portfolio Manager

智能持仓管理系统 - 一个"省心型"股票持仓智能管家

## 项目简介

本系统专注于帮助已有持仓的投资者进行仓位管理、风险监控和调仓建议。系统通过每日风险监控和每周深度分析，以主动推送的方式为用户提供投资决策支持。

核心理念：**Push > Chat**，让用户省心。

## 功能特性

- 📊 **持仓管理**: 录入和维护股票持仓信息
- 📈 **技术分析**: 自动计算MA、RSI、MACD、布林带等技术指标
- 🤖 **AI分析**: 基于LLM的智能投资分析
- 📱 **每日监控**: 收盘后自动风险提醒
- 📋 **周报生成**: 每周深度分析和调仓建议
- 🔔 **多渠道推送**: 支持微信、企业微信等通知方式
- 📊 **收益看板**: Web端可视化展示
- 🔄 **回测功能**: 评估AI建议的历史效果

## 技术栈

### 后端
- **FastAPI**: 现代化的Python Web框架
- **SQLAlchemy**: ORM数据库操作
- **MySQL**: 数据存储
- **APScheduler**: 定时任务调度
- **Pandas**: 数据处理和技术指标计算
- **Jinja2**: HTML模板渲染

### 前端
- **Next.js 14**: React框架
- **TypeScript**: 类型安全
- **Tailwind CSS**: UI样式
- **Recharts**: 数据可视化

### 外部服务
- **Wind API**: 市场数据源
- **Gemini API**: AI分析引擎
- **ServerChan**: 微信推送

## 项目结构

```
.
├── app/
│   ├── models/          # 数据库模型
│   ├── services/        # 业务逻辑服务
│   ├── api/            # API端点
│   ├── core/           # 核心配置
│   └── main.py         # FastAPI应用入口
├── templates/          # Jinja2模板
├── prompts/           # LLM提示词模板
├── alembic/           # 数据库迁移
├── tests/             # 测试文件
├── .env               # 环境变量配置
├── pyproject.toml     # 项目依赖
└── README.md          # 项目文档
```

## 快速开始

### 环境要求

- Python 3.10+
- MySQL 5.7+
- Poetry (Python包管理工具)

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd smart-portfolio-manager
```

2. 安装依赖
```bash
poetry install
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入数据库和API配置
```

4. 初始化数据库
```bash
poetry run alembic upgrade head
```

5. 启动开发服务器
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. 访问API文档
打开浏览器访问: http://localhost:8000/docs

## 配置说明

### 数据库配置
```env
DB_HOST=frp3.ccszxc.site
DB_PORT=14269
DB_USER=root
DB_PASSWORD=zxc123
DB_NAME=portfolio_db
```

### LLM API配置
```env
LLM_API_URL=http://frp3.ccszxc.site:14266/v1/chat/completions
LLM_API_KEY=zxc123
LLM_MODEL=gemini-3-pro-preview-thinking
```

### ServerChan配置
```env
SERVERCHAN_KEY=your_serverchan_key_here
```

## 开发指南

### 运行测试
```bash
poetry run pytest
```

### 代码格式化
```bash
poetry run black app/
poetry run isort app/
```

### 数据库迁移
```bash
# 创建新迁移
poetry run alembic revision --autogenerate -m "description"

# 应用迁移
poetry run alembic upgrade head

# 回滚迁移
poetry run alembic downgrade -1
```

## 部署

### Docker部署
```bash
docker build -t smart-portfolio-manager .
docker run -p 8000:8000 --env-file .env smart-portfolio-manager
```

### 生产环境配置
- 使用Gunicorn或Uvicorn作为WSGI服务器
- 配置Nginx作为反向代理
- 使用Supervisor或systemd管理进程
- 配置日志轮转和监控

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系项目维护者。
