# Infrastructure Changelog

All notable changes to AXIOM infrastructure will be documented in this file.

**Format**: Based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

**Categories**:
- `Added` - New services, networks, or features
- `Changed` - Configuration changes to existing services
- `Fixed` - Bug fixes and corrections
- `Removed` - Deprecated or removed services
- `Security` - Security-related changes

---

## [Unreleased]

### Planned
- ATLAS AI environment (port range 7000-7999)
- Neo4j graph database for NEXUS
- Automated backup system for all volumes
- Prometheus metrics collection
- Alerting system (Alertmanager)

---

## [1.1.0] - 2025-11-29

### Added - Personal Projects Integration

- ✅ Integrated 4 personal projects with FORGE infrastructure
- ✅ Port allocations in PRISM range (6000-6999):
  - 6100: Pilote-Patrimoine (nest.axoiq.com)
  - 6200-6203: Note_synch (trilium, neo4j, graph-api)
  - 6300-6301: Homelab_MSH (dashboard, pulse)
  - 6400: FinDash (findash.axoiq.com)
- ✅ Traefik routes for all personal projects
- ✅ Added FinDash to Traefik dynamic.yml (file provider)

### Added - Docker Operations Skills & Scripts

- ✅ Created `.claude/skills/zz-docker-ops.md` - Start/Stop/Restart/Status operations
- ✅ Created `.claude/skills/zz-network-test.md` - Quick network connectivity test
- ✅ Created `.dev/scripts/docker-ops.ps1` - PowerShell CLI for Docker operations

### Changed - SYNAPSE Production

- ✅ Migrated from Nginx to Traefik labels
- ✅ Removed nginx service from docker-compose.prod.yml
- ✅ Added CORS and security headers middlewares

### Changed - Docker Compose Cleanup

- ✅ Removed obsolete `version: '3.8'` declarations
- ✅ Resolved port conflicts (3000, 5432, 5173)
- ✅ All personal projects now use forge-network

### Removed

- ✅ Pilote-Patrimoine: Removed standalone Traefik (docker-compose.prod.yml, traefik-dynamic.yml)

---

## [1.0.0] - 2025-11-28

### Added - Infrastructure Management System
- ✅ Created central infrastructure registry (`.dev/infra/registry.yml`)
- ✅ Created comprehensive infrastructure documentation (`.dev/infra/infrastructure.md`)
- ✅ Created infrastructure changelog (this file)
- ✅ Defined port allocation ranges for all applications
- ✅ Documented all Docker networks and their purposes
- ✅ Created complete service inventory with dependencies
- ✅ Defined startup order with health checks
- ✅ Created validation rules for ports, networks, and dependencies
- ✅ Documented environment variables and SSL/TLS configuration

### Changed - SYNAPSE Docker Configuration
- ✅ Added `container_name: synapse-frontend` to frontend service
- ✅ Added `networks: [default, forge-network]` to frontend service
- ✅ Fixed: Frontend can now resolve `synapse-backend:8000` via Docker DNS
- ✅ Fixed: Vite dev server proxy now works correctly

### Changed - Traefik SSL Configuration
- ✅ Changed SYNAPSE backend from `tls.certresolver=letsencrypt` to `tls=true`
- ✅ Changed SYNAPSE frontend from `tls.certresolver=letsencrypt` to `tls=true`
- ✅ Changed Traefik dashboard from `tls.certresolver=letsencrypt` to `tls=true`
- ✅ Now uses local mkcert certificates via file provider (no ACME errors)

### Fixed - Frontend Container Issues
- ✅ Fixed: Frontend container now starts successfully
- ✅ Fixed: Frontend container visible in Docker Desktop
- ✅ Fixed: Port 4000 now serves SYNAPSE frontend (not wiki)
- ✅ Fixed: Vite proxy can reach backend via Docker DNS

---

## [0.2.5] - 2025-11-27

### Added - AssetHistory Integration
- ✅ Integrated AssetHistory component into AssetDetails component
- ✅ Added "Version History" tab with History icon
- ✅ Fixed apiClient import (default import instead of named)

