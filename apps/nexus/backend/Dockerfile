# ==============================================================================
# NEXUS BACKEND - Dockerfile
# ==============================================================================
# FastAPI + Python 3.11 + PostgreSQL + Redis
#
# Features:
#   - Multi-stage build for smaller image size
#   - Security: Non-root user
#   - Health checks
#   - Development and production ready
#
# Build:
#   docker build -t nexus-backend:latest .
#
# Run (via docker-compose.dev.yml):
#   docker-compose -f docker-compose.dev.yml up backend
# ==============================================================================

FROM python:3.11-slim as base

LABEL maintainer="Nexus Team"
LABEL version="0.2.0"
LABEL description="Nexus Backend API (FastAPI)"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ==============================================================================
# DEVELOPMENT STAGE
# ==============================================================================
FROM base as development

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 nexus && \
    chown -R nexus:nexus /app

USER nexus

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ==============================================================================
# PRODUCTION STAGE (multi-stage build)
# ==============================================================================
FROM base as production

# Copy requirements file
COPY requirements.txt .

# Install production dependencies only
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 nexus && \
    chown -R nexus:nexus /app

USER nexus

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Production command with Gunicorn
CMD ["gunicorn", "app.main:app", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]

# ==============================================================================
# NOTES
# ==============================================================================
# 1. Build Targets:
#    Development: docker build --target development -t nexus-backend:dev .
#    Production:  docker build --target production -t nexus-backend:prod .
#
# 2. Default target is 'development' (used by docker-compose.dev.yml)
#
# 3. Security:
#    - Runs as non-root user (nexus:1000)
#    - Minimal system dependencies
#    - No cache files
#
# 4. Health Check:
#    - Endpoint: /api/v1/health
#    - Interval: 30 seconds
#    - Timeout: 10 seconds
#    - Start period: 40 seconds (allows for app initialization)
#
# 5. Volume Mounts (configured in docker-compose.dev.yml):
#    - ./backend:/app (live code updates in development)
#    - /app/.venv (persist virtual environment)
#
# 6. Environment Variables:
#    - Set in docker-compose.dev.yml
#    - DATABASE_URL, REDIS_URL, SECRET_KEY, etc.
#
# 7. Production Deployment:
#    - Use Gunicorn with 4 worker processes
#    - UvicornWorker for async support
#    - Logs to stdout/stderr for container logging
# ==============================================================================
