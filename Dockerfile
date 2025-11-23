# Multi-stage build for production - Frontend + Backend build + Runtime
# Stage 1: Build frontend with empty API_BASE_URL for relative paths
FROM node:20-alpine AS frontend-builder

WORKDIR /build

COPY web/package*.json ./
RUN npm ci

COPY web/ ./

# Build with empty VITE_API_BASE_URL for relative paths (/api/...)
ARG VITE_API_BASE_URL=http://localhost
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Stage 2: Build backend dependencies and prepare app
FROM python:3.12-slim AS backend-builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Stage 3: Final runtime image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    FLASK_APP=api.main:app \
    PYTHONPATH=/app

WORKDIR /app

# Install runtime dependencies only (no gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    redis-tools \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /app/data /app/frontend_dist && \
    chown -R appuser:appuser /app

# Copy virtual environment from backend builder
COPY --from=backend-builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy application code
COPY --chown=appuser:appuser backend/app ./app
COPY --chown=appuser:appuser backend/alembic ./alembic
COPY --chown=appuser:appuser backend/alembic.ini .
COPY --chown=appuser:appuser backend/scripts ./scripts
COPY --chown=appuser:appuser backend/entrypoint.sh .

# Copy built frontend from stage 1
COPY --chown=appuser:appuser --from=frontend-builder /build/dist ./frontend_build

# Switch to non-root user
USER appuser

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run with entrypoint script that applies migrations and starts gunicorn
CMD ["./entrypoint.sh"]
