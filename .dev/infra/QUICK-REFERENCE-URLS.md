# Quick Reference - AXIOM URLs

**Source of Truth:** `.dev/infra/url-registry.yml`
**Last Updated:** 2025-11-29

---

## 🚀 AXIOM Applications

### AI OS (Central System)

| Component | URL | Status | Description |
|-----------|-----|--------|-------------|
| **ATLAS** | - | ✅ Active | AI OS (Claude Code agents) |
| **CORTEX** | https://cortex.axoiq.com | 🚧 Development | Memory Engine (in ATLAS) |

### Applications

| App | URL | Status |
|-----|-----|--------|
| **SYNAPSE** (Frontend) | https://synapse.axoiq.com | ✅ Active |
| **SYNAPSE** (API) | https://api.axoiq.com | ✅ Active |
| **NEXUS** (Frontend) | https://nexus.axoiq.com | ✅ Active |
| **NEXUS** (API) | https://api-nexus.axoiq.com | ✅ Active |
| **APEX** | https://apex.axoiq.com | 📋 Planned |

---

## 🔧 FORGE Infrastructure

| Service | URL | Port | Credentials |
|---------|-----|------|-------------|
| **Traefik Dashboard** | https://traefik.axoiq.com | 8888 | - |
| **Grafana** | https://grafana.axoiq.com | 3000 | admin / admin |
| **pgAdmin** | https://pgadmin.axoiq.com | 5050 | admin@axoiq.com / admin |
| **Prisma Studio** | https://prisma.axoiq.com | 5555 | - |
| **Loki** | https://loki.axoiq.com | 3100 | API only |
| **Wiki (Docsify)** | https://wiki.axoiq.com | 3080 | - |
| **MeiliSearch** | - | 7700 | API only (no UI) |
| **PostgreSQL** | - | 5433 | Internal only |
| **Redis** | - | 6379 | Internal only |

---

## 📱 Personal Projects

| App | URL | Status | Description |
|-----|-----|--------|-------------|
| **FinDash** | https://findash.axoiq.com | ✅ Active | Personal finance dashboard |
| **Pulse** | https://pulse.axoiq.com | 📋 Planned | Homelab monitor |
| **Trilium** | https://trilium.axoiq.com | 📋 Planned | Hierarchical notes |
| **Neo4j** | https://neo4j.axoiq.com | 📋 Planned | Graph database |
| **Homelab** | https://homelab.axoiq.com | 📋 Planned | Infrastructure dashboard |

---

## 🧪 Testing & QA (Future)

| Service | URL | Status |
|---------|-----|--------|
| **ReportPortal** | https://reportportal.axoiq.com | 📋 Planned |
| **Allure Reports** | https://allure.axoiq.com | 📋 Planned |

---

## 📋 Port Allocation Ranges

| Application | Port Range | Status |
|-------------|------------|--------|
| **FORGE** | 3000-3999 | 9 ports allocated |
| **SYNAPSE** | 4000-4999 | 2 ports allocated |
| **NEXUS** | 5000-5999 | 2 ports allocated |
| **APEX** | 6000-6999 | Reserved |
| **CORTEX** | 7000-7999 | 2 ports allocated |

---

## 🔍 Quick Access Commands

### Start Infrastructure
```powershell
# FORGE (always first!)
cd D:\Projects\AXIOM\forge
docker compose -f docker-compose.yml -f docker-compose.traefik.yml up -d

# SYNAPSE
cd D:\Projects\AXIOM\apps\synapse
docker compose -f docker-compose.dev.yml -f docker-compose.traefik-labels.yml up -d

# NEXUS
cd D:\Projects\AXIOM\apps\nexus
docker compose -f docker-compose.dev.yml -f docker-compose.traefik-labels.yml up -d

# FinDash
cd D:\Projects\8-Perso\FinDash
docker compose up -d
```

### Verify DNS
```powershell
# Test domain resolution
ping synapse.axoiq.com
ping nexus.axoiq.com
ping findash.axoiq.com

# Flush DNS cache (if needed)
ipconfig /flushdns
```

### Check Traefik Status
```powershell
# Traefik dashboard
http://localhost:8888
# or
https://traefik.axoiq.com

# Check running services
docker ps | findstr forge
docker ps | findstr synapse
docker ps | findstr nexus
```

---

## ⚠️ Important Rules

### DO NOT
- ❌ Access via `localhost:PORT` (use domains instead)
- ❌ Start apps without Traefik labels (`-f docker-compose.traefik-labels.yml`)
- ❌ Modify port allocations without updating `url-registry.yml`

### ALWAYS
- ✅ Use https://{app}.axoiq.com for all access
- ✅ Start FORGE before any other application
- ✅ Read `url-registry.yml` before allocating new ports/domains
- ✅ Update registry when adding new services

---

## 📚 Related Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| **URL Registry** | `.dev/infra/url-registry.yml` | Source of truth (THIS IS AUTHORITATIVE) |
| **Hosts Template** | `.dev/infra/hosts-entries.txt` | Windows hosts file entries |
| **Traefik Rule** | `.claude/agents/rules/10-traefik-routing.md` | Agent routing rules |
| **Registry Rule** | `.claude/agents/rules/11-url-registry.md` | Agent URL allocation process |
| **Infrastructure** | `.dev/infra/infrastructure.md` | Full infrastructure documentation |

---

## 🤖 For AI Agents

**BEFORE creating any new service or application:**

1. **Read** `.dev/infra/url-registry.yml`
2. **Check** available ports in appropriate range
3. **Validate** domain follows convention (`{app}.axoiq.com`)
4. **Ask user** for approval using `AskUserQuestion`
5. **Update** registry after allocation

**Validation Skill:** Use `skill: "zz-url-check"` to verify allocations

---

**Generated:** 2025-11-29
**Maintainer:** AXIOM Platform
**Version:** 1.0.0
