# Docker Networking Best Practices

Guide for configuring service-to-service communication in AXIOM using Docker DNS resolution.

---

## Core Principles

### 1. Always Use Docker DNS Names

**DO:**
```yaml
DATABASE_URL=postgresql://postgres:postgres@forge-postgres:5432/synapse
REDIS_URL=redis://forge-redis:6379
```

**DON'T:**
```yaml
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/synapse  # ❌
DATABASE_URL=postgresql://postgres:postgres@192.168.1.10:5432/synapse  # ❌
```

### 2. Never Hardcode IP Addresses

Hardcoded IPs break when:
- Containers restart with different IPs
- Moving between environments (dev/staging/prod)
- Deploying to different infrastructure

**Exception:** External services outside your Docker network (client servers, external APIs).

### 3. Use Container Names for Service Discovery

Docker automatically creates DNS entries for:
- Container names (`container_name: forge-postgres`)
- Service names in docker-compose (`services: postgres:`)

---

## FORGE Network Architecture

All AXIOM applications communicate via the shared `forge-network` bridge network.

### Network Topology

```
┌──────────────────────────────────────────────────────────┐
│                    forge-network (bridge)                 │
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ SYNAPSE  │  │  NEXUS   │  │  CORTEX  │  │  PRISM   │ │
│  │ :4000    │  │  :5173   │  │  :8000   │  │  :6000   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
│       │             │             │             │        │
│       └─────────────┴─────────────┴─────────────┘        │
│                          │                               │
│  ┌───────────────────────┴────────────────────────────┐  │
│  │          FORGE Infrastructure Services             │  │
│  │                                                     │  │
│  │  ┌─────────┐  ┌───────┐  ┌──────┐  ┌───────────┐  │  │
│  │  │postgres │  │ redis │  │ loki │  │meilisearch│  │  │
│  │  │ :5432   │  │ :6379 │  │:3100 │  │   :7700   │  │  │
│  │  └─────────┘  └───────┘  └──────┘  └───────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Service Names

| Service | Container Name | DNS Name | Internal Port |
|---------|---------------|----------|---------------|
| PostgreSQL | `forge-postgres` | `forge-postgres` | 5432 |
| Redis | `forge-redis` | `forge-redis` | 6379 |
| Grafana | `forge-grafana` | `forge-grafana` | 3000 |
| Loki | `forge-loki` | `forge-loki` | 3100 |
| MeiliSearch | `forge-meilisearch` | `forge-meilisearch` | 7700 |
| Traefik | `forge-traefik` | `forge-traefik` | 80, 443 |

---

## Communication Patterns

### Pattern 1: Backend to Database (Docker DNS)

**Correct:**
```python
# In Python/FastAPI backend
DATABASE_URL = "postgresql://postgres:postgres@forge-postgres:5432/synapse"
```

**Why it works:**
- Docker DNS resolves `forge-postgres` to the current container IP
- Works across container restarts
- Works in any environment with `forge-network`

### Pattern 2: Backend to Cache (Docker DNS)

**Correct:**
```python
REDIS_URL = "redis://forge-redis:6379"
```

### Pattern 3: Backend to Backend (Docker DNS)

**Correct:**
```javascript
// SYNAPSE calling CORTEX API
const CORTEX_API_URL = "http://cortex-backend:8000";
```

**DON'T:**
```javascript
const CORTEX_API_URL = "http://localhost:8000";  // ❌ Only works locally
const CORTEX_API_URL = "http://192.168.1.10:8000";  // ❌ IP will change
```

### Pattern 4: Frontend to Backend (Public URLs)

**Important:** Frontends run in the browser, not in Docker!

**Correct:**
```javascript
// For production (via Traefik)
const API_URL = "https://api.axoiq.com";

