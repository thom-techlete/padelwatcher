# Copilot Instructions - Padel Watcher

Padel Watcher is a comprehensive padel court availability tracking and notification system. The project has evolved from basic data collection to a full-stack application with API, database, and user management.

## Current Architecture

### Backend (Flask + SQLAlchemy)
- **API**: RESTful Flask API with JWT authentication (`backend/app/api.py`)
- **Database**: SQLite with SQLAlchemy ORM and Alembic migrations
- **Models**: User management, locations, courts, availability, search orders (`backend/app/models.py`)
- **Services**: Business logic layer (`backend/app/services.py`)
- **Providers**: Court data fetching from Playtomic API (`backend/app/courtfinder/`)

### Frontend (Planned)
- React/Vue.js application in `/web/` directory
- API integration with backend
- User dashboard for search orders and notifications

## Current Features

✅ **User Management**: Registration, login, JWT authentication
✅ **Location Management**: Add padel clubs by slug, automatic court discovery
✅ **Availability Tracking**: Fetch and store court availability data
✅ **Time Range Search**: Find courts available within flexible time windows
✅ **Search Orders**: Automated availability checking with notifications
✅ **REST API**: Complete API with proper error handling and validation
✅ **Database**: Normalized schema with migrations
✅ **Testing**: Comprehensive test suite

## Development Guidelines

**Frontend Development**: When working on frontend/UI/UX code (anything in the `web/` directory), always read and follow the guidelines in `.github/instructions/frontend.instructions.md` first.

### Code Organization
- **Backend code** in `backend/app/`
- **Tests** in `backend/tests/`
- **Scripts** in `backend/scripts/`
- **Database files** in `data/` (gitignored)
- **Frontend** in `web/` (future)

### Import Structure
Use `app.` prefix for all backend imports:
```python
from app.models import Location, Court
from app.services import AvailabilityService
from app.config import SECRET_KEY
```

### Database Operations
- Use SQLAlchemy ORM for all database operations
- Create migrations with `alembic revision --autogenerate`
- Apply with `alembic upgrade head`

### API Design
- RESTful endpoints with proper HTTP methods
- JWT authentication required for protected routes
- Consistent error responses
- Input validation with Pydantic DTOs

## Current Development Focus

### High Priority
- **Web Frontend**: React/Vue.js dashboard for users
- **Notification Service**: Email/SMS notifications for search orders
- **Additional Providers**: Support for more court booking platforms
- **Production Deployment**: Docker, PostgreSQL, monitoring

### Medium Priority
- **Advanced Filtering**: Price ranges, court quality, amenities
- **User Preferences**: Favorite locations, default search settings
- **Analytics**: Usage statistics, popular times/locations
- **Mobile App**: React Native companion app

### Technical Debt
- **Database Migration**: PostgreSQL for production
- **Caching**: Redis for performance
- **Rate Limiting**: API protection
- **Logging**: Structured logging and monitoring

## Coding Standards

### Python Best Practices
- Follow PEP 8 style guide
- Use type hints where appropriate
- Write comprehensive docstrings
- Keep functions focused and testable
- Use meaningful variable names

### API Standards
- RESTful resource naming
- Proper HTTP status codes
- Consistent JSON response format
- Input validation and sanitization
- Comprehensive error messages

### Testing
- Unit tests for services
- Integration tests for API endpoints
- Test database operations
- Mock external API calls

## File Structure Reference

```
padelwatcher/
├── backend/
│   ├── app/                    # Core application
│   │   ├── api.py             # Flask REST API
│   │   ├── models.py          # Database models
│   │   ├── services.py        # Business logic
│   │   ├── config.py          # Configuration
│   │   └── courtfinder/       # Provider integrations
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Test suite
│   ├── scripts/               # Utilities
│   └── requirements.txt       # Dependencies
├── data/                      # Database files
├── web/                       # Frontend (planned)
├── README.md                  # Main documentation
├── DEVELOPMENT.md             # Development guide
└── CONTRIBUTING.md            # Contribution guidelines
```

## Quick Commands

```bash
# Run API
cd backend && python -m app.api

# Run tests
cd backend && python tests/test_api.py

# Create migration
cd backend && alembic revision --autogenerate -m "message"

# Apply migrations
cd backend && alembic upgrade head
```

**Note**: When making backend code changes, there's no need to kill, restart, or start the API. The Flask development server auto-reloads when code changes are detected. If the API is not running, ask the user to start it with `cd backend && python -m app.api`.

## Security Notes

- JWT tokens for authentication
- Password hashing with Werkzeug
- Input validation and sanitization
- Environment variables for secrets
- No secrets in code or git

## Future Goals

1. **Complete Web Frontend**: User-friendly dashboard
2. **Notification System**: Real-time alerts for court availability
3. **Multi-Provider Support**: Integration with multiple booking platforms
4. **Production Deployment**: Scalable infrastructure
5. **Mobile Applications**: iOS/Android apps
6. **Advanced Features**: Court booking, user communities, tournaments

This project has grown from a simple data collection script to a full-featured court availability platform. Focus on maintainable, scalable code that can support future growth.
