# Nexus Architecture Overview

This document provides a high-level overview of Nexus's technical architecture.

---

## System Architecture

### Current (Phase 1) - Frontend Only

```
┌─────────────────────────────────────┐
│         Browser (Client)            │
│  ┌───────────────────────────────┐  │
│  │   React 19 Application        │  │
│  │   - Components (UI)           │  │
│  │   - Pages (Routes)            │  │
│  │   - Stores (Zustand)          │  │
│  │   - Routing (React Router)    │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Future (Phase 2+) - Full Stack

```
┌─────────────────────────────────────────────────────────────┐
│                       Browser (Client)                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            React 19 Frontend                          │  │
│  │  ┌─────────┐  ┌──────────┐  ┌────────────────────┐  │  │
│  │  │  Pages  │  │ Components │  │  TanStack Query   │  │  │
│  │  └─────────┘  └──────────┘  └────────────────────┘  │  │
│  │  ┌─────────┐  ┌──────────┐  ┌────────────────────┐  │  │
│  │  │  Stores │  │  TipTap  │  │   WebSocket Client │  │  │
│  │  └─────────┘  └──────────┘  └────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/WebSocket
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐   │
│  │   API Routes │  │  Auth (JWT)   │  │  WebSocket      │   │
│  └──────────────┘  └───────────────┘  └─────────────────┘   │
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐   │
│  │   Services   │  │  Graph Engine │  │  AI Integration │   │
│  └──────────────┘  └───────────────┘  └─────────────────┘   │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   PostgreSQL    │  │    Redis     │  │  File Storage  │  │
│  │   (Main DB)     │  │   (Cache)    │  │   (Uploads)    │  │
│  └─────────────────┘  └──────────────┘  └────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## Architecture Principles

### 1. **Frontend-First**
- Start with UI/UX
- Add backend as needed
- Static site generation where possible

### 2. **API-Driven**
- Backend exposes REST/GraphQL APIs
- Frontend is one client among many
- Enables integrations and automations

### 3. **Real-Time Ready**
- WebSocket support for collaboration
- Optimistic updates in UI
- CRDT-based conflict resolution (Yjs)

### 4. **Scalable**
- Horizontal scaling via Docker
- Database read replicas
- Redis caching layer
- CDN for static assets

### 5. **Type-Safe**
- TypeScript on frontend
- Pydantic schemas on backend
- Shared types via code generation

---

## Technology Stack

### Frontend (Current)

| Layer | Technology | Purpose |
|-------|------------|---------|
| **UI Framework** | React 19 | Component-based UI |
| **Language** | TypeScript 5.9 | Type safety |
| **Build Tool** | Vite 7 | Fast dev server & bundling |
| **Styling** | Tailwind CSS 4 | Utility-first CSS |
| **Routing** | React Router 7 | Client-side routing |
| **State (Client)** | Zustand 5 | Global app state |
| **State (Server)** | TanStack Query 5 | Server state caching |
| **Icons** | Lucide React | Icon library |

### Backend (Phase 2+)

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Framework** | FastAPI | Python web framework |
| **Language** | Python 3.11+ | Backend logic |
| **Database** | PostgreSQL 15 | Primary data store |
| **ORM** | SQLAlchemy 2 | Database abstraction |
| **Migrations** | Alembic | Schema versioning |
| **Cache** | Redis 7 | Session cache, pub/sub |
| **Auth** | JWT + OAuth2 | Authentication |
| **WebSocket** | FastAPI WebSocket | Real-time communication |

### Additional Libraries (Future Phases)

| Library | Purpose | Phase |
|---------|---------|-------|
| **TipTap** | Rich text editor | Phase 2 |
| **@dnd-kit** | Drag-and-drop | Phase 3 |
| **gantt-task-react** | Gantt charts | Phase 4 |
| **react-force-graph-3d** | 3D graph visualization | Phase 5 |
| **Three.js** | WebGL rendering | Phase 5 |
| **NetworkX** | Graph algorithms (backend) | Phase 5 |
| **Yjs** | CRDT collaboration | Phase 6 |
| **Claude API** | AI integration | Phase 6 |

---

## Data Flow

### Current (Phase 1) - Static

```
User Action → React Component → Zustand Store → UI Update
```

### Future (Phase 2+) - With Backend

```
User Action
    ↓
React Component
    ↓
TanStack Query
    ↓
HTTP Request → FastAPI → Database
    ↓              ↓          ↓
Response      Service    PostgreSQL
    ↓              ↓
TanStack Query Cache
    ↓
UI Update
```

### Real-Time (Phase 6) - Collaboration

```
User A Types
    ↓
TipTap Editor
    ↓
Yjs CRDT Update
    ↓
WebSocket Client → WebSocket Server → Broadcast
                                          ↓
                              User B WebSocket Client
                                          ↓
                                   Yjs CRDT Merge
                                          ↓
                                  TipTap Editor Update
```

---

## Component Architecture

### Frontend Component Hierarchy

