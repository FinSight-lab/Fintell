# Project Structure

```
smart-portfolio-manager/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── api/                      # API endpoints (to be implemented)
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── portfolio.py         # Portfolio management endpoints
│   │   ├── reports.py           # Report endpoints
│   │   └── backtest.py          # Backtest endpoints
│   ├── core/                     # Core configuration and utilities
│   │   ├── __init__.py
│   │   ├── config.py            # Application settings
│   │   └── database.py          # Database connection
│   ├── models/                   # SQLAlchemy database models (to be implemented)
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── portfolio.py         # Portfolio and Position models
│   │   ├── report.py            # Report model
│   │   └── cache.py             # Stock data cache model
│   └── services/                 # Business logic services (to be implemented)
│       ├── __init__.py
│       ├── wind_data.py         # Wind API client
│       ├── indicators.py        # Technical indicators calculation
│       ├── llm_client.py        # LLM API client
│       ├── report_service.py    # Report generation
│       ├── notification.py      # Notification service
│       └── portfolio_service.py # Portfolio management
│
├── alembic/                      # Database migrations
│   ├── versions/                 # Migration scripts
│   ├── env.py                    # Alembic environment configuration
│   └── script.py.mako           # Migration template
│
├── templates/                    # Jinja2 HTML templates
│   ├── README.md
│   └── weekly_report.html       # (to be created in task 5.1)
│
├── prompts/                      # LLM prompt templates
│   ├── README.md
│   ├── weekly_report.txt        # (to be created in task 4.2)
│   └── daily_report.txt         # (optional)
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_config.py           # Configuration tests
│   └── ...                      # More tests to be added
│
├── docs/                         # Documentation
│   └── PRD.md                   # Product requirements
│
├── .kiro/                        # Kiro spec files
│   └── specs/
│       └── smart-portfolio-manager/
│           ├── requirements.md   # Requirements document
│           ├── design.md        # Design document
│           └── tasks.md         # Implementation tasks
│
├── .env                          # Environment variables (not in git)
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── alembic.ini                   # Alembic configuration
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # Docker image definition
├── pyproject.toml                # Poetry project configuration
├── requirements.txt              # Python dependencies
├── run.py                        # Development server runner
├── README.md                     # Project documentation
├── QUICKSTART.md                 # Quick start guide
├── PROJECT_STRUCTURE.md          # This file
│
├── stock_position.json           # Legacy: Portfolio data
├── stock_query.py                # Legacy: Technical analysis module
└── vx_notice_push.py            # Legacy: Notification service

```

## Directory Descriptions

### `/app` - Main Application
The core application code organized by responsibility:
- `main.py`: FastAPI app initialization and configuration
- `api/`: REST API endpoints grouped by resource
- `core/`: Configuration, database, and shared utilities
- `models/`: SQLAlchemy ORM models
- `services/`: Business logic and external service integrations

### `/alembic` - Database Migrations
Alembic migration scripts for database schema versioning:
- `versions/`: Individual migration files
- `env.py`: Migration environment setup (configured to use our settings)

### `/templates` - HTML Templates
Jinja2 templates for generating HTML reports:
- Used for email/WeChat notifications
- Styled for mobile viewing

### `/prompts` - LLM Prompts
Text templates for LLM API requests:
- Variables are replaced with actual data before sending
- Structured to produce JSON responses

### `/tests` - Test Suite
Unit and integration tests:
- `test_*.py`: Test modules
- Organized to mirror the app structure

### `/docs` - Documentation
Project documentation and specifications

### `/.kiro` - Kiro Specs
Spec-driven development artifacts:
- Requirements, design, and task tracking

## Key Files

- `.env`: Environment configuration (database, API keys)
- `pyproject.toml`: Python project metadata and dependencies
- `requirements.txt`: Pip-compatible dependency list
- `alembic.ini`: Database migration configuration
- `run.py`: Development server launcher
- `Dockerfile`: Container image definition
- `docker-compose.yml`: Multi-container setup

## Legacy Files

These files are from the original implementation and will be refactored:
- `stock_position.json`: Portfolio data (will migrate to database)
- `stock_query.py`: Technical indicators (will move to `app/services/indicators.py`)
- `vx_notice_push.py`: Notification logic (will move to `app/services/notification.py`)

## Implementation Status

✅ **Completed (Task 1)**:
- Project structure
- Core configuration
- Database setup
- FastAPI application skeleton
- Development environment

🔄 **Next Steps (Task 2)**:
- Database models
- Alembic migrations
- Database session management

📋 **Upcoming**:
- Data collection services
- LLM integration
- Report generation
- API endpoints
- Frontend application
