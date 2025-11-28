# Design Document

## Overview

智能持仓管理系统采用前后端分离架构，后端使用 FastAPI 提供 RESTful API 和定时任务服务，前端使用 Next.js + React 构建响应式 Web 应用。系统通过 Wind API 获取市场数据，利用大语言模型（Gemini）进行智能分析，并通过多种渠道推送通知。

### Architecture Principles

- **关注点分离**: 数据采集、分析引擎、通知推送、Web服务各自独立
- **可扩展性**: 支持新增数据源、分析模型、通知渠道
- **可靠性**: 任务失败重试、数据持久化、错误日志
- **用户控制**: AI提供建议，用户保留最终决策权

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  Next.js + React + Tailwind CSS + Chart.js/Recharts        │
│  (Dashboard, Portfolio Management, Reports, Settings)        │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/REST API
┌────────────────────┴────────────────────────────────────────┐
│                      Backend Layer (FastAPI)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Auth API   │  │Portfolio API │  │ Report API   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                      Service Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Data Collector│  │ AI Analyzer  │  │  Notifier    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Wind API   │  │  Gemini LLM  │  │  ServerChan  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                    Data Layer                                │
│  PostgreSQL (Users, Portfolios, Reports, Rebalancing)       │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI (Python 3.10+)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- APScheduler (Task Scheduling)
- Pydantic (Data Validation)
- httpx (Async HTTP Client)

**Frontend:**
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Recharts / Chart.js (Visualization)
- SWR (Data Fetching)

**External Services:**
- Wind API (Market Data)
- Gemini API (AI Analysis)
- ServerChan / Enterprise WeChat (Notifications)


## Components and Interfaces

### Backend Components

#### 1. Authentication Service

**Responsibilities:**
- User registration and login
- JWT token generation and validation
- Session management

**Key Methods:**
```python
class AuthService:
    def register_user(email: str, password: str) -> User
    def authenticate(email: str, password: str) -> TokenPair
    def refresh_token(refresh_token: str) -> AccessToken
    def validate_token(token: str) -> User
```

#### 2. Portfolio Service

**Responsibilities:**
- CRUD operations for portfolio positions
- Portfolio metrics calculation
- Position validation

**Key Methods:**
```python
class PortfolioService:
    def create_position(user_id: int, position: PositionCreate) -> Position
    def update_position(position_id: int, updates: PositionUpdate) -> Position
    def delete_position(position_id: int) -> bool
    def get_user_portfolio(user_id: int) -> Portfolio
    def calculate_metrics(portfolio: Portfolio) -> PortfolioMetrics
```

#### 3. Data Collector Service

**Responsibilities:**
- Fetch market data from Wind API
- Calculate technical indicators
- Cache and store historical data

**Key Methods:**
```python
class DataCollectorService:
    def fetch_stock_data(stock_codes: List[str], start_date: date, end_date: date) -> DataFrame
    def calculate_indicators(stock_code: str, price_data: DataFrame) -> TechnicalIndicators
    def get_stock_info(stock_codes: List[str]) -> List[StockInfo]
```

**Technical Indicators Structure:**
```python
class TechnicalIndicators(BaseModel):
    stock_code: str
    current_price: float
    volume: float
    pe_ttm: Optional[float]
    turnover: Optional[float]
    ma5: float
    ma10: float
    ma20: float
    ma30: float
    ma250: float
    rsi6: Optional[float]
    rsi12: Optional[float]
    rsi24: Optional[float]
    macd_dif: float
    macd_dea: float
    macd: float
    boll_mid: float
    boll_upper: float
    boll_lower: float
```

#### 4. AI Analyzer Service

**Responsibilities:**
- Generate daily and weekly analysis reports
- Produce structured rebalancing suggestions
- Manage LLM prompts and response parsing