### Added - SYNAPSE Services
- ✅ SYNAPSE backend (FastAPI) on port 8001
- ✅ SYNAPSE frontend (React 19 + Vite) on port 4000
- ✅ Development docker-compose configuration
- ✅ Production docker-compose configuration with nginx

---

## [0.2.0] - 2025-11-20

### Added - Traefik Reverse Proxy
- ✅ Traefik v3.6.2 container
- ✅ HTTP entrypoint (port 80)
- ✅ HTTPS entrypoint (port 443)
- ✅ Dashboard (port 8888)
- ✅ Docker provider for automatic service discovery
- ✅ File provider for static configuration
- ✅ Let's Encrypt ACME certificate resolver
- ✅ Prometheus metrics enabled
- ✅ Traefik labels for SYNAPSE application

### Added - SSL Certificates
- ✅ mkcert wildcard certificate for `*.axoiq.com`
- ✅ Certificate files in `forge/config/traefik/`
- ✅ Traefik file provider configuration (`certificates.yml`)
- ✅ PowerShell script for certificate generation (`generate-ssl-certs.ps1`)

### Added - Domain Configuration
- ✅ Domain: `axoiq.com`
- ✅ SYNAPSE frontend: `synapse.axoiq.com`
- ✅ SYNAPSE backend API: `api.axoiq.com`
- ✅ Traefik dashboard: `traefik.axoiq.com`
- ✅ Hosts file entries for local development

---

## [0.1.0] - 2025-11-15

### Added - FORGE Infrastructure (Initial Setup)
- ✅ PostgreSQL 15 (Alpine) - Port 5433
- ✅ Redis 7 (Alpine) - Port 6379
- ✅ Grafana 10.0.0 - Port 3000
- ✅ Loki 2.9.0 - Port 3100
- ✅ Promtail - Log collection agent
- ✅ MeiliSearch v1.5 - Port 7700
- ✅ pgAdmin 4 - Port 5050
- ✅ Prisma Studio - Port 5555
- ✅ Docsify Wiki (nginx) - Port 3080

### Added - Docker Networks
- ✅ `forge-network` - External bridge network for shared infrastructure
- ✅ `synapse-internal` - Internal network for SYNAPSE production

### Added - Docker Volumes
- ✅ `postgres-data` - PostgreSQL data persistence
- ✅ `redis-data` - Redis data persistence
- ✅ `grafana-data` - Grafana dashboards and config
- ✅ `loki-data` - Loki log storage
- ✅ `meili-data` - MeiliSearch indexes
- ✅ `traefik-certs` - Traefik SSL certificates
- ✅ `traefik-logs` - Traefik access logs

### Added - Configuration Files
- ✅ `forge/docker-compose.yml` - Main FORGE stack
- ✅ `forge/config/loki.yml` - Loki configuration
- ✅ `forge/config/promtail.yml` - Promtail configuration
- ✅ `apps/synapse/docker-compose.dev.yml` - SYNAPSE development
- ✅ `apps/synapse/docker-compose.yml` - SYNAPSE production

---

## Infrastructure Decisions

### Port Allocation Strategy (2025-11-28)

**Decision**: Segregate ports by application with 1000-port ranges

**Rationale**:
- Prevents port conflicts between applications
- Makes it easy to identify which app owns a port
- Scalable for future applications
- Clear mental model for developers

**Ranges**:
- FORGE: 3000-3999
- SYNAPSE: 4000-4999
- NEXUS: 5000-5999
- PRISM: 6000-6999
- ATLAS: 7000-7999

### Network Architecture (2025-11-20)

**Decision**: Use `forge-network` as shared infrastructure network

**Rationale**:
- All applications can access shared services (DB, cache, logs)
- Docker DNS enables service discovery by container name
- Applications can also have private internal networks
- Production can use network isolation for security

**Networks**:
- `forge-network`: All FORGE services + all application services
- `synapse-internal`: SYNAPSE production isolation
- `default`: Docker Compose local networks

### SSL/TLS Strategy (2025-11-20)

**Decision**: Use mkcert for local development, Let's Encrypt for production

**Rationale**:
- mkcert provides trusted local certificates (no browser warnings)
- Let's Encrypt ACME fails for local domains (not publicly resolvable)
- Traefik file provider enables mkcert certificate usage
- Easy switch to ACME for production deployment

