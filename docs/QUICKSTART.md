# Quick Start Guide

## Prerequisites

- Python 3.10 or higher
- MySQL database (or use the provided connection)
- Git

## Installation

### Option 1: Using existing Python environment

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
# The .env file is already configured with the database and LLM API settings
# Update SERVERCHAN_KEY if you want WeChat notifications
```

3. Initialize database:
```bash
python -m alembic upgrade head
```

4. Run the development server:
```bash
python run.py
```

5. Access the API:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Option 2: Using Poetry

1. Install dependencies:
```bash
poetry install
```

2. Run the development server:
```bash
poetry run python run.py
```

### Option 3: Using Docker

1. Build and run:
```bash
docker-compose up --build
```

2. Access the API at http://localhost:8000

## Verify Installation

Test that everything is working:

```bash
# Test configuration loading
python -c "from app.core.config import settings; print('Config OK')"

# Test FastAPI app
python -c "from app.main import app; print('FastAPI OK')"

# Run tests
pytest tests/
```

## Next Steps

1. Review the project structure in README.md
2. Check the implementation plan in `.kiro/specs/smart-portfolio-manager/tasks.md`
3. Start implementing the next task (Task 2: Database Models)

## Troubleshooting

### Database Connection Issues
- Verify the database credentials in `.env`
- Check network connectivity to `frp3.ccszxc.site:14269`
- Ensure MySQL is running

### Import Errors
- Make sure you're in the project root directory
- Verify all dependencies are installed
- Check Python version (must be 3.10+)

### Port Already in Use
- Change the port in `run.py` or use:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```
