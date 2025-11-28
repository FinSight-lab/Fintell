# Requirements Document

## Introduction

本系统是一个"省心型"股票持仓智能管家，专注于帮助已有持仓的投资者进行仓位管理、风险监控和调仓建议。系统不做聊天交互、不提供选股服务，而是通过每日风险监控和每周深度分析，以主动推送的方式为用户提供投资决策支持。

核心理念：Push > Chat，让用户省心。

## Glossary

- **System**: 智能持仓管理系统
- **User**: 已有股票持仓的投资者
- **Portfolio**: 用户的股票投资组合
- **Position**: 单只股票的持仓信息（代码、数量、成本价）
- **Daily Report**: 每日盯盘风险提醒报告
- **Weekly Report**: 每周深度投资分析报告
- **Rebalancing Suggestion**: 调仓建议，包含具体操作和理由
- **Wind API**: 万得金融数据接口
- **Technical Indicators**: 技术指标（MA、RSI、MACD、BOLL等）
- **Dashboard**: Web端收益和持仓看板
- **Notification Channel**: 通知渠道（微信、企业微信等）

## Requirements

### Requirement 1: 持仓录入与配置管理

**User Story:** 作为投资者，我希望能够录入和维护我的股票持仓信息，以便系统能够基于我的实际持仓进行分析。

#### Acceptance Criteria

1. WHEN User submits portfolio data, THE System SHALL validate stock codes against Wind API format (XXXXXX.SH or XXXXXX.SZ)
2. THE System SHALL store position quantity, cost price, and total assets for each stock in Portfolio
3. WHEN User updates position information, THE System SHALL recalculate portfolio metrics within 1 second
4. THE System SHALL allow User to configure risk preference (conservative, balanced, or aggressive)
5. WHERE User specifies rebalancing frequency preference, THE System SHALL support weekly, bi-weekly, or monthly intervals

### Requirement 2: 数据采集与技术指标计算

**User Story:** 作为系统管理员，我希望系统能够自动从Wind API获取行情数据并计算技术指标，以便为AI分析提供准确的数据基础。

#### Acceptance Criteria

1. THE System SHALL fetch closing price, volume, PE(TTM), and turnover rate from Wind API for each stock in Portfolio daily
2. THE System SHALL calculate moving averages (MA5, MA10, MA20, MA30, MA250) based on historical closing prices
3. THE System SHALL calculate RSI indicators (RSI6, RSI12, RSI24) with accuracy within 0.01%
4. THE System SHALL calculate MACD indicators (DIF, DEA, MACD) using standard parameters (12, 26, 9)
5. THE System SHALL calculate Bollinger Bands (20-day period, 2 standard deviations)
6. WHEN data fetching fails, THE System SHALL retry up to 3 times with exponential backoff
7. THE System SHALL transform all indicators into structured JSON format for AI consumption

### Requirement 3: 每日风险监控与提醒

**User Story:** 作为投资者，我希望系统每天收盘后自动分析我的持仓风险，并在发现异常时及时提醒我，以便我能够快速响应市场变化。

#### Acceptance Criteria

1. WHEN trading day closes, THE System SHALL trigger daily analysis within 30 minutes after market close (15:30-16:00)
2. THE System SHALL detect if any stock breaks key support levels based on technical indicators
3. IF any stock shows high-volume decline exceeding 5%, THEN THE System SHALL generate risk alert
4. THE System SHALL evaluate each stock's trend status (uptrend, downtrend, or consolidation)
5. THE System SHALL generate Daily Report containing brief evaluation and risk alerts for each position
6. THE System SHALL push Daily Report to User via configured Notification Channel within 5 minutes of generation

### Requirement 4: 每周深度分析与调仓建议

**User Story:** 作为投资者，我希望系统每周生成深度分析报告并提供具体的调仓建议，以便我能够优化持仓配置。

#### Acceptance Criteria

1. THE System SHALL trigger weekly analysis at configured time (default: Friday 16:00)
2. THE System SHALL analyze technical structure (trend, support/resistance) for each stock in Portfolio
3. THE System SHALL evaluate fundamental aspects and valuation for each stock
4. THE System SHALL calculate profit/loss for each position based on current price and cost price
5. THE System SHALL assess portfolio-level risks including concentration and volatility
6. THE System SHALL generate structured Rebalancing Suggestions with specific actions (buy, sell, reduce, hold)
7. WHEN Weekly Report is generated, THE System SHALL push it to User via configured Notification Channel
8. THE System SHALL include reasoning and data support for each Rebalancing Suggestion

