---
inclusion: always
---

# Project Structure

## File Organization

```
.
├── stock_position.json      # Portfolio configuration (positions, costs, assets)
├── stock_query.py           # Technical indicator calculation module
└── vx_notice_push.py        # Main scheduler and notification service
```

## Module Responsibilities

### stock_query.py
Core technical analysis module providing:
- `wind_to_df()` - Convert Wind API responses to pandas DataFrames
- `calc_ma()` - Moving averages (5, 10, 20, 30, 250 days)
- `calc_rsi()` - Relative Strength Index (6, 12, 24 periods)
- `calc_macd()` - MACD indicator (DIF, DEA, MACD)
- `calc_boll()` - Bollinger Bands (20-day, 2 std dev)
- `get_stock_recent_info()` - Main function to fetch and calculate all indicators

### vx_notice_push.py
Orchestration and notification service:
- `load_config()` - Load portfolio from JSON
- `sanitize_dataframe()` - Clean data for JSON serialization
- `analyze_portfolio()` - Generate AI analysis report
- `push_wechat()` - Send notifications via ServerChan
- Scheduled execution (commented out, runs on-demand)

### stock_position.json
Portfolio data structure:
- `stocks` - List of stock codes (Shanghai/Shenzhen exchanges)
- `positions` - Share quantities per stock
- `cost_prices` - Average cost basis per stock
- `total_assets` - Total portfolio value

## Code Conventions

- Stock codes use Wind format: `XXXXXX.SH` (Shanghai) or `XXXXXX.SZ` (Shenzhen)
- Stock codes are case-insensitive in the JSON config
- Date ranges default to 90 days for technical analysis
- All monetary values in CNY
- Pandas display options configured for full output in main execution
