# AXIOM CLI Reference

Complete reference for the `axiom.ps1` command-line interface.

---

## Overview

The AXIOM CLI (`axiom.ps1`) provides a user-friendly interface for managing AXIOM infrastructure without needing to remember complex Docker commands.

**Location**: `.dev/scripts/axiom.ps1`

---

## Usage

```powershell
.\axiom.ps1 <command> [service] [options]
```

**Get Help**:
```powershell
.\.dev\scripts\axiom.ps1 -Help
```

---

## Commands

### status

Show infrastructure status - which containers are running, their status, and port mappings.

**Usage**:
```powershell
.\.dev\scripts\axiom.ps1 status
```

**Output**:
```
NAMES                STATUS              PORTS
synapse-backend      Up 2 hours          0.0.0.0:8001->8000/tcp
synapse-frontend     Up 2 hours          0.0.0.0:4000->4000/tcp
forge-postgres       Up 5 hours          0.0.0.0:5433->5432/tcp
forge-redis          Up 5 hours          0.0.0.0:6379->6379/tcp
...
```

---

### ports

List all allocated ports with service mappings.

**Usage**:
```powershell
.\.dev\scripts\axiom.ps1 ports
```

**Output**:
```
Allocated Ports:
  80     → forge-traefik           [http]          Traefik HTTP entrypoint
  443    → forge-traefik           [https]         Traefik HTTPS entrypoint
  3000   → forge-grafana           [web]           Grafana - Observability dashboard
  4000   → synapse-frontend        [web]           SYNAPSE React 19 frontend
  ...

Available Ports by Application:
  SYNAPSE    (4000-4999): 2 allocated, 998 available
  NEXUS      (5000-5999): 2 allocated, 998 available
  APEX       (6000-6999): 0 allocated, 1000 available
  ...
```

---

### start

Start a service or application stack.

**Usage**:
```powershell
.\.dev\scripts\axiom.ps1 start <service>
```

**Services**:
- `forge` - Start all FORGE infrastructure services
- `traefik` - Start Traefik reverse proxy
- `synapse` - Start SYNAPSE application (automatically starts FORGE if needed)
- `nexus` - Start NEXUS application (automatically starts FORGE if needed)
- `<container_name>` - Start a specific container

**Examples**:
```powershell
# Start FORGE infrastructure
.\.dev\scripts\axiom.ps1 start forge

# Start SYNAPSE (auto-starts FORGE if needed)
.\.dev\scripts\axiom.ps1 start synapse

# Start specific container
.\.dev\scripts\axiom.ps1 start synapse-backend
```

**Behavior**:
- Checks dependencies (e.g., SYNAPSE requires FORGE)
- Automatically starts dependencies if not running
- Uses `--build` flag for applications to rebuild images
- Returns to original directory after operation

---

### stop

Stop a service or application stack.

**Usage**:
```powershell
.\.dev\scripts\axiom.ps1 stop <service>
```

**Services**: Same as `start` command

**Examples**:
```powershell
# Stop SYNAPSE application
.\.dev\scripts\axiom.ps1 stop synapse

# Stop FORGE infrastructure
.\.dev\scripts\axiom.ps1 stop forge

# Stop specific container
.\.dev\scripts\axiom.ps1 stop synapse-backend
```

**Behavior**:
- Uses `docker-compose down` for stacks (removes containers)
- Uses `docker stop` for individual containers
- Does NOT remove volumes (data is preserved)

---

### restart

Restart a specific container.

**Usage**:
```powershell
.\.dev\scripts\axiom.ps1 restart <container_name>
```

**Examples**:
```powershell
# Restart backend
.\.dev\scripts\axiom.ps1 restart synapse-backend

# Restart database
.\.dev\scripts\axiom.ps1 restart forge-postgres
```

**Behavior**:
- Uses `docker restart` (fast, preserves container)
- Does NOT rebuild image
- For rebuilds, use `stop` + `start` instead

---

### logs

Show logs for a specific service in follow mode.

**Usage**:
```powershell
.\.dev\scripts\axiom.ps1 logs <container_name>
```

**Examples**:
```powershell
# Follow backend logs
.\.dev\scripts\axiom.ps1 logs synapse-backend

# Follow frontend logs
.\.dev\scripts\axiom.ps1 logs synapse-frontend
```

**Behavior**:
- Follows logs in real-time (like `tail -f`)
- Shows last 100 lines initially
- Press `Ctrl+C` to exit

---

### validate

Validate infrastructure configuration against registry rules.

**Usage**:
```powershell
.\.dev\scripts\axiom.ps1 validate
```

**Checks**:
- ✅ Port conflicts (no duplicate allocations)
- ✅ Port ranges (all ports within correct app range)
- ✅ Network requirements (services on `forge-network`)
- ✅ Dependencies (all dependencies running)
- ✅ forge-network existence
- ✅ Health checks for critical services

**Example Output**:
```
==============================================================================
AXIOM Infrastructure Validator
==============================================================================

Validating port allocations...
  ✅ No port conflicts detected

Validating port ranges...
  ✅ All ports in correct ranges

Validating network requirements...
  ✅ All running services on correct networks

Validating service dependencies...
  ✅ All dependencies satisfied for running services

Validating Docker networks...
  ✅ forge-network exists

Validating health checks...
  ✅ All critical services have health checks

==============================================================================
✅ VALIDATION PASSED - No issues detected
==============================================================================
```

