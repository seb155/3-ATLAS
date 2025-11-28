# Installation

Get SYNAPSE running on your machine in 5 minutes.

---

## Prerequisites

Before starting, ensure you have:

- **[Docker Desktop](https://docker.com/products/docker-desktop)** - Container platform
- **[Node.js 20+](https://nodejs.org)** *(optional, for local frontend dev)*
- **[Python 3.11+](https://python.org)** *(optional, for local backend dev)*
- **Git** - To clone the repository

**Operating Systems:**
- ✅ Windows 10/11 (WSL2)
- ✅ macOS (Intel & Apple Silicon)
- ✅ Linux (Ubuntu, Debian, Fedora)

---

## Quick Start (Recommended)

### 1. Clone Repository

```bash
git clone https://github.com/seb155/EPCB-Tools.git
cd EPCB-Tools
```

### 2. Start Everything

**Windows:**
```powershell
.\dev.ps1
```

**Linux/macOS:**
```bash
./dev.sh  # Coming soon
# Or manual:
cd workspace && docker-compose up -d
cd ../apps/synapse && docker-compose -f docker-compose.dev.yml up
```

**What this does:**
1. Starts workspace infrastructure (PostgreSQL, Prisma Studio, pgAdmin, Redis)
2. Starts SYNAPSE backend (FastAPI)
3. Starts SYNAPSE frontend (React with hot-reload)

### 3. Verify Installation

After 30-60 seconds, check:

**Frontend:** http://localhost:4000  
**Backend API:** http://localhost:8001/docs  
**Prisma Studio:** http://localhost:5555  
**pgAdmin:** http://localhost:5050  

### 4. Login

Use these credentials:

| Field | Value |
|-------|-------|
| Email | `admin@aurumax.com` |
| Password | `admin123!` |

---

## Architecture Overview

SYNAPSE uses a **workspace/apps monorepo** structure:

```
EPCB-Tools/
├── workspace/          # Shared dev infrastructure
│   ├── PostgreSQL      # Database (port 5433)
│   ├── Prisma Studio   # DB GUI (port 5555)
│   ├── pgAdmin         # DB admin (port 5050)
│   └── Redis           # Cache (port 6379)
│
└── apps/synapse/       # SYNAPSE application
    ├── backend/        # FastAPI (port 8001)
    ├── frontend/       # React (port 4000)
    └── docker-compose.dev.yml
```

**Benefits:**
- ✅ Workspace runs once, supports multiple projects
- ✅ SYNAPSE connects to shared workspace for dev
- ✅ Clean separation for production deployment

---

## Manual Setup (Alternative)

If you prefer step-by-step control:

### Step 1: Start Workspace

```bash
cd workspace
docker-compose up -d
```

**Verify:**
```bash
docker ps | grep workspace
# Should show: workspace-postgres, workspace-prisma, workspace-pgadmin, workspace-redis
```

### Step 2: Start SYNAPSE

```bash
cd apps/synapse
docker-compose -f docker-compose.dev.yml up --build
```

**Verify:**
```bash
docker ps | grep synapse
# Should show: synapse-backend-1, synapse-frontend-1
```

---

## Verification Checklist

After installation, verify:

- [ ] `docker ps` shows 6 running containers
- [ ] http://localhost:4000 loads login page
- [ ] http://localhost:5555 loads Prisma Studio
- [ ] Login works with `admin@aurumax.com` / `admin123!`
- [ ] Project selector shows 2 projects (GoldMine Phase 1, Test Import)
- [ ] GoldMine project shows 12 assets

**All green?** You're ready! → [Next: First Steps](02-first-steps.md)

---

## Troubleshooting

### Port already in use

**Problem:** Another service is using workspace ports

**Check:**
```powershell
netstat -ano | findstr "4000 5433 5555 5050 6379 8001"
```

**Fix:** Stop conflicting services or change ports in `workspace/.env`

### Docker not running

**Symptoms:** "Cannot connect to Docker daemon"

**Fix:**
- Windows: Launch Docker Desktop app
- Linux: `sudo systemctl start docker`
- macOS: Start Docker Desktop

### Containers not starting

**Check logs:**
```bash
cd workspace
docker-compose logs -f

cd apps/synapse
docker-compose -f docker-compose.dev.yml logs -f backend
```

### Database connection failed

**Problem:** Backend can't reach PostgreSQL

**Verify workspace is running:**
```bash
docker exec workspace-postgres pg_isready -U postgres
# Expected: "accepting connections"
```

**Fix:** Start workspace first (`cd workspace && docker-compose up -d`)

---

## Windows-Specific: Performance Optimization

For best performance on Windows, configure WSL2 resources:

```powershell
.\scripts\optimize_wsl.ps1
wsl --shutdown
# Restart Docker Desktop
```

This optimizes memory/CPU allocation for your system.

---

## Stopping Services

**Stop everything:**
```powershell
.\stop.ps1
```

**Or manually:**
```bash
# Stop SYNAPSE
cd apps/synapse
docker-compose -f docker-compose.dev.yml down

# Stop workspace (optional, can keep running)
cd workspace
docker-compose down
```

**Note:** Workspace can stay running between dev sessions. Only stop when rebooting or troubleshooting.

---

## Next Steps

✅ **Installation complete!**

**Continue to:**
- **[First Steps](02-first-steps.md)** - Learn to use SYNAPSE
- **[Architecture Overview](03-architecture-overview.md)** - Understand the system

**For developers:**
- **[Project Structure](../developer-guide/01-project-structure.md)** - Deep dive into codebase
