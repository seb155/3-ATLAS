FROM python:3.11-slim

LABEL maintainer="AXIOM Team"
LABEL description="Claude Code Usage Exporter for Prometheus"

WORKDIR /app

# Copy application
COPY exporter.py .
COPY requirements.txt .

# Install dependencies (none currently, but future-proofing)
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -u 1000 exporter
USER exporter

# Expose metrics port
EXPOSE 9091

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9091/health')" || exit 1

# Run exporter
CMD ["python", "-u", "exporter.py"]