**Key Methods:**
```python
class AIAnalyzerService:
    def generate_daily_report(portfolio: Portfolio, indicators: List[TechnicalIndicators]) -> DailyReport
    def generate_weekly_report(portfolio: Portfolio, indicators: List[TechnicalIndicators]) -> WeeklyReport
    def parse_rebalancing_suggestions(llm_response: str) -> List[RebalancingSuggestion]
```

**Prompt Templates:**
- `daily_report_prompt.txt`: 简短风险提醒模板
- `weekly_report_prompt.txt`: 深度分析模板（已有雏形）

**LLM Response Schema:**
```python
class RebalancingSuggestion(BaseModel):
    stock_code: str
    stock_name: str
    action: Literal["buy", "sell", "reduce", "hold"]
    target_weight_change: float  # percentage
    reasoning: str
    priority: Literal["high", "medium", "low"]

class WeeklyReport(BaseModel):
    report_date: date
    summary: str
    stock_analyses: List[StockAnalysis]
    portfolio_risk_assessment: str
    rebalancing_suggestions: List[RebalancingSuggestion]
    markdown_content: str
```

#### 5. Notification Service

**Responsibilities:**
- Send notifications via multiple channels
- Retry failed notifications
- Track notification history

**Key Methods:**
```python
class NotificationService:
    def send_notification(user_id: int, title: str, content: str, channel: str) -> bool
    def send_daily_report(user_id: int, report: DailyReport) -> bool
    def send_weekly_report(user_id: int, report: WeeklyReport) -> bool
```

**Supported Channels:**
- ServerChan (WeChat)
- Enterprise WeChat Webhook
- Email (future)

#### 6. Rebalancing Service

**Responsibilities:**
- Record rebalancing plans
- Update portfolio based on confirmed plans
- Track execution history

**Key Methods:**
```python
class RebalancingService:
    def create_plan(user_id: int, suggestions: List[RebalancingSuggestion]) -> RebalancingPlan
    def confirm_plan(plan_id: int, adjustments: List[PositionAdjustment]) -> bool
    def execute_plan(plan_id: int) -> ExecutionResult
    def get_history(user_id: int, start_date: date, end_date: date) -> List[RebalancingPlan]
```

#### 7. Backtest Service

**Responsibilities:**
- Calculate hypothetical returns
- Compare AI vs actual performance
- Compute risk metrics

**Key Methods:**
```python
class BacktestService:
    def run_backtest(user_id: int, start_date: date, end_date: date) -> BacktestResult
    def calculate_metrics(returns: Series) -> RiskMetrics
```


### Frontend Components

#### Page Structure

```
app/
├── (auth)/
│   ├── login/
│   └── register/
├── dashboard/
│   ├── page.tsx              # 收益看板主页
│   └── components/
│       ├── AssetSummary.tsx  # 资产概览卡片
│       ├── NetValueChart.tsx # 净值曲线
│       └── PositionTable.tsx # 持仓列表
├── portfolio/
│   ├── page.tsx              # 持仓管理
│   └── components/
│       ├── PositionForm.tsx  # 持仓录入表单
│       └── ImportDialog.tsx  # CSV导入
├── reports/
│   ├── page.tsx              # 报告列表
│   ├── [id]/page.tsx         # 报告详情
│   └── components/
│       ├── ReportCard.tsx
│       └── RebalancingPanel.tsx  # 调仓建议面板
├── backtest/
│   ├── page.tsx              # 回测分析
│   └── components/
│       ├── BacktestChart.tsx
│       └── MetricsTable.tsx
└── settings/
    ├── page.tsx              # 设置页面
    └── components/
        ├── RiskPreference.tsx
        └── NotificationConfig.tsx
```

#### Key React Components

**1. AssetSummary Component**
```typescript
interface AssetSummaryProps {
  totalAssets: number;
  dailyPnL: number;
  cumulativeReturn: number;
  maxDrawdown: number;
}
```

