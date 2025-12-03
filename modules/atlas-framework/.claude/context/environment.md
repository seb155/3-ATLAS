# Environment Context

> Auto-detecte par ATLAS au debut de chaque session

## Detection Automatique

### OS Detection

```javascript
// Via platform
const os = process.platform; // 'win32' | 'linux' | 'darwin'
```

| Platform | Shell | Path Style |
|----------|-------|------------|
| win32 | PowerShell | `D:\Projects\` |
| linux | Bash | `/home/user/` |
| darwin | Zsh/Bash | `/Users/` |

### Mode Detection

| Fichier | Mode |
|---------|------|
| `docker-compose.dev.yml` | Development |
| `docker-compose.yml` | Production |
| `.env.local` | Local override |

## Environnement Actuel

```yaml
# Auto-rempli par ATLAS
os: [auto]
shell: [auto]
mode: [auto]
docker_running: [auto]
forge_services: [auto]
```

## Docker Status

### Containers FORGE

```bash
# Verification
docker ps --filter "name=forge-"
```

### Services Requis

| Service | Required For |
|---------|--------------|
| forge-postgres | All apps |
| forge-redis | Sessions, Cache |
| forge-traefik | Routing (prod) |
| forge-grafana | Monitoring |

## Variables d'Environnement

### Backend (SYNAPSE)

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/synapse
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key
DEBUG=true
```

### Frontend (All)

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Ports Utilises

> **IMPORTANT:** Cette section est la reference unique pour tous les AI agents.
> Toujours verifier ici avant d'assigner un nouveau port.

### FORGE Infrastructure (Shared)

| Port | Service | Container | Notes |
|------|---------|-----------|-------|
| 3000 | Grafana | forge-grafana | Monitoring UI |
| 3080 | Wiki (Docsify) | forge-wiki | Documentation |
| 3100 | Loki | forge-loki | Log aggregation |
| 5050 | pgAdmin | forge-pgadmin | DB Admin UI |
| 5433 | PostgreSQL | forge-postgres | Database (default: 5432 remapped) |
| 5555 | Prisma Studio | forge-prisma | DB Viewer |
| 6379 | Redis | forge-redis | Cache/Sessions |
| 7700 | MeiliSearch | forge-meilisearch | Search engine |
| 9090 | Prometheus | forge-prometheus | Metrics (reserved) |

### Applications

| Port | App | Service | Container | Notes |
|------|-----|---------|-----------|-------|
| 4000 | SYNAPSE | Frontend (Vite) | synapse-frontend | Main UI |
| 8000 | SYNAPSE | Backend API | synapse-backend | FastAPI internal |
| 8001 | SYNAPSE | Backend API (exposed) | synapse-backend | API Docs: /docs |
| 5173 | NEXUS | Frontend (Vite) | nexus-frontend | Reserved |
| 8100 | NEXUS | Backend API | nexus-backend | Reserved |
| 5174 | PRISM | Frontend (Vite) | prism-frontend | Reserved |
| 8200 | PRISM | Backend API | prism-backend | Reserved |
| 5175 | ATLAS | Frontend (Vite) | atlas-frontend | Reserved |
| 8300 | ATLAS | Backend API | atlas-backend | Reserved |

### Port Ranges (Convention)

| Range | Usage |
|-------|-------|
| 3000-3999 | Monitoring & Tools (Grafana, Loki, etc.) |
| 4000-4999 | SYNAPSE (Frontend: 4000, reserved: 4001-4099) |
| 5000-5099 | pgAdmin, Prisma, DB tools |
| 5173-5199 | Vite Dev Servers (NEXUS: 5173, PRISM: 5174, ATLAS: 5175) |
| 5400-5499 | Databases (PostgreSQL: 5433) |
| 5500-5599 | DB viewers (Prisma Studio: 5555) |
| 6000-6999 | Cache (Redis: 6379) |
| 7000-7999 | Search (MeiliSearch: 7700) |
| 8000-8099 | SYNAPSE Backend |
| 8100-8199 | NEXUS Backend |
| 8200-8299 | PRISM Backend |
| 8300-8399 | ATLAS Backend |
| 9000-9999 | Metrics & Observability |

### Port Conflict Resolution

Si un port est occupe:
1. Verifier avec `netstat -ano | findstr :<PORT>` (Windows) ou `lsof -i :<PORT>` (Linux/Mac)
2. Identifier le processus: `tasklist /FI "PID eq <PID>"` (Windows)
3. Soit arreter le processus, soit utiliser un port alternatif dans la range reservee

### Reserved Ports (Ne pas utiliser)

| Port | Reason |
|------|--------|
| 80 | HTTP (Traefik prod) |
| 443 | HTTPS (Traefik prod) |
| 22 | SSH |
| 3306 | MySQL (reserved for future) |
| 27017 | MongoDB (reserved for future) |
