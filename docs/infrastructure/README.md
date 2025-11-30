# AXIOM Infrastructure Documentation

Complete guide to managing and deploying AXIOM's Docker infrastructure.

---

## Quick Links

- **[Getting Started](getting-started.md)** - Start here for setup and basics
- **[Docker Networking](docker-networking.md)** - Network best practices and DNS resolution
- **[Environment Variables](environment-variables.md)** - Managing .env files and configuration
- **[Port Management](port-management.md)** - Port allocation rules and registry
- **[Network Architecture](network-architecture.md)** - Docker networks and service communication
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
- **[CLI Reference](cli-reference.md)** - axiom.ps1 command reference
- **[For Developers](for-developers.md)** - Developer workflows

---

## What is AXIOM Infrastructure?

AXIOM uses a **centralized Infrastructure as Code** system to manage all Docker containers, networks, and port allocations across multiple applications:

- **FORGE**: Shared infrastructure (PostgreSQL, Redis, Grafana, Loki, etc.)
- **SYNAPSE**: MBSE Platform (MVP Dec 2025)
- **NEXUS**: Knowledge Graph + Notes/Wiki
- **PRISM**: Enterprise Dashboard (planned)
- **ATLAS**: AI Collaboration Environment (planned)

---

## Architecture Overview

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
         └──────────────────────────────────────────────┘
```

---

## Key Concepts

### 1. Port Allocation Ranges

Each application has a **dedicated 1000-port range**:

| Application | Range | Allocated | Available |
|-------------|-------|-----------|-----------|
| **FORGE** | 3000-3999 | 9 ports | 991 ports |
| **SYNAPSE** | 4000-4999 | 2 ports | 998 ports |
| **NEXUS** | 5000-5999 | 2 ports | 998 ports |
| **PRISM** | 6000-6999 | 0 ports | 1000 ports |
| **ATLAS** | 7000-7999 | 0 ports | 1000 ports |

**Rule**: No port can be allocated to multiple services. All allocations are tracked in the central registry.

### 2. forge-network

All AXIOM applications and FORGE infrastructure services communicate via a shared Docker bridge network called `forge-network`.

**Benefits**:
- Service discovery via Docker DNS (e.g., `forge-postgres:5432`)
- Shared infrastructure access (database, cache, logs)
- Network isolation from external traffic

**Requirement**: All SYNAPSE, NEXUS, PRISM, and ATLAS services **MUST** be on `forge-network` to access shared infrastructure.

### 3. Central Registry

**File**: `.dev/infra/registry.yml`

The registry is the **single source of truth** for:
- Port allocations
- Service definitions
- Network configuration
- Startup order
- Validation rules

**All infrastructure changes MUST update the registry.**

---

## Quick Start

### Install Prerequisites

- Docker Desktop for Windows (WSL2 backend)
- PowerShell 5.1+
- mkcert (for local SSL certificates)
- PowerShell YAML module

```powershell
# Install PowerShell YAML module
Install-Module -Name powershell-yaml -Force -Scope CurrentUser

# Install mkcert (Chocolatey)
choco install mkcert

# Or with Scoop
scoop install mkcert
```

### Start Infrastructure

**Option 1: Use the CLI** (Recommended)
```powershell
# Start FORGE infrastructure
.\.dev\scripts\axiom.ps1 start forge

# Start SYNAPSE application
.\.dev\scripts\axiom.ps1 start synapse

# Check status
.\.dev\scripts\axiom.ps1 status
```

**Option 2: Manual Docker Compose**
```powershell
# Create forge-network (one-time)
docker network create forge-network

# Start FORGE
cd forge
docker-compose up -d

# Start SYNAPSE
cd apps\synapse
docker-compose -f docker-compose.dev.yml up -d
```

### Verify Everything is Running

```powershell
# Use CLI
.\.dev\scripts\axiom.ps1 health

# Or check Docker directly
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Access Applications

**Direct Port Access**:
- SYNAPSE Frontend: http://localhost:4000
- SYNAPSE API Docs: http://localhost:8001/docs
- Grafana: http://localhost:3000
- Wiki: http://localhost:3080

**With Traefik SSL** (requires setup):
- SYNAPSE Frontend: https://synapse.axoiq.com
- SYNAPSE API: https://api.axoiq.com/docs
- Traefik Dashboard: https://traefik.axoiq.com:8888

---

## Common Tasks

### Check Infrastructure Status

```powershell
.\.dev\scripts\axiom.ps1 status
```

### View Port Allocations

```powershell
.\.dev\scripts\axiom.ps1 ports
```

### Validate Configuration

```powershell
.\.dev\scripts\axiom.ps1 validate
```

### View Logs

```powershell
.\.dev\scripts\axiom.ps1 logs synapse-backend
```

### Restart Service

```powershell
.\.dev\scripts\axiom.ps1 restart synapse-backend
```

---

## Documentation Structure

| Guide | Purpose | For |
|-------|---------|-----|
| [Getting Started](getting-started.md) | Initial setup and deployment | New developers |
| [Port Management](port-management.md) | Port allocation rules and process | Adding new services |
| [Network Architecture](network-architecture.md) | Docker networks and topology | Understanding service communication |
| [Troubleshooting](troubleshooting.md) | Common issues and solutions | Debugging infrastructure problems |
| [CLI Reference](cli-reference.md) | Complete CLI command reference | Daily operations |
| [For Developers](for-developers.md) | Developer workflows and best practices | Development |
| [Docker Networking](docker-networking.md) | Network best practices and anti-patterns | Understanding service communication |
| [Environment Variables](environment-variables.md) | .env management and auto-generation | Configuration management |

---

## Network Best Practices

### Use Docker DNS Names (Never IPs)

**Correct:**
```env
DATABASE_URL=postgresql://postgres:postgres@forge-postgres:5432/synapse
REDIS_URL=redis://forge-redis:6379
```

**Incorrect:**
```env
DATABASE_URL=postgresql://postgres:postgres@192.168.1.10:5432/synapse  # ❌
REDIS_URL=redis://localhost:6379                                       # ❌
```

**Why:** Docker DNS names work across environments and container restarts. IPs and localhost only work in specific scenarios.

**See:** [Docker Networking Guide](docker-networking.md) for complete patterns and anti-patterns.

### Environment Variable Auto-Generation

All applications use `.env.template` with auto-generation scripts:

```powershell
cd apps/synapse/backend
.\generate-env.ps1
```

The script automatically detects Docker vs local environment and generates appropriate configuration.

**See:** [Environment Variables Guide](environment-variables.md) for complete setup instructions.

---

## Advanced Topics

### Adding New Application

1. Determine port from available range
2. Create docker-compose configuration
3. Update central registry (`.dev/infra/registry.yml`)
4. Update documentation
5. Validate with `axiom.ps1 validate`

**See**: [Port Management Guide](port-management.md)

### SSL/TLS Configuration

AXIOM uses **mkcert** for local development and **Let's Encrypt** for production.

**See**: [Getting Started - SSL Setup](getting-started.md#ssl-setup)

### Log Aggregation

All containers send logs to **Loki**, viewable in **Grafana**.

**Access**: http://localhost:3000

---

## Support

**Infrastructure Issues**:
- Check [Troubleshooting Guide](troubleshooting.md)
- Run `axiom.ps1 validate` for diagnostics
- Check [Infrastructure Changelog](../../.dev/infra/CHANGELOG.md)

**For AI Agents**:
- Use `skill: "infra"` for quick status
- Invoke DevOps Manager agent for complex issues

---

**Version**: 1.0
**Last Updated**: 2025-11-28 18:44
**Maintainer**: AXIOM Platform Team
