---
description: Complete onboarding for new developers
---

# Onboarding Workflow

**Goal:** Get new developer from zero to productive in 15 minutes.

## 1. Prerequisites Check

Verify installed:
- Docker Desktop
- Git
- Node.js 20+ (optional, for local dev)
- Python 3.11+ (optional, for local dev)

## 2. Clone & Setup

```bash
git clone https://github.com/seb155/EPCB-Tools.git
cd EPCB-Tools
```

## 3. Quick Start

// turbo
.\dev.ps1

**What this does:**
1. Starts workspace (PostgreSQL, Prisma, pgAdmin, Redis)
2. Starts SYNAPSE (backend + frontend with hot-reload)

**Wait:** 30-60 seconds for containers to start

## 4. Verify

// turbo
docker ps | grep -E "workspace|synapse"

**Expected:** 6 containers running

## 5. Access Application

- **Frontend:** http://localhost:4000
- **Login:** admin@aurumax.com / admin123!
- **API Docs:** http://localhost:8001/docs
- **Prisma Studio:** http://localhost:5555

## 6. Read Documentation

**Essential reading (15min):**
1. `docs/getting-started/01-installation.md`
2. `docs/getting-started/02-first-steps.md`
3. `docs/developer-guide/01-project-structure.md`

## 7. Load Context

// turbo
cat .dev/context/project-state.md

**This shows:** Current sprint, architecture, known issues

## 8. Ready!

**Next steps:**
- Create feature branch
- Read `.dev/roadmap/current-sprint.md` for current work
- Check `.agent/rules/` and `.agent/workflows/` for AI collaboration

**Need help?** See `docs/README.md`
