FROM python:3.11-slim

LABEL maintainer="AXIOM Team"
LABEL description="Claude Code Usage Exporter PRO for Prometheus"
LABEL version="2.0"

WORKDIR /app

# Create non-root user first
RUN useradd -m -u 1000 exporter

# Copy all exporter versions and set ownership
COPY --chown=exporter:exporter exporter.py .
COPY --chown=exporter:exporter exporter_pro.py .
COPY --chown=exporter:exporter requirements.txt .

# Install dependencies (none currently, but future-proofing)
RUN pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER exporter

# Expose metrics port
EXPOSE 9091

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9091/health')" || exit 1

# Default to PRO version (use EXPORTER_VERSION=standard for legacy)
ENV EXPORTER_VERSION=pro

# Run exporter based on version
CMD ["sh", "-c", "if [ \"$EXPORTER_VERSION\" = 'standard' ]; then python -u exporter.py; else python -u exporter_pro.py; fi"]
