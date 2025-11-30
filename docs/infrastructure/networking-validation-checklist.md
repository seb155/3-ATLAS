# Networking and Environment Configuration Validation Checklist

**Purpose**: Ensure all AXIOM applications and personal projects follow Docker networking best practices and use proper environment variable management.

**Last Audit**: 2025-11-29
**Status**: ✅ **PASSED** - All applications validated

---

## Overview

This document provides a comprehensive checklist for validating Docker networking configuration and environment variable management across all AXIOM applications and related projects.

### Key Requirements

1. **NO hardcoded IP addresses** in application code or configuration
2. **Docker DNS names** for all inter-service communication (e.g., `forge-postgres`, `forge-redis`)
3. **Template-based `.env` management** with auto-generation scripts
4. **forge-network integration** for all AXIOM applications
5. **Proper Traefik routing** with labels and domain names
6. **External service URLs documented** clearly (e.g., Proxmox, Home Assistant)

---

## Validation Steps

### Step 1: Scan for Hardcoded IPs

**Command:**
```powershell
# Scan for localhost:port patterns
Get-ChildItem -Path "apps\" -Recurse -Include *.py,*.yml,*.yaml,*.js,*.jsx,*.ts,*.tsx |
  Select-String -Pattern "localhost:[0-9]|127\.0\.0\.1:[0-9]"

# Scan for private IP ranges
Get-ChildItem -Path "apps\" -Recurse -Include *.py,*.yml,*.yaml,*.js,*.jsx,*.ts,*.tsx |
  Select-String -Pattern "192\.168\.|172\.1[6-9]\.|172\.2[0-9]\.|172\.3[01]\.|10\."
```

**Allowed Exceptions:**
- ✅ `localhost` in frontend `.env` (VITE_API_URL for local dev)
- ✅ `localhost` in print statements or logs (documentation only)
- ✅ `localhost` in test files (conftest.py, *.test.tsx)
- ✅ Default fallbacks in config.py (if overridden by .env)
- ✅ External infrastructure IPs in `.env.example` (Proxmox, UniFi, Home Assistant)

**NOT Allowed:**
- ❌ Hardcoded `localhost` in docker-compose environment variables
- ❌ Hardcoded IPs in Python/TypeScript application code
- ❌ Hardcoded IPs in production configuration

### Step 2: Verify Docker DNS Usage

**Check these files in each application:**

```bash
# Backend configuration
cat apps/*/backend/app/config.py
# Should use environment variables for DB_URL, REDIS_URL

# Docker Compose
cat apps/*/docker-compose.dev.yml
# Should use Docker DNS names like forge-postgres:5432
```

**Expected Patterns:**
```yaml
# ✅ CORRECT - Docker DNS
environment:
  DATABASE_URL: postgresql://postgres:postgres@forge-postgres:5432/synapse
  REDIS_URL: redis://forge-redis:6379

# ❌ INCORRECT - Hardcoded localhost
environment:
  DATABASE_URL: postgresql://postgres:postgres@localhost:5433/synapse
```

### Step 3: Validate Environment Templates

**For each application, verify:**

- [ ] `.env.template` exists with `{{PLACEHOLDER}}` syntax
- [ ] `generate-env.ps1` script exists and is functional
- [ ] `.env.example` exists with documentation
- [ ] `.env` is gitignored
- [ ] `.gitignore` includes `.env` but excludes `.env.template`

**Test:**
```powershell
cd apps/synapse/backend
.\generate-env.ps1
cat .env  # Verify correct values replaced
```

### Step 4: Check forge-network Integration

**All AXIOM applications should connect to forge-network:**

```bash
# Check docker-compose.yml
grep -r "forge-network" apps/*/docker-compose*.yml
```

**Expected:**
```yaml
networks:
  - forge-network

networks:
  forge-network:
    external: true
```

### Step 5: Verify Traefik Labels

**For production-ready applications:**

