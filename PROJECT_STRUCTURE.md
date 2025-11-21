# Padel Watcher Project Structure

## Overview

```
padelwatcher/
├── README.md              # Main project documentation
├── DEVELOPMENT.md         # Development guide
├── CONTRIBUTING.md        # Contribution guidelines
├── .gitignore            # Git ignore rules
│
├── backend/              # Backend API and services
│   ├── app/             # Main application code
│   │   ├── __init__.py
│   │   ├── api.py       # Flask REST API endpoints
│   │   ├── models.py    # SQLAlchemy database models
│   │   ├── services.py  # Business logic layer
│   │   ├── config.py    # Configuration management
│   │   └── courtfinder/ # Court provider integrations
│   │       ├── __init__.py
│   │       ├── padelmate.py  # Playtomic API client
│   │       └── playmate.json # Provider configuration
│   │
│   ├── alembic/         # Database migrations
│   │   ├── env.py
│   │   ├── README
│   │   ├── script.py.mako
│   │   └── versions/    # Migration files
│   │
│   ├── tests/           # Test suite
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_comprehensive_time_range.py
│   │   ├── test_search_workflow.py
│   │   └── ...
│   │
│   ├── scripts/         # Utility scripts
│   │   ├── __init__.py
│   │   ├── api_demo.py
│   │   ├── run_api.sh
│   │   └── search_scheduler.py
│   │
│   ├── alembic.ini      # Alembic configuration
│   ├── requirements.txt # Python dependencies
│   ├── .env.example     # Environment variables template
│   └── API_DOCUMENTATION.md
│
├── data/                # Database files (gitignored)
│   └── padel.db        # SQLite database
│
├── web/                 # Frontend (future implementation)
│   └── README.md
│
├── .github/            # GitHub configuration
│   └── copilot-instructions.md
│
└── .venv/              # Python virtual environment (gitignored)
```

## Directory Explanations

### `/backend/app/`
**Main application code**
- `api.py`: Flask REST API with JWT authentication
- `models.py`: SQLAlchemy ORM models and Pydantic DTOs
- `services.py`: Business logic and database operations
- `config.py`: Centralized configuration management
- `courtfinder/`: Provider-specific integrations for fetching court data

### `/backend/alembic/`
**Database migrations**
- Version control for database schema
- Run `alembic upgrade head` to apply migrations
- Run `alembic revision -m "message"` to create new migration

### `/backend/tests/`
**Test suite**
- API endpoint tests
- Integration tests
- Time range functionality tests
- Search workflow tests

### `/backend/scripts/`
**Utility scripts**
- `api_demo.py`: API usage examples
- `run_api.sh`: Convenience script to start API
- `search_scheduler.py`: Background job scheduler

### `/data/`
**Database files**
- SQLite database (not in git)
- Automatically created on first run
- Migrations handle schema changes

### `/web/`
**Frontend application**
- To be implemented
- React/Vue.js planned
- API integration

## File Purposes

| File | Purpose |
|------|---------|
| `README.md` | Main project documentation |
| `DEVELOPMENT.md` | Developer setup and workflow |
| `CONTRIBUTING.md` | Contribution guidelines |
| `.gitignore` | Files to exclude from git |
| `backend/requirements.txt` | Python dependencies |
| `backend/.env.example` | Environment variable template |
| `backend/alembic.ini` | Database migration config |
| `backend/API_DOCUMENTATION.md` | Complete API reference |

## Import Structure

All imports use the `app.` prefix for clarity:

```python
from app.models import Location, Court
from app.services import AvailabilityService
from app.config import SECRET_KEY
```

## Running the Application

From project root:
```bash
# Activate virtual environment
source .venv/bin/activate

# Run API
cd backend
python -m app.api
```

Or use the convenience script:
```bash
./backend/scripts/run_api.sh
```

## Database Location

The database is stored in `data/padel.db` and configured in:
- `backend/app/config.py`: Database path
- `backend/alembic.ini`: Migration database URL

Both point to the same database file in the `data/` directory.