### Requirement 5: 调仓确认与执行

**User Story:** 作为投资者，我希望能够在Web界面上查看AI的调仓建议并选择性确认执行，以便我保持对投资决策的最终控制权。

#### Acceptance Criteria

1. THE System SHALL display structured Rebalancing Suggestions in web interface with stock code, action, target weight change, and reasoning
2. WHEN User selects suggestions to execute, THE System SHALL allow User to adjust target positions before confirmation
3. WHEN User confirms rebalancing plan, THE System SHALL record the plan with timestamp and user ID
4. THE System SHALL update Portfolio positions in database based on confirmed rebalancing plan
5. THE System SHALL remind User to execute actual trades in brokerage app after confirmation
6. THE System SHALL NOT execute real trades automatically

### Requirement 6: 收益看板与可视化

**User Story:** 作为投资者，我希望能够在Web看板上直观地查看我的持仓收益、资产分布和历史表现，以便我了解投资组合的整体状况。

#### Acceptance Criteria

1. THE System SHALL display total assets, daily profit/loss, cumulative return, and maximum drawdown on Dashboard
2. THE System SHALL render portfolio net value curve with date range selector
3. THE System SHALL display position list table showing market value, profit/loss, weight, and latest technical signals for each stock
4. THE System SHALL render industry/sector distribution pie chart based on current positions
5. WHEN User selects a time period, THE System SHALL update all charts and metrics within 2 seconds
6. THE System SHALL display position change history based on rebalancing records

### Requirement 7: 回测与策略效果评估

**User Story:** 作为投资者，我希望能够回测AI调仓建议的历史效果，以便我评估系统建议的可靠性并建立信任。

#### Acceptance Criteria

1. THE System SHALL calculate hypothetical returns if User had followed all AI Rebalancing Suggestions
2. THE System SHALL compare AI-suggested portfolio performance against actual portfolio performance
3. THE System SHALL calculate risk metrics including maximum drawdown and Sharpe ratio for both scenarios
4. WHEN User selects a historical time range, THE System SHALL display backtest results within 5 seconds
5. THE System SHALL allow User to filter backtest by rebalancing strategy parameters

### Requirement 8: 通知配置与推送管理

**User Story:** 作为投资者，我希望能够配置通知方式和频率，以便我按照自己的偏好接收分析报告。

#### Acceptance Criteria

1. THE System SHALL support ServerChan (WeChat), Enterprise WeChat, and email as Notification Channels
2. WHEN User configures notification settings, THE System SHALL validate API keys and webhooks before saving
3. THE System SHALL allow User to enable or disable Daily Report and Weekly Report notifications independently
4. WHERE User sets custom notification time, THE System SHALL respect the configured schedule
5. IF notification delivery fails, THEN THE System SHALL retry up to 3 times and log the failure

### Requirement 9: 用户认证与数据隔离

**User Story:** 作为系统管理员，我希望系统能够支持多用户并确保每个用户只能访问自己的持仓数据，以便保护用户隐私和数据安全。

#### Acceptance Criteria

1. THE System SHALL require User authentication via token-based mechanism before accessing any portfolio data
2. THE System SHALL isolate portfolio data by user ID to prevent cross-user data access
3. WHEN User logs in, THE System SHALL generate session token valid for 24 hours
4. THE System SHALL validate user permissions before executing any portfolio modification operations
5. THE System SHALL log all portfolio access and modification operations with user ID and timestamp

### Requirement 10: 系统定时任务管理

**User Story:** 作为系统管理员，我希望系统能够可靠地执行定时任务（数据采集、分析、推送），以便用户能够按时收到报告。

#### Acceptance Criteria

1. THE System SHALL execute daily data fetching task at 15:30 on every trading day
2. THE System SHALL execute daily analysis task at 16:00 on every trading day
3. THE System SHALL execute weekly analysis task at configured time (default: Friday 16:00)
4. WHEN any scheduled task fails, THE System SHALL log error details and send alert to system administrator
5. THE System SHALL provide task execution history and status monitoring interface
6. THE System SHALL skip task execution on non-trading days based on exchange calendar
