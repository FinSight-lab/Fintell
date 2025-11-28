---
inclusion: always
---

# Technology Stack

## Core Technologies

- **Language**: Python 3
- **Data Processing**: pandas, numpy
- **Market Data**: Wind API (wind_linker)
- **Scheduling**: APScheduler (BlockingScheduler)
- **LLM Integration**: Gemini API via OpenAI-compatible endpoint
- **Notifications**: ServerChan (WeChat push service)

## Key Libraries

- `pandas` - Data manipulation and technical indicator calculations
- `numpy` - Numerical operations
- `requests` - HTTP requests for API calls
- `apscheduler` - Cron-based job scheduling
- `wind_linker` - Wind financial data API client

## Environment Variables

Required environment variables:
- `GEMINI_API_KEY` - API key for LLM service
- `SERVER_CHAN_KEY` - ServerChan key for WeChat notifications
- `NO_PROXY='*'` - Proxy bypass configuration

## Common Commands

```bash
# Run stock query analysis
python stock_query.py

# Run portfolio analysis and push notification
python vx_notice_push.py

# Test with specific stocks (modify __main__ section in stock_query.py)
```

## Configuration

Stock positions and costs are managed in `stock_position.json`.
