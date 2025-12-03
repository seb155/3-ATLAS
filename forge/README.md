# Workspace - Shared Development Infrastructure

> **Reusable infrastructure** for all EPCB-Tools projects.

---

## Quick Start

```powershell
# From project root
.\dev.ps1      # Start workspace + SYNAPSE

# Or manually
cd workspace
docker-compose up -d
```

---

## Services

| Service | Port | Purpose |
|---------|------|---------|
| **PostgreSQL** | 5433 | Database server |
| **Prisma Studio** | 5555 | Visual DB admin |
| **pgAdmin** | 5050 | Advanced DB admin |
| **Redis** | 6379 | Cache (future) |

---

## Structure

```
workspace/
├── docker-compose.yml           # Service definitions
├── .env                         # Environment variables
├── databases/postgres/init/     # DB initialization
│   └── 01-create-databases.sql  # Creates synapse, synapse_test
└── scripts/
    └── start.sh                 # Startup helper
```

---

## Credentials

| Service | User | Password |
|---------|------|----------|
| PostgreSQL | postgres | postgres |
| pgAdmin | dev@workspace.local | admin |
| Prisma Studio | (no auth) | - |

---

## Commands

```bash
# Start workspace
docker-compose up -d

# View logs
docker-compose logs -f

# Stop (keeps data)
docker-compose down

# Stop + delete data
docker-compose down -v

# Access PostgreSQL
docker exec -it forge-postgres psql -U postgres -d synapse
```

---

## Network

Workspace creates `forge-network` that apps connect to:

```yaml
# In app's docker-compose.dev.yml
networks:
  default:
    name: forge-network
    external: true
```

---

## Troubleshooting

**Port conflict:**
```bash
netstat -ano | findstr :5555  # Find process
```

**Network not found:**
```bash
docker-compose up -d  # Start workspace first
```

**Check status:**
```bash
docker ps | grep workspace
```

---

**Updated:** 2025-11-23
