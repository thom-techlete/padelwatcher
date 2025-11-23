# API Refactoring Documentation

## Overview

The Flask API has been refactored from a single monolithic `api.py` file into a modular blueprint-based architecture. Each set of related endpoints is now organized into its own blueprint module.

## New Structure

```
backend/app/
├── api.py                 # Main Flask app (simplified, registers blueprints)
├── routes/
│   ├── __init__.py
│   ├── auth.py           # Authentication endpoints
│   ├── locations.py      # Location/Club management
│   ├── search.py         # Court search functionality
│   ├── search_orders.py  # Automated search orders
│   └── admin.py          # Admin operations
├── services.py           # Business logic (unchanged)
├── models.py             # Database models (unchanged)
├── config.py             # Configuration (unchanged)
└── ...
```

## Blueprint Organization

### 1. **Authentication (`routes/auth.py`)**
- **Endpoints**: `/api/auth/*`
- **Functionality**: User registration, login, profile management
- **Key Routes**:
  - `POST /api/auth/register` - Register new user
  - `POST /api/auth/login` - Login and get JWT token
  - `GET /api/auth/me` - Get current user info
  - `PUT /api/auth/profile` - Update user profile
  - `PUT /api/auth/password` - Change password

### 2. **Locations (`routes/locations.py`)**
- **Endpoints**: `/api/locations/*`
- **Functionality**: Manage padel clubs and their courts
- **Key Routes**:
  - `GET /api/locations` - Get all clubs
  - `POST /api/locations` - Add new club by slug
  - `GET /api/locations/<id>/courts` - Get courts for a club
  - `DELETE /api/locations/<id>` - Delete location (admin only)

### 3. **Search (`routes/search.py`)**
- **Endpoints**: `/api/search/*`
- **Functionality**: One-time court availability searches
- **Key Routes**:
  - `POST /api/search/available` - Search for available courts
- **Shared Utility**: `perform_court_search()` - Core search logic used by both search and search orders

### 4. **Search Orders (`routes/search_orders.py`)**
- **Endpoints**: `/api/search-orders/*`
- **Functionality**: Automated recurring searches with notifications
- **Key Routes**:
  - `POST /api/search-orders` - Create search order
  - `GET /api/search-orders` - List user's orders
  - `GET /api/search-orders/<id>` - Get specific order
  - `PUT /api/search-orders/<id>` - Update order
  - `DELETE /api/search-orders/<id>` - Cancel order
  - `POST /api/search-orders/<id>/execute` - Manually execute order

### 5. **Admin (`routes/admin.py`)**
- **Endpoints**: `/api/admin/*`
- **Functionality**: Administrative operations (requires admin role)
- **Key Routes**:
  - `GET /api/admin/users/pending` - List pending approvals
  - `POST /api/admin/users/<id>/approve` - Approve user
  - `DELETE /api/admin/users/<id>/reject` - Reject user
  - `POST /api/admin/users/<id>/activate` - Activate user
  - `POST /api/admin/users/<id>/deactivate` - Deactivate user
  - `GET /api/admin/users` - List all users
  - `POST /api/admin/cache/clear` - Clear search cache
  - `POST /api/admin/refresh-all-data` - Refresh all data
  - `POST /api/admin/test-email` - Test email system
  - `POST /api/admin/availability/fetch` - Fetch availability data

## Key Design Decisions

### 1. **Authentication Decorator**
- Each blueprint imports and uses the `token_required` decorator from `routes/auth.py`
- Enables protected routes while maintaining separation of concerns

### 2. **Admin Authorization**
- `routes/admin.py` includes a `require_admin` decorator
- Stacks with `token_required` for dual-layer protection

### 3. **Service Access**
- Each blueprint has a `get_services()` function
- Lazy imports to avoid circular dependency issues
- Consistent interface across all blueprints

### 4. **Shared Utilities**
- `perform_court_search()` function is duplicated between `search.py` and referenced by `search_orders.py`
- **Better approach**: Could be moved to a shared `routes/utils.py` module (see recommendations)

### 5. **Blueprint Registration**
- All blueprints registered in main `api.py` file
- Clean initialization in one place
- Error handlers and health check remain in main app

## Migration Guide

### For Developers

**Old way (monolithic):**
```python
# All routes in backend/app/api.py
@app.route('/api/auth/login', methods=['POST'])
def login(): ...
```

**New way (modular):**
```python
# In backend/app/routes/auth.py
@auth_bp.route('/login', methods=['POST'])
def login(): ...

# Blueprint URL prefix is defined in the module
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
```

### For Testing

Routes can now be tested by importing individual blueprints:
```python
from app.routes.auth import auth_bp
from app.routes.search import search_bp

# Register in test app
app.register_blueprint(auth_bp)
app.register_blueprint(search_bp)
```

## Recommendations for Further Improvement

### 1. **Extract Shared Search Logic**
Create `routes/utils.py`:
```python
# routes/utils.py
def perform_court_search(...):
    """Centralized search logic"""
    pass
```

Then import and use across blueprints:
```python
from app.routes.utils import perform_court_search
```

### 2. **Create a Decorators Module**
```python
# routes/decorators.py
def token_required(f):
    """Token authentication"""
    pass

def require_admin(f):
    """Admin access requirement"""
    pass

def validate_json(*required_fields):
    """JSON validation"""
    pass
```

### 3. **Response Helper Functions**
```python
# routes/responses.py
def success(data, status_code=200):
    return jsonify({'success': True, 'data': data}), status_code

def error(message, status_code=400):
    return jsonify({'error': message}), status_code
```

### 4. **Service Wrapper**
```python
# routes/services.py
class ServiceLayer:
    """Centralized service access with lazy loading"""
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

## Testing the Refactoring

### Run Syntax Check
```bash
python -m py_compile backend/app/api.py backend/app/routes/*.py
```

### Run the Server
```bash
cd backend
python -m app.api
```

### Test Endpoints
All endpoints remain the same from the client's perspective:
- `POST http://localhost:5000/api/auth/login`
- `GET http://localhost:5000/api/locations`
- `POST http://localhost:5000/api/search/available`
- etc.

## Benefits of This Refactoring

1. ✅ **Modularity** - Each blueprint handles one domain
2. ✅ **Maintainability** - Easier to find and modify related code
3. ✅ **Scalability** - Easy to add new blueprints for new features
4. ✅ **Testability** - Blueprints can be tested independently
5. ✅ **Code Reuse** - Shared utilities and decorators across blueprints
6. ✅ **Separation of Concerns** - Clear boundaries between different features
7. ✅ **Onboarding** - New developers can understand the codebase structure more easily

## Backward Compatibility

✅ **Fully backward compatible** - All API endpoints remain unchanged
- Same URLs
- Same request/response formats
- Same authentication mechanism
- Same error handling

Clients don't need to change anything!

## Files Created

- `/backend/app/routes/__init__.py` - Routes package initialization
- `/backend/app/routes/auth.py` - Authentication blueprint (246 lines)
- `/backend/app/routes/locations.py` - Locations blueprint (73 lines)
- `/backend/app/routes/search.py` - Search blueprint (212 lines)
- `/backend/app/routes/search_orders.py` - Search orders blueprint (305 lines)
- `/backend/app/routes/admin.py` - Admin blueprint (347 lines)

## Files Modified

- `/backend/app/api.py` - Refactored from ~1400 lines to ~200 lines

## Archive

- `/backend/app/api_old.py` - Backup of original monolithic API (for reference)
