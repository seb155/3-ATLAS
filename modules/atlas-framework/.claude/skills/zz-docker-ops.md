# Docker Operations Skill

This skill provides quick Docker infrastructure operations for AXIOM and personal projects.

---

## Usage

**Invoke with**:
- Skill tool: `skill: "docker-ops"`
- User request: "start all" / "stop all" / "restart traefik" / "docker status"

---

## What This Skill Does

Provides 5 operations for managing Docker infrastructure:

1. **start-all** - Start all AXIOM + personal project containers
2. **stop-all** - Stop all containers in reverse order
3. **restart** - Stop then start (clean restart)
4. **status** - Quick status of all services
5. **restart-traefik** - Reload Traefik configuration

---

## When to Use This Skill

### Use This Skill When:
- ✅ Starting/stopping all infrastructure
- ✅ Quick restart after configuration changes
- ✅ Checking overall container status
- ✅ Reloading Traefik routes

### Use Network-Test Skill When:
- 🔍 Testing HTTP connectivity
- 🔍 Validating Traefik routes
- 🔍 Checking port availability

### Use DevOps Manager Agent When:
- 🔧 Diagnosing complex problems
- 🔧 Adding new services
- 🔧 Port allocation conflicts
- 🔧 Network troubleshooting

---

## Operations

### 1. start-all - Start All Services

**Order of startup** (dependencies respected):

```
Phase 1: FORGE Core
├── forge-postgres
├── forge-redis
└── forge-traefik

Phase 2: FORGE Services
├── forge-grafana
├── forge-loki
├── forge-pgadmin (optional)
├── forge-prisma (optional)
├── forge-meilisearch
└── forge-wiki

Phase 3: AXIOM Applications
├── synapse-backend
├── synapse-frontend
├── nexus-backend (if configured)
└── nexus-frontend (if configured)

Phase 4: Personal Projects
├── trilium-sync (Note_synch)
├── notes-neo4j
├── notes-graph-api
├── pulse (Homelab)
├── homelab-dashboard
├── findash-app
└── pilote-patrimoine
```

**Commands**:
```powershell
# Phase 1: FORGE Core
cd D:\Projects\AXIOM\forge
docker compose up -d forge-postgres forge-redis forge-traefik

# Phase 2: FORGE Services (wait for core)
docker compose up -d

# Phase 3: SYNAPSE
cd D:\Projects\AXIOM\apps\synapse
docker compose -f docker-compose.dev.yml up -d

# Phase 4: Personal Projects (parallel)
cd D:\Projects\Note_synch && docker compose up -d
cd D:\Projects\8-Perso\Homelab_MSH\dashboard\pulse && docker compose up -d
cd D:\Projects\8-Perso\FinDash && docker compose up -d
```

---

### 2. stop-all - Stop All Services

**Order of shutdown** (reverse of startup):

```powershell
# Phase 1: Personal Projects
cd D:\Projects\Note_synch && docker compose down
cd D:\Projects\8-Perso\Homelab_MSH\dashboard\pulse && docker compose down
cd D:\Projects\8-Perso\Homelab_MSH\dashboard && docker compose down
cd D:\Projects\8-Perso\FinDash && docker compose down
cd D:\Projects\8-Perso\Pilote-Patrimoine && docker compose down

# Phase 2: AXIOM Applications
cd D:\Projects\AXIOM\apps\synapse && docker compose -f docker-compose.dev.yml down
cd D:\Projects\AXIOM\apps\nexus && docker compose down

# Phase 3: FORGE (last)
cd D:\Projects\AXIOM\forge && docker compose down
```

---

### 3. restart - Full Restart

Execute stop-all then start-all with 5-second wait between.

---

### 4. status - Quick Status

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Output format**:
```markdown
# Docker Status

## FORGE Infrastructure
✅ forge-postgres (5433) - healthy
✅ forge-redis (6379) - healthy
✅ forge-traefik (80, 443, 8888) - healthy
✅ forge-grafana (3000) - healthy
✅ forge-loki (3100) - healthy
📋 forge-pgadmin - not running (optional)
📋 forge-prisma - not running (optional)

## AXIOM Applications
✅ synapse-backend (8001) - healthy
✅ synapse-frontend (4000) - healthy
❌ nexus-backend - not running
❌ nexus-frontend - not running

## Personal Projects
✅ trilium-sync (6200) - healthy
✅ notes-neo4j (6201, 6202) - healthy
✅ notes-graph-api (6203) - healthy
✅ pulse (6301) - healthy
⚠️ homelab-dashboard (6300) - restarting
✅ findash-app (6400) - healthy
❌ pilote-patrimoine (6100) - build error

## Summary
- **Running**: 12/15
- **Issues**: 2 (homelab-dashboard, pilote-patrimoine)
```