**For Detailed Validation**:
```powershell
# Run validation script directly with verbose output
.\.dev\scripts\validate-infra.ps1 -Verbose
```

---

### health

Check health status of all infrastructure services.

**Usage**:
```powershell
.\.dev\scripts\axiom.ps1 health
```

**Example Output**:
```
Infrastructure Health Check
============================

FORGE Infrastructure:
  ✅ forge-postgres        - healthy
  ✅ forge-redis           - healthy
  ✅ forge-loki            - healthy
  ⚠️  forge-grafana        - degraded

Application Services:
  ✅ synapse-backend       - running
  ✅ synapse-frontend      - running
  📋 nexus-backend         - not running
  📋 nexus-frontend        - not running
```

**Status Indicators**:
- ✅ Healthy/Running
- ⚠️ Degraded (running but slow/unhealthy)
- ❌ Not running (expected to be running)
- 📋 Not running (optional service)

---

### networks

List Docker networks and their memberships.

**Usage**:
```powershell
.\.dev\scripts\axiom.ps1 networks
```

**Example Output**:
```
Docker Networks
===============

Network List:
NETWORK ID     NAME               DRIVER    SCOPE
abc123def456   forge-network      bridge    local
ghi789jkl012   synapse_default    bridge    local
...

forge-network Members:
  - forge-postgres
  - forge-redis
  - forge-loki
  - synapse-backend
  - synapse-frontend
  ...
```

---

### urls

Show all access URLs for applications and services.

**Usage**:
```powershell
.\.dev\scripts\axiom.ps1 urls
```

**Example Output**:
```
Access URLs
===========

Development (Direct Ports):
  SYNAPSE Frontend:      http://localhost:4000
  SYNAPSE API Docs:      http://localhost:8001/docs
  Grafana:               http://localhost:3000 (admin/admin)
  Wiki:                  http://localhost:3080
  Traefik Dashboard:     http://localhost:8888
  pgAdmin:               http://localhost:5050
  Prisma Studio:         http://localhost:5555
  MeiliSearch:           http://localhost:7700

Development (with Traefik SSL):
  SYNAPSE Frontend:      https://synapse.axoiq.com
  SYNAPSE API:           https://api.axoiq.com/docs
  Traefik Dashboard:     https://traefik.axoiq.com:8888
  Grafana:               https://grafana.axoiq.com
```

---

## Common Workflows

### Daily Startup

```powershell
# Check what's running
.\.dev\scripts\axiom.ps1 status

# Start SYNAPSE (auto-starts FORGE)
.\.dev\scripts\axiom.ps1 start synapse

# Verify health
.\.dev\scripts\axiom.ps1 health
```

### Debugging Issues

```powershell
# Validate configuration
.\.dev\scripts\axiom.ps1 validate

# Check service health
.\.dev\scripts\axiom.ps1 health

# View logs for problematic service
.\.dev\scripts\axiom.ps1 logs synapse-backend

# Check network membership
.\.dev\scripts\axiom.ps1 networks
```

### Adding New Service

```powershell
# Check available ports
.\.dev\scripts\axiom.ps1 ports

# After configuration, validate
.\.dev\scripts\axiom.ps1 validate

# Start new service
.\.dev\scripts\axiom.ps1 start <new-service>

# Verify
.\.dev\scripts\axiom.ps1 status
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (validation failed, service not found, etc.) |

**Usage in Scripts**:
```powershell
.\.dev\scripts\axiom.ps1 validate
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Infrastructure is valid"
} else {
    Write-Host "❌ Validation failed"
    exit 1
}
```

---

## Tips & Tricks

### Alias for Convenience

Add to PowerShell profile (`$PROFILE`):

```powershell
# Create short alias
Set-Alias axiom "D:\Projects\AXIOM\.dev\scripts\axiom.ps1"

# Or create function for easier path
function axiom {
    & "D:\Projects\AXIOM\.dev\scripts\axiom.ps1" @args
}
```

Then use:
```powershell
axiom status
axiom start synapse
```

### Watch Mode for Logs

```powershell
# Open multiple terminals
# Terminal 1: Backend logs
.\.dev\scripts\axiom.ps1 logs synapse-backend

# Terminal 2: Frontend logs
.\.dev\scripts\axiom.ps1 logs synapse-frontend
```

### Quick Health Loop

```powershell
# Monitor health every 5 seconds
while ($true) {
    Clear-Host
    .\.dev\scripts\axiom.ps1 health
    Start-Sleep -Seconds 5
}
```

---

## Extending the CLI

The CLI is a PowerShell script that can be extended. To add new commands:

1. Edit `.dev/scripts/axiom.ps1`
2. Add function for new command
3. Add case to main switch statement
4. Update help text

**Example**:
```powershell
function Get-MyNewCommand {
    # Your implementation
}

# In main switch
switch ($Command.ToLower()) {
    ...
    "mynewcommand" { Get-MyNewCommand }
}
```

---

## See Also

- [Troubleshooting Guide](troubleshooting.md) - Common issues and solutions
- [For Developers](for-developers.md) - Developer workflows
- [Validation Script Reference](../../.dev/scripts/validate-infra.ps1) - Direct validation script
- [Central Registry](../../.dev/infra/registry.yml) - Infrastructure configuration

---

**Version**: 1.0
**Last Updated**: 2025-11-28 18:44
