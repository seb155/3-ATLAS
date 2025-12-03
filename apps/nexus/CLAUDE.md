# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Nexus** - Knowledge Graph Portal combining Notes, Wiki, Tasks, AI Chat & 3D Graph Visualization
**Current Phase:** 2.0 - Notes/Wiki System + TriliumNext Integration
**Version:** v0.2.0
**Target:** Functional MVP by Q2 2026

## TriliumNext Integration (NEW)

NEXUS is now integrated with TriliumNext for bidirectional note synchronization.

### Configuration

```env
# In backend/.env
TRILIUM_ETAPI_URL=https://notes.s-gagnon.com
TRILIUM_ETAPI_TOKEN=<your_etapi_token>
TRILIUM_SYNC_INTERVAL=60
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/trilium/status` | GET | Check Trilium connection |
| `/api/v1/trilium/notes` | GET | Search Trilium notes |
| `/api/v1/trilium/notes/{id}` | GET | Get Trilium note details |
| `/api/v1/trilium/sync/import` | POST | Import from Trilium |
| `/api/v1/trilium/sync/push/{id}` | POST | Push note to Trilium |
| `/api/v1/trilium/sync/full` | POST | Full bidirectional sync |
| `/api/v1/trilium/sync/status/{id}` | GET | Get sync status for note |

### Architecture

```
NEXUS ◄──────────► TriliumNext
  │      ETAPI        │
  │                   │
  ▼                   ▼
PostgreSQL        SQLite
(notes +          (source of
trilium_sync)      truth)
```

### Key Files

- `backend/app/services/trilium_sync.py` - Sync service
- `backend/app/routers/trilium.py` - API endpoints
- `backend/app/models/trilium_sync.py` - Sync mapping model

## Workspace Integration (EPCB-Tools)

**Nexus is integrated with the EPCB-Tools workspace** for shared infrastructure and SSO authentication.

### Running Modes

**1. Workspace Mode (Recommended for Development)**
- Shared PostgreSQL (forge-postgres)
- Shared Redis (forge-redis)
- Shared authentication (workspace_auth.users)
- Traefik routing with SSL (nexus.localhost)
- Loki/Grafana logging

```powershell
# Start from workspace directory
cd D:\Projects\EPCB-Tools\workspace
.\start-nexus.ps1

# Access
# Frontend: https://nexus.localhost or http://localhost:5173
# Backend:  https://api-nexus.localhost/docs or http://localhost:8000/docs
```

**2. Standalone Mode (Isolated Development)**
- Own PostgreSQL (localhost:5432)
- Own Redis (localhost:6379)
- No SSO, isolated from other apps

```powershell
# Start from Nexus directory
cd D:\Projects\nexus
.\dev.ps1

# Access
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000/docs
```

### Shared Authentication (SSO)

Users are stored in `workspace_auth.users` schema and shared across Nexus, Synapse, and other workspace apps.

**Default admin account (unified with AXIOM):**
- Email: `admin@aurumax.com`
- Password: `admin123!`

**JWT tokens** created by any workspace app (Nexus, Synapse) are valid across all apps.

**Environment variables (workspace mode):**
```env
DATABASE_URL=postgresql://postgres:postgres@forge-postgres:5432/nexus
AUTH_DATABASE_URL=postgresql://postgres:postgres@forge-postgres:5432/postgres?options=-csearch_path%3Dworkspace_auth
REDIS_URL=redis://forge-redis:6379
REDIS_KEY_PREFIX=nexus:
SECRET_KEY=<shared-workspace-secret>  # MUST match across apps
```

## Development Commands