---

### 5. restart-traefik - Reload Traefik

When Traefik configuration changes or routes aren't detected:

```powershell
docker restart forge-traefik

# Wait for startup
Start-Sleep -Seconds 5

# Verify routes
curl -s http://localhost:8888/api/http/routers | ConvertFrom-Json | Select-Object -Property name, status
```

**Expected output**:
```markdown
# Traefik Reload Complete

## Registered Routes
✅ synapse-frontend-prod@file
✅ synapse-backend-prod@file
✅ nexus-frontend-prod@file
✅ findash-prod@file
✅ pulse@docker
✅ trilium@docker
✅ neo4j@docker

**Total**: 25 routes active
```

---

## Service Registry

### Port Allocations

| Service | Port | Type | Project |
|---------|------|------|---------|
| forge-postgres | 5433 | DB | FORGE |
| forge-redis | 6379 | Cache | FORGE |
| forge-traefik | 80, 443, 8888 | Proxy | FORGE |
| forge-grafana | 3000 | Monitor | FORGE |
| forge-loki | 3100 | Logs | FORGE |
| synapse-backend | 8001 | API | SYNAPSE |
| synapse-frontend | 4000 | Web | SYNAPSE |
| trilium-sync | 6200 | Web | Note_synch |
| notes-neo4j | 6201, 6202 | DB | Note_synch |
| notes-graph-api | 6203 | API | Note_synch |
| homelab-dashboard | 6300 | Web | Homelab |
| pulse | 6301 | Web | Homelab |
| findash-app | 6400 | Web | FinDash |
| pilote-patrimoine | 6100 | Web | Pilote |

### Docker Compose Locations

| Project | Path | Compose File |
|---------|------|--------------|
| FORGE | `AXIOM/forge/` | `docker-compose.yml` |
| SYNAPSE | `AXIOM/apps/synapse/` | `docker-compose.dev.yml` |
| NEXUS | `AXIOM/apps/nexus/` | `docker-compose.dev.yml` |
| Note_synch | `Note_synch/` | `docker-compose.yml` |
| Homelab Dashboard | `8-Perso/Homelab_MSH/dashboard/` | `docker-compose.yml` |
| Homelab Pulse | `8-Perso/Homelab_MSH/dashboard/pulse/` | `docker-compose.yml` |
| FinDash | `8-Perso/FinDash/` | `docker-compose.yml` |
| Pilote-Patrimoine | `8-Perso/Pilote-Patrimoine/` | `docker-compose.yml` |

---

## Status Indicators

- ✅ **Running and healthy**
- ❌ **Not running** (should be running)
- ⚠️ **Warning** (unhealthy, restarting)
- 📋 **Info** (optional service, stopped is OK)

---

## Error Handling

### Common Issues

**forge-network doesn't exist**:
```powershell
docker network create forge-network
```

**Container keeps restarting**:
```powershell
docker logs <container> --tail 50
```

**Port already in use**:
```powershell
netstat -ano | findstr :<port>
taskkill /PID <pid> /F
```

**Traefik not detecting container**:
1. Check container has `traefik.enable=true` label
2. Check container is on `forge-network`
3. Restart Traefik: `docker restart forge-traefik`

---

## Files Referenced

- `AXIOM/.dev/infra/registry.yml` - Port allocations
- `AXIOM/forge/docker-compose.yml` - FORGE services
- `AXIOM/forge/config/traefik/dynamic.yml` - Traefik routes

---

## Performance Notes

- Start operations run in parallel where possible
- Stop operations run sequentially (dependencies)
- Status check completes in <2 seconds
- All paths are Windows-compatible (D:\Projects\...)

---

**For complex diagnosis or configuration changes, use DevOps Manager agent.**
