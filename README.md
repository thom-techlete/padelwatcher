# Padel Watcher

A comprehensive padel court availability tracking and notification system. Search for available courts across multiple locations, create automated search orders, and get notified when courts become available.

## Features

- 🎾 **Multi-location Support**: Track availability across multiple padel clubs
- 🔍 **Time Range Search**: Find courts available within flexible time windows
- 🔔 **Search Orders**: Set up automated searches with notifications
- 🏠 **Indoor/Outdoor Filtering**: Search by court type preferences
- 🔐 **Secure API**: JWT-based authentication with user management
- 📊 **Data Persistence**: PostgreSQL database with migrations
- 🌐 **REST API**: Clean, RESTful API design
- 📧 **Email Notifications**: Automated alerts when courts are found
- 🐳 **Docker Ready**: Production-ready Docker configuration
- 🚀 **Production Ready**: Complete deployment infrastructure

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
## 🚀 Production Deployment

### Docker Deployment (Recommended)

The easiest way to deploy Padel Watcher is using Docker:

1. **Clone and Configure**
   ```bash
   git clone https://github.com/thom-techlete/padelwatcher.git
   cd padelwatcher
   cp .env.example .env
   # Edit .env with your production values
   ```

2. **Deploy**
   ```bash
   ./scripts/deploy.sh
   ```

3. **Create Admin User**
   ```bash
   docker-compose exec backend python scripts/create_admin.py
   ```

**📚 Complete deployment guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)

**✅ Deployment checklist**: See [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)

**⚡ Quick reference**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### What's Included

- ✅ PostgreSQL database with automated backups
- ✅ Production-optimized Flask backend with Gunicorn
- ✅ React frontend with Nginx
- ✅ Nginx reverse proxy with SSL/TLS support
- ✅ Docker Compose orchestration
- ✅ Health checks and monitoring
- ✅ Security hardening
- ✅ Automated deployment scripts

## Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/thom-techlete/padelwatcher.git
   cd padelwatcher
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   alembic upgrade head
   python -m app.api
   ```

3. **Frontend Setup**
   ```bash
   cd web
   npm install
   npm run dev
   ```

## Technology Stack

- **Backend**: Flask, SQLAlchemy, Alembic, Gunicorn
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: JWT (PyJWT)
- **API**: RESTful with CORS support
- **Frontend**: React, TypeScript, TanStack Router, TanStack Query
- **Styling**: Tailwind CSS
- **Data Fetching**: httpx, BeautifulSoup
- **Scheduling**: APScheduler (background tasks)
- **Email**: Gmail SMTP
- **Deployment**: Docker, Docker Compose, Nginx

## Security

This project implements security best practices:
- JWT authentication
- Password hashing (Werkzeug/PBKDF2)
- Rate limiting
- CORS protection
- SQL injection protection (SQLAlchemy ORM)
- Security headers
- Non-root container users
- Environment variable configuration

See [SECURITY.md](SECURITY.md) for details.

## Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete production deployment guide
- **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)** - Pre-deployment checklist
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Common commands and operations
- **[SECURITY.md](SECURITY.md)** - Security policy and best practices
- **[backend/API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md)** - API reference
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Roadmap

### ✅ Completed (MVP)
- [x] Web frontend (React + TypeScript)
- [x] Email notifications
- [x] PostgreSQL support
- [x] Rate limiting
- [x] User management dashboard
- [x] Docker deployment
- [x] Production-ready infrastructure

### 🚧 Future Enhancements
- [ ] SMS notifications
- [ ] Multi-provider support (beyond PadelMate)
- [ ] Court booking integration
- [ ] Mobile app (React Native)
- [ ] Advanced filtering (price, court quality, etc.)
- [ ] User preferences and favorites
- [ ] Analytics dashboard
- [ ] Webhook support
- [ ] API versioning

## Support

- **Issues**: [GitHub Issues](https://github.com/thom-techlete/padelwatcher/issues)
- **Documentation**: See documentation files listed above
- **Security**: See [SECURITY.md](SECURITY.md) for reporting vulnerabilities

## License

MIT License - see LICENSE file for details