```bash
# Check Traefik labels
grep -r "traefik.enable" apps/*/docker-compose*.yml
```

**Expected patterns:**
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.<app>.rule=Host(`<app>.axoiq.com`)"
  - "traefik.http.routers.<app>.entrypoints=websecure"
  - "traefik.http.routers.<app>.tls.certresolver=letsencrypt"
```

---

## Application-by-Application Audit

### AXIOM Applications

#### ✅ SYNAPSE (Backend)

**Status**: PASSED ✅

**Checks:**
- [x] .env.template with {{PLACEHOLDERS}}
- [x] generate-env.ps1 script
- [x] Docker DNS for database (`forge-postgres:5432`)
- [x] Docker DNS for Redis (`forge-redis:6379`)
- [x] CORS from environment variable
- [x] forge-network integration
- [x] Traefik labels configured
- [x] MeiliSearch uses Docker DNS (`forge-meilisearch:7700`)

**Files:**
- `apps/synapse/backend/.env.template`
- `apps/synapse/backend/generate-env.ps1`
- `apps/synapse/backend/app/main.py:60` - CORS from env (with localhost fallback for dev)

**Notes:**
- MeiliSearch default changed from `localhost:7700` to `forge-meilisearch:7700` (2025-11-29)

#### ✅ NEXUS (Backend)

**Status**: PASSED ✅

**Checks:**
- [x] .env.template with {{PLACEHOLDERS}}
- [x] generate-env.ps1 script
- [x] Docker DNS for database
- [x] Docker DNS for Redis
- [x] forge-network integration
- [x] Traefik labels configured
- [x] Standalone mode documented (DEPLOYMENT.md)

**Files:**
- `apps/nexus/backend/.env.template`
- `apps/nexus/backend/generate-env.ps1`
- `apps/nexus/DEPLOYMENT.md`

**Notes:**
- Trilium URL (`https://notes.s-gagnon.com`) is external service - correctly not using Docker DNS
- Standalone docker-compose corrected to use ports 5500, 5501, 5000 (NEXUS range)

#### ✅ CORTEX (AI Engine)

**Status**: PASSED ✅