**2. NetValueChart Component**
```typescript
interface NetValueChartProps {
  data: Array<{date: string; value: number}>;
  benchmark?: Array<{date: string; value: number}>;
  dateRange: [Date, Date];
  onDateRangeChange: (range: [Date, Date]) => void;
}
```

**3. PositionTable Component**
```typescript
interface Position {
  stockCode: string;
  stockName: string;
  quantity: number;
  costPrice: number;
  currentPrice: number;
  marketValue: number;
  profitLoss: number;
  profitLossPercent: number;
  weight: number;
  technicalSignal: 'bullish' | 'bearish' | 'neutral';
}
```

**4. RebalancingPanel Component**
```typescript
interface RebalancingSuggestion {
  id: string;
  stockCode: string;
  stockName: string;
  action: 'buy' | 'sell' | 'reduce' | 'hold';
  targetWeightChange: number;
  reasoning: string;
  priority: 'high' | 'medium' | 'low';
  selected: boolean;
  adjustedTarget?: number;
}

interface RebalancingPanelProps {
  suggestions: RebalancingSuggestion[];
  onConfirm: (selected: RebalancingSuggestion[]) => void;
}
```

### API Endpoints

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout

#### Portfolio Management
- `GET /api/portfolio` - Get user portfolio
- `POST /api/portfolio/positions` - Create position
- `PUT /api/portfolio/positions/{id}` - Update position
- `DELETE /api/portfolio/positions/{id}` - Delete position
- `GET /api/portfolio/metrics` - Get portfolio metrics
- `POST /api/portfolio/import` - Import from CSV/JSON

#### Market Data
- `GET /api/market/stocks/{code}` - Get stock info
- `GET /api/market/indicators` - Get technical indicators for portfolio

#### Reports
- `GET /api/reports` - List reports (daily/weekly)
- `GET /api/reports/{id}` - Get report detail
- `POST /api/reports/generate` - Manually trigger report generation

#### Rebalancing
- `GET /api/rebalancing/suggestions` - Get latest suggestions
- `POST /api/rebalancing/plans` - Create rebalancing plan
- `PUT /api/rebalancing/plans/{id}/confirm` - Confirm and execute plan
- `GET /api/rebalancing/history` - Get rebalancing history

#### Backtest
- `POST /api/backtest/run` - Run backtest
- `GET /api/backtest/results/{id}` - Get backtest results

#### Settings
- `GET /api/settings/preferences` - Get user preferences
- `PUT /api/settings/preferences` - Update preferences
- `GET /api/settings/notifications` - Get notification config
- `PUT /api/settings/notifications` - Update notification config


## Data Models

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Portfolios Table
```sql
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    total_assets DECIMAL(15, 2) NOT NULL,
    available_cash DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);
```

#### Positions Table
```sql
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    quantity INTEGER NOT NULL,
    cost_price DECIMAL(10, 4) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(portfolio_id, stock_code)
);
```

#### Stock Data Cache Table
```sql
CREATE TABLE stock_data_cache (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    close_price DECIMAL(10, 4),
    volume BIGINT,
    pe_ttm DECIMAL(10, 4),
    turnover DECIMAL(10, 4),
    indicators JSONB,  -- Store all technical indicators
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, date)
);

CREATE INDEX idx_stock_data_code_date ON stock_data_cache(stock_code, date DESC);
```

#### Reports Table
```sql
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    report_type VARCHAR(20) NOT NULL,  -- 'daily' or 'weekly'
    report_date DATE NOT NULL,
    content JSONB NOT NULL,  -- Structured report data
    markdown_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_user_date ON reports(user_id, report_date DESC);
```

#### Rebalancing Plans Table
```sql
CREATE TABLE rebalancing_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    report_id INTEGER REFERENCES reports(id),
    status VARCHAR(20) NOT NULL,  -- 'pending', 'confirmed', 'executed'
    suggestions JSONB NOT NULL,
    confirmed_adjustments JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP,
    executed_at TIMESTAMP
);
```

