# Infrastructure Management Policy

**Status**: MANDATORY FOR ALL AGENTS
**Effective Date**: 2025-11-28 18:44
**Enforcement**: Automatic via CLAUDE.md

---

## 🔴 Critical Rule: Registry First

### The Golden Rule

**BEFORE any operation involving ports, networks, or Docker configuration:**

```
YOU MUST READ: .dev/infra/registry.yml
```

**NO EXCEPTIONS.**

---

## When This Policy Applies

### ✅ MUST Read Registry For:

1. **Port Operations**
   - Allocating new port
   - Checking if port is available
   - Resolving port conflicts
   - Changing existing port allocation

2. **Network Operations**
   - Adding service to network
   - Configuring docker-compose networks
   - Diagnosing network connectivity
   - Validating network requirements

3. **Service Configuration**
   - Adding new service
   - Modifying existing service
   - Creating docker-compose files
   - Updating service dependencies

4. **Infrastructure Diagnosis**
   - Troubleshooting startup failures
   - Investigating connectivity issues
   - Validating infrastructure state

5. **Configuration Validation**
   - Before deployment
   - Before committing changes
   - Before suggesting fixes

---

## Enforcement Procedure

### Step 1: Read Registry (ALWAYS FIRST)

```
Read file: .dev/infra/registry.yml
```

**What to extract**:
- Port allocations for target application
- Network requirements
- Service dependencies
- Startup order
- Validation rules

### Step 2: Verify Against Registry

**Check**:
- ✅ Port is in correct range for application
- ✅ Port not already allocated
- ✅ Service includes required networks
- ✅ Dependencies are defined
- ✅ Follows naming conventions

### Step 3: Consult DevOps Manager (If Needed)

For complex operations:
```
Use Task tool with:
  subagent_type: "devops-manager"
  prompt: "Your infrastructure request"
```

DevOps Manager will:
- Re-validate against registry
- Generate configuration
- Update registry
- Update documentation

### Step 4: Update Registry (After Changes)

After making infrastructure changes:
- ✅ Update `registry.yml` with new allocation
- ✅ Update `infrastructure.md` documentation
- ✅ Add entry to `CHANGELOG.md`
- ✅ Run validation: `.dev/scripts/axiom.ps1 validate`

---

## Examples of Correct Behavior

### Example 1: Adding New Service

**❌ WRONG**:
```
Agent: "I'll add the new service on port 6500"
[Creates docker-compose without checking registry]
```

**✅ CORRECT**:
```
Agent: "Let me check the infrastructure registry first"
[Reads .dev/infra/registry.yml]
Agent: "I see PRISM range is 6000-6999, and no ports are allocated yet"
Agent: "Port 6000 is available. I'll use that as it's the first in range"
[Invokes devops-manager to validate and update registry]
```

### Example 2: Diagnosing Network Issue

**❌ WRONG**:
```
Agent: "The service can't connect to database"
Agent: "Try adding networks: [default, forge-network]"
```

**✅ CORRECT**:
```
Agent: "The service can't connect to database"
Agent: "Let me check the infrastructure registry first"
[Reads .dev/infra/registry.yml]
Agent: "Registry shows all SYNAPSE services MUST be on forge-network"
Agent: "Current docker-compose is missing forge-network"
[Provides exact fix with registry reference]
```

### Example 3: Port Conflict

**❌ WRONG**:
```
Agent: "Port 4000 is in use, let's try 4001"
```

**✅ CORRECT**:
```
Agent: "Port 4000 conflict detected"
[Reads .dev/infra/registry.yml]
Agent: "Registry shows port 4000 allocated to synapse-frontend"
Agent: "Checking if synapse-frontend is running..."
[Diagnoses root cause: container not starting due to different issue]
[Fixes actual problem instead of changing port]
```

---

## Consequences of Not Following Policy

### If Agent Skips Registry Check:

