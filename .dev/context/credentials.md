# Development Credentials

**Single source of truth for local development access.**

---

## 🚀 Portal (New!)

| Service | URL | Credentials |
|---------|-----|-------------|
| **Portal Dashboard** | https://portal.localhost | (no auth) |
| **Traefik Dashboard** | http://localhost:8888 | (no auth - dev only) |

## Application

| Service | URL (Direct) | URL (via Portal) | Credentials |
|---------|--------------|------------------|-------------|
| **Frontend** | http://localhost:4000 | https://synapse.localhost | admin@aurumax.com / admin123! |
| **API Docs** | http://localhost:8001/docs | https://api.localhost/docs | (uses JWT from login) |

## Database Tools

| Tool | URL (Direct) | URL (via Portal) | Credentials |
|------|--------------|------------------|-------------|
| **Prisma Studio** | http://localhost:5555 | https://prisma.localhost | (no auth) |
| **pgAdmin** | http://localhost:5050 | https://pgadmin.localhost | postgres / postgres |
| **PostgreSQL** | localhost:5433 | (internal only) | postgres / postgres / synapse |

## Monitoring & Logging

| Tool | URL (Direct) | URL (via Portal) | Credentials |
|------|--------------|------------------|-------------|
| **Grafana** | http://localhost:3000 | https://grafana.localhost | admin / xZfFu3&FZCBe |
| **Loki** | http://localhost:3100/ready | https://loki.localhost | (no auth - API only) |
| **DevConsole** | Frontend `Ctrl+\`` | - | - |

## Testing & Reporting

| Tool | URL (Direct) | URL (via Portal) | Credentials | Notes |
|------|--------------|------------------|-------------|-------|
| **Allure** | http://localhost:5252 | https://allure.localhost | (no auth) | ~100MB RAM |
| **ReportPortal** | http://localhost:8080 | https://reportportal.localhost | default / superadmin / erebus | ~4-6GB RAM |
| **RabbitMQ** | http://localhost:15672 | https://rabbitmq.localhost | rabbitmq / rabbitmq | ReportPortal only |

## Cache

| Tool | URL | Credentials |
|------|-----|-------------|
| **Redis** | localhost:6379 | (no auth) |

## Quick Start

```powershell
# New: Modern Portal with SSL
.\workspace\start-portal.ps1   # Start Portal + All Services
.\workspace\stop-portal.ps1    # Stop everything

# Legacy: Direct start
.\dev.ps1    # Start everything (no portal)
.\stop.ps1   # Stop everything
```

---

**Updated:** 2025-11-24
