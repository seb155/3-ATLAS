---
description: Docker troubleshooting for workspace/apps architecture
---

# Docker Troubleshooting

**Goal:** Diagnose and fix Docker issues.

## Common Issues

### 1. Containers Not Starting

**Check workspace:**
```bash
cd workspace
docker-compose ps
docker-compose logs
```

**Check SYNAPSE:**
```bash
cd apps/synapse
docker-compose -f docker-compose.dev.yml ps
docker-compose -f docker-compose.dev.yml logs
```

**Fix:** Rebuild
```bash
docker-compose -f docker-compose.dev.yml up --build
```

### 2. Port Conflicts

**Check ports:**
```powershell
netstat -ano | findstr "4000 5433 5555 8001"
```

**Fix:** Stop conflicting services or change ports in `.env`

### 3. Database Connection Failed

**Verify workspace running:**
```bash
docker exec forge-postgres pg_isready -U postgres
```

**Expected:** "accepting connections"

**Fix:** Start workspace first
```bash
cd workspace && docker-compose up -d
```

### 4. Frontend/Backend Not Loading

**Check logs:**
```bash
docker-compose -f docker-compose.dev.yml logs backend
docker-compose -f docker-compose.dev.yml logs frontend
```

**Common fixes:**
- Clear browser cache
- Restart containers
- Check `.env` file
- Rebuild: `--build` flag

### 5. Out of Disk Space

**Clean:**
```bash
docker system prune -a --volumes
```

**Warning:** This removes ALL unused Docker data

## Full Guide

See: `docs/getting-started/01-installation.md#troubleshooting`
