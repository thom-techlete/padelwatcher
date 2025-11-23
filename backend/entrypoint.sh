#!/bin/bash
set -e

echo "Applying database migrations..."
alembic upgrade head

echo "Checking for admin user..."
if ! python -c "from app.services import AvailabilityService; service = AvailabilityService(); admin = service.get_user_by_email('admin@padelwatcher.com'); exit(0 if admin else 1)"; then
    echo "No admin user found, creating default admin..."
    python scripts/create_admin.py
else
    echo "Admin user already exists."
fi

echo "Starting application..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 --access-logfile - --error-logfile - app.api:app