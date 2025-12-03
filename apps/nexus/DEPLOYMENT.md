# NEXUS Deployment Guide

Version: 0.2.0
Status: Phase 2.0 - Notes/Wiki System + TriliumNext Integration

## Overview

NEXUS supports two deployment modes:
1. **FORGE Integration Mode** - Shared AXIOM infrastructure (recommended for development)
2. **Standalone Mode** - Independent deployment (production/isolated testing)

---

## FORGE Integration Mode (Recommended)

Uses shared AXIOM FORGE infrastructure for seamless integration with other AXIOM apps.

### Benefits

- ✅ Shared PostgreSQL database (`forge-postgres`)
- ✅ Shared Redis cache (`forge-redis`)
- ✅ SSO authentication with SYNAPSE, CORTEX, etc.
- ✅ Traefik routing with SSL (`https://nexus.axoiq.com`)
- ✅ Centralized logging (Loki/Grafana)
- ✅ No port conflicts

### Prerequisites

1. FORGE infrastructure must be running:
   ```powershell
   cd D:\Projects\AXIOM\forge
   docker compose up -d
   ```

2. Add `nexus.axoiq.com` to your hosts file:
   ```
   # C:\Windows\System32\drivers\etc\hosts
   127.0.0.1 nexus.axoiq.com
   127.0.0.1 api-nexus.axoiq.com
   ```

### Start FORGE Mode

```powershell
cd D:\Projects\AXIOM\apps\nexus

# Generate environment file (auto-detects Docker mode)
cd backend
.\generate-env.ps1
cd ..

# Start services
docker compose -f docker-compose.dev.yml up -d
```

### Access

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | https://nexus.axoiq.com | - |
| Backend API | https://api-nexus.axoiq.com/docs | - |
| Login | https://nexus.axoiq.com/login | admin@aurumax.com / admin123! |

### Environment Variables (Auto-Generated)

When running `generate-env.ps1` in FORGE mode, the script generates:

```env
DATABASE_URL=postgresql://postgres:postgres@forge-postgres:5432/nexus
REDIS_URL=redis://forge-redis:6379
LOKI_URL=http://forge-loki:3100
ENVIRONMENT=docker
```

---

## Standalone Mode

Independent deployment with dedicated PostgreSQL and Redis instances.

### Benefits

- ✅ Fully isolated from AXIOM workspace
- ✅ Can be deployed independently
- ✅ No dependencies on FORGE
- ✅ Uses dedicated NEXUS port range (5000-5999)

### Port Allocation

| Service | External Port | Internal Port | Description |
|---------|---------------|---------------|-------------|
| Backend API | 5000 | 8000 | FastAPI server |
| PostgreSQL | 5500 | 5432 | Database |
| Redis | 5501 | 6379 | Cache |
| Frontend | 5173 | 5173 | Vite dev server |

### Start Standalone Mode

```powershell
cd D:\Projects\AXIOM\apps\nexus

# Start services
docker compose up -d
```

### Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:5000/docs |
| PostgreSQL | localhost:5500 |
| Redis | localhost:5501 |

### Environment Variables (Hardcoded)

Standalone mode uses hardcoded service names in `docker-compose.yml`:

```env
DATABASE_URL=postgresql://nexus:nexus_dev_password@postgres-standalone:5432/nexus_dev
REDIS_URL=redis://redis-standalone:6379
ENVIRONMENT=standalone
```

---

## Switching Between Modes

### From FORGE → Standalone

1. Stop FORGE mode:
   ```powershell
   docker compose -f docker-compose.dev.yml down
   ```

2. Start standalone:
   ```powershell
   docker compose up -d
   ```

3. Access at `http://localhost:5000`

### From Standalone → FORGE

1. Stop standalone:
   ```powershell
   docker compose down
   ```

2. Ensure FORGE is running:
   ```powershell
   cd D:\Projects\AXIOM\forge
   docker compose up -d
   ```

3. Regenerate .env for Docker DNS:
   ```powershell
   cd D:\Projects\AXIOM\apps\nexus\backend
   .\generate-env.ps1 -Force
   ```

4. Start FORGE mode:
   ```powershell
   cd D:\Projects\AXIOM\apps\nexus
   docker compose -f docker-compose.dev.yml up -d
   ```

5. Access at `https://nexus.axoiq.com`

---

## Environment File Management

### Auto-Generation Script

The `generate-env.ps1` script automatically detects your environment:

```powershell
cd backend
.\generate-env.ps1
```

**Detection logic:**
1. Checks if running inside Docker container (`/.dockerenv`)
2. Checks for `DOCKER_CONTAINER=true` environment variable
3. Checks if `forge-network` exists (`docker network ls`)

**Output:**
- **Docker mode:** Uses `forge-postgres:5432`, `forge-redis:6379`
- **Local mode:** Uses `localhost:5433`, `localhost:6379`

### Force Regeneration

To overwrite existing `.env`:

```powershell
.\generate-env.ps1 -Force
```

The script automatically backs up your current `.env` with a timestamp.

### Manual Configuration

If you need to manually edit `.env`:

