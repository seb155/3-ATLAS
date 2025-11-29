# Agent Quick Reference - Infrastructure Management

Quick reference for AI agents working with AXIOM infrastructure.

---

## When to Use Infrastructure Tools

### Use `skill: "infra"` When:
✅ Checking what services are running
✅ Finding available ports
✅ Quick status check
✅ Looking up service URLs
✅ Checking which networks exist

**Fast, read-only, no changes**

### Use `devops-manager` Agent When:
🔧 Diagnosing complex problems
🔧 Adding new services
🔧 Validating configurations
🔧 Fixing port conflicts
🔧 Network troubleshooting
🔧 Major infrastructure changes

**Intelligent, can make changes, validates**

---

## Quick Invocations

### Check Infrastructure Status

```
skill: "infra"
```

**Returns**:
- Running services
- Port allocations
- Network health
- Quick troubleshooting commands

### Diagnose Infrastructure Problem

```
Use Task tool with:
  subagent_type: "devops-manager"
  prompt: "Diagnose why synapse-frontend won't start"
```

**DevOps Manager Will**:
1. Read registry.yml for expected state
2. Check actual Docker state
3. Identify root cause
4. Provide exact fix with file paths
5. Provide verification commands

### Add New Service

```
Use Task tool with:
  subagent_type: "devops-manager"
  prompt: "Add PRISM backend service on port 6000"
```

**DevOps Manager Will**:
1. Check port availability in PRISM range (6000-6999)
2. Validate no conflicts
3. Generate docker-compose configuration
4. Update registry.yml
5. Update documentation

### Validate Configuration

```
Use Task tool with:
  subagent_type: "devops-manager"
  prompt: "Validate this docker-compose configuration: [paste config]"
```

---

## Files You Need to Know

### Primary References (Read FIRST)

1. **`.dev/infra/registry.yml`** - SINGLE SOURCE OF TRUTH
   - Port allocations
   - Service definitions
   - Network configuration
   - Startup order
   - Validation rules

2. **`.dev/infra/infrastructure.md`** - Complete documentation
   - Architecture overview
   - Service inventory
   - Troubleshooting guides
   - Operations procedures

3. **`.dev/infra/CHANGELOG.md`** - Change history
   - Recent changes
   - Known issues
   - Migration notes
   - Rollback procedures

### Docker Compose Files

4. **`forge/docker-compose.yml`** - FORGE infrastructure
5. **`forge/docker-compose.traefik.yml`** - Traefik reverse proxy
6. **`apps/synapse/docker-compose.dev.yml`** - SYNAPSE development
7. **`apps/synapse/docker-compose.traefik-labels.yml`** - Traefik routing

---

## Port Allocation Quick Check

### Ranges

| Application | Range | Rule |
|-------------|-------|------|
| FORGE | 3000-3999 | Shared infrastructure |
| SYNAPSE | 4000-4999 | MBSE platform |
| NEXUS | 5000-5999 | Knowledge graph |
| PRISM | 6000-6999 | Dashboard |
| ATLAS | 7000-7999 | AI environment |

### Currently Allocated

**FORGE (3000-3999)**:
- 3000: Grafana
- 3080: Wiki
- 3100: Loki

**System Ports**:
- 80, 443: Traefik HTTP/HTTPS
- 5433: PostgreSQL
- 6379: Redis
- 7700: MeiliSearch
- 8888: Traefik Dashboard

**SYNAPSE (4000-4999)**:
- 4000: Frontend
- 8001: Backend (grandfathered, outside range)

**NEXUS (5000-5999)**:
- 5173: Frontend
- 8000: Backend

**Available**:
- SYNAPSE: 4001-4999 (998 ports)
- NEXUS: 5001-5172, 5174-5999 (998 ports)
- PRISM: 6000-6999 (1000 ports - ALL AVAILABLE)
- ATLAS: 7000-7999 (1000 ports - ALL AVAILABLE)

---

## Network Requirements

### forge-network (External Bridge)

**Required for**:
- All FORGE services
- All SYNAPSE services
- All NEXUS services
- All PRISM services
- All ATLAS services

**Why**: Enables Docker DNS resolution of shared infrastructure (forge-postgres, forge-redis, etc.)

**Configuration**:
```yaml
services:
  your-service:
    networks:
      - default         # For docker-compose local communication
      - forge-network   # For shared infrastructure access
```

### Verification

```bash
# Check if service is on forge-network
docker inspect <service_name> | grep forge-network
# Should output: "forge-network"
```

---

## Common Scenarios

### Scenario 1: Container Won't Start

**Steps**:
1. Invoke `devops-manager` agent
2. Agent reads logs: `docker logs <container> --tail 50`
3. Agent checks network: `docker inspect <container>`
4. Agent identifies root cause
5. Agent provides fix

