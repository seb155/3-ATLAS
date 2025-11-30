# Infrastructure Guide for Developers

Quick reference for developers working with AXIOM infrastructure.

---

## Daily Workflows

### Starting Your Development Environment

**Quick Start** (All-in-One):
```powershell
# From AXIOM root
.\dev.ps1
```

**Manual Start**:
```powershell
# Check status
.\.dev\scripts\axiom.ps1 status

# Start SYNAPSE (auto-starts FORGE)
.\.dev\scripts\axiom.ps1 start synapse

# View logs
.\.dev\scripts\axiom.ps1 logs synapse-backend
.\.dev\scripts\axiom.ps1 logs synapse-frontend
```

### Accessing Services

**Development URLs** (Direct Ports):
- SYNAPSE: http://localhost:4000
- API Docs: http://localhost:8001/docs
- Grafana: http://localhost:3000
- Database (pgAdmin): http://localhost:5050

**With Traefik SSL**:
- SYNAPSE: https://synapse.axoiq.com
- API: https://api.axoiq.com/docs

---

## Common Tasks

### Viewing Logs

**CLI Method** (Recommended):
```powershell
# Follow logs (Ctrl+C to exit)
.\.dev\scripts\axiom.ps1 logs synapse-backend
```

**Docker Method**:
```powershell
# Last 100 lines, follow mode
docker logs synapse-backend -f --tail 100

# Last 50 lines (no follow)
docker logs synapse-backend --tail 50

# All logs since specific time
docker logs synapse-backend --since 30m
```

### Restarting Services

**After Code Changes**:
```powershell
# Rebuild and restart backend
cd apps\synapse
docker-compose -f docker-compose.dev.yml up -d --build backend

# Rebuild and restart frontend
docker-compose -f docker-compose.dev.yml up -d --build frontend
```

**Quick Restart** (No Rebuild):
```powershell
.\.dev\scripts\axiom.ps1 restart synapse-backend
```

### Database Operations

**Access PostgreSQL**:
```powershell
# Interactive psql shell
docker exec -it forge-postgres psql -U postgres -d synapse

# Run single query
docker exec forge-postgres psql -U postgres -d synapse -c "SELECT * FROM users LIMIT 5;"
```

**Run Migrations**:
```powershell
# Inside backend container
docker exec synapse-backend alembic upgrade head

# Create new migration
docker exec synapse-backend alembic revision --autogenerate -m "Add new table"
```

**Database GUI** (pgAdmin):
- URL: http://localhost:5050
- Email: admin@axoiq.com
- Password: admin123!

### Redis Operations

**Access Redis CLI**:
```powershell
# Interactive redis-cli
docker exec -it forge-redis redis-cli

# Get all keys
docker exec forge-redis redis-cli KEYS "*"

# Get specific value
docker exec forge-redis redis-cli GET mykey

# Flush all (⚠️ DELETES ALL DATA)
docker exec forge-redis redis-cli FLUSHALL
```

---

## Understanding the Architecture

### Network Communication

**Internal Communication** (Docker DNS):
```yaml
# Backend connects to database using Docker DNS
DATABASE_URL: postgresql://postgres:postgres@forge-postgres:5432/synapse

# Frontend proxy to backend
VITE_PROXY_TARGET: http://synapse-backend:8000
```

**External Access** (Host Ports):
- Frontend: `localhost:4000` → `synapse-frontend:4000`
- Backend: `localhost:8001` → `synapse-backend:8000`
- Database: `localhost:5433` → `forge-postgres:5432`

### Why forge-network?

All services must be on `forge-network` to communicate:

```yaml
# ✅ Correct - Service can reach database
services:
  backend:
    networks:
      - default
      - forge-network  # ← Required!

# ❌ Wrong - Service can't reach database
services:
  backend:
    networks:
      - default  # Only local network
```

### Port Allocation Rules

**Your Application's Range**:
- SYNAPSE: 4000-4999
- NEXUS: 5000-5999
- APEX: 6000-6999
- CORTEX: 7000-7999

**Check Available Ports**:
```powershell
.\.dev\scripts\axiom.ps1 ports
```