#### User Preferences Table
```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    risk_preference VARCHAR(20) DEFAULT 'balanced',  -- 'conservative', 'balanced', 'aggressive'
    rebalancing_frequency VARCHAR(20) DEFAULT 'weekly',  -- 'weekly', 'biweekly', 'monthly'
    max_position_weight DECIMAL(5, 2) DEFAULT 30.00,
    notification_channels JSONB,  -- {serverchan_key, wechat_webhook, email}
    daily_report_enabled BOOLEAN DEFAULT TRUE,
    weekly_report_enabled BOOLEAN DEFAULT TRUE,
    notification_time TIME DEFAULT '16:00:00',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);
```

#### Notification Log Table
```sql
CREATE TABLE notification_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    content TEXT,
    status VARCHAR(20) NOT NULL,  -- 'sent', 'failed', 'retrying'
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Pydantic Models (API Schemas)

```python
# Request/Response Models
class PositionCreate(BaseModel):
    stock_code: str = Field(..., regex=r'^\d{6}\.(SH|SZ|sh|sz)$')
    quantity: int = Field(..., gt=0)
    cost_price: float = Field(..., gt=0)

class PositionUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, gt=0)

class PositionResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: str
    quantity: int
    cost_price: float
    current_price: float
    market_value: float
    profit_loss: float
    profit_loss_percent: float
    weight: float

class PortfolioMetrics(BaseModel):
    total_assets: float
    total_market_value: float
    available_cash: float
    daily_pnl: float
    cumulative_return: float
    position_count: int

class RebalancingSuggestionResponse(BaseModel):
    id: str
    stock_code: str
    stock_name: str
    action: Literal["buy", "sell", "reduce", "hold"]
    current_weight: float
    target_weight: float
    target_weight_change: float
    reasoning: str
    priority: Literal["high", "medium", "low"]

class RebalancingPlanCreate(BaseModel):
    suggestions: List[RebalancingSuggestionResponse]
    adjustments: Optional[List[Dict[str, Any]]]

class UserPreferencesUpdate(BaseModel):
    risk_preference: Optional[Literal["conservative", "balanced", "aggressive"]]
    rebalancing_frequency: Optional[Literal["weekly", "biweekly", "monthly"]]
    max_position_weight: Optional[float] = Field(None, ge=0, le=100)
    daily_report_enabled: Optional[bool]
    weekly_report_enabled: Optional[bool]
    notification_time: Optional[str]
```


## Error Handling

### Error Categories

1. **Client Errors (4xx)**
   - 400 Bad Request: Invalid input data
   - 401 Unauthorized: Missing or invalid token
   - 403 Forbidden: Insufficient permissions
   - 404 Not Found: Resource not found
   - 409 Conflict: Duplicate resource

2. **Server Errors (5xx)**
   - 500 Internal Server Error: Unexpected server error
   - 502 Bad Gateway: External service failure
   - 503 Service Unavailable: Temporary service outage

### Error Response Format

```python
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]]
    timestamp: datetime