// For local development
const API_URL = "http://localhost:8001";
```

**DON'T:**
```javascript
const API_URL = "http://synapse-backend:8000";  // ❌ Browser can't resolve Docker DNS
```

---

## Environment-Specific Configuration

### Docker Mode (Containers Talking to Each Other)

Use Docker DNS names:
```env
DATABASE_HOST=forge-postgres
DATABASE_PORT=5432
REDIS_HOST=forge-redis
REDIS_PORT=6379
```

### Local Mode (Running Outside Docker)

Use localhost with external ports:
```env
DATABASE_HOST=localhost
DATABASE_PORT=5433  # External port mapping
REDIS_HOST=localhost
REDIS_PORT=6379
```

### How to Switch

Use the `generate-env.ps1` script (auto-detects environment):
```powershell
cd backend
.\generate-env.ps1
```

The script automatically detects:
1. If running inside Docker container
2. If `forge-network` exists
3. Generates correct `.env` with appropriate DNS names

---

## Anti-Patterns

### ❌ Anti-Pattern 1: Hardcoded Localhost

**Problem:**
```python
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/synapse"
```

**Why it's bad:**
- Only works when running outside Docker
- Breaks in containerized environment
- Not portable

**Solution:**
```python
# Use Docker DNS for containers
DATABASE_URL = "postgresql://postgres:postgres@forge-postgres:5432/synapse"
```

### ❌ Anti-Pattern 2: Hardcoded IP Addresses

**Problem:**
```python
REDIS_URL = "redis://172.18.0.5:6379"
```

**Why it's bad:**
- IP changes on container restart
- Different IPs in different environments
- Impossible to maintain

**Solution:**
```python
REDIS_URL = "redis://forge-redis:6379"
```

### ❌ Anti-Pattern 3: Mixed Docker/Localhost

**Problem:**
```env
DATABASE_URL=postgresql://postgres:postgres@forge-postgres:5432/synapse
REDIS_URL=redis://localhost:6379
```

**Why it's bad:**
- Inconsistent configuration
- Half works in Docker, half doesn't
- Debugging nightmare

**Solution:**
```env
# All Docker DNS (for Docker environment)
DATABASE_URL=postgresql://postgres:postgres@forge-postgres:5432/synapse
REDIS_URL=redis://forge-redis:6379
```

---

## Troubleshooting

### Error: "Could not resolve host: forge-postgres"

**Cause:** Not connected to `forge-network`

**Solution:**
```yaml
# In docker-compose.yml
services:
  backend:
    networks:
      - forge-network

networks:
  forge-network:
    external: true
```

### Error: "Connection refused to forge-postgres:5432"

**Possible causes:**
1. FORGE infrastructure not running
2. Service not healthy yet

**Solution:**
```powershell
# Check if FORGE is running
docker ps | findstr forge

# Start FORGE if needed
cd D:\Projects\AXIOM\forge
docker compose up -d

# Check service health
docker inspect forge-postgres | findstr Health
```

### Error: "Name does not resolve" from frontend

**Cause:** Frontend code trying to use Docker DNS names

**Explanation:** Browsers can't resolve Docker DNS names!

**Solution:**
```javascript
// Use public URLs for frontend
const API_URL = process.env.VITE_API_URL || "http://localhost:8001";
```

---

## Best Practices Checklist

When creating a new service:

- [ ] Use Docker DNS names for all inter-service communication
- [ ] Never hardcode IP addresses
- [ ] Connect to `forge-network`
- [ ] Use `.env.template` with placeholders
- [ ] Provide `generate-env.ps1` script
- [ ] Document service name in URL registry
- [ ] Test both Docker and local modes
- [ ] Update Traefik configuration if needed

---

## Examples

### Example 1: New Backend Service

```yaml
# docker-compose.dev.yml
services:
  backend:
    image: myapp-backend
    environment:
      # Docker DNS names (from .env)
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
    networks:
      - forge-network

networks:
  forge-network:
    external: true
```

```env
# .env.template
DATABASE_URL=postgresql://postgres:postgres@{{DATABASE_HOST}}:{{DATABASE_PORT}}/myapp
REDIS_URL=redis://{{REDIS_HOST}}:{{REDIS_PORT}}/3
```

### Example 2: Service Calling Another Service

```python
# In SYNAPSE backend calling CORTEX API
import httpx

async def call_cortex_api():
    # Docker DNS name (works in containers)
    cortex_url = os.getenv("CORTEX_URL", "http://cortex-backend:8000")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{cortex_url}/api/v1/analyze")
        return response.json()
```

```env
# .env
CORTEX_URL=http://cortex-backend:8000  # Docker mode
# CORTEX_URL=http://localhost:8000    # Local mode
```

---

## Related Documentation

- [Environment Variables Guide](environment-variables.md)
- [Infrastructure Overview](README.md)
- [Traefik Routing Rules](../../.claude/agents/rules/10-traefik-routing.md)
- [URL Registry](../../.dev/infra/url-registry.yml)

---

**Last Updated:** 2025-11-29
**Version:** 1.0
