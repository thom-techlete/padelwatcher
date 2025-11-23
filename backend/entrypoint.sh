#!/bin/bash
set -e

echo "Updating frontend files..."
# Clean up existing files in the volume and copy new ones from the build
# Use || true to ignore error if directory is empty
rm -rf /app/frontend_dist/* || true
cp -r /app/frontend_build/. /app/frontend_dist/

echo "Applying database migrations..."
alembic upgrade head

echo "Checking for admin user..."
if ! python -c "from app.models import User; from app.services import AvailabilityService; service = AvailabilityService(); admin_exists = service.session.query(User).filter(User.is_admin == True).first() is not None; exit(0 if admin_exists else 1)"; then
    echo "No admin user found, creating default admin..."
    python scripts/create_admin.py
else
    echo "Admin user already exists."
fi

echo "Starting application..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 --access-logfile - --error-logfile - app.api:app
