#!/bin/bash
set -e

echo "Applying database migrations..."
alembic upgrade head

echo "Starting application..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 --access-logfile - --error-logfile - app.api:app