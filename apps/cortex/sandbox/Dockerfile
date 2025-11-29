FROM python:3.11-slim

WORKDIR /app

# Install Docker CLI for container management
RUN apt-get update && apt-get install -y \
    curl \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    docker \
    pydantic

# Copy application
COPY manager.py .

# Create non-root user (but keep docker access)
RUN useradd -m -u 1000 sandbox

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "manager:app", "--host", "0.0.0.0", "--port", "8000"]