**Common Causes**:
- Port conflict → Kill process or change port
- Not on forge-network → Add networks configuration
- Missing dependency → Start dependency first

### Scenario 2: Can't Connect to Database

**Quick Check**:
```bash
# Is service on forge-network?
docker inspect synapse-backend | grep forge-network

# Is postgres running?
docker ps | grep forge-postgres

# Can service reach postgres?
docker exec synapse-backend ping forge-postgres
```

**Fix**:
Add to docker-compose:
```yaml
networks:
  - forge-network
```

### Scenario 3: Port Already Allocated

**Check Registry**:
1. Read `.dev/infra/registry.yml`
2. Search for port number
3. If allocated, choose different port
4. If not allocated but conflict exists, find process:
   ```bash
   netstat -ano | findstr :<port>
   ```

**Update Registry After Allocation**:
```yaml
port_registry:
  allocated:
    <new_port>:
      service: "your-service"
      app: "your-app"
      type: "api"
      internal_port: 8000
      description: "Service description"
```

---

## Validation Rules to Enforce

### Port Rules

1. **No Duplicates**: Each port → ONE service only
2. **Within Range**: Ports must be in correct app range
3. **No System Ports**: Avoid <1024 except Traefik/nginx

### Network Rules

1. **forge-network Required**: All apps MUST be on forge-network
2. **Internal Isolation**: Production services should have internal network

### Dependency Rules

1. **Dependencies Exist**: All `depends_on` services must be defined
2. **No Circular Deps**: No A → B → A chains
3. **Startup Order**: Follow tier-based startup

---

## When to Update Registry

**ALWAYS update registry.yml when**:
- ✅ Adding new service
- ✅ Allocating new port
- ✅ Changing port allocation
- ✅ Adding network
- ✅ Changing service dependencies

**Also update**:
- ✅ infrastructure.md (service inventory)
- ✅ CHANGELOG.md (change history)

---

## Docker DNS Names

**Internal Communication** (inside Docker network):
```yaml
# ✅ Correct
DATABASE_URL: postgresql://user:pass@forge-postgres:5432/db
REDIS_URL: redis://forge-redis:6379

# ❌ Wrong
DATABASE_URL: postgresql://user:pass@localhost:5433/db
```

**External Access** (from host):
```bash
# ✅ Correct
psql -h localhost -p 5433 -U postgres

# ❌ Wrong (inside Docker)
psql -h forge-postgres -p 5433 -U postgres
```

---

## Handoff to DevOps Manager

When you encounter:
- Complex infrastructure issues
- Need to add/modify services
- Port conflicts that need resolution
- Network configuration problems
- Validation needed

**Invoke DevOps Manager**:
```
Use Task tool with:
  subagent_type: "devops-manager"
  prompt: "Detailed description of task with context"
```

**Provide Context**:
- Current error/issue
- What you've already checked
- Expected vs actual state
- Relevant file paths

---

## Emergency Commands

### Check What's Running

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Check forge-network Exists

```bash
docker network ls | grep forge-network
```

### Recreate forge-network

```bash
docker network create forge-network
```

### Validate Infrastructure

```powershell
.dev\scripts\axiom.ps1 validate
# Or
.dev\scripts\validate-infra.ps1 -Verbose
```

---

## Success Criteria

You're successful when:
- ✅ No port conflicts
- ✅ All services on correct networks
- ✅ Dependencies satisfied
- ✅ Registry updated after changes
- ✅ Documentation updated
- ✅ Validation passes

---

## Best Practices for Agents

1. **Read registry FIRST**: Always check `.dev/infra/registry.yml` before making changes
2. **Validate BEFORE deploying**: Use devops-manager to validate configurations
3. **Update documentation**: Registry + infrastructure.md + CHANGELOG.md
4. **Use DevOps Manager for complex tasks**: Don't try to solve everything yourself
5. **Preserve data**: Never delete volumes without user confirmation

---

## Quick Reference Cards

### Adding Service Checklist

- [ ] Read registry.yml for available ports
- [ ] Choose port from correct range
- [ ] Create docker-compose configuration
- [ ] Add forge-network to service
- [ ] Update registry.yml
- [ ] Update infrastructure.md
- [ ] Add CHANGELOG entry
- [ ] Validate with devops-manager
- [ ] Test deployment

### Debugging Checklist

- [ ] Read service logs
- [ ] Check if on forge-network
- [ ] Verify dependencies are running
- [ ] Check for port conflicts
- [ ] Validate configuration
- [ ] Consult DevOps Manager if stuck

---

**Remember**: When in doubt, invoke DevOps Manager agent. It has deep knowledge of all infrastructure rules and can handle complex scenarios.

**Version**: 1.0
**Last Updated**: 2025-11-28 18:44
