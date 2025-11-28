# Deployment

Deploy SYNAPSE for development and production.

---

## Development Deployment

### Quick Start

```powershell
.\dev.ps1
```

This starts:
1. **Workspace** (shared infrastructure)
   - PostgreSQL (database)
   - Prisma Studio (DB GUI)
   - pgAdmin (DB admin)
   - Redis (cache)

2. **SYNAPSE** (application)
   - Backend (FastAPI with hot-reload)
   - Frontend (Vite dev server with hot-reload)

### Manual Start

**Step 1 - Workspace (once per boot):**
```bash
cd workspace
docker-compose up -d
```

**Step 2 - SYNAPSE dev:**
```bash
cd apps/synapse
docker-compose -f docker-compose.dev.yml up --build
```

### What's Running

After startup, verify:
```bash
docker ps
```

Should show 6 containers:
- `workspace-postgres`
- `workspace-prisma`
- `workspace-pgadmin`
- `workspace-redis`
- `synapse-backend-1`
- `synapse-frontend-1`

---

## Production Deployment (Future)

### Architecture

**Production uses standalone deployment:**
```
apps/synapse/
  ├── db (dedicated PostgreSQL)
  ├── backend
  └── frontend
```

**vs Development (workspace shared DB)**

### Steps (Proxmox VM)

**1. Prepare server:**
```bash
# Install Docker + Docker Compose
curl -fsSL https://get.docker.com | sh
```

**2. Create production compose:**

Create `apps/synapse/docker-compose.yml`:
```yaml
version: '3.8'
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: synapse
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@db:5432/synapse
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres-data:
```

**3. Deploy:**
```bash
cd apps/synapse
docker-compose up -d
```

---

## Environment Variables

**Development (`.env` in workspace/):**
```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=synapse
```

**Production (`.env` in apps/synapse/):**
```bash
DB_PASSWORD=<secure-password>
SECRET_KEY=<jwt-secret>
ENVIRONMENT=production
```

---

## Stopping Services

**Development:**
```powershell
.\stop.ps1  # Stops workspace + SYNAPSE
```

**Or manually:**
```bash
cd apps/synapse
docker-compose -f docker-compose.dev.yml down

cd workspace
docker-compose down  # Optional, can keep running
```

**Production:**
```bash
cd apps/synapse
docker-compose down
```

---

## Troubleshooting

See [Installation Guide](../getting-started/01-installation.md#troubleshooting) for common issues.

---

## Next Steps

- [Installation](../getting-started/01-installation.md) - Development setup
- [Project Structure](01-project-structure.md) - Understand codebase
