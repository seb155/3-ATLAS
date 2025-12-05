# Skill: Docker Service

Cree un service Docker complet pour FORGE.

## Usage

```text
/skill docker-service [service-name]
```

## Templates Generes

1. `Dockerfile` - Image Docker
2. `docker-compose.service.yml` - Config Compose
3. `healthcheck.sh` - Script de health check

## Exemple

```text
/skill docker-service redis-cache

Genere:
- forge/services/redis-cache/Dockerfile
- forge/services/redis-cache/docker-compose.yml
- forge/services/redis-cache/healthcheck.sh
```

## Structure Dockerfile

```dockerfile
# {SERVICE_NAME} Service
# FORGE Infrastructure - AXIOM Platform

FROM {base_image}:{version}

LABEL maintainer="AXIOM Team"
LABEL service="{service_name}"

# Environment
ENV SERVICE_NAME={service_name}
ENV TZ=UTC

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration
COPY config/ /etc/{service}/

# Health check
COPY healthcheck.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/healthcheck.sh
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# Expose ports
EXPOSE {port}

# Run service
CMD ["{command}"]
```

## Structure Docker Compose

```yaml
# {SERVICE_NAME} Service
# Part of FORGE Infrastructure

services:
  forge-{service_name}:
    build:
      context: ./services/{service_name}
      dockerfile: Dockerfile
    container_name: forge-{service_name}
    restart: unless-stopped

    environment:
      - SERVICE_NAME={service_name}
      - TZ=UTC

    ports:
      - "{host_port}:{container_port}"

    volumes:
      - {service_name}_data:/data
      - ./config/{service_name}:/etc/{service_name}:ro

    networks:
      - forge-network

    healthcheck:
      test: ["CMD", "/usr/local/bin/healthcheck.sh"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.{service_name}.rule=Host(`{service_name}.localhost`)"

volumes:
  {service_name}_data:

networks:
  forge-network:
    external: true
```

## Structure Health Check

```bash
#!/bin/bash
# Health check for {SERVICE_NAME}

set -e

# Check if service is responding
if curl -sf http://localhost:{port}/health > /dev/null 2>&1; then
    echo "OK: {SERVICE_NAME} is healthy"
    exit 0
else
    echo "FAIL: {SERVICE_NAME} is not responding"
    exit 1
fi
```

## Integration FORGE

Pour integrer au FORGE principal:

```yaml
# Dans forge/docker-compose.yml, ajouter:

include:
  - path: ./services/{service_name}/docker-compose.yml
```

## Services FORGE Existants

| Service | Port | Usage |
|---------|------|-------|
| forge-postgres | 5433 | Base de donnees |
| forge-redis | 6379 | Cache/Sessions |
| forge-grafana | 3000 | Monitoring |
| forge-loki | 3100 | Logs |
| forge-traefik | 80/443 | Reverse proxy |
| forge-meilisearch | 7700 | Search |
