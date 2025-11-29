# AXIOM Infrastructure Management System

**Status**: ✅ Fully Implemented
**Version**: 1.0
**Date**: 2025-11-28 18:44

---

## Overview

Professional-grade Infrastructure as Code solution for managing the AXIOM Docker infrastructure with centralized configuration, AI-powered diagnosis, and automated validation.

### What Was Created

**Phase 1: Central Registry & Documentation**
- ✅ [registry.yml](registry.yml) - Single source of truth (ports, services, networks, rules)
- ✅ [infrastructure.md](infrastructure.md) - Complete AI-readable documentation
- ✅ [CHANGELOG.md](CHANGELOG.md) - Infrastructure change history

**Phase 2: DevOps Manager Agent**
- ✅ [.claude/agents/devops-manager.md](../../.claude/agents/devops-manager.md) - Opus-powered intelligent agent for infrastructure management

**Phase 3: Infra Skill**
- ✅ [.claude/skills/infra.md](../../.claude/skills/infra.md) - Quick reference skill for infrastructure status

**Phase 4: Validation & CLI Scripts**
- ✅ [.dev/scripts/validate-infra.ps1](../scripts/validate-infra.ps1) - Automated validation script
- ✅ [.dev/scripts/axiom.ps1](../scripts/axiom.ps1) - User-friendly CLI for operations

---

## Quick Start

### For Users (PowerShell CLI)

```powershell
# View infrastructure status
.\.dev\scripts\axiom.ps1 status

# View port allocations
.\.dev\scripts\axiom.ps1 ports

# Start SYNAPSE
.\.dev\scripts\axiom.ps1 start synapse

# View logs
.\.dev\scripts\axiom.ps1 logs synapse-backend

# Validate infrastructure
.\.dev\scripts\axiom.ps1 validate

# Check health
.\.dev\scripts\axiom.ps1 health

# Show all URLs
.\.dev\scripts\axiom.ps1 urls
```

### For AI Agents (Claude Code)

**Quick Reference (Read-Only)**:
```
skill: "infra"
```
Shows running services, port allocations, and quick status.

**Complex Operations (Diagnosis, Configuration, Validation)**:
```
Use Task tool with subagent_type="devops-manager"
```
Invokes intelligent Opus-powered agent for infrastructure management.

---

## Architecture

### Single Source of Truth: registry.yml

All infrastructure configuration is centralized in [registry.yml](registry.yml):

- **Port Allocations**: Complete registry with no conflicts
- **Service Definitions**: All FORGE, SYNAPSE, NEXUS services
- **Network Configuration**: forge-network topology
- **Startup Order**: Tier-based dependency management
- **Validation Rules**: Automated enforcement

### Port Allocation Ranges

| Application | Range | Allocated | Available |
|-------------|-------|-----------|-----------|
| **FORGE** | 3000-3999 | 9 ports | 991 ports |
| **SYNAPSE** | 4000-4999 | 2 ports | 998 ports |
| **NEXUS** | 5000-5999 | 2 ports | 998 ports |
| **PRISM** | 6000-6999 | 0 ports | 1000 ports |
| **ATLAS** | 7000-7999 | 0 ports | 1000 ports |

**Rule**: Each application has a dedicated 1000-port range. No conflicts allowed.

### Validation Rules Enforced

1. **Port Conflicts**: No duplicate port allocations
2. **Port Ranges**: All ports within correct application range
3. **Network Requirements**: Services on `forge-network` if accessing shared infrastructure
4. **Dependencies**: All dependencies running before dependent services
5. **Health Checks**: Critical services have health checks defined

---

## How It Works

### Workflow for Adding New Service

1. **User/Agent**: "I need to add PRISM backend service"

2. **Invoke DevOps Manager Agent**:
   ```
   Use Task tool with:
   - subagent_type: "devops-manager"
   - prompt: "Add PRISM backend service on port 6000"
   ```

3. **DevOps Manager**:
   - Reads `registry.yml` to check port availability
   - Validates port 6000 is in PRISM range (6000-6999)
   - Checks for conflicts (none found)
   - Generates docker-compose configuration
   - Provides registry update instructions
   - Updates documentation

4. **Result**:
   - New service configured
   - Registry updated
   - Documentation updated
   - CHANGELOG entry added
   - All validated automatically

### Workflow for Diagnosing Issues

1. **User**: "SYNAPSE frontend won't start"

2. **Invoke DevOps Manager Agent**:
   ```
   Use Task tool with:
   - subagent_type: "devops-manager"
   - prompt: "Diagnose why synapse-frontend won't start"
   ```

3. **DevOps Manager**:
   - Reads `registry.yml` for expected configuration
   - Runs `docker ps` to check actual state
   - Reads `docker logs synapse-frontend` for errors
   - Checks network configuration
   - Identifies root cause
   - Provides specific fix with file paths and line numbers

4. **Result**:
   - Root cause identified (e.g., not on forge-network)
   - Exact fix provided (add networks configuration)
   - Verification commands provided
   - Issue resolved

---

## Files Reference

### Registry & Documentation

| File | Purpose | Used By |
|------|---------|---------|
| [registry.yml](registry.yml) | Central infrastructure registry | DevOps Manager, validate-infra.ps1, axiom.ps1 |
| [infrastructure.md](infrastructure.md) | Complete documentation | AI agents, developers |
| [CHANGELOG.md](CHANGELOG.md) | Change history | Tracking, rollback procedures |

### AI Agents & Skills