### Frontend Development

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server (http://localhost:5173)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

**Note:** Port 5173 is used (not 3000) to avoid Grafana conflict.

### Backend Development

```bash
# Navigate to backend
cd backend

# Run server (via Docker - recommended)
docker compose -f docker-compose.dev.yml up backend

# Or locally with venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Run migrations
docker exec nexus-backend alembic upgrade head

# Access API docs
# http://localhost:8000/docs
```

### Backend Structure

```
backend/app/
├── main.py                    # FastAPI app
├── config.py                  # Settings (env vars)
├── database.py                # DB connections
├── models/
│   ├── user.py               # User model (workspace_auth)
│   ├── note.py               # Note + WikiLink models
│   └── trilium_sync.py       # Trilium sync mapping
├── routers/
│   ├── auth.py               # Authentication endpoints
│   ├── notes.py              # Notes CRUD
│   └── trilium.py            # Trilium sync endpoints
├── services/
│   ├── notes.py              # Notes business logic
│   └── trilium_sync.py       # Trilium ETAPI client
└── utils/
    └── dependencies.py       # Auth dependency
```

## Architecture

### State Management Pattern

**Zustand stores** with persistence middleware:
- `useAppStore.ts` - Global app state (sidebar, active tab)
- `useAuthStore.ts` - Authentication state (Phase 2+)
- `useThemeStore.ts` - Theme system with localStorage persistence

**Store pattern:**
```typescript
// All stores follow this pattern
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useStore = create()(
  persist(
    (set, get) => ({
      // State
      value: initial,

      // Actions (mutations)
      setValue: (newValue) => set({ value: newValue }),

      // Computed/selectors
      getComputed: () => get().value * 2,
    }),
    { name: 'storage-key' }
  )
);
```

### Component Architecture

**Layout Components:**
- `AppLayout.tsx` - Main container with sidebar + content area
- `Sidebar.tsx` - Navigation with icons (uses Lucide React)
- `TopBar.tsx` - Page title and actions
- `StatusBar.tsx` - Bottom status bar

**UI Components (`frontend/src/components/ui/`):**
- `Badge.tsx` - Status indicators with variants
- `Button.tsx` - Enhanced buttons with loading states
- `Card.tsx` - Container with glass morphism variants
- `StatCard.tsx` - Dashboard statistics display
- `Skeleton.tsx` - Loading placeholders with shimmer animation

**Component conventions:**
- All components use `@/` path alias (configured in `vite.config.ts` and `tsconfig.app.json`)
- TypeScript with strict mode enabled
- Tailwind CSS 4 for styling with custom design tokens
- Variants handled via `clsx` and `tailwind-merge` utilities

### Theme System

**13 pre-built themes** (6 dark, 6 light, 1 custom template) in `frontend/src/themes/`:
- Each theme is a JSON file with design tokens
- Themes apply CSS custom properties to `:root`
- `useThemeStore` manages active theme + custom theme CRUD
- `applyTheme()` function in `frontend/src/themes/index.ts` handles application
- Smooth transitions via CSS (configured in `index.css`)

**Theme token structure:**
```typescript
{
  id: string,
  name: string,
  mode: 'light' | 'dark',
  colors: { /* CSS custom properties */ },
  author?: string,
  version?: string
}
```

### Routing Structure

React Router DOM 7 with animated page transitions:
- `/` - Dashboard (stats + recent activity)
- `/notes` - Notes page (placeholder for Phase 2)
- `/tasks` - Tasks page (placeholder for Phase 3)
- `/roadmap` - Roadmap page (placeholder for Phase 4)
- `/graph` - Graph visualization (placeholder for Phase 5)
- `/settings` - Settings page (theme selector implemented)

**Route animations:** Configured in `App.tsx` with Tailwind animate utilities.

## Session Start Protocol

**IMPORTANT:** At the start of every session, run the smart resume script OR manually read context files.

### Quick Start (Recommended)

```powershell
.\.dev\scripts\smart-resume.ps1
```

### Manual Context Load

Read these files in order:
1. `.dev/context/project-state.md` - Current phase, version, tech stack
2. `.dev/journal/2025-11/YYYY-MM-DD.md` - Today's work log
3. `.dev/roadmap/current-sprint.md` - Active sprint details
4. `.dev/testing/test-status.md` - Test validation status

## AI Workflows

Slash commands available in `.agent/workflows/`:
- `/00-start` - Session start protocol
- `/01-new-feature` - Structured feature development
- `/02-new-component` - React component template
- `/03-database-migration` - DB schema changes (Phase 2+)
- `/04-test-validation` - Test tracking workflow

## Build Configuration

### TypeScript

**Strict mode enabled** with aggressive linting:
- `strict: true`
- `noUnusedLocals: true`
- `noUnusedParameters: true`
- Target: ES2022
- Module: ESNext (bundler mode)
- Path aliases: `@/*` → `./src/*`

### Vite

**Configuration (`frontend/vite.config.ts`):**
- React plugin with Fast Refresh
- Path alias resolution (`@` → `src/`)
- Dev server: `http://localhost:5173` (host: 0.0.0.0)
- Build output: `frontend/dist/`

### Tailwind CSS 4

**Custom design system:**
- CSS custom properties for theme tokens
- Utility classes for animations (`animate-in`, `fade-in`, etc.)
- Shadow system for depth hierarchy
- Glass morphism variants for cards
- 60fps animations via GPU-accelerated transforms

**Key files:**
- `frontend/src/index.css` - Global styles + theme setup
- `frontend/tailwind.config.js` - Tailwind configuration

## Development Tracking

All development tracking lives in `.dev/`:

**Structure:**
- `.dev/journal/` - Daily development logs (YYYY-MM-DD.md format)
- `.dev/context/` - Project state, credentials, decisions
- `.dev/testing/` - Test status tracking
- `.dev/roadmap/` - Phase roadmaps, current sprint
- `.dev/decisions/` - Architecture Decision Records (ADRs)

**Update these when:**
- Starting/ending sessions → Update journal
- Completing features → Update project-state.md
- Running tests → Update test-status.md
- Making architectural decisions → Create ADR

## Tech Stack Reference

**Frontend:**
- React 19.2.0 + TypeScript 5.9
- Vite 7.2.4
- Tailwind CSS 4.1.17
- React Router DOM 7.9.6
- Zustand 5.0.8 (state management)
- TanStack Query 5.90.11 (data fetching)
- Lucide React 0.555.0 (icons)
- TipTap (rich text editor)

**Backend:**
- FastAPI 0.109.0 (Python 3.11+)
- SQLAlchemy 2.0.25 + Alembic 1.13.1
- PostgreSQL 15 (via Docker)
- Redis 7 (caching)
- aiohttp 3.9.3 (async HTTP for Trilium)

**Integrations:**
- TriliumNext (ETAPI sync)
- Workspace SSO (JWT shared auth)

**Planned:**
- pgvector (AI embeddings)
- react-force-graph-3d (3D visualization)
- Yjs (CRDT collaboration)

## Known Patterns

### Import aliases

Always use `@/` prefix for src imports:
```typescript
// Good
import { Button } from '@/components/ui/Button';
import { useAppStore } from '@/stores/useAppStore';

// Bad
import { Button } from '../components/ui/Button';
import { useAppStore } from '../../stores/useAppStore';
```

### Utility function usage

`clsx` + `tailwind-merge` for className composition:
```typescript
import { cn } from '@/lib/utils';

// cn() is a utility that merges Tailwind classes intelligently
<div className={cn('base-class', variant && 'variant-class', className)} />
```

### Component prop patterns

```typescript
interface ComponentProps {
  children?: React.ReactNode;
  className?: string;
  variant?: 'default' | 'primary' | 'secondary';
  // ... other props
}

export function Component({
  children,
  className,
  variant = 'default',
  ...props
}: ComponentProps) {
  return (
    <div className={cn(baseStyles, variantStyles[variant], className)} {...props}>
      {children}
    </div>
  );
}
```

## Session End Checklist

Before ending a session:
1. Update `.dev/journal/YYYY-MM-DD.md` with completed work and next steps
2. Update `.dev/testing/test-status.md` if tests were added/validated
3. Review `git status` and commit changes with clear message
4. Update `.dev/context/project-state.md` if major changes occurred

---

**Last Updated:** 2025-11-29
**For AI System Documentation:** See `.agent/workflows/00-start.md`