# Example
{
    "error_code": "INVALID_STOCK_CODE",
    "message": "Stock code format is invalid. Expected format: XXXXXX.SH or XXXXXX.SZ",
    "details": {
        "provided_code": "60051",
        "expected_format": "XXXXXX.SH or XXXXXX.SZ"
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Retry Strategy

**Wind API Failures:**
- Retry up to 3 times with exponential backoff (1s, 2s, 4s)
- If all retries fail, use cached data if available
- Log failure and alert system admin

**LLM API Failures:**
- Retry up to 2 times with 5-second delay
- If fails, skip report generation and notify user
- Queue for manual retry

**Notification Failures:**
- Retry up to 3 times with 30-second intervals
- Log failure in notification_log table
- Display failed notifications in user dashboard

### Logging Strategy

```python
# Log Levels
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Warning messages (e.g., using cached data)
- ERROR: Error messages (e.g., API failure after retries)
- CRITICAL: Critical issues requiring immediate attention

# Log Format
{
    "timestamp": "2024-01-15T10:30:00Z",
    "level": "ERROR",
    "service": "DataCollectorService",
    "method": "fetch_stock_data",
    "user_id": 123,
    "message": "Wind API request failed after 3 retries",
    "error": "ConnectionTimeout",
    "stack_trace": "..."
}
```

## Testing Strategy

### Unit Tests

**Backend:**
- Test each service method independently
- Mock external dependencies (Wind API, LLM API)
- Test data validation and business logic
- Target: 80%+ code coverage

**Frontend:**
- Test React components with React Testing Library
- Test hooks and utility functions
- Mock API calls with MSW (Mock Service Worker)

### Integration Tests

- Test API endpoints with test database
- Test scheduled tasks execution
- Test notification delivery flow
- Test authentication and authorization

### End-to-End Tests

- Test complete user workflows:
  - User registration → Portfolio setup → Report generation → Rebalancing
- Use Playwright or Cypress for frontend E2E tests
- Test critical paths only

### Performance Tests

- Load test API endpoints (target: <200ms response time for 95th percentile)
- Test concurrent user scenarios
- Test data fetching for large portfolios (100+ positions)

### Test Data

```python
# Sample test portfolio
TEST_PORTFOLIO = {
    "user_id": 1,
    "positions": [
        {"stock_code": "600519.SH", "quantity": 100, "cost_price": 1458.96},
        {"stock_code": "000651.SZ", "quantity": 4000, "cost_price": 40.75},
    ],
    "total_assets": 422157.20
}

# Mock Wind API response
MOCK_WIND_RESPONSE = {
    "Fields": ["CLOSE", "VOLUME", "PE_TTM", "TURN"],
    "Data": [[1500.0, 1000000, 35.5, 0.8]],
    "Times": ["2024-01-15"]
}
```


## Scheduled Tasks Design

### Task Scheduler Architecture

Using APScheduler with PostgreSQL job store for persistence and distributed execution support.

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

jobstores = {
    'default': SQLAlchemyJobStore(url='postgresql://...')
}

scheduler = AsyncIOScheduler(jobstores=jobstores)
```

### Task Definitions

#### 1. Daily Data Collection Task

**Schedule:** Every trading day at 15:30 (after market close)
**Duration:** ~5-10 minutes
**Steps:**
1. Fetch list of all unique stock codes from active portfolios
2. Call Wind API to get latest market data
3. Calculate technical indicators
4. Store in stock_data_cache table
5. Update cache timestamp

```python
@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=15, minute=30)
async def daily_data_collection():
    stock_codes = await get_all_active_stocks()
    for code in stock_codes:
        try:
            data = await wind_service.fetch_stock_data(code)
            indicators = calculate_indicators(data)
            await cache_service.store(code, indicators)
        except Exception as e:
            logger.error(f"Failed to fetch data for {code}: {e}")
```

#### 2. Daily Report Generation Task

**Schedule:** Every trading day at 16:00
**Duration:** ~10-15 minutes
**Steps:**
1. For each user with daily_report_enabled=True
2. Fetch user portfolio and latest indicators
3. Call AI analyzer to generate daily report
4. Store report in database
5. Send notification via configured channels

```python
@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=16, minute=0)
async def daily_report_generation():
    users = await get_users_with_daily_report_enabled()
    for user in users:
        try:
            portfolio = await portfolio_service.get_user_portfolio(user.id)
            indicators = await data_service.get_latest_indicators(portfolio.stock_codes)
            report = await ai_service.generate_daily_report(portfolio, indicators)
            await report_service.save(report)
            await notification_service.send_daily_report(user.id, report)
        except Exception as e:
            logger.error(f"Failed to generate daily report for user {user.id}: {e}")
