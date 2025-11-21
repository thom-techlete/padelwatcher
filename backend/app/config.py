"""
Configuration for Padel Watcher API
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
else:
    # Default to SQLite in data directory
    DATABASE_PATH = DATA_DIR / "padel.db"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"

# API Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 24))

# Flask configuration
DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
PORT = int(os.environ.get('FLASK_PORT', 5000))

# Email configuration (Gmail SMTP)
GMAIL_SMTP_SERVER = os.environ.get('GMAIL_SMTP_SERVER', 'smtp.gmail.com')
GMAIL_SMTP_PORT = int(os.environ.get('GMAIL_SMTP_PORT', 587))
GMAIL_AUTH_CODE = os.environ.get('GMAIL_AUTH_CODE', '')
GMAIL_SENDER_EMAIL = os.environ.get('GMAIL_SENDER_EMAIL', '')
GMAIL_SENDER_EMAIL_NAME = os.environ.get('GMAIL_SENDER_EMAIL_NAME', 'Padel Watcher')
FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL', 'http://127.0.0.1:5173')