**Before Adding New Port**:
1. Choose port from your app's range
2. Check registry for conflicts: `.dev/infra/registry.yml`
3. Update registry after allocation
4. Validate: `.\.dev\scripts\axiom.ps1 validate`

---

## Troubleshooting

### Container Won't Start

**Check logs first**:
```powershell
.\.dev\scripts\axiom.ps1 logs <container_name>
```

**Common Causes**:

1. **Port Conflict**:
   ```powershell
   # Find what's using the port
   netstat -ano | findstr :4000

   # Kill the process
   taskkill /PID <PID> /F
   ```

2. **Not on forge-network**:
   ```powershell
   # Check network membership
   docker inspect synapse-backend | findstr forge-network

   # Should show "forge-network"
   # If not, add to docker-compose.yml
   ```

3. **Missing Dependencies**:
   ```powershell
   # Start FORGE first
   .\.dev\scripts\axiom.ps1 start forge

   # Wait 5 seconds
   Start-Sleep -Seconds 5

   # Then start your app
   .\.dev\scripts\axiom.ps1 start synapse
   ```

### Can't Connect to Database

**Verify Database is Running**:
```powershell
# Check postgres is up
docker ps | findstr forge-postgres

# Test connection from backend
docker exec synapse-backend ping forge-postgres
```

**Check Connection String**:
```yaml
# ✅ Correct (Internal Docker DNS)
DATABASE_URL: postgresql://postgres:postgres@forge-postgres:5432/synapse

# ❌ Wrong (External port, doesn't work inside Docker)
DATABASE_URL: postgresql://postgres:postgres@localhost:5433/synapse
```

### Frontend Can't Reach Backend

**Check Vite Proxy Configuration**:
```typescript
// vite.config.ts
server: {
  proxy: {
    '/api/v1': {
      target: 'http://synapse-backend:8000',  // Docker DNS
      changeOrigin: true
    }
  }
}
```

**Verify Both on forge-network**:
```powershell
docker inspect synapse-frontend | findstr forge-network
docker inspect synapse-backend | findstr forge-network
```

### Validation Fails

**Run Validation**:
```powershell
.\.dev\scripts\axiom.ps1 validate
```

**Common Issues**:
- Port conflicts → Change port or kill conflicting process
- Range violations → Move port to correct range for your app
- Network issues → Add `forge-network` to service
- Missing dependencies → Start dependencies first

---

## Development Best Practices

### 1. Always Use Docker DNS for Internal Communication

**✅ DO**:
```yaml
environment:
  - DATABASE_URL=postgresql://user:pass@forge-postgres:5432/db
  - REDIS_URL=redis://forge-redis:6379
```

**❌ DON'T**:
```yaml
environment:
  - DATABASE_URL=postgresql://user:pass@localhost:5433/db  # Won't work!
  - REDIS_URL=redis://localhost:6379  # Won't work!
```

### 2. Check Infrastructure Before Development

```powershell
# Quick health check
.\.dev\scripts\axiom.ps1 health

# Validate configuration
.\.dev\scripts\axiom.ps1 validate
```

### 3. Use Volumes for Hot Reload

**Frontend** (Vite auto-reloads):
```yaml
volumes:
  - ./frontend/src:/app/src  # ✅ Code changes auto-reload
  - /app/node_modules        # ✅ Don't override node_modules
```

**Backend** (Uvicorn --reload):
```yaml
volumes:
  - ./backend/app:/app/app  # ✅ Code changes auto-reload
```

### 4. Clean Up Regularly

```powershell
# Stop unused containers
docker ps -a | findstr Exited

# Remove stopped containers
docker container prune

# Remove unused volumes (⚠️ CAREFUL - removes data)
docker volume prune

# Remove unused images
docker image prune
```

---

## Performance Tips

### Faster Builds

**Use BuildKit**:
```powershell
# Enable Docker BuildKit
$env:DOCKER_BUILDKIT=1

# Build with cache
docker-compose build
```

