# 001 - Workspace Monorepo Architecture

**Status:** ✅ Accepted  
**Date:** 2025-11-23  
**Deciders:** Sébastien Gagné (seb155), AI (Gemini)  
**Tags:** #architecture #docker #monorepo #workspace

---

## Context

SYNAPSE development requires several dev tools running constantly:
- PostgreSQL (database)
- Prisma Studio (DB GUI)
- pgAdmin (DB admin)
- Redis (cache - future)

**Problems with single docker-compose:**
1. Not reusable for future projects
2. Mixes infrastructure with application
3. Can't deploy SYNAPSE standalone easily
4. Dev tools restart every time app restarts

**Goal:** Efficient dev environment + clean production deployment

---

## Decision

Implement **workspace/apps monorepo** architecture:

```
EPCB-Tools/
├── workspace/              # Shared dev infrastructure
│   ├── docker-compose.yml  # PostgreSQL, Prisma, pgAdmin, Redis
│   └── scripts/            # Startup scripts
│
└── apps/synapse/           # SYNAPSE application
    ├── backend/
    ├── frontend/
    └── docker-compose.dev.yml  # Connects to workspace
```

**Development workflow:**
- Workspace starts once (shared DB, tools)
- Apps connect to workspace
- Independent app development

**Production deployment:**
- SYNAPSE deploys standalone
- Includes own dedicated PostgreSQL
- No workspace dependency

---

## Consequences

### Positive ✅

1. **Efficient development**
   - Workspace runs once, supports multiple projects
   - Shared PostgreSQL = faster, less memory
   - Dev tools always available (Prisma Studio, pgAdmin)

2. **Clean separation**
   - Infrastructure (workspace) vs Application (apps)
   - Clear responsibilities
   - Easier to understand

3. **Flexible deployment**
   - DEV: Shared workspace (efficient)
   - PROD: Standalone app (portable)
   - Can switch models easily

4. **Scalable**
   - Add more apps to workspace easily
   - Workspace tools benefit all projects
   - Standard monorepo pattern

### Negative ⚠️

1. **Initial complexity**
   - Two docker-compose files to manage
   - More complex startup (workspace + app)
   - Need to document workflow clearly

2. **Learning curve**
   - Developers need to understand structure
   - Different DEV vs PROD configs
   - Network configuration between containers

3. **Maintenance**
   - Two Docker configs to keep in sync
   - Need automation scripts (dev.ps1, stop.ps1)

### Neutral ℹ️

- Industry-standard pattern (similar to Nx, Turborepo, but simpler)
- More upfront work, less ongoing maintenance
- Trade complexity for flexibility

---

## Alternatives Considered

### 1. Single docker-compose ❌

**Pros:**
- Simple
- One file to manage
- Easy to understand

**Cons:**
- Not reusable
- Mixes concerns (infra + app)
- Can't deploy standalone
- Tools restart with app

**Rejected:** Not scalable, not industry standard

### 2. Separate repositories ❌

**Pros:**
- Complete isolation
- Independent versioning

**Cons:**
- Too fragmented
- Duplicate configs
- Hard to share tools
- Complex development workflow

**Rejected:** Overkill for single team

### 3. Nx/Turborepo monorepo ❌

**Pros:**
- Full-featured monorepo tools
- Caching, task orchestration
- TypeScript/JavaScript optimized

**Cons:**
- Overkill for our needs
- Learning curve
- Python backend not well supported
- Complex configuration

**Rejected:** Too complex, we only have 1 app currently

### 4. Docker Compose profiles ❌

**Pros:**
- Single docker-compose.yml
- Profiles for different scenarios

**Cons:**
- Still mixes infra + app
- Not as clean separation
- Limited flexibility

**Rejected:** Not standard, less clear

---

## Implementation

### Files Created

1. **`workspace/docker-compose.yml`**
   - PostgreSQL (port 5433)
   - Prisma Studio (port 5555)
   - pgAdmin (port 5050)
   - Redis (port 6379)

2. **`apps/synapse/docker-compose.dev.yml`**
   - Backend (FastAPI with hot-reload)
   - Frontend (Vite dev server)
   - Connects to `forge-postgres`

3. **Quick start scripts**
   - `dev.ps1` - Start workspace + SYNAPSE
   - `stop.ps1` - Stop everything cleanly

### Migration

- Moved all SYNAPSE files from root to `apps/synapse/`
- Updated all import paths
- Updated Docker configs
- Cleaned project root (41 → 15 files)

### Documentation

- Created README_WORKSPACE.md
- Updated README.md
- Created docs/getting-started/01-installation.md
- Created docs/developer-guide/06-deployment.md

---

## Verification

**Success criteria:**
- [x] Workspace starts independently
- [x] SYNAPSE connects to workspace
- [x] Hot-reload works (backend + frontend)
- [x] All ports accessible
- [x] Documentation clear
- [x] Quick start < 5 minutes

**Tested:**
- ✅ Windows (WSL2 + Docker Desktop)
- ⏳ Linux (pending)
- ⏳ macOS (pending)

---

## Lessons Learned

1. **Upfront planning pays off**
   - Took time to design structure properly
   - Saved hours of refactoring later

2. **Documentation critical**
   - New structure requires good docs
   - Users need clear quick start

3. **Automation essential**
   - Scripts make workflow smooth
   - `dev.ps1` hides complexity

4. **Industry patterns work**
   - Workspace/apps is proven
   - Don't reinvent the wheel

---

## References

- [Monorepo Best Practices](https://monorepo.tools/)
- [Docker Compose Multi-Project](https://docs.docker.com/compose/multiple-compose-files/)
- Task: Workspace Architecture Refactor
- Journal: 2025-11-23

---

## Future Considerations

**When to revisit:**
- Adding 2nd application to workspace
- Production deployment to Proxmox
- Performance issues (unlikely)

**Possible improvements:**
- Add more workspace tools (monitoring, etc.)
- Automate workspace setup even more
- Cross-platform scripts (bash equivalent)

---

**Decision Status:** ✅ Implemented and Working  
**Would we choose differently?** No - proven to be correct choice