**Configuration**:
- Dev: `tls=true` (uses file provider)
- Prod: `tls.certresolver=letsencrypt` (uses ACME)

### Log Aggregation Strategy (2025-11-15)

**Decision**: Loki + Promtail + Grafana for centralized logging

**Rationale**:
- Loki is lightweight and purpose-built for logs
- Promtail automatically collects Docker container logs
- Grafana provides powerful query and visualization
- LogQL query language is intuitive
- No need for Elasticsearch (heavy resource usage)

**Architecture**:
- Promtail: Scrapes `/var/lib/docker/containers/**/*.log`
- Loki: Stores and indexes logs
- Grafana: Query and visualize

---

## Migration Notes

### From Individual Port Access to Traefik (2025-11-20)

**Before**:
- Direct access: `http://localhost:4000`, `http://localhost:8001`
- No SSL/TLS
- Manual port management

**After**:
- Domain access: `https://synapse.axoiq.com`, `https://api.axoiq.com`
- Automatic SSL/TLS with mkcert certificates
- Traefik manages routing via labels

**Migration Steps**:
1. Generate mkcert certificates
2. Add hosts file entries
3. Start Traefik: `docker-compose -f docker-compose.traefik.yml up -d`
4. Add Traefik labels to application services
5. Access via domains instead of ports

**Backward Compatibility**: Direct port access still works (e.g., `http://localhost:4000`)

---

## Known Issues

### Issue: NEXUS Backend Port Conflict (8000)

**Status**: Open

**Impact**: NEXUS backend and SYNAPSE backend both use port 8000 internally

**Workaround**:
- SYNAPSE exposes 8001→8000 (no conflict on host)
- NEXUS exposes 8000→8000
- Only one can run at a time on host port 8000

**Planned Fix**: Move NEXUS backend to port 5000 (within NEXUS range)

### Issue: Individual File Volume Mounts on Windows

**Status**: Monitoring

**Impact**: May fail on some Windows Docker configurations

**Example**:
```yaml
volumes:
  - ./frontend/index.tsx:/app/index.tsx  # May fail
```

**Workaround**: Use directory mounts instead:
```yaml
volumes:
  - ./frontend:/app
  - /app/node_modules
```

---

## Rollback Procedures

### Rollback Traefik SSL Changes (to ACME)

If you need to switch back to ACME certificates:

1. **Edit `apps/synapse/docker-compose.traefik-labels.yml`**:
```yaml
# Change FROM:
- "traefik.http.routers.synapse.tls=true"

# TO:
- "traefik.http.routers.synapse.tls.certresolver=letsencrypt"
```

2. **Edit `forge/docker-compose.traefik.yml`**:
```yaml
# Uncomment production ACME server
- "--certificatesresolvers.letsencrypt.acme.caserver=https://acme-v02.api.letsencrypt.org/directory"
```

3. **Restart Traefik**:
```powershell
docker restart forge-traefik
```

### Rollback Frontend Network Changes

If frontend networking causes issues:

1. **Edit `apps/synapse/docker-compose.dev.yml`**:
```yaml
frontend:
  # Remove these lines:
  # container_name: synapse-frontend
  # networks:
  #   - default
  #   - forge-network
```

2. **Rebuild**:
```powershell
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up --build
```

---

## Future Enhancements

### Planned Infrastructure Additions

#### Q1 2026
- [ ] Prometheus metrics collection
- [ ] Alertmanager for alerting
- [ ] Automated backup system
- [ ] Disaster recovery procedures

#### Q2 2026
- [ ] Neo4j graph database for NEXUS
- [ ] Elasticsearch for advanced search (if MeiliSearch insufficient)
- [ ] RabbitMQ or Redis Streams for event bus

#### Q3 2026
- [ ] Kubernetes migration plan
- [ ] Multi-environment support (dev, staging, prod)
- [ ] CI/CD pipeline integration

---

**Changelog Maintenance**:
- Update this file BEFORE making infrastructure changes
- Use Git to track changes to this file
- Include migration notes for breaking changes
- Document rollback procedures for risky changes
- Tag releases in Git matching changelog versions