**Problems**:
- ❌ Port conflicts (service won't start)
- ❌ Network misconfiguration (services can't communicate)
- ❌ Registry becomes out of sync (chaos)
- ❌ Validation failures
- ❌ Wasted time debugging preventable issues

**Impact**:
- Infrastructure becomes unreliable
- Developers lose trust in automation
- Manual intervention required
- Registry loses value as source of truth

---

## Special Cases

### When Registry Check Can Be Skipped

**NEVER.**

There are NO exceptions. Even for trivial changes, read the registry.

**Why**: Registry contains validation rules, dependencies, and context that may not be obvious.

### When to Invoke DevOps Manager Instead

If task involves:
- Multiple services
- Complex validation
- Generating new configurations
- Major infrastructure changes

**Then**: Invoke DevOps Manager agent instead of doing it yourself.

DevOps Manager will:
1. Read registry (automatic)
2. Validate thoroughly
3. Generate correct configuration
4. Update all documentation
5. Ensure consistency

---

## Registry Structure Reference

### Key Sections to Check

```yaml
# Port allocations - Check FIRST
port_registry:
  ranges:          # Port ranges by application
  allocated:       # Currently allocated ports

# Network requirements
networks:
  forge-network:   # Required for shared infrastructure access

# Service definitions
services:
  forge:           # FORGE infrastructure services
  synapse:         # SYNAPSE application services
  nexus:           # NEXUS application services

# Startup order (dependencies)
startup_order:     # Tier-based startup sequence

# Validation rules (enforce automatically)
validation_rules:
  ports:           # Port allocation rules
  networks:        # Network requirement rules
  dependencies:    # Dependency rules
```

### Quick Lookup Examples

**Find available port for PRISM**:
```yaml
# Read registry.yml
port_registry:
  ranges:
    prism: { start: 6000, end: 6999 }
  allocated:
    # Check if any PRISM ports allocated
    # If not, use 6000 (first in range)
```

**Check network requirements for SYNAPSE**:
```yaml
# Read registry.yml
networks:
  forge-network:
    services:
      - synapse-backend
      - synapse-frontend
      # ^ Must be on forge-network
```

**Find service dependencies**:
```yaml
# Read registry.yml
services:
  synapse:
    dev:
      - name: synapse-backend
        dependencies: [forge-postgres, forge-redis, forge-loki, forge-meilisearch]
      # ^ Must start AFTER these services
```

---

## Validation After Changes

### Always Run Validation

```powershell
# After ANY infrastructure change
.\.dev\scripts\axiom.ps1 validate
```

**This checks**:
- ✅ No port conflicts
- ✅ Ports in correct ranges
- ✅ Network requirements met
- ✅ Dependencies satisfied
- ✅ Registry consistency

### If Validation Fails

**DO NOT PROCEED**

1. Read validation error messages
2. Re-read registry to understand rule
3. Fix configuration
4. Re-validate
5. Only proceed when validation passes

---

## Updating the Registry

### When to Update

**After**:
- Adding new service
- Changing port allocation
- Modifying networks
- Updating dependencies

### How to Update

```yaml
# 1. Add port allocation
port_registry:
  allocated:
    6000:
      service: "prism-backend"
      app: "prism"
      type: "api"
      internal_port: 8000
      description: "PRISM enterprise dashboard backend"
      networks: ["default", "forge-network"]

# 2. Add service definition
services:
  prism:
    dev:
      - name: "prism-backend"
        image: "prism-backend:dev"
        ports: [6000]
        networks: ["default", "forge-network"]
        dependencies: ["forge-postgres", "forge-redis"]
        compose_file: "apps/prism/docker-compose.dev.yml"
```

### Also Update

- ✅ `.dev/infra/infrastructure.md` - Service inventory section
- ✅ `.dev/infra/CHANGELOG.md` - Add entry with date and change
- ✅ `CLAUDE.md` - If port ranges change

---

## Best Practices

### 1. Always Read Registry First

**Before writing ANY docker-compose configuration**:
```
1. Read .dev/infra/registry.yml
2. Extract relevant information
3. Design configuration based on registry
4. Validate against registry rules
```

### 2. Use DevOps Manager for Complex Tasks

**Don't try to do everything yourself**:
- Adding services → DevOps Manager
- Resolving conflicts → DevOps Manager
- Major changes → DevOps Manager

### 3. Keep Registry in Sync

**Registry must always reflect reality**:
- Update immediately after changes
- Never deploy without updating registry
- Validate after every update

### 4. Document Everything

**Traceability is critical**:
- CHANGELOG entry for every change
- Update infrastructure.md
- Reference registry in commit messages

---

## Quick Checklist for Agents

Before ANY infrastructure operation:

- [ ] Read `.dev/infra/registry.yml`
- [ ] Extract port allocations for target app
- [ ] Check network requirements
- [ ] Verify dependencies
- [ ] Validate against rules
- [ ] Invoke DevOps Manager if complex
- [ ] Update registry after changes
- [ ] Update documentation
- [ ] Run validation script
- [ ] Verify deployment

**If you can't check all boxes, STOP and consult DevOps Manager.**

---

## Summary

🔴 **THE RULE**: Read `.dev/infra/registry.yml` BEFORE any port, network, or Docker configuration operation.

🔴 **NO EXCEPTIONS**: This is MANDATORY for ALL agents.

🔴 **VALIDATION**: Always run `axiom.ps1 validate` after changes.

🔴 **UPDATES**: Keep registry, docs, and changelog in sync.

**Remember**: Registry is the SINGLE SOURCE OF TRUTH. Respect it.

---

**Policy Version**: 1.0
**Last Updated**: 2025-11-28 18:44
**Enforcement**: Automatic via CLAUDE.md
**Authority**: AXIOM Platform Team
**Questions**: Consult DevOps Manager agent
