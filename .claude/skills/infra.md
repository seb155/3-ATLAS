# Infrastructure Skill - Quick Reference

This skill provides quick access to AXIOM infrastructure information without invoking the full DevOps Manager agent.

---

## Usage

**Invoke with**:
- Skill tool: `skill: "infra"`
- Slash command: `/infra` (if configured)
- Directly by user: "Show me infrastructure status"

---

## What This Skill Does

Reads the infrastructure registry and provides a quick status report including:

1. **Running Services** - What containers are currently up
2. **Port Allocations** - Complete port map with availability
3. **Network Status** - Docker network health
4. **Quick Troubleshooting** - Common commands for diagnosing issues

This skill is **read-only** and **fast**. For complex diagnosis, configuration changes, or validation, use the **DevOps Manager** agent instead.

---

## When to Use This Skill vs DevOps Manager Agent

### Use This Skill (infra) When:
- ✅ Checking what services are running
- ✅ Finding available ports
- ✅ Quick status check
- ✅ Looking up service URLs
- ✅ Checking which networks exist

### Use DevOps Manager Agent When:
- 🔧 Diagnosing complex problems
- 🔧 Adding new services
- 🔧 Validating configurations
- 🔧 Fixing port conflicts
- 🔧 Network troubleshooting
- 🔧 Major infrastructure changes

**Rule of Thumb**: If you just need info → use this skill. If you need action → use DevOps Manager agent.

---

## Implementation

When this skill is invoked, perform the following steps:

### Step 1: Read Infrastructure Registry

Read `.dev/infra/registry.yml` to get:
- Port allocations
- Service definitions
- Network configuration
- Available ports by application

### Step 2: Check Current Docker State

Run this command:
```powershell
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Step 3: Generate Status Report

Combine registry data with current Docker state to show:
- Which services SHOULD be running (from registry)
- Which services ARE running (from Docker)
- Port allocation summary
- Available ports by app

---

## Output Format

Provide output in this structure:

```markdown
# AXIOM Infrastructure Status

## Running Services

### FORGE Infrastructure
✅ forge-postgres (5433→5432) - healthy
✅ forge-redis (6379→6379) - healthy
✅ forge-loki (3100→3100) - healthy
✅ forge-grafana (3000→3000) - healthy
✅ forge-meilisearch (7700→7700) - healthy
✅ forge-traefik (80, 443, 8888) - healthy
❌ forge-pgadmin (5050→80) - not running
❌ forge-prisma (5555→5555) - not running
✅ forge-wiki (3080→3080) - healthy

### SYNAPSE Application
✅ synapse-backend (8001→8000) - healthy
✅ synapse-frontend (4000→4000) - healthy

### NEXUS Application
❌ nexus-backend (8000→8000) - not running
❌ nexus-frontend (5173→5173) - not running

## Port Allocations

### Allocated Ports by Range

**FORGE (3000-3999)** - 3 ports allocated, 997 available
- 3000: Grafana
- 3080: Wiki
- 3100: Loki

**System Ports** (80, 443, 5433, 6379, 7700, 8888)
- 80: Traefik HTTP
- 443: Traefik HTTPS
- 5433: PostgreSQL
- 6379: Redis
- 7700: MeiliSearch
- 8888: Traefik Dashboard

**SYNAPSE (4000-4999)** - 2 ports allocated, 998 available
- 4000: Frontend
- 8001: Backend (outside range - grandfathered)

**NEXUS (5000-5999)** - 2 ports allocated, 998 available
- 5173: Frontend
- 8000: Backend (CONFLICT with synapse-backend in production!)

**PRISM (6000-6999)** - 0 ports allocated, 1000 available
- Ready for allocation

**ATLAS (7000-7999)** - 0 ports allocated, 1000 available
- Ready for allocation

### Available Ports (for new services)

- SYNAPSE: 4001-4999 (998 ports)
- NEXUS: 5001-5172, 5174-5999 (998 ports)
- PRISM: 6000-6999 (1000 ports)
- ATLAS: 7000-7999 (1000 ports)

## Networks

### Active Docker Networks
✅ forge-network (external) - 15 services
✅ synapse_default (local) - 2 services
⚠️  synapse-internal (production only) - 0 services

### Network Membership

**forge-network** (shared infrastructure):
- All FORGE services
- synapse-backend
- synapse-frontend
- nexus-backend (when running)
- nexus-frontend (when running)

## Quick Access URLs

### Development (Direct Ports)
- SYNAPSE Frontend: http://localhost:4000
- SYNAPSE API Docs: http://localhost:8001/docs
- Grafana: http://localhost:3000 (admin/admin)
- Wiki: http://localhost:3080
- Traefik Dashboard: http://localhost:8888
- pgAdmin: http://localhost:5050
- Prisma Studio: http://localhost:5555
- MeiliSearch: http://localhost:7700

### Development (with Traefik SSL)
- SYNAPSE Frontend: https://synapse.axoiq.com
- SYNAPSE API: https://api.axoiq.com/docs
- Traefik Dashboard: https://traefik.axoiq.com:8888
- Grafana: https://grafana.axoiq.com

## Quick Commands

**Start all FORGE services**:
```powershell
cd forge && docker-compose up -d
```

**Start SYNAPSE dev**:
```powershell
cd apps\synapse && docker-compose -f docker-compose.dev.yml up -d
```

**View logs**:
```powershell
docker logs <service_name> -f --tail 100
```

**Restart service**:
```powershell
docker restart <service_name>
```

**Check service health**:
```powershell
docker inspect --format='{{.State.Health.Status}}' <service_name>
```