```

#### 3. Weekly Report Generation Task

**Schedule:** Configurable per user (default: Friday 16:00)
**Duration:** ~15-20 minutes per user
**Steps:**
1. For each user based on their notification_time preference
2. Fetch user portfolio, preferences, and 90-day indicators
3. Call AI analyzer to generate comprehensive weekly report
4. Parse rebalancing suggestions from LLM response
5. Store report and suggestions in database
6. Send notification with report link

```python
@scheduler.scheduled_job('cron', day_of_week='fri', hour=16, minute=0)
async def weekly_report_generation():
    users = await get_users_with_weekly_report_enabled()
    for user in users:
        try:
            portfolio = await portfolio_service.get_user_portfolio(user.id)
            preferences = await settings_service.get_preferences(user.id)
            indicators = await data_service.get_indicators_90d(portfolio.stock_codes)
            
            report = await ai_service.generate_weekly_report(
                portfolio, indicators, preferences
            )
            suggestions = await ai_service.parse_rebalancing_suggestions(report)
            
            await report_service.save(report)
            await rebalancing_service.create_plan(user.id, report.id, suggestions)
            await notification_service.send_weekly_report(user.id, report)
        except Exception as e:
            logger.error(f"Failed to generate weekly report for user {user.id}: {e}")
```

#### 4. Data Cleanup Task

**Schedule:** Every Sunday at 02:00
**Duration:** ~5 minutes
**Steps:**
1. Delete stock_data_cache older than 1 year
2. Archive old reports (older than 6 months)
3. Clean up notification_log (older than 3 months)

```python
@scheduler.scheduled_job('cron', day_of_week='sun', hour=2, minute=0)
async def data_cleanup():
    cutoff_date = datetime.now() - timedelta(days=365)
    await db.execute(
        "DELETE FROM stock_data_cache WHERE date < :cutoff",
        {"cutoff": cutoff_date}
    )
    # Archive and cleanup logic...
```

### Task Monitoring

- Store task execution logs in dedicated table
- Track success/failure rates
- Alert on consecutive failures (3+ times)
- Provide admin dashboard for task status

```sql
CREATE TABLE task_execution_log (
    id SERIAL PRIMARY KEY,
    task_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    error_message TEXT,
    metadata JSONB
);
```

## Security Considerations

### Authentication & Authorization

- Use JWT tokens with 24-hour expiration
- Refresh tokens valid for 30 days
- Store password hashes using bcrypt (cost factor: 12)
- Implement rate limiting on auth endpoints (5 attempts per minute)

### Data Protection

- Encrypt sensitive data at rest (API keys, tokens)
- Use HTTPS for all API communications
- Implement CORS with whitelist of allowed origins
- Sanitize all user inputs to prevent SQL injection

### API Security

- Require authentication for all portfolio/report endpoints
- Validate user ownership before returning data
- Implement request rate limiting (100 requests per minute per user)
- Log all data modification operations with user ID

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:pass@localhost/portfolio_db
JWT_SECRET_KEY=<random-256-bit-key>
WIND_API_KEY=<wind-api-key>
GEMINI_API_KEY=<gemini-api-key>

# Optional
SERVERCHAN_KEY=<serverchan-key>
WECHAT_WEBHOOK=<wechat-webhook-url>
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

## Deployment Architecture

### Development Environment
- Docker Compose with PostgreSQL, Redis, and FastAPI
- Hot reload enabled for rapid development
- Mock external APIs for testing

### Production Environment
- Backend: Docker containers on cloud VM (Aliyun/AWS)
- Frontend: Vercel or Netlify for Next.js deployment
- Database: Managed PostgreSQL (RDS)
- Caching: Redis for session and data caching
- Monitoring: Prometheus + Grafana for metrics
- Logging: ELK stack or cloud logging service

### CI/CD Pipeline
1. Code push to GitHub
2. Run tests (unit + integration)
3. Build Docker images
4. Deploy to staging environment
5. Run E2E tests
6. Manual approval for production deployment
7. Deploy to production with zero-downtime rolling update