1. Copy from `.env.template`:
   ```powershell
   cd backend
   copy .env.template .env
   ```

2. Replace `{{PLACEHOLDERS}}` with actual values:
   - `{{DATABASE_HOST}}` → `forge-postgres` (Docker) or `localhost` (Local)
   - `{{DATABASE_PORT}}` → `5432` (Docker) or `5433` (Local)
   - `{{REDIS_HOST}}` → `forge-redis` (Docker) or `localhost` (Local)
   - `{{ENV_MODE}}` → `docker` or `local`

---

## Troubleshooting

### Port Conflicts (Standalone Mode)

**Error:** `bind: address already in use`

**Solution:** Ensure ports 5000, 5500, 5501 are not in use:

```powershell
# Check what's using the ports
netstat -ano | findstr "5000"
netstat -ano | findstr "5500"
netstat -ano | findstr "5501"

# Kill process if needed
taskkill /PID <process_id> /F
```

### Connection Issues (FORGE Mode)

**Error:** `could not resolve host: forge-postgres`

**Solutions:**

1. **Verify FORGE is running:**
   ```powershell
   docker ps | findstr forge
   ```

2. **Verify forge-network exists:**
   ```powershell
   docker network ls | findstr forge
   ```

3. **Recreate network if needed:**
   ```powershell
   docker network create forge-network
   ```

4. **Restart services:**
   ```powershell
   docker compose -f docker-compose.dev.yml restart
   ```

### Environment Detection Issues

**Problem:** Script detects wrong environment

**Solution:**

1. **Check Docker status:**
   ```powershell
   docker network ls
   ```

2. **Manually verify .env:**
   ```powershell
   cat backend\.env
   ```

3. **Force regeneration:**
   ```powershell
   cd backend
   .\generate-env.ps1 -Force
   ```

### Database Connection Errors

**Error:** `connection refused` or `authentication failed`

**FORGE mode:**
```powershell
# Test database connection
docker exec -it forge-postgres psql -U postgres -d nexus

# Check logs
docker logs forge-postgres --tail 50
```

**Standalone mode:**
```powershell
# Test database connection
docker exec -it nexus-postgres-standalone psql -U nexus -d nexus_dev

# Check logs
docker logs nexus-postgres-standalone --tail 50
```

---

## Development Workflows

### Frontend Development Only

If you're only working on the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` and can connect to either:
- FORGE backend: `https://api-nexus.axoiq.com`
- Standalone backend: `http://localhost:5000`

### Backend Development Only

**With Docker:**
```powershell
# FORGE mode
docker compose -f docker-compose.dev.yml up backend

# Standalone mode
docker compose up backend-standalone
```

**Locally (without Docker):**
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Ensure .env points to accessible database
uvicorn app.main:app --reload --port 8000
```

### Full Stack Development

**FORGE mode (recommended):**
```powershell
# Terminal 1: Start infrastructure
cd D:\Projects\AXIOM\forge
docker compose up -d

# Terminal 2: Start NEXUS backend
cd D:\Projects\AXIOM\apps\nexus
docker compose -f docker-compose.dev.yml up backend

# Terminal 3: Start frontend
cd D:\Projects\AXIOM\apps\nexus\frontend
npm run dev
```

**Standalone mode:**
```powershell
# Terminal 1: Start all services
cd D:\Projects\AXIOM\apps\nexus
docker compose up

# Terminal 2: Start frontend
cd frontend
npm run dev
```

---

## Production Deployment

For production deployment, use **Standalone mode** with:

1. **Environment-specific configuration:**
   ```env
   ENVIRONMENT=production
   DEBUG=false
   LOG_LEVEL=INFO
   ```

2. **Secure credentials:**
   - Generate new `SECRET_KEY`
   - Use strong database passwords
   - Configure proper CORS origins

3. **Persistent volumes:**
   - Ensure `postgres_standalone_data` volume is backed up
   - Configure volume backup strategy

4. **Reverse proxy:**
   - Use Traefik or Nginx for SSL termination
   - Configure proper domain names

5. **Monitoring:**
   - Set up health check endpoints
   - Configure logging to external service
   - Monitor resource usage

---

## Additional Resources

- **Main README:** [README.md](README.md)
- **AXIOM Documentation:** [D:\Projects\AXIOM\CLAUDE.md](../../CLAUDE.md)
- **Infrastructure Docs:** [D:\Projects\AXIOM\docs\infrastructure\](../../docs/infrastructure/)
- **NEXUS Project Docs:** [CLAUDE.md](CLAUDE.md)

---

## Support

For deployment issues:

1. **Check logs:**
   ```powershell
   # FORGE mode
   docker logs nexus-backend -f

   # Standalone mode
   docker logs nexus-backend-standalone -f
   ```

2. **Validate configuration:**
   ```powershell
   cat backend\.env
   ```

3. **Consult documentation:**
   - This file (DEPLOYMENT.md)
   - CLAUDE.md in this directory
   - AXIOM infrastructure docs

---

**Last Updated:** 2025-11-29
**Version:** 0.2.0
