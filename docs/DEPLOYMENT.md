# Production Deployment Guide

This guide covers deploying AXOIQ SYNAPSE to production environments.

## Pre-Deployment Checklist

### Security Requirements

- [ ] **SECRET_KEY**: Generate a secure random key
  ```bash
  # Generate 64-character hex key
  openssl rand -hex 32
  ```

- [ ] **Database Credentials**: Use strong passwords (min 16 chars, mixed case, numbers, symbols)

- [ ] **CORS Configuration**: Set `ALLOWED_ORIGINS` to your production domain(s)
  ```bash
  ALLOWED_ORIGINS=https://app.yourdomain.com,https://admin.yourdomain.com
  ```

- [ ] **SSL/TLS**: Ensure HTTPS is configured (via Traefik, nginx, or cloud provider)

- [ ] **Firewall**: Only expose necessary ports (443 for HTTPS, internal ports for services)

### Environment Variables

Create a `.env` file with production values:

```bash
# =============================================================================
# PRODUCTION ENVIRONMENT CONFIGURATION
# =============================================================================

# Environment
ENVIRONMENT=production

# -----------------------------------------------------------------------------
# DATABASE
# -----------------------------------------------------------------------------
POSTGRES_SERVER=your-db-host.com
POSTGRES_PORT=5432
POSTGRES_USER=synapse_prod
POSTGRES_PASSWORD=<STRONG_PASSWORD_HERE>
POSTGRES_DB=synapse_prod

# Or use DATABASE_URL directly
DATABASE_URL=postgresql://synapse_prod:<PASSWORD>@your-db-host.com:5432/synapse_prod

# -----------------------------------------------------------------------------
# AUTHENTICATION & SECURITY
# -----------------------------------------------------------------------------
# CRITICAL: Generate with `openssl rand -hex 32`
SECRET_KEY=<YOUR_64_CHAR_HEX_KEY>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60  # Shorter in production

# -----------------------------------------------------------------------------
# CORS (comma-separated list of allowed origins)
# -----------------------------------------------------------------------------
ALLOWED_ORIGINS=https://synapse.yourdomain.com

# -----------------------------------------------------------------------------
# OPTIONAL: Redis for caching/sessions
# -----------------------------------------------------------------------------
REDIS_URL=redis://your-redis-host.com:6379/0
```

### Database Preparation

1. **Run migrations**:
   ```bash
   cd apps/synapse/backend
   alembic upgrade head
   ```

2. **Create indexes** (if not using Alembic):
   ```sql
   CREATE INDEX IF NOT EXISTS ix_asset_project_id ON assets(project_id);
   CREATE INDEX IF NOT EXISTS ix_asset_type_project ON assets(type, project_id);
   CREATE INDEX IF NOT EXISTS ix_lbs_project_id ON lbs_nodes(project_id);
   CREATE INDEX IF NOT EXISTS ix_connection_project_id ON connections(project_id);
   ```

3. **Verify constraints**:
   ```bash
   docker exec -it postgres psql -U postgres -d synapse -c "\di"
   ```

## Deployment Options

### Option 1: Docker Compose (Recommended)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build:
      context: ./apps/synapse/backend
      dockerfile: Dockerfile
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./apps/synapse/frontend
      dockerfile: Dockerfile
      args:
        - VITE_API_URL=/api/v1
    restart: unless-stopped

  traefik:
    image: traefik:v3.0
    command:
      - "--providers.docker=true"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@yourdomain.com"
    ports:
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
```

Deploy:
```bash
docker compose -f docker-compose.prod.yml up -d
```

### Option 2: Kubernetes

See `k8s/` directory for Kubernetes manifests (coming soon).

### Option 3: Cloud Platforms

**AWS:**
- ECS Fargate for containers
- RDS PostgreSQL for database
- ElastiCache for Redis
- ALB for load balancing

**Azure:**
- Azure Container Apps
- Azure Database for PostgreSQL
- Azure Cache for Redis

**GCP:**
- Cloud Run for containers
- Cloud SQL for PostgreSQL
- Memorystore for Redis

## Post-Deployment

### Health Checks

```bash
# Backend health
curl https://synapse.yourdomain.com/health
# Expected: {"status":"healthy"}

# API endpoint
curl https://synapse.yourdomain.com/api/v1/
# Expected: {"message":"Welcome to AXOIQ SYNAPSE API"}
```

### Monitoring Setup

1. **Grafana**: Connect to Loki for log aggregation
2. **Alerts**: Configure for:
   - 5xx error rate > 1%
   - Response time > 2s
   - Database connection failures
   - Disk usage > 80%

### Backup Strategy

```bash
# Daily PostgreSQL backup
pg_dump -U synapse_prod -h localhost synapse_prod > backup_$(date +%Y%m%d).sql

# Compress and upload to S3/Azure Blob
gzip backup_$(date +%Y%m%d).sql
aws s3 cp backup_$(date +%Y%m%d).sql.gz s3://your-backup-bucket/
```

### Log Rotation

Configure logrotate for container logs:
```
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    missingok
    delaycompress
    copytruncate
}
```

## Security Hardening

### Network Security

- [ ] VPC/VNet isolation for database
- [ ] Security groups limiting access
- [ ] WAF rules for common attacks
- [ ] Rate limiting on API endpoints

### Application Security

- [ ] Disable debug mode
- [ ] Remove development endpoints
- [ ] Enable HSTS headers
- [ ] CSP headers configured
- [ ] Secrets in vault (not env files)

### Secrets Management

**AWS Secrets Manager:**
```python
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']
```

**Azure Key Vault:**
```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://your-vault.vault.azure.net/", credential=credential)
secret = client.get_secret("SECRET_KEY")
```

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check backend container is running: `docker ps`
   - Check backend logs: `docker logs synapse-backend`
   - Verify health endpoint responds

2. **Database Connection Failed**
   - Verify DATABASE_URL is correct
   - Check network connectivity to database
   - Verify credentials

3. **CORS Errors**
   - Check ALLOWED_ORIGINS matches your frontend URL exactly
   - Include protocol (https://)
   - No trailing slashes

4. **401 Unauthorized**
   - Verify SECRET_KEY matches between deployments
   - Check token expiration settings
   - Clear browser storage and re-login

### Support

- GitHub Issues: https://github.com/your-org/epcb-tools/issues
- Documentation: https://docs.yourdomain.com

---

*Last updated: 2025-11-28*
