# Development Guide

## Setup

1. **Clone and setup environment**
   ```bash
   git clone <repo-url>
   cd padelwatcher
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your settings
   ```

3. **Initialize database**
   ```bash
   cd backend
   alembic upgrade head
   ```

## Running the Application

### Development Mode

```bash
cd backend
python -m app.api
```

The API runs on `http://localhost:5000` by default.

### Production Mode

```bash
pip install gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app.api:app
```

## Testing

Run all tests:
```bash
cd backend
python tests/test_api.py
python tests/test_comprehensive_time_range.py
python tests/test_search_workflow.py
```

## Database Migrations

### Create a migration
```bash
cd backend
alembic revision --autogenerate -m "Description"
```

### Apply migrations
```bash
cd backend
alembic upgrade head
```

### Rollback
```bash
cd backend
alembic downgrade -1
```

## Project Structure Explained

```
padelwatcher/
├── backend/
│   ├── app/                    # Application code
│   │   ├── api.py             # Flask REST API
│   │   ├── models.py          # Database models
│   │   ├── services.py        # Business logic
│   │   ├── config.py          # Configuration
│   │   └── courtfinder/       # Court scraping/API
│   │       └── padelmate.py   # Playtomic integration
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Test files
│   ├── scripts/               # Utility scripts
│   └── requirements.txt       # Dependencies
├── data/                      # Database files (gitignored)
├── web/                       # Frontend (future)
└── README.md                  # Main documentation
```

## Code Organization

### Models (`app/models.py`)
- SQLAlchemy ORM models
- Pydantic DTOs for validation
- Database schema definitions

### Services (`app/services.py`)
- `AvailabilityService`: Database operations
- Business logic layer
- No direct HTTP handling

### API (`app/api.py`)
- Flask REST endpoints
- JWT authentication
- Request/response handling
- Delegates to services

### Court Finder (`app/courtfinder/`)
- Provider-specific integrations
- `PadelMateService`: Playtomic API client
- Scraping and data normalization

## Adding a New Feature

1. **Update models** if needed (`app/models.py`)
2. **Create migration** (`alembic revision`)
3. **Add service methods** (`app/services.py`)
4. **Create API endpoint** (`app/api.py`)
5. **Write tests** (`tests/`)
6. **Update documentation**

## Common Tasks

### Add a new endpoint
```python
@app.route('/api/new-endpoint', methods=['POST'])
@token_required
def new_endpoint(current_user):
    data = request.get_json()
    # Process data
    return jsonify({'result': 'success'}), 200
```

### Add a new service method
```python
def new_service_method(self, param):
    result = self.session.query(Model).filter(...).all()
    return result
```

### Add a new model
```python
class NewModel(Base):
    __tablename__ = 'new_table'
    id = Column(Integer, primary_key=True)
    # Add fields
```

Then create and run migration:
```bash
alembic revision --autogenerate -m "Add new_table"
alembic upgrade head
```

## User Management

### User Approval System

All user accounts require admin approval before they can access the API:

1. **User Registration**: Users register but remain unapproved
2. **Admin Approval**: Admins review and approve/reject accounts
3. **Access Granted**: Only approved users can login and use the API

### Creating Admin Users

To create an admin user, run the initialization script:

```bash
cd backend
python scripts/create_admin.py
```

This creates an admin account: `admin@padelwatcher.com` / `admin123`

### Admin Endpoints

- `GET /api/admin/users/pending` - View users awaiting approval
- `POST /api/admin/users/{user_id}/approve` - Approve a user
- `DELETE /api/admin/users/{user_id}/reject` - Reject a user
- `GET /api/admin/users` - View all users

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key | `dev-secret-key...` |
| `JWT_EXPIRATION_HOURS` | Token expiration | `24` |
| `FLASK_DEBUG` | Debug mode | `True` |
| `FLASK_HOST` | Server host | `0.0.0.0` |
| `FLASK_PORT` | Server port | `5000` |

## Best Practices

1. **Always use migrations** for schema changes
2. **Keep services separate** from API layer
3. **Use DTOs** for validation
4. **Write tests** for new features
5. **Document API endpoints** in docstrings
6. **Use environment variables** for config
7. **Follow RESTful conventions**
8. **Handle errors gracefully**

## Debugging

### Enable debug mode
```bash
export FLASK_DEBUG=True
python -m app.api
```

### Check database state
```bash
cd backend
alembic current
alembic history
```

### View logs
The Flask development server prints logs to stdout.

For production with gunicorn:
```bash
gunicorn --access-logfile - --error-logfile - app.api:app
```

## Performance Tips

1. Use connection pooling for database
2. Add indexes for frequently queried fields
3. Cache frequently accessed data
4. Use background tasks for heavy operations
5. Implement pagination for large result sets

## Security Checklist

- [x] User approval system implemented
- [ ] Change SECRET_KEY in production
- [ ] Change admin password in production
- [ ] Use HTTPS
- [ ] Implement rate limiting
- [ ] Validate all inputs
- [ ] Sanitize user data
- [ ] Use parameterized queries (already done via SQLAlchemy)
- [ ] Keep dependencies updated
- [ ] Don't commit secrets to git
- [ ] Use environment variables
- [ ] Implement proper logging
- [ ] Add request validation