**Checks:**
- [x] .env.template with {{PLACEHOLDERS}}
- [x] generate-env.ps1 script
- [x] Docker DNS for database
- [x] Docker DNS for Redis (DB #2)
- [x] AI service URLs use Docker DNS (litellm:4000, ollama:11434)
- [x] forge-network integration

**Files:**
- `apps/cortex/.env.template`
- `apps/cortex/generate-env.ps1`
- `apps/cortex/backend/app/core/config.py` - defaults changed to Docker DNS

**Notes:**
- External API keys (ANTHROPIC_API_KEY, etc.) properly marked as MANUAL configuration

### Personal Projects

#### ✅ FinDash

**Status**: PASSED ✅

**Checks:**
- [x] forge-network integration
- [x] Traefik labels configured
- [x] Port 6400 (PRISM range)
- [x] .env.template created (for GEMINI_API_KEY)
- [x] .env.example created
- [x] No hardcoded IPs

**Files:**
- `8-Perso/FinDash/.env.template`
- `8-Perso/FinDash/.env.example`
- `8-Perso/FinDash/docker-compose.yml`

**Notes:**
- Frontend-only app, no backend dependencies
- GEMINI_API_KEY is optional (AI features)

#### ✅ Homelab_MSH

**Status**: PASSED ✅

**Checks:**
- [x] Docker DNS for internal database (`@db:5432`)
- [x] forge-network integration
- [x] Traefik labels configured
- [x] Port 6300-6301 (PRISM range)
- [x] .env.example updated with clear documentation
- [x] External infrastructure IPs properly documented

**Files:**
- `8-Perso/Homelab_MSH/dashboard/docker-compose.yml` - uses `@db:5432` ✅
- `8-Perso/Homelab_MSH/dashboard/.env.example` - updated with sections
- `8-Perso/Homelab_MSH/pulse/docker-compose.yml`

**Notes:**
- Proxmox, PBS, UniFi URLs are external infrastructure (correctly using IPs/domains)
- Database uses internal Docker DNS (`@db:5432`)

#### ✅ Note_synch

**Status**: PASSED ✅

**Checks:**
- [x] Docker DNS for Neo4j (`bolt://neo4j:7687`)
- [x] forge-network integration
- [x] Traefik labels configured
- [x] Ports 6200-6203 (PRISM range)
- [x] External Trilium URL properly documented

**Files:**
- `Note_synch/docker-compose.yml` - Neo4j uses `bolt://neo4j:7687` ✅
- `Note_synch/.env.example`

**Notes:**
- Trilium URL (`https://notes.s-gagnon.com`) is external service - correct

#### ✅ HomeAssistant MCP

**Status**: PASSED ✅

**Checks:**
- [x] .env.example updated with clear documentation
- [x] External service URLs properly documented
- [x] No hardcoded IPs in code

**Files:**
- `8-Perso/HomeAssistant/homeassistant-mcp/.env.example` - updated
- `8-Perso/HomeAssistant/influxdb-mcp/.env.example` - updated

**Notes:**
- Home Assistant and InfluxDB are external services - correctly using URLs/domains
- MCP servers are local Python scripts (not Docker services)

---

## Final Validation Commands

### 1. Environment Generation Test

```powershell
# Test all AXIOM apps
$apps = @("synapse", "nexus", "cortex")
foreach ($app in $apps) {
    cd "D:\Projects\AXIOM\apps\$app\backend"
    Write-Host "Testing $app..." -ForegroundColor Cyan
    .\generate-env.ps1 -Force
    if ($?) {
        Write-Host "  ✅ $app .env generated successfully" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $app .env generation failed" -ForegroundColor Red
    }
}
```

### 2. Docker DNS Validation

```powershell
# Verify no localhost in docker-compose environment sections
Get-ChildItem -Path "D:\Projects\AXIOM\apps" -Recurse -Filter "docker-compose*.yml" |
  Select-String -Pattern "environment:" -Context 0,10 |
  Select-String -Pattern "localhost|127\.0\.0\.1" |
  Where-Object { $_.Line -notmatch "^#" }  # Exclude comments
```

**Expected**: No results (or only in commented sections)

### 3. forge-network Connectivity Test

```bash
# Start FORGE infrastructure
cd D:\Projects\AXIOM\forge
docker compose up -d

# Verify network exists
docker network inspect forge-network

# Start an app and test DNS resolution
cd D:\Projects\AXIOM\apps\synapse
docker compose -f docker-compose.dev.yml up -d

# Test database connection from backend container
docker exec synapse-backend ping forge-postgres -c 2
docker exec synapse-backend ping forge-redis -c 2
```

**Expected**: Successful ping responses

### 4. Traefik Routing Test

```bash
# Check Traefik can see services
docker logs forge-traefik --tail 100 | grep -i "router\|service"

# Test HTTPS access
curl -k https://synapse.axoiq.com/health
curl -k https://api.axoiq.com/docs
```

**Expected**: HTTP 200 responses

---

## Documentation Checklist

### User Documentation

- [x] `docs/infrastructure/docker-networking.md` - Networking best practices
- [x] `docs/infrastructure/environment-variables.md` - .env management guide
- [x] `docs/infrastructure/README.md` - Updated with networking section
- [x] `docs/infrastructure/networking-validation-checklist.md` (this file)

### AI Agent Documentation

- [x] `.claude/agents/rules/12-docker-networking.md` - Mandatory networking rules
- [x] `.claude/context/standards/environment-variables.md` - Templates and patterns

### Application-Specific Documentation

- [x] `apps/nexus/DEPLOYMENT.md` - FORGE vs standalone modes
- [x] All `.env.example` files updated with clear sections and comments

---

## Common Issues and Solutions

### Issue 1: Connection Refused to forge-postgres

**Symptoms:**
```
psycopg2.OperationalError: could not connect to server: Connection refused
```

**Diagnosis:**
```bash
# Check if FORGE is running
docker ps | grep forge

# Check if service is on forge-network
docker inspect <container-name> | grep forge-network
```

**Solution:**
```bash
# Start FORGE infrastructure
cd D:\Projects\AXIOM\forge
docker compose up -d

# Ensure app is on forge-network (check docker-compose.yml)
```

### Issue 2: DNS Name Not Resolving

**Symptoms:**
```
getaddrinfo failed: Name or service not known
```

**Diagnosis:**
```bash
# Verify container is on forge-network
docker network inspect forge-network

# Test DNS resolution from inside container
docker exec <container-name> nslookup forge-postgres
```

**Solution:**
Add to docker-compose.yml:
```yaml
networks:
  - forge-network

networks:
  forge-network:
    external: true
```

### Issue 3: Wrong Environment Detected

**Symptoms:**
```
generate-env.ps1 detects Docker but I'm running locally
```

**Diagnosis:**
```powershell
# Check if forge-network exists
docker network ls | findstr forge
```

**Solution:**
```powershell
# Stop Docker services
docker compose down

# Force regenerate
.\generate-env.ps1 -Force
```

---

## Maintenance Schedule

### Monthly (1st of month)

- [ ] Run full hardcoded IP scan
- [ ] Test environment generation for all apps
- [ ] Verify forge-network connectivity
- [ ] Check Traefik routing for all domains

### Quarterly (Every 3 months)

- [ ] Review and update documentation
- [ ] Audit new applications or services
- [ ] Update validation scripts if needed
- [ ] Review AI agent rules for compliance

### On New Service Addition

- [ ] Create `.env.template` with placeholders
- [ ] Copy `generate-env.ps1` script
- [ ] Create `.env.example` with documentation
- [ ] Add to forge-network
- [ ] Configure Traefik labels
- [ ] Test environment generation
- [ ] Add to this checklist
- [ ] Update AI agent rules if needed

---

## Audit History

| Date | Auditor | Status | Issues Found | Notes |
|------|---------|--------|--------------|-------|
| 2025-11-29 | Claude Code | ✅ PASSED | 0 critical, 1 minor | MeiliSearch default updated to Docker DNS |

### 2025-11-29 Audit Details

**Scope**: Full workspace scan (AXIOM + personal projects)

**Changes Made**:
1. Created `.env.template` and `generate-env.ps1` for all AXIOM apps
2. Updated SYNAPSE CORS to use environment variable exclusively
3. Corrected NEXUS standalone docker-compose port allocation
4. Updated CORTEX config.py defaults to use Docker DNS
5. Created comprehensive documentation (user + AI agents)
6. Updated personal project .env.example files with clear sections
7. Fixed MeiliSearch service default from `localhost:7700` to `forge-meilisearch:7700`

**Non-Issues (Allowed)**:
- Frontend localhost URLs for local development (VITE_API_URL)
- Test files with localhost references
- Print statements in seed_demo.py (documentation only)
- External infrastructure IPs (Proxmox, UniFi, Home Assistant, Trilium)
- Cable sizing numeric values (10.5, 310.16) - not IPs

**Recommendations**:
- Consider adding `MEILISEARCH_URL` to `.env.template` for all apps using MeiliSearch
- Add validation script to CI/CD pipeline
- Create automated test for Docker DNS resolution

---

## References

- [Docker Networking Guide](docker-networking.md)
- [Environment Variables Guide](environment-variables.md)
- [Infrastructure Overview](README.md)
- [AI Agent Rule 12](../../.claude/agents/rules/12-docker-networking.md)
- [AI Standards](../../.claude/context/standards/environment-variables.md)

---

**Version**: 1.0
**Last Updated**: 2025-11-29
**Next Audit**: 2025-12-29
