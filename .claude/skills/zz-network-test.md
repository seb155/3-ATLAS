# Network Test Skill - Quick Connectivity Check

Fast skill for testing AXIOM infrastructure connectivity. Use for rapid health checks.

---

## Usage

**Invoke with**:
- Skill tool: `skill: "network-test"`
- User request: "test network" / "check services" / "are services up?"

---

## What This Skill Does

Performs 4 quick checks in sequence:

1. **forge-network** - Docker network exists and containers connected
2. **Traefik** - Reverse proxy responding and routes registered
3. **HTTP Services** - All services respond on their ports
4. **Traefik Routes** - Domain routing configured

Completes in <5 seconds.

---

## Implementation

### Step 1: Check forge-network

```powershell
docker network inspect forge-network --format "{{range .Containers}}{{.Name}} {{end}}"
```

**Expected**: List of container names on the network

### Step 2: Check Traefik

```powershell
# API responding?
curl -s -o /dev/null -w "%{http_code}" http://localhost:8888/api/http/routers

# Count routes
$routes = (curl -s http://localhost:8888/api/http/routers | ConvertFrom-Json).Count
```

**Expected**: HTTP 200, routes > 15

### Step 3: Check HTTP Services

Test each port with curl:

```powershell
$services = @{
    "forge-postgres" = 5433
    "forge-redis" = 6379
    "forge-grafana" = 3000
    "forge-loki" = 3100
    "forge-traefik-dashboard" = 8888
    "synapse-backend" = 8001
    "synapse-frontend" = 4000
    "trilium-sync" = 6200
    "neo4j-browser" = 6201
    "graph-api" = 6203
    "homelab-dashboard" = 6300
    "pulse" = 6301
    "findash" = 6400
    "pilote-patrimoine" = 6100
}

foreach ($svc in $services.GetEnumerator()) {
    $code = curl -s -o /dev/null -w "%{http_code}" "http://localhost:$($svc.Value)"
    # 200 = OK, 000 = Not responding
}
```

### Step 4: Check Traefik Routes

```powershell
$routers = curl -s http://localhost:8888/api/http/routers | ConvertFrom-Json
$routers | Where-Object { $_.status -eq "enabled" } | Select-Object name, rule
```

---

## Output Format

```markdown
# Network Test Results

## 1. Docker Network
✅ **forge-network** exists with 12 containers:
   forge-postgres, forge-redis, forge-traefik, forge-grafana,
   synapse-backend, synapse-frontend, trilium-sync, notes-neo4j,
   notes-graph-api, pulse, findash-app, nexus-backend

## 2. Traefik Status
✅ **API**: Responding (HTTP 200)
✅ **Routes**: 25 active routes

## 3. HTTP Connectivity

| Service | Port | Status | Response |
|---------|------|--------|----------|
| forge-grafana | 3000 | ✅ | 200 |
| forge-loki | 3100 | ✅ | 200 |
| traefik-dashboard | 8888 | ✅ | 200 |
| synapse-backend | 8001 | ✅ | 200 |
| synapse-frontend | 4000 | ✅ | 200 |
| trilium-sync | 6200 | ✅ | 200 |
| neo4j-browser | 6201 | ✅ | 200 |
| graph-api | 6203 | ✅ | 200 |
| homelab-dashboard | 6300 | ❌ | 000 |
| pulse | 6301 | ✅ | 200 |
| findash | 6400 | ✅ | 200 |
| pilote-patrimoine | 6100 | ❌ | 000 |

## 4. Traefik Routes

| Route | Domain | Status |
|-------|--------|--------|
| synapse-frontend-prod@file | synapse.axoiq.com | ✅ |
| synapse-backend-prod@file | api.axoiq.com | ✅ |
| findash-prod@file | findash.axoiq.com | ✅ |
| pulse@docker | pulse.axoiq.com | ✅ |
| trilium@docker | trilium.axoiq.com | ✅ |
| neo4j@docker | neo4j.axoiq.com | ✅ |
| graph-api@docker | graph.axoiq.com | ✅ |

## Summary

- **Network**: ✅ OK
- **Traefik**: ✅ OK (25 routes)
- **Services**: ⚠️ 10/12 responding
- **Issues**: homelab-dashboard, pilote-patrimoine not responding
```

---

## Status Indicators

- ✅ **OK** - Service responding (HTTP 2xx)
- ⚠️ **Warning** - Service responding with error (HTTP 4xx/5xx)
- ❌ **Down** - No response (HTTP 000 or connection refused)
- 📋 **Skip** - Optional service, not critical

---

## Quick Commands

If issues detected, suggest these fixes:

```markdown
## Quick Fixes

### Container not on network
```powershell
docker network connect forge-network <container_name>
```

### Service not responding
```powershell
docker logs <container_name> --tail 30
docker restart <container_name>
```

### Traefik not detecting service
```powershell
docker restart forge-traefik
```

### Check if port is blocked
```powershell
netstat -ano | findstr :<port>
```
```

---

## Port Reference

| Range | Application | Allocated |
|-------|-------------|-----------|
| 3000-3999 | FORGE | 3000, 3080, 3100 |
| 4000-4999 | SYNAPSE | 4000 |
| 5000-5999 | NEXUS | 5173 |
| 6000-6999 | Personal | 6100-6400 |
| 7000-7999 | ATLAS | (reserved) |
| System | Various | 80, 443, 5433, 6379, 7700, 8001, 8888 |

---

## When to Escalate

If this skill detects issues that can't be fixed with quick commands:

```markdown
**Issues requiring DevOps Manager agent**:
- Port conflicts (multiple services on same port)
- Network configuration problems
- Traefik certificate issues
- Database connection failures

Use: `subagent_type: "devops-manager"`
```

---

## Performance

- Total execution: <5 seconds
- Parallel HTTP checks when possible
- Minimal output for quick scanning
- Color-coded status for visual parsing

---

**For detailed diagnosis, use DevOps Manager agent. For start/stop operations, use docker-ops skill.**
