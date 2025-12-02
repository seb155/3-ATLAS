# ATLAS 2.0 - Sandbox Pool

Pre-warmed Docker containers for isolated parallel agent execution.

## Quick Start

```bash
# Build the sandbox image
docker compose -f docker-compose.sandbox.yml build

# Start pre-warmed sandboxes
docker compose -f docker-compose.sandbox.yml up -d

# Check pool status
python pool-manager.py status
```

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      SANDBOX POOL                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│  │  sandbox-    │ │  sandbox-    │ │  sandbox-    │           │
│  │  backend     │ │  frontend    │ │  qa          │           │
│  │  (pre-warm)  │ │  (pre-warm)  │ │  (pre-warm)  │           │
│  └──────────────┘ └──────────────┘ └──────────────┘           │
│                                                                │
│  Each sandbox:                                                 │
│  - Python 3.11 + Node.js 20                                   │
│  - FastAPI, pytest, ruff (backend)                            │
│  - TypeScript, vitest, eslint (frontend)                      │
│  - 1 CPU, 1GB RAM limit                                       │
│  - Mounted: /workspace → AXIOM root                           │
└────────────────────────────────────────────────────────────────┘
```

## Pool Manager Commands

```bash
# Show pool status
python pool-manager.py status

# Acquire sandbox for agent
python pool-manager.py acquire backend-builder

# Release sandbox back to pool
python pool-manager.py release backend-builder

# Execute command in agent's sandbox
python pool-manager.py exec backend-builder pytest tests/

# Pre-warm pool (create minimum containers)
python pool-manager.py warm

# Cleanup idle/stopped sandboxes
python pool-manager.py cleanup
```

## Configuration

Edit `sandbox-config.yml`:

```yaml
pool:
  min_warm: 2      # Always keep 2 sandboxes ready
  max_size: 5      # Maximum 5 concurrent sandboxes
  idle_timeout: 300  # Recycle after 5 min idle

sandbox:
  resources:
    cpu: "1.0"
    memory: "1Gi"
```

## Docker Compose Usage

```bash
# Start with specific number of sandboxes
docker compose -f docker-compose.sandbox.yml up -d --scale sandbox=3

# View logs
docker compose -f docker-compose.sandbox.yml logs -f

# Stop all
docker compose -f docker-compose.sandbox.yml down
```

## Integration with ATLAS

The sandbox pool integrates with ATLAS parallel agents:

1. **ATLAS dispatches parallel tasks** to multiple agents
2. **Each agent acquires a sandbox** via pool-manager
3. **Work happens in isolated containers** (no file conflicts)
4. **Results merge back** to main workspace
5. **Sandboxes released** back to pool

## Files

| File | Purpose |
|------|---------|
| `Dockerfile.agent` | Sandbox container image |
| `docker-compose.sandbox.yml` | Pool orchestration |
| `sandbox-config.yml` | Pool configuration |
| `pool-manager.py` | CLI for pool management |

## Network

Sandboxes join `forge_default` network to access:
- PostgreSQL (forge-postgres)
- Redis (forge-redis)
- Other FORGE services

## Security

- Containers run as non-root user `agent`
- `no-new-privileges` security option
- Resource limits enforced (CPU, memory)
- Read-only rootfs option available
