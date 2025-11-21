# Padel Watcher

A comprehensive padel court availability tracking and notification system. Search for available courts across multiple locations, create automated search orders, and get notified when courts become available.

## Features

- 🎾 **Multi-location Support**: Track availability across multiple padel clubs
- 🔍 **Time Range Search**: Find courts available within flexible time windows
- 🔔 **Search Orders**: Set up automated searches with notifications
- 🏠 **Indoor/Outdoor Filtering**: Search by court type preferences
- 🔐 **Secure API**: JWT-based authentication
- 📊 **Data Persistence**: SQLite database with migrations
- 🌐 **REST API**: Clean, RESTful API design

## Project Structure

```
padelwatcher/
├── backend/                 # Backend API and services
│   ├── app/                # Main application code
│   │   ├── api.py         # Flask API endpoints
│   │   ├── models.py      # Database models
│   │   ├── services.py    # Business logic
│   │   ├── config.py      # Configuration
│   │   └── courtfinder/   # Court finding services
│   ├── alembic/           # Database migrations
│   ├── tests/             # Test files
│   ├── scripts/           # Utility scripts
│   └── requirements.txt   # Python dependencies
├── data/                  # Database files (gitignored)
├── web/                   # Frontend (to be implemented)
├── .github/              # GitHub configuration
└── README.md             # This file
```

## Quick Start

### Prerequisites

- Python 3.12+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd padelwatcher
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration
   ```

5. **Run database migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

6. **Start the API**
   ```bash
   cd backend
   python -m app.api
   ```

The API will be available at `http://localhost:5000`

## Usage

### Authentication

**Default demo account:**
- Email: `demo@example.com`
- Password: `demo123`

**Login to get a JWT token:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@example.com", "password": "demo123"}'
```

### Search for Courts

**Search for available courts in a time range:**
```bash
curl -X POST http://localhost:5000/api/search/available \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-11-16",
    "start_time_range": "18:00",
    "end_time_range": "21:00",
    "duration": 60,
    "indoor": true
  }'
```

### Create Search Order

**Set up automated availability checking:**
```bash
curl -X POST http://localhost:5000/api/search-orders \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-11-16",
    "start_time_range": "18:00",
    "end_time_range": "21:00",
    "duration": 60
  }'
```

### Add Location

**Add a new padel club by slug:**
```bash
curl -X POST http://localhost:5000/api/locations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"slug": "padel-mate-amstelveen"}'
```

## API Documentation

For complete API documentation, see the interactive API demo:

```bash
cd backend
python scripts/api_demo.py
```

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/locations` | Get all locations |
| POST | `/api/locations` | Add new location |
| GET | `/api/locations/{id}/courts` | Get courts for location |
| POST | `/api/search/available` | Search available courts |
| POST | `/api/search-orders` | Create search order |
| GET | `/api/search-orders` | Get user's search orders |
| GET | `/api/search-orders/{id}` | Get search order details |
| DELETE | `/api/search-orders/{id}` | Cancel search order |
| POST | `/api/search-orders/{id}/fetch` | Fetch availability |
| POST | `/api/availability/fetch` | Fetch all availability |

## Development

### Running Tests

```bash
cd backend
python tests/test_api.py
python tests/test_comprehensive_time_range.py
```

### Database Migrations

**Create a new migration:**
```bash
cd backend
alembic revision -m "Description of changes"
```

**Apply migrations:**
```bash
cd backend
alembic upgrade head
```

**Rollback migration:**
```bash
cd backend
alembic downgrade -1
```

### Code Structure

- **`app/api.py`**: Flask application and REST endpoints
- **`app/models.py`**: SQLAlchemy database models
- **`app/services.py`**: Business logic and database operations
- **`app/courtfinder/`**: Court availability fetching services
- **`app/config.py`**: Application configuration

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app.api:app
```

### Environment Variables

Set these in production:

```bash
export SECRET_KEY='your-super-secret-random-key'
export JWT_EXPIRATION_HOURS=24
export FLASK_DEBUG=False
```

### Docker (Optional)

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/
COPY data/ ./data/

WORKDIR /app/backend
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.api:app"]
```

## Security Notes

⚠️ **Important for Production:**

- Change the `SECRET_KEY` to a strong random value
- Use environment variables for sensitive data
- Enable HTTPS
- Implement rate limiting
- Use a production database (PostgreSQL recommended)
- Store users in a proper database (currently in-memory for MVP)
- Add request validation and sanitization
- Implement proper logging and monitoring

## Technology Stack

- **Backend**: Flask, SQLAlchemy, Alembic
- **Database**: SQLite (development), PostgreSQL (recommended for production)
- **Authentication**: JWT (PyJWT)
- **API**: RESTful with CORS support
- **Data Fetching**: httpx, BeautifulSoup
- **Scheduling**: APScheduler (for periodic tasks)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Roadmap

- [ ] Web frontend (React/Vue)
- [ ] Email/SMS notifications
- [ ] PostgreSQL support
- [ ] Rate limiting
- [ ] User management dashboard
- [ ] Multi-provider support (beyond Playtomic)
- [ ] Court booking integration
- [ ] Mobile app (React Native)
- [ ] Advanced filtering (price, court quality, etc.)
- [ ] User preferences and favorites

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review the API demo script

## Acknowledgments

- Built for padel enthusiasts
- Powered by the Playtomic API
- Inspired by the need for better court availability tracking
