# AXIOM Infrastructure Documentation

**Version:** 1.1
**Last Updated:** 2025-11-29 16:00
**Environment:** Development
**Platform:** Docker + Docker Compose

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Network Topology](#network-topology)
4. [Service Inventory](#service-inventory)
5. [Port Allocations](#port-allocations)
6. [Getting Started](#getting-started)
7. [Operations](#operations)
8. [Troubleshooting](#troubleshooting)
9. [SSL/TLS Configuration](#ssltls-configuration)
10. [Monitoring & Logs](#monitoring--logs)

---

## Overview

**AXIOM** is a unified development platform built as a monorepo containing multiple applications:

| Application | Purpose | Status | Port Range |
|-------------|---------|--------|------------|
| **FORGE** | Shared infrastructure (DB, cache, logs, etc.) | ✅ Active | 3000-3999 |
| **SYNAPSE** | MBSE Platform (Model-Based Systems Engineering) | ✅ MVP | 4000-4999 |
| **NEXUS** | Knowledge Graph + Notes/Wiki | 🚧 Phase 1.5 | 5000-5999 |
| **PRISM** | Enterprise Dashboard | 📋 Planning | 6000-6999 |
| **ATLAS** | AI Collaboration Environment | 📋 Planning | 7000-7999 |

### Infrastructure Philosophy

- **Shared Infrastructure**: All applications use FORGE services (PostgreSQL, Redis, Loki, etc.)
- **Network Isolation**: Applications communicate via `forge-network` Docker bridge
- **Port Segregation**: Each application has a dedicated 1000-port range
- **SSL Local Development**: Uses mkcert for trusted local certificates
- **Observability-First**: Centralized logging (Loki) and monitoring (Grafana)

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        TRAEFIK (v3.6.2)                      │
│          Reverse Proxy + SSL/TLS Termination                 │
│       :80 (HTTP) | :443 (HTTPS) | :8888 (Dashboard)          │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴──────────────┐
         │                          │
    ┌────▼────┐              ┌──────▼──────┐
    │ SYNAPSE │              │    NEXUS    │
    │  :4000  │              │    :5173    │
    └────┬────┘              └──────┬──────┘
         │                          │
         └──────────┬───────────────┘
                    │
         ┌──────────▼──────────────────────────────────┐
         │          FORGE NETWORK                       │
         │  (Shared Infrastructure Services)            │
         │                                              │
         │  ┌─────────┐  ┌───────┐  ┌──────┐  ┌────┐  │
         │  │PostgreSQL│  │ Redis │  │ Loki │  │Meili│ │
         │  │  :5433  │  │ :6379 │  │:3100 │  │:7700│ │
         │  └─────────┘  └───────┘  └──────┘  └────┘  │
         │                                              │
         │  ┌────────┐  ┌────────┐  ┌──────┐          │
         │  │Grafana │  │pgAdmin │  │ Wiki │          │
         │  │ :3000  │  │ :5050  │  │:3080 │          │
         │  └────────┘  └────────┘  └──────┘          │
         └──────────────────────────────────────────────┘
```

### Technology Stack

#### FORGE Infrastructure
- **Database**: PostgreSQL 15 (Alpine)
- **Cache**: Redis 7 (Alpine)
- **Logs**: Loki 2.9.0 + Promtail
- **Monitoring**: Grafana 10.0.0
- **Search**: MeiliSearch v1.5
- **Reverse Proxy**: Traefik v3.6.2
- **Management**: pgAdmin 4, Prisma Studio
- **Docs**: Docsify (nginx)

#### SYNAPSE Stack
- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React 19 + TypeScript + Vite
- **State**: Zustand
- **Routing**: React Router v6
- **ORM**: SQLAlchemy + Alembic
- **Auth**: JWT (passlib + python-jose)

#### NEXUS Stack
- **Backend**: FastAPI
- **Frontend**: React + Vite
- **Knowledge Graph**: Neo4j (planned)

---

## Network Topology

### Docker Networks

AXIOM uses three Docker networks:

#### 1. `forge-network` (External Bridge)

**Purpose**: Shared infrastructure network for all AXIOM applications.

**Services**:
- All FORGE services (postgres, redis, loki, grafana, etc.)
- All application backends (synapse-backend, nexus-backend)
- All application frontends (synapse-frontend, nexus-frontend)
- Traefik reverse proxy

**Configuration**:
```yaml
networks:
  forge-network:
    external: true
```

**DNS Resolution**: Services can reach each other by container name:
- `synapse-backend` → `forge-postgres:5432`
- `synapse-frontend` → `synapse-backend:8000`
- `nexus-backend` → `forge-redis:6379`

#### 2. `synapse-internal` (Internal Bridge)

**Purpose**: Production-only internal network for SYNAPSE services.

**Services** (production only):
- synapse-backend
- synapse-frontend
- synapse-nginx
- synapse-ollama
- synapse-redis (separate from FORGE redis)

**Isolation**: Not connected to external networks.

#### 3. `default` (Compose-Local)

**Purpose**: Default network created by docker-compose for each stack.

**Usage**: Services within the same docker-compose stack can communicate.

### Network Diagram

```
┌────────────────────────────────────────────────────────┐
│                   forge-network                         │
│  (All apps + shared infrastructure)                     │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  FORGE   │  │ SYNAPSE  │  │  NEXUS   │             │
│  │ Services │  │ Services │  │ Services │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│              synapse-internal (Production)              │
│  (Isolated production network)                          │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  nginx   │  │ backend  │  │ frontend │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└────────────────────────────────────────────────────────┘
```

---

## Service Inventory

### FORGE Infrastructure Services

| Service | Container | Image | Ports | Purpose |
|---------|-----------|-------|-------|---------|
| **PostgreSQL** | `forge-postgres` | `postgres:15-alpine` | 5433→5432 | Shared database for all apps |
| **Redis** | `forge-redis` | `redis:7-alpine` | 6379→6379 | Shared cache + pub/sub |
| **Loki** | `forge-loki` | `grafana/loki:2.9.0` | 3100→3100 | Log aggregation |
| **Promtail** | `forge-promtail` | `grafana/promtail:2.9.0` | - | Log collection agent |
| **Grafana** | `forge-grafana` | `grafana/grafana:10.0.0` | 3000→3000 | Observability dashboard |
| **MeiliSearch** | `forge-meilisearch` | `getmeili/meilisearch:v1.5` | 7700→7700 | Full-text search |
| **pgAdmin** | `forge-pgadmin` | `dpage/pgadmin4:latest` | 5050→80 | PostgreSQL GUI |
| **Prisma Studio** | `forge-prisma` | `prisma/studio:latest` | 5555→5555 | Database browser |
| **Wiki** | `forge-wiki` | `nginx:alpine` | 3080→3080 | Documentation (Docsify) |
| **Traefik** | `forge-traefik` | `traefik:v3.6.2` | 80, 443, 8888 | Reverse proxy + SSL |

**Health Checks**:
- PostgreSQL: `pg_isready -U postgres`
- Redis: `redis-cli ping`
- Loki: `wget --spider http://localhost:3100/ready`
- Grafana: `wget --spider http://localhost:3000/api/health`
- MeiliSearch: `curl http://localhost:7700/health`
- Traefik: `traefik healthcheck --ping`

### SYNAPSE Application Services

#### Development Environment

| Service | Container | Ports | Networks | Dependencies |
|---------|-----------|-------|----------|--------------|
| **Backend** | `synapse-backend` | 8001→8000 | default, forge-network | forge-postgres, forge-redis, forge-loki, forge-meilisearch |
| **Frontend** | `synapse-frontend` | 4000→4000 | default, forge-network | synapse-backend |

**Compose Files**:
- `apps/synapse/docker-compose.dev.yml` - Main development stack
- `apps/synapse/docker-compose.traefik-labels.yml` - Traefik routing (overlay)

**Frontend Vite Proxy**:
```javascript
server: {
  proxy: {
    '/api/v1': {
      target: 'http://synapse-backend:8000',  // Uses Docker DNS
      changeOrigin: true,
      rewrite: (path) => path
    }
  }
}
```

#### Production Environment

| Service | Container | Ports | Networks |
|---------|-----------|-------|----------|
| **Backend** | `synapse-backend` | - | synapse-internal |
| **Frontend** | `synapse-frontend` | - | synapse-internal |
| **Nginx** | `synapse-nginx` | 80, 443 | synapse-internal, forge-network |
| **Ollama** | `synapse-ollama` | 11434 | synapse-internal |
| **Redis** | `synapse-redis` | - | synapse-internal |

**Compose File**: `apps/synapse/docker-compose.yml`

### NEXUS Application Services

#### Development Environment

| Service | Container | Ports | Networks | Dependencies |
|---------|-----------|-------|----------|--------------|
| **Backend** | `nexus-backend` | 8000→8000 | forge-network | forge-postgres, forge-redis |
| **Frontend** | `nexus-frontend` | 5173→5173 | forge-network | nexus-backend |

**Compose File**: `apps/nexus/standalone/docker-compose.dev.yml`

### Personal Projects (PRISM Range 6000-6999)

Personal projects are integrated with FORGE infrastructure for shared services and unified Traefik routing.

#### Note_synch - TriliumNext Bidirectional Sync

| Service | Container | Ports | Traefik Route |
|---------|-----------|-------|---------------|
| **Dashboard** | `trilium-sync` | 6200→8080 | trilium.axoiq.com |
| **Neo4j Browser** | `notes-neo4j` | 6201→7474 | neo4j.axoiq.com |
| **Neo4j Bolt** | `notes-neo4j` | 6202→7687 | - |
| **Graph API** | `notes-graph-api` | 6203→8081 | graph.axoiq.com |

**Location**: `D:\Projects\Note_synch\docker-compose.yml`

#### Homelab_MSH - Proxmox Monitoring

| Service | Container | Ports | Traefik Route |
|---------|-----------|-------|---------------|
| **Dashboard** | `homelab-dashboard` | 6300→3000 | homelab.axoiq.com |
| **Pulse** | `pulse` | 6301→7655 | pulse.axoiq.com |
| **PostgreSQL** | `homelab-db` | (internal) | - |

**Location**: `D:\Projects\8-Perso\Homelab_MSH\dashboard\`

#### FinDash - Personal Finance Dashboard

| Service | Container | Ports | Traefik Route |
|---------|-----------|-------|---------------|
| **App** | `findash-app` | 6400→5173 | findash.axoiq.com |

**Location**: `D:\Projects\8-Perso\FinDash\docker-compose.yml`

#### Pilote-Patrimoine - Property Management

| Service | Container | Ports | Traefik Route |
|---------|-----------|-------|---------------|
| **App** | `pilote-patrimoine` | 6100→80 | nest.axoiq.com |

**Location**: `D:\Projects\8-Perso\Pilote-Patrimoine\docker-compose.yml`

#### Integration Requirements

All personal projects must:
1. Connect to `forge-network` (external)
2. Include Traefik labels for HTTPS routing
3. Use ports in range 6000-6999
4. Add healthcheck for monitoring

**Example Traefik Labels**:
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.myapp.rule=Host(`myapp.axoiq.com`)"
  - "traefik.http.routers.myapp.entrypoints=websecure"
  - "traefik.http.routers.myapp.tls.certresolver=letsencrypt"
  - "traefik.http.services.myapp.loadbalancer.server.port=80"
networks:
  forge-network:
    external: true
```

---

## Port Allocations

### Port Allocation Strategy

Each application has a **dedicated 1000-port range**:

| Range | Application | Status | Usage |
|-------|-------------|--------|-------|
| **3000-3999** | FORGE | Active | 9 ports allocated |
| **4000-4999** | SYNAPSE | Active | 2 ports allocated |
| **5000-5999** | NEXUS | Phase 1.5 | 2 ports allocated |
| **6000-6999** | PRISM/Personal | Active | 8 ports allocated |
| **7000-7999** | ATLAS | Available | - |

### Currently Allocated Ports

#### FORGE (3000-3999)
- **3000**: Grafana (observability)
- **3080**: Wiki (documentation)
- **3100**: Loki (log aggregation)

#### System Ports
- **80**: Traefik HTTP
- **443**: Traefik HTTPS
- **8888**: Traefik Dashboard

#### Database/Cache Ports
- **5433**: PostgreSQL (external)
- **5050**: pgAdmin
- **5555**: Prisma Studio
- **6379**: Redis
- **7700**: MeiliSearch

#### SYNAPSE (4000-4999)
- **4000**: Frontend (React + Vite)
- **8001**: Backend (FastAPI) - *Note: Outside range but grandfathered*

#### NEXUS (5000-5999)
- **5173**: Frontend (Vite)
- **8000**: Backend (FastAPI) - *Conflicts with synapse-backend in production*

#### PRISM/Personal Projects (6000-6999)
- **6100**: Pilote-Patrimoine (nest.axoiq.com)
- **6200**: Note_synch Dashboard (trilium.axoiq.com)
- **6201**: Note_synch Neo4j Browser (neo4j.axoiq.com)
- **6202**: Note_synch Neo4j Bolt
- **6203**: Note_synch Graph API (graph.axoiq.com)
- **6300**: Homelab Dashboard (homelab.axoiq.com)
- **6301**: Homelab Pulse (pulse.axoiq.com)
- **6400**: FinDash (findash.axoiq.com)

### Port Conflict Detection

**Rule**: Each port can only be allocated to ONE service.

**Validation**: Run `.dev/scripts/validate-infra.ps1` to check for conflicts.

### Available Ports

- **SYNAPSE**: 4001-4999 (998 available)
- **NEXUS**: 5001-5172, 5174-5999 (998 available)
- **PRISM/Personal**: 6001-6099, 6102-6199, 6204-6299, 6302-6399, 6401-6999 (992 available)
- **ATLAS**: 7000-7999 (1000 available)

---

## Getting Started

### Prerequisites

- Docker Desktop for Windows (with WSL2 backend)
- PowerShell 5.1+
- mkcert (for local SSL certificates)
- Git

### Quick Start

#### Option 1: All-in-One Script (Recommended)

```powershell
# Start FORGE + SYNAPSE
.\dev.ps1
```

This script:
1. Starts FORGE infrastructure
2. Waits for services to be healthy
3. Starts SYNAPSE development stack
4. Opens browser to http://localhost:4000

#### Option 2: Manual Startup

**Step 1: Create forge-network (one-time)**

```powershell
docker network create forge-network
```

**Step 2: Start FORGE Infrastructure**

```powershell
cd forge
docker-compose up -d
```

**Step 3: Verify FORGE is Healthy**

```powershell
docker ps
# Should show all FORGE containers with "Up" status
```

**Step 4: Start SYNAPSE**

```powershell
cd apps\synapse
docker-compose -f docker-compose.dev.yml up --build
```

**Step 5: Access Applications**

- Frontend: http://localhost:4000
- Backend API: http://localhost:8001/docs
- Grafana: http://localhost:3000
- Wiki: http://localhost:3080

#### Option 3: With Traefik SSL (Domain Access)

**Step 1: Generate SSL Certificates (one-time)**

```powershell
cd forge
.\generate-ssl-certs.ps1
```

**Step 2: Add hosts file entries (one-time)**

Add to `C:\Windows\System32\drivers\etc\hosts`:

```
127.0.0.1 synapse.axoiq.com
127.0.0.1 api.axoiq.com
127.0.0.1 traefik.axoiq.com
127.0.0.1 nexus.axoiq.com
127.0.0.1 grafana.axoiq.com
```

**Step 3: Start FORGE with Traefik**

```powershell
cd forge
docker-compose -f docker-compose.yml -f docker-compose.traefik.yml up -d
```

**Step 4: Start SYNAPSE with Traefik Labels**

```powershell
cd apps\synapse
docker-compose -f docker-compose.dev.yml -f docker-compose.traefik-labels.yml up -d
```

**Step 5: Access via Domains**

- Frontend: https://synapse.axoiq.com (no SSL warning!)
- Backend API: https://api.axoiq.com/docs
- Traefik Dashboard: http://traefik.axoiq.com:8888

---

## Operations

### Starting Services

**Start All FORGE Services**:
```powershell
cd forge
docker-compose up -d
```

**Start Specific FORGE Service**:
```powershell
cd forge
docker-compose up -d forge-postgres forge-redis
```

**Start SYNAPSE Development**:
```powershell
cd apps\synapse
docker-compose -f docker-compose.dev.yml up --build
```

**Start NEXUS Development**:
```powershell
cd apps\nexus\standalone
docker-compose -f docker-compose.dev.yml up --build
```

### Stopping Services

**Stop SYNAPSE**:
```powershell
cd apps\synapse
docker-compose -f docker-compose.dev.yml down
```

**Stop FORGE**:
```powershell
cd forge
docker-compose down
```

**Stop and Remove Volumes** (⚠️ Data Loss):
```powershell
docker-compose down -v
```

### Rebuilding Services

**Rebuild SYNAPSE Backend**:
```powershell
cd apps\synapse
docker-compose -f docker-compose.dev.yml build --no-cache backend
docker-compose -f docker-compose.dev.yml up -d backend
```

**Rebuild SYNAPSE Frontend**:
```powershell
cd apps\synapse
docker-compose -f docker-compose.dev.yml build --no-cache frontend
docker-compose -f docker-compose.dev.yml up -d frontend
```

### Viewing Logs

**View All Logs (Follow Mode)**:
```powershell
docker-compose -f docker-compose.dev.yml logs -f
```

**View Specific Service Logs**:
```powershell
docker logs synapse-backend -f --tail 100
```

**View Last 50 Lines**:
```powershell
docker logs synapse-backend --tail 50
```

### Database Operations

**Access PostgreSQL Shell**:
```powershell
docker exec -it forge-postgres psql -U postgres -d synapse
```

**Run Migrations (SYNAPSE)**:
```powershell
# Inside backend container
docker exec -it synapse-backend alembic upgrade head
```

**Create Migration**:
```powershell
docker exec -it synapse-backend alembic revision --autogenerate -m "description"
```

### Redis Operations

**Access Redis CLI**:
```powershell
docker exec -it forge-redis redis-cli
```

**View All Keys**:
```powershell
docker exec -it forge-redis redis-cli KEYS "*"
```

**Flush All Data** (⚠️ Data Loss):
```powershell
docker exec -it forge-redis redis-cli FLUSHALL
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Frontend Container Not Starting

**Symptoms**:
- Container not visible in `docker ps`
- Port 4000 not accessible
- Container exits immediately after start

**Diagnosis**:
```powershell
# Check frontend logs
docker logs synapse-frontend --tail 50

# Check if container exists but exited
docker ps -a | findstr synapse-frontend
```

**Common Causes**:

1. **Not on forge-network**
   - Vite proxy can't reach `synapse-backend:8000`
   - Fix: Ensure `networks: [default, forge-network]` in docker-compose.dev.yml

2. **Port conflict**
   - Another process using port 4000
   - Find: `netstat -ano | findstr :4000`
   - Kill: `taskkill /PID <PID> /F`

3. **Volume mount failure**
   - Individual file mounts fail on Windows
   - Fix: Use directory mount instead

#### Issue 2: Backend Can't Connect to Database

**Symptoms**:
- Backend logs show "connection refused" errors
- Can't connect to `forge-postgres:5432`

**Diagnosis**:
```powershell
# Check if backend is on forge-network
docker inspect synapse-backend | findstr forge-network

# Check if postgres is running
docker ps | findstr forge-postgres
```

**Fix**:
1. Ensure PostgreSQL is running: `docker-compose up -d forge-postgres`
2. Ensure backend is on `forge-network`
3. Verify `DATABASE_URL` uses `forge-postgres:5432` (NOT localhost:5433)

#### Issue 3: Traefik SSL Certificate Errors

**Symptoms**:
- Browser shows SSL warnings
- ACME certificate validation failures
- "Domain name does not end with a valid public suffix (TLD)"

**Root Cause**: Trying to use Let's Encrypt ACME for local development domain.

**Fix**:

1. **Use local mkcert certificates** (recommended for dev):

Edit `docker-compose.traefik-labels.yml`:
```yaml
# CHANGE FROM:
- "traefik.http.routers.synapse.tls.certresolver=letsencrypt"

# TO:
- "traefik.http.routers.synapse.tls=true"
```

2. **Generate mkcert certificates**:
```powershell
cd forge
.\generate-ssl-certs.ps1
```

3. **Restart Traefik**:
```powershell
docker restart forge-traefik
```

#### Issue 4: Port Already Allocated

**Symptoms**:
- `Error: port is already allocated`
- Container fails to start

**Find What's Using Port**:
```powershell
# Windows
netstat -ano | findstr :<PORT>

# Get process name
tasklist | findstr <PID>
```

**Solutions**:
1. Kill the process: `taskkill /PID <PID> /F`
2. Change port in docker-compose.yml
3. Stop conflicting Docker container

#### Issue 5: Docker Network Not Found

**Symptoms**:
- `network forge-network declared as external, but could not be found`

**Fix**:
```powershell
docker network create forge-network
```

### Health Check Commands

**Check All Container Status**:
```powershell
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Check Service Health**:
```powershell
# PostgreSQL
docker exec forge-postgres pg_isready -U postgres

# Redis
docker exec forge-redis redis-cli ping

# Backend API
curl http://localhost:8001/health
```

**Check Network Membership**:
```powershell
docker inspect <container_name> --format '{{range $net, $config := .NetworkSettings.Networks}}{{$net}} {{end}}'
```

**Validate Infrastructure**:
```powershell
.\.dev\scripts\validate-infra.ps1
```

### Emergency Procedures

**Nuclear Option - Reset Everything** (⚠️ ALL DATA LOST):
```powershell
# Stop all containers
docker stop $(docker ps -aq)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all volumes
docker volume prune -f

# Remove networks
docker network prune -f

# Recreate forge-network
docker network create forge-network

# Rebuild from scratch
cd forge && docker-compose up -d
cd apps\synapse && docker-compose -f docker-compose.dev.yml up --build
```

---

## SSL/TLS Configuration

### Local Development (mkcert)

**Certificate Provider**: mkcert (local CA)

**Wildcard Certificate**: `*.axoiq.com`

**Valid For**:
- synapse.axoiq.com
- api.axoiq.com
- nexus.axoiq.com
- traefik.axoiq.com
- grafana.axoiq.com

**Certificate Location**: `forge/config/traefik/`

**Files**:
- `axoiq.com.crt` - Certificate
- `axoiq.com.key` - Private key
- `certificates.yml` - Traefik config

**Traefik Configuration**:

File provider enabled:
```yaml
--providers.file.directory=/etc/traefik/dynamic
--providers.file.watch=true
```

Certificate configuration (`forge/config/traefik/certificates.yml`):
```yaml
tls:
  certificates:
    - certFile: /etc/traefik/dynamic/axoiq.com.crt
      keyFile: /etc/traefik/dynamic/axoiq.com.key
```

**Using Certificates in Traefik Labels**:

```yaml
labels:
  - "traefik.http.routers.synapse.tls=true"  # Uses file provider certs
```

**NOT THIS**:
```yaml
labels:
  - "traefik.http.routers.synapse.tls.certresolver=letsencrypt"  # ❌ Fails for local
```

### Production (Let's Encrypt)

For production deployment:

1. **Change TLS Mode**:
```yaml
--certificatesresolvers.letsencrypt.acme.caserver=https://acme-v02.api.letsencrypt.org/directory  # Remove staging
```

2. **Use ACME Resolver**:
```yaml
labels:
  - "traefik.http.routers.synapse.tls.certresolver=letsencrypt"
```

3. **Set Production Domain**:
```bash
DOMAIN=yourdomain.com
ACME_EMAIL=admin@yourdomain.com
```

---

## Monitoring & Logs

### Log Aggregation (Loki + Grafana)

**Architecture**:
- **Loki**: Log aggregation service (port 3100)
- **Promtail**: Log collection agent (runs on Docker host)
- **Grafana**: Visualization dashboard (port 3000)

**Log Collection**:
- Promtail scrapes `/var/lib/docker/containers/**/*.log`
- Sends logs to Loki at `http://forge-loki:3100`
- Grafana queries Loki for visualization

**Access Grafana**:
- URL: http://localhost:3000
- Default credentials: admin/admin (change on first login)

**Loki Data Source**:
Already configured in Grafana provisioning:
- URL: http://forge-loki:3100
- Name: Loki

**Querying Logs**:

LogQL examples:
```logql
# All SYNAPSE logs
{container_name=~"synapse-.*"}

# Backend errors only
{container_name="synapse-backend"} |= "ERROR"

# Frontend requests in last hour
{container_name="synapse-frontend"} |= "request" [1h]
```

### Health Monitoring

**Container Health Checks**:

All critical services have health checks defined:
- PostgreSQL: `pg_isready -U postgres`
- Redis: `redis-cli ping`
- Loki: `wget --spider http://localhost:3100/ready`
- Grafana: `wget --spider http://localhost:3000/api/health`

**Check Container Health**:
```powershell
docker inspect --format='{{.State.Health.Status}}' <container_name>
```

### Metrics (Prometheus - Optional)

Traefik metrics enabled:
```yaml
--metrics.prometheus=true
```

Metrics endpoint: http://localhost:8080/metrics

---

## Maintenance

### Backups

**Volumes to Backup**:
- `postgres-data` - All application databases
- `redis-data` - Cache snapshots
- `grafana-data` - Dashboards and config
- `loki-data` - Log storage
- `meili-data` - Search indexes

**Backup Command**:
```powershell
# Backup PostgreSQL
docker exec forge-postgres pg_dumpall -U postgres > backup_$(Get-Date -Format 'yyyyMMdd').sql

# Backup all volumes
docker run --rm -v postgres-data:/data -v D:\backups:/backup alpine tar czf /backup/postgres_data_$(date +%Y%m%d).tar.gz /data
```

**Restore PostgreSQL**:
```powershell
cat backup.sql | docker exec -i forge-postgres psql -U postgres
```

### Updates

**Check for Updates**:
```powershell
# Pull latest images
docker-compose pull

# Rebuild with new images
docker-compose up -d --build
```

**Update Strategy**:
1. **Security Updates**: Apply immediately
2. **Minor Versions**: Weekly check
3. **Major Versions**: Manual testing required

### Log Retention

- **Docker Logs**: 7 days (managed by Docker daemon)
- **Loki Logs**: 30 days retention
- **Grafana**: Unlimited

---

## Quick Reference

### Common Commands

```powershell
# Start everything
.\dev.ps1

# View status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# View logs
docker logs synapse-backend -f --tail 100

# Restart service
docker restart synapse-backend

# Rebuild service
docker-compose -f docker-compose.dev.yml build --no-cache backend

# Access database
docker exec -it forge-postgres psql -U postgres -d synapse

# Access Redis
docker exec -it forge-redis redis-cli

# Validate infrastructure
.\.dev\scripts\validate-infra.ps1

# Check ports
.\.dev\scripts\axiom.ps1 ports
```

### Access URLs

#### Development (localhost)
- SYNAPSE Frontend: http://localhost:4000
- SYNAPSE API Docs: http://localhost:8001/docs
- Grafana: http://localhost:3000
- Wiki: http://localhost:3080
- Traefik Dashboard: http://localhost:8888
- pgAdmin: http://localhost:5050
- Prisma Studio: http://localhost:5555

#### Development (with Traefik SSL)
- SYNAPSE Frontend: https://synapse.axoiq.com
- SYNAPSE API: https://api.axoiq.com/docs
- Traefik Dashboard: https://traefik.axoiq.com:8888
- Grafana: https://grafana.axoiq.com

### File Locations

| Component | Path |
|-----------|------|
| Infrastructure Registry | `.dev/infra/registry.yml` |
| This Documentation | `.dev/infra/infrastructure.md` |
| Infrastructure Changelog | `.dev/infra/CHANGELOG.md` |
| DevOps Manager Agent | `.claude/agents/devops-manager.md` |
| Infra Skill | `.claude/skills/infra.md` |
| Validation Script | `.dev/scripts/validate-infra.ps1` |
| AXIOM CLI | `.dev/scripts/axiom.ps1` |
| FORGE Compose | `forge/docker-compose.yml` |
| Traefik Compose | `forge/docker-compose.traefik.yml` |
| SYNAPSE Dev Compose | `apps/synapse/docker-compose.dev.yml` |
| SYNAPSE Traefik Labels | `apps/synapse/docker-compose.traefik-labels.yml` |

---

**For AI Agents**: This documentation is the complete reference for AXIOM infrastructure. When diagnosing issues or planning changes, always:
1. Read [.dev/infra/registry.yml](.dev/infra/registry.yml) for current state
2. Validate against rules defined in registry
3. Update this documentation after changes
4. Log changes to [.dev/infra/CHANGELOG.md](.dev/infra/CHANGELOG.md)
5. Use DevOps Manager agent for complex diagnosis
