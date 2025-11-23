"""
Configuration for Padel Watcher API
Environment-aware configuration that changes based on FLASK_ENV
"""

import os
from pathlib import Path

# Environment detection
FLASK_ENV = os.environ.get("FLASK_ENV", "development").lower()
IS_PRODUCTION = FLASK_ENV == "production"

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Explicit DATABASE_URL takes precedence
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
else:
    # Build from environment variables
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "padelwatcher")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "padelwatcher_dev_password")
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "padelwatcher")
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")

    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Database connection pool settings (for PostgreSQL)
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": int(os.environ.get("DB_POOL_SIZE", 5 if IS_PRODUCTION else 2)),
    "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", 10 if IS_PRODUCTION else 5)),
    "pool_recycle": int(os.environ.get("DB_POOL_RECYCLE", 3600)),
    "pool_pre_ping": True,  # Verify connections before using them
}

# ============================================================================
# API CONFIGURATION
# ============================================================================
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", 24))

# Production security check
if IS_PRODUCTION:
    if SECRET_KEY == "dev-secret-key-change-in-production":
        raise ValueError("SECRET_KEY must be set in production environment")
    if not DATABASE_URL and "padelwatcher" not in SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL must be properly configured in production")

# ============================================================================
# FLASK CONFIGURATION
# ============================================================================
DEBUG = (
    os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    if not IS_PRODUCTION
    else False
)
HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
PORT = int(os.environ.get("FLASK_PORT", 5000))

# ============================================================================
# CORS CONFIGURATION
# ============================================================================
if IS_PRODUCTION:
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS",
        "https://padelwatcher.techletes.ai,https://www.padelwatcher.techletes.ai",
    ).split(",")
else:
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

# ============================================================================
# EMAIL CONFIGURATION (Gmail SMTP)
# ============================================================================
GMAIL_SMTP_SERVER = os.environ.get("GMAIL_SMTP_SERVER", "smtp.gmail.com")
GMAIL_SMTP_PORT = int(os.environ.get("GMAIL_SMTP_PORT", 587))
GMAIL_AUTH_CODE = os.environ.get("GMAIL_AUTH_CODE", "")
GMAIL_SENDER_EMAIL = os.environ.get("GMAIL_SENDER_EMAIL", "")
GMAIL_SENDER_EMAIL_NAME = os.environ.get("GMAIL_SENDER_EMAIL_NAME", "Padel Watcher")

if IS_PRODUCTION:
    if not GMAIL_AUTH_CODE or not GMAIL_SENDER_EMAIL:
        raise ValueError(
            "Email configuration (GMAIL_AUTH_CODE, GMAIL_SENDER_EMAIL) must be set in production"
        )

# ============================================================================
# FRONTEND CONFIGURATION
# ============================================================================
if IS_PRODUCTION:
    FRONTEND_BASE_URL = os.environ.get(
        "FRONTEND_BASE_URL", "https://padelwatcher.techletes.ai"
    )
else:
    FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL", "http://127.0.0.1:5173")

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO" if IS_PRODUCTION else "DEBUG")

# ============================================================================
# SCHEDULER CONFIGURATION
# ============================================================================
SCHEDULER_INTERVAL_MINUTES = int(os.environ.get("SCHEDULER_INTERVAL_MINUTES", 15))