**Validate infrastructure**:
```powershell
.\.dev\scripts\validate-infra.ps1
```

## Issues Detected

[List any issues detected, e.g.:]
⚠️  pgAdmin is not running (optional service, OK if not needed)
⚠️  NEXUS backend port 8000 conflicts with SYNAPSE backend in production

## Recommendations

[Provide 1-3 quick recommendations based on status]

**For complex issues or configuration changes, use the DevOps Manager agent.**
```

---

## Status Indicators

Use these indicators consistently:

- ✅ **Running and healthy**
- ❌ **Not running** (expected to be running)
- ⚠️ **Warning** (running but degraded, or potential issue)
- 📋 **Info** (optional service not running)

---

## Port Availability Logic

When showing available ports:

1. **Read registry.yml** to get `port_registry.allocated`
2. **Calculate available ports** by subtracting allocated from range
3. **Warn about conflicts** if ports overlap or are outside range
4. **Show next available port** for each application

**Example**:
```
SYNAPSE (4000-4999):
  Allocated: 4000 (frontend), 8001 (backend - outside range)
  Available: 4001-4999
  Next available: 4001
  Total available: 999 ports
```

---

## Network Health Check

When checking networks:

1. **List all networks**: `docker network ls`
2. **Check forge-network exists**: Must exist for infrastructure to work
3. **Inspect forge-network**: `docker network inspect forge-network`
4. **Count services**: How many containers are on forge-network?

**If forge-network doesn't exist**:
```markdown
❌ **CRITICAL**: forge-network does not exist!

**Fix**:
```powershell
docker network create forge-network
```

All AXIOM applications require this network to access shared infrastructure.
```

---

## Quick Troubleshooting Guide

Include this section if any issues are detected:

```markdown
## Quick Troubleshooting

### Frontend Not Running
```powershell
# Check logs
docker logs synapse-frontend --tail 50

# Check if port 4000 is blocked
netstat -ano | findstr :4000

# Rebuild and restart
cd apps\synapse
docker-compose -f docker-compose.dev.yml up -d --build frontend
```

### Backend Can't Connect to Database
```powershell
# Verify backend is on forge-network
docker inspect synapse-backend | findstr forge-network

# Check PostgreSQL is running
docker ps | grep forge-postgres

# Test connection
docker exec synapse-backend ping forge-postgres
```

### Traefik SSL Errors
```powershell
# Check certificate files exist
ls forge\config\traefik\axoiq.com.*

# Verify file provider is enabled
docker logs forge-traefik | grep "file provider"

# Restart Traefik
docker restart forge-traefik
```

**For complex issues**: Invoke DevOps Manager agent
```

---

## Files Read by This Skill

This skill reads the following files:

1. **Primary**: `.dev/infra/registry.yml` - Infrastructure registry
2. **Secondary** (optional): `.dev/infra/infrastructure.md` - Additional context
3. **Real-time**: Docker commands for current state

**Do NOT modify files**. This skill is read-only.

---

## Performance Optimization

To keep this skill fast:

1. **Read registry.yml only once** per invocation
2. **Run Docker commands in parallel** if possible:
   ```powershell
   # Get container status
   $status = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

   # Get network info (parallel)
   $networks = docker network ls
   ```
3. **Cache common data** during session if invoked multiple times
4. **Limit output** to most relevant information

---

## Agent Handoff

If the user's request requires more than status checking:

```markdown
## Action Required

Your request requires configuration changes or complex diagnosis.

**Invoking DevOps Manager agent** for:
- [Specific task, e.g., "Validate new service configuration"]
- [Reason, e.g., "Requires port allocation and registry update"]

DevOps Manager will provide detailed guidance and configuration changes.
```

Then use the Task tool to invoke the DevOps Manager agent:
```
subagent_type: "devops-manager"
prompt: "User wants to [specific request]. Current infra status: [summary from this skill]"
```

---

## Example Invocations

### Example 1: User Asks "What's running?"

**Output**:
```markdown
# AXIOM Infrastructure Status

## Currently Running
✅ FORGE: 9/10 services running (pgAdmin stopped)
✅ SYNAPSE: 2/2 services running
❌ NEXUS: 0/2 services running

**Access SYNAPSE**: http://localhost:4000
**Access Grafana**: http://localhost:3000

All critical services are healthy.
```

### Example 2: User Asks "What ports are available for PRISM?"

**Output**:
```markdown
# Port Availability for PRISM

**Range**: 6000-6999 (1000 ports)
**Allocated**: 0 ports
**Available**: All ports (6000-6999)

**Recommended starting port**: 6000

**To allocate a port**, invoke DevOps Manager agent:
"DevOps Manager, I need to allocate port 6000 for PRISM backend"
```

### Example 3: User Asks "Is the database running?"

**Output**:
```markdown
# Database Status

✅ **forge-postgres**: Running and healthy
- Port: 5433→5432
- Status: accepting connections
- Health: pg_isready returns OK

**Connection strings**:
- External: `postgresql://postgres:postgres@localhost:5433/dbname`
- Internal (Docker): `postgresql://postgres:postgres@forge-postgres:5432/dbname`

**Quick test**:
```powershell
docker exec forge-postgres pg_isready -U postgres
```
```

---

## Success Metrics

This skill is successful when:

- ✅ Provides status in <3 seconds
- ✅ Clearly shows running vs stopped services
- ✅ Highlights issues that need attention
- ✅ Provides actionable next steps
- ✅ Knows when to hand off to DevOps Manager
- ✅ Doesn't try to fix problems (read-only)

---

**Remember**: You're a quick reference tool, not a troubleshooter. For anything beyond status checking, hand off to DevOps Manager.
