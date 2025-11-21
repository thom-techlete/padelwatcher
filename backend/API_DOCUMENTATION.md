# Padel Watcher API

Flask-based REST API for the Padel Court Availability Search Service.

## Quick Start

### Installation

```bash
# Install API dependencies
pip install -r requirements-api.txt
```

### Running the API

```bash
# Development mode
python api.py

# Production mode (use gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

The API will be available at `http://localhost:5000`

### Environment Variables

Create a `.env` file:

```bash
SECRET_KEY=your-secret-key-here
JWT_EXPIRATION_HOURS=24
```

## Authentication

**NEW: User Approval System**

All user accounts require admin approval before they can access the API. The approval workflow is:

1. User registers → Account created but marked as unapproved
2. Admin reviews pending users → Approves or rejects accounts
3. Approved users can login and access the API

### Register a New User

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'
```

Response:
```json
{
  "message": "User registered successfully. Please wait for admin approval.",
  "user_id": "user_example"
}
```

### Login

**Only approved users can login successfully.**

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'
```

Response (for approved users):
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": "user_example",
  "is_admin": false,
  "expires_in": 86400
}
```

Response (for unapproved users):
```json
{
  "message": "Invalid credentials or account not approved"
}
```

### Using the Token

Include the token in the Authorization header:

```bash
curl -X GET http://localhost:5000/api/locations \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Admin Endpoints

**Admin access required for all admin endpoints.**

#### Get Pending Users

```bash
curl -X GET http://localhost:5000/api/admin/users/pending \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### Approve User

```bash
curl -X POST http://localhost:5000/api/admin/users/{user_id}/approve \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### Reject User

```bash
curl -X DELETE http://localhost:5000/api/admin/users/{user_id}/reject \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### Get All Users

```bash
curl -X GET http://localhost:5000/api/admin/users \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## API Endpoints

### Health Check

**GET** `/health`
- Public endpoint
- Returns API status

### Locations

**GET** `/api/locations`
- Get all available locations/clubs
- Requires authentication

**POST** `/api/locations`
- Add a new location by slug
- Requires authentication
- Body: `{"slug": "club-slug", "date": "2025-11-16"}`

**GET** `/api/locations/{location_id}/courts`
- Get all courts for a specific location
- Requires authentication

### Search

**POST** `/api/search/available`
- Search for available courts within a time range
- Requires authentication
- Body:
```json
{
  "date": "2025-11-16",
  "start_time_range": "18:00",
  "end_time_range": "21:00",
  "duration": 60,
  "indoor": true
}
```

### Search Orders

**POST** `/api/search-orders`
- Create a new search order for automated availability checking
- Requires authentication
- Body:
```json
{
  "date": "2025-11-16",
  "start_time_range": "18:00",
  "end_time_range": "21:00",
  "duration": 60,
  "indoor": null
}
```

**GET** `/api/search-orders`
- Get all search orders for the current user
- Requires authentication

**GET** `/api/search-orders/{order_id}`
- Get results for a specific search order
- Requires authentication

**DELETE** `/api/search-orders/{order_id}`
- Cancel a search order
- Requires authentication

**POST** `/api/search-orders/{order_id}/fetch`
- Manually trigger availability fetch for a search order
- Requires authentication

### Availability

**POST** `/api/availability/fetch`
- Fetch and store availability for all locations
- Requires authentication
- Body: `{"date": "2025-11-16", "sport_id": "PADEL"}`

## Example Usage

### Complete Workflow

```bash
# 1. Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'

# 2. Login
TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}' \
  | jq -r '.token')

# 3. Add a location
curl -X POST http://localhost:5000/api/locations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"slug": "padel-mate-amstelveen"}'

# 4. Search for available courts
curl -X POST http://localhost:5000/api/search/available \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-11-16",
    "start_time_range": "18:00",
    "end_time_range": "21:00",
    "duration": 60,
    "indoor": true
  }'

# 5. Create a search order
ORDER_ID=$(curl -X POST http://localhost:5000/api/search-orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-11-16",
    "start_time_range": "18:00",
    "end_time_range": "21:00",
    "duration": 60
  }' | jq -r '.search_order_id')

# 6. Fetch availability for search order
curl -X POST http://localhost:5000/api/search-orders/$ORDER_ID/fetch \
  -H "Authorization: Bearer $TOKEN"

# 7. Get search order results
curl -X GET http://localhost:5000/api/search-orders/$ORDER_ID \
  -H "Authorization: Bearer $TOKEN"
```

## Security Notes

⚠️ **For MVP/Development Only**

- Users are stored in memory (lost on restart)
- Change `SECRET_KEY` in production
- Use environment variables for sensitive data
- For production:
  - Use a proper database for user storage
  - Add rate limiting
  - Use HTTPS
  - Add request validation
  - Implement proper logging
  - Add monitoring

## Production Deployment

```bash
# Install production dependencies
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --error-logfile - api:app
```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements-api.txt ./
RUN pip install -r requirements.txt -r requirements-api.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api:app"]
```

## Default Admin Credentials

For testing and administration, a default admin account is available:

- **Email**: `admin@padelwatcher.com`
- **Password**: `admin123`
- **User ID**: `admin`

⚠️ **Change the admin password in production!**

## Security Notes

## Error Responses

All errors follow this format:

```json
{
  "message": "Error description"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `500` - Internal Server Error