| File | Type | Model | Purpose |
|------|------|-------|---------|
| [devops-manager.md](../../.claude/agents/devops-manager.md) | Agent | Opus | Infrastructure orchestration, diagnosis, validation |
| [infra.md](../../.claude/skills/infra.md) | Skill | - | Quick status reference (read-only) |

### Automation Scripts

| File | Purpose | Usage |
|------|---------|-------|
| [validate-infra.ps1](../scripts/validate-infra.ps1) | Validate infrastructure against registry rules | `.dev\scripts\validate-infra.ps1` |
| [axiom.ps1](../scripts/axiom.ps1) | User-friendly CLI for common operations | `.dev\scripts\axiom.ps1 <command>` |

---

## Validation

### Automated Validation

Run validation script to check for issues:

```powershell
.\.dev\scripts\validate-infra.ps1
```

**Checks**:
- ✅ Port conflicts
- ✅ Port range violations
- ✅ Network requirements
- ✅ Dependency satisfaction
- ✅ forge-network existence
- ✅ Health checks for critical services

**Exit Codes**:
- `0` - All validations passed
- `1` - Issues detected (see output for details)

### Manual Validation

Before deploying new service:

1. Check port availability:
   ```powershell
   .\.dev\scripts\axiom.ps1 ports
   ```

2. Validate configuration:
   ```powershell
   .\.dev\scripts\validate-infra.ps1 -Verbose
   ```

3. Consult DevOps Manager agent for approval

---

## Maintenance

### Adding New Service

1. **Determine port**: Check registry for available port in correct range
2. **Create docker-compose**: Configure service with correct network
3. **Update registry.yml**: Add port allocation and service definition
4. **Update infrastructure.md**: Add service to inventory
5. **Add CHANGELOG entry**: Document the addition
6. **Validate**: Run `validate-infra.ps1` to confirm

### Changing Port Allocation

1. **Check registry**: Verify new port is available
2. **Update docker-compose**: Change port mapping
3. **Update registry.yml**: Move allocation from old to new port
4. **Update CHANGELOG**: Document the change
5. **Validate**: Ensure no conflicts
6. **Restart service**: Apply changes

### Troubleshooting

**Issue: Port conflict detected**
```powershell
# Find what's using the port
netstat -ano | findstr :<port>

# Either kill the process or change port allocation
# Update registry.yml with new allocation
```

**Issue: Service can't connect to database**
```powershell
# Verify service is on forge-network
docker inspect <service> | findstr forge-network

# Add networks configuration if missing
# Update docker-compose file
```

**Issue: Validation fails**
```powershell
# Run validation with verbose output
.\.dev\scripts\validate-infra.ps1 -Verbose

# Follow recommendations in output
# Consult DevOps Manager agent if needed
```

---

## Integration with Claude Code

### Invoking DevOps Manager Agent

The DevOps Manager agent is invoked using Claude Code's Task tool:

```
subagent_type: "devops-manager"
prompt: "Your infrastructure request here"
```

**When to use**:
- Adding new services
- Diagnosing infrastructure problems
- Validating configurations
- Complex network issues
- Major infrastructure changes

### Using Infra Skill

The Infra skill provides quick status without invoking a full agent:

```
skill: "infra"
```

**When to use**:
- Quick status check
- Finding available ports
- Checking what's running
- Looking up service URLs

### Agent Handoff

Infra skill will automatically recommend using DevOps Manager agent when:
- Complex diagnosis needed
- Configuration changes required
- Validation needed before deployment

---

## Benefits

### Before This System

- ❌ Port conflicts were common
- ❌ No central registry of allocations
- ❌ Manual tracking in scattered files
- ❌ Difficult to diagnose issues
- ❌ No automated validation
- ❌ Agents didn't know infrastructure state

### After This System

- ✅ Single source of truth (registry.yml)
- ✅ Automated conflict detection
- ✅ AI-powered diagnosis (DevOps Manager)
- ✅ Quick reference (Infra skill)
- ✅ Automated validation scripts
- ✅ User-friendly CLI (axiom.ps1)
- ✅ Self-documenting infrastructure
- ✅ Changelog for traceability

---

## Future Enhancements

**Planned**:
- [ ] Automated backup system for all volumes
- [ ] Prometheus metrics collection
- [ ] Alerting system (Alertmanager)
- [ ] Multi-environment support (dev, staging, prod)
- [ ] Kubernetes migration path

**Under Consideration**:
- [ ] Auto-fix mode for validate-infra.ps1
- [ ] Health check dashboard (web UI)
- [ ] Slack/Discord integration for alerts
- [ ] Cost tracking for cloud deployments

---

## Credits

**Created**: 2025-11-28
**Version**: 1.0
**Maintainer**: AXIOM Platform Team

**Tools Used**:
- Docker & Docker Compose
- PowerShell 5.1+
- PowerShell-YAML module
- Claude Code with Opus model (DevOps Manager)

---

## Support

**For infrastructure questions**:
1. Check [infrastructure.md](infrastructure.md) for documentation
2. Run `axiom.ps1 status` or `axiom.ps1 health` for current state
3. Invoke DevOps Manager agent for complex issues
4. Check [CHANGELOG.md](CHANGELOG.md) for recent changes

**For validation errors**:
1. Run `validate-infra.ps1 -Verbose` for details
2. Consult DevOps Manager agent for resolution
3. Check registry.yml for expected configuration

**For CLI help**:
```powershell
.\.dev\scripts\axiom.ps1 -Help
```

---

**Documentation**: [infrastructure.md](infrastructure.md)
**Registry**: [registry.yml](registry.yml)
**Changelog**: [CHANGELOG.md](CHANGELOG.md)