**Multi-Stage Builds** (Already configured):
```dockerfile
# Frontend Dockerfile uses multi-stage
FROM node:20-alpine AS builder
# ... build steps ...
FROM node:20-alpine AS runtime
COPY --from=builder /app/dist /app/dist
```

### Faster Startups

**Use Docker Compose Profiles** (Future):
```yaml
# Only start what you need
services:
  essential-service:
    profiles: ["dev"]
  optional-service:
    profiles: ["full"]
```

```powershell
# Start only dev profile
docker-compose --profile dev up -d
```

### Reduce Log Noise

**Filter Logs**:
```powershell
# Only errors
docker logs synapse-backend 2>&1 | Select-String "ERROR"

# Exclude health checks
docker logs synapse-backend | Select-String -NotMatch "health"
```

---

## IDE Integration

### VS Code

**Recommended Extensions**:
- Docker (ms-azuretools.vscode-docker)
- Remote - Containers (ms-vscode-remote.remote-containers)

**Tasks Configuration** (`.vscode/tasks.json`):
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start SYNAPSE",
      "type": "shell",
      "command": ".dev/scripts/axiom.ps1 start synapse",
      "problemMatcher": []
    },
    {
      "label": "View Backend Logs",
      "type": "shell",
      "command": ".dev/scripts/axiom.ps1 logs synapse-backend",
      "problemMatcher": []
    }
  ]
}
```

---

## Environment Variables

### Where to Set Them

**FORGE Level** (`forge/.env`):
```bash
DOMAIN=axoiq.com
ACME_EMAIL=admin@axoiq.com
MEILI_MASTER_KEY=your_key_here
```

**SYNAPSE Level** (`apps/synapse/.env`):
```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@forge-postgres:5432/synapse

# Backend
SECRET_KEY=your_secret_key
ENVIRONMENT=development

# Frontend
VITE_API_URL=http://localhost:8001
```

### Required vs Optional

**Required** (App won't start without):
- `DATABASE_URL`
- `SECRET_KEY`

**Optional** (Has defaults):
- `DOMAIN` (defaults to `localhost`)
- `LOG_LEVEL` (defaults to `INFO`)

---

## Helpful Aliases

Add to PowerShell profile (`$PROFILE`):

```powershell
# AXIOM shortcuts
function axiom { & "D:\Projects\AXIOM\.dev\scripts\axiom.ps1" @args }
function ax-start { axiom start synapse }
function ax-stop { axiom stop synapse }
function ax-logs-be { axiom logs synapse-backend }
function ax-logs-fe { axiom logs synapse-frontend }
function ax-health { axiom health }
function ax-validate { axiom validate }

# Docker shortcuts
function dps { docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" }
function dlogs { param($container) docker logs $container -f --tail 100 }
function dexec { param($container) docker exec -it $container sh }
```

Usage:
```powershell
ax-start
ax-health
dlogs synapse-backend
```

---

## Emergency Procedures

### Nuclear Reset (⚠️ ALL DATA LOST)

```powershell
# Stop everything
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all volumes (⚠️ DELETES ALL DATA)
docker volume rm $(docker volume ls -q)

# Recreate network
docker network create forge-network

# Start fresh
.\.dev\scripts\axiom.ps1 start forge
.\.dev\scripts\axiom.ps1 start synapse
```

### Backup Before Reset

```powershell
# Backup database
docker exec forge-postgres pg_dumpall -U postgres > backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql

# Backup volumes (if needed)
docker run --rm -v postgres-data:/data -v D:\backups:/backup alpine tar czf /backup/postgres_$(Get-Date -Format 'yyyyMMdd').tar.gz /data
```

---

## See Also

- [CLI Reference](cli-reference.md) - Complete CLI command reference
- [Troubleshooting](troubleshooting.md) - Detailed troubleshooting guide
- [Network Architecture](network-architecture.md) - Understanding Docker networks
- [Infrastructure Registry](../../.dev/infra/registry.yml) - Port allocations and service definitions

---

**Questions?** Check the [Troubleshooting Guide](troubleshooting.md) or consult the DevOps Manager agent.

**Version**: 1.0
**Last Updated**: 2025-11-28 18:44
