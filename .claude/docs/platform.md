# AXIOM Platform Overview

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        ATLAS (AI OS)                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  CORTEX (Memory)  │  Agents  │  ECHO  │  Note_synch      │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   ┌──────────┐         ┌──────────┐         ┌──────────┐
   │   APEX   │         │  NEXUS   │         │ SYNAPSE  │
   └──────────┘         └──────────┘         └──────────┘
```

## Applications

| App | Purpose | URL | Status |
|-----|---------|-----|--------|
| **ATLAS** | AI OS (CORTEX, Agents, ECHO) | - | Active |
| **CORTEX** | Memory Engine (CAG/RAG) | `https://cortex.axoiq.com` | Dev |
| **APEX** | Enterprise Portal | `https://apex.axoiq.com` | Planning |
| **NEXUS** | Knowledge Portal + CORTEX UI | `https://nexus.axoiq.com` | Phase 2.0 |
| **SYNAPSE** | MBSE Platform (FastAPI + React 19) | `https://synapse.axoiq.com` | MVP Dec 2025 |

**FORGE** = Shared infrastructure via Traefik reverse proxy

## Quick Access URLs

| App | URL | Login |
|-----|-----|-------|
| **SYNAPSE** | https://synapse.axoiq.com | admin@aurumax.com / admin123! |
| **SYNAPSE API** | https://api.axoiq.com | - |
| **NEXUS** | https://nexus.axoiq.com | admin@aurumax.com / admin123! |
| **NEXUS API** | https://api-nexus.axoiq.com | - |
| **Grafana** | https://grafana.axoiq.com | admin / admin |
| **pgAdmin** | https://pgadmin.axoiq.com | admin@axoiq.com / admin |
| **Traefik** | https://traefik.axoiq.com | - |
| **FinDash** | https://findash.axoiq.com | - |

**IMPORTANT:** Always use domain names, NEVER localhost:PORT

## Quick Start

### Prerequisites (once)
```powershell
# As Administrator - add to hosts file
notepad C:\Windows\System32\drivers\etc\hosts
# Copy content from: .dev\infra\hosts-entries.txt
```

### Start Services
```powershell
# 1. FORGE (always first)
cd D:\Projects\AXIOM\forge
docker compose -f docker-compose.yml -f docker-compose.traefik.yml up -d

# 2. SYNAPSE
cd D:\Projects\AXIOM\apps\synapse
docker compose -f docker-compose.dev.yml -f docker-compose.traefik-labels.yml up -d

# 3. NEXUS
cd D:\Projects\AXIOM\apps\nexus
docker compose -f docker-compose.dev.yml -f docker-compose.traefik-labels.yml up -d
```

## Key Registry Files

| File | Purpose |
|------|---------|
| `.dev/infra/url-registry.yml` | URL source of truth |
| `.dev/infra/registry.yml` | Ports & services registry |
| `.dev/infra/QUICK-REFERENCE-URLS.md` | Quick URL reference |