```
App
├── AppLayout
│   ├── TopBar
│   │   ├── MenuButton
│   │   ├── Logo
│   │   ├── ThemeToggle
│   │   └── UserMenu (Phase 6)
│   ├── Sidebar
│   │   └── NavigationItem[]
│   ├── MainContent
│   │   └── Routes
│   │       ├── Dashboard
│   │       ├── Notes (Phase 2)
│   │       │   ├── NoteTree
│   │       │   ├── NoteEditor (TipTap)
│   │       │   └── BacklinksPanel
│   │       ├── Tasks (Phase 3)
│   │       │   ├── KanbanBoard
│   │       │   ├── TaskDetail
│   │       │   └── CommentThread
│   │       ├── Roadmap (Phase 4)
│   │       │   ├── GanttChart
│   │       │   └── MilestoneList
│   │       ├── Graph (Phase 5)
│   │       │   ├── GraphCanvas (3D)
│   │       │   ├── NodeInfo
│   │       │   └── AnalyticsPanel
│   │       └── Settings
│   └── StatusBar
└── GlobalModals
    ├── CommandPalette (future)
    └── SearchModal (future)
```

---

## Database Schema (Phase 2+)

### Core Tables

**users**
```sql
id, email, password_hash, name, created_at, updated_at
```

**notes**
```sql
id, user_id, title, content, parent_id, created_at, updated_at
```

**note_links**
```sql
id, source_note_id, target_note_id, created_at
```

**tasks** (Phase 3)
```sql
id, user_id, title, description, status, priority, due_date, created_at
```

**task_notes** (Phase 3)
```sql
id, task_id, note_id, created_at
```

**milestones** (Phase 4)
```sql
id, title, description, target_date, created_at
```

**graph_cache** (Phase 5)
```sql
id, user_id, graph_data (JSON), metrics (JSON), updated_at
```

**[→ Full Database Documentation](database.md)**

---

## Security Architecture

### Authentication (Phase 2+)

```
User Login
    ↓
Email + Password
    ↓
FastAPI /auth/login
    ↓
Verify credentials (bcrypt)
    ↓
Generate JWT (access + refresh tokens)
    ↓
Return tokens to client
    ↓
Store in httpOnly cookies (secure)
```

### Authorization

- **JWT tokens** for stateless auth
- **Role-based access control** (RBAC) for teams
- **Row-level security** in PostgreSQL
- **API rate limiting** via Redis

### Security Best Practices

- ✅ HTTPS only in production
- ✅ CORS configured properly
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS prevention (React escaping + CSP headers)
- ✅ CSRF tokens for state-changing operations
- ✅ Password hashing with bcrypt
- ✅ Rate limiting on API endpoints

---

## Deployment Architecture

### Development

```
Local Machine
├── Vite Dev Server (port 5173)
└── (FastAPI dev server - Phase 2+, port 8000)
```

### Production (Future)

```
                    ┌──────────────┐
                    │   Traefik    │ (Reverse Proxy + SSL)
                    └──────┬───────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
    ┌──────▼──────┐              ┌────────▼────────┐
    │   Frontend  │              │    Backend      │
    │   (Nginx)   │              │   (Uvicorn)     │
    │   Static    │              │   FastAPI App   │
    └─────────────┘              └────────┬────────┘
                                          │
                          ┌───────────────┴─────────────┐
                          │                             │
                   ┌──────▼──────┐            ┌────────▼────────┐
                   │ PostgreSQL  │            │     Redis       │
                   │  (Primary)  │            │    (Cache)      │
                   └─────────────┘            └─────────────────┘
```

**[→ Deployment Guide](../developer-guide/deployment.md)**

---

## Performance Considerations

### Frontend Optimization

- **Code Splitting** - Route-based lazy loading
- **Tree Shaking** - Remove unused code
- **Minification** - Terser for JS, cssnano for CSS
- **Image Optimization** - WebP format, lazy loading
- **Caching** - Service worker (future)

### Backend Optimization (Phase 2+)

- **Database Indexing** - On frequently queried columns
- **Query Optimization** - Use EXPLAIN, avoid N+1
- **Caching** - Redis for hot data
- **Background Jobs** - Celery for heavy tasks
- **CDN** - CloudFlare for static assets

### Graph Performance (Phase 5)

- **Web Workers** - Offload graph calculations
- **Viewport Culling** - Only render visible nodes
- **Level of Detail** - Simplify distant nodes
- **Caching** - Pre-compute expensive metrics
- **Incremental Updates** - Don't recalculate entire graph

---

## Monitoring & Observability (Future)

- **Frontend:** Sentry for error tracking
- **Backend:** Prometheus + Grafana metrics
- **Logs:** Structured logging (JSON), Loki
- **Tracing:** OpenTelemetry for distributed tracing
- **Uptime:** UptimeRobot or similar

---

## Further Reading

- **[Frontend Architecture](frontend.md)** - Deep dive into React setup
- **[Backend Architecture](backend.md)** - FastAPI structure (Phase 2+)
- **[Database Design](database.md)** - Schema and relationships
- **[Tech Stack Rationale](tech-stack.md)** - Why we chose each technology

---

**[⬆ Back to Docs Home](../README.md)**

*Last Updated: 2025-11-27*
