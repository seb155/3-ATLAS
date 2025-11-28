# SYNAPSE Roadmap

Development roadmap and sprint planning for SYNAPSE MBSE Platform.

---

## Current Version: v0.2.2

**Status:** UX Professional + Infrastructure ✅ MOSTLY COMPLETE
**Updated:** 2025-11-28

---

## Version Overview

| Version | Name | Status | Target Date |
|---------|------|--------|-------------|
| v0.2.1 | Logging & Monitoring | ✅ DONE | 2025-11-24 |
| v0.2.2 | UX Professional + Infra | 🔄 IN PROGRESS | 2025-11-29 |
| v0.2.3 | 3-Tier Asset Model | ⬜ PLANNED | 2025-12-06 |
| v0.2.4 | Breakdown Structures | ⬜ PLANNED | 2025-12-13 |
| v0.2.5 | Search & Navigation (Advanced) | ⬜ PLANNED | 2025-12-20 |
| v0.2.6 | Package Generation | ⬜ PLANNED | 2026-01-03 |
| v0.2.7 | Version History | ⬜ PLANNED | 2026-01-10 |
| v0.2.8 | Baselines & Impact Analysis | ⬜ PLANNED | 2026-01-17 |
| v0.2.9 | Rule Visualization | ⬜ PLANNED | 2026-01-24 |
| v0.2.10 | Visual Rule Editor | ⬜ PLANNED | 2026-01-31 |
| v0.2.11 | Rule Templates Library | ⬜ PLANNED | 2026-02-07 |
| v0.2.12 | Lifecycle Whiteboard | ⬜ PLANNED | 2026-02-14 |
| v0.3.0 | Multi-Tenant Auth | ⬜ PLANNED | 2026-02-28 |
| v0.4.0 | Background Processing | ⬜ PLANNED | 2026-03-14 |
| v0.5.0 | AI Integration | 🟡 PARTIAL | 2026-04-11 |
| v0.6.0 | P&ID Intelligence | ⬜ PLANNED | 2026-05-09 |
| v0.7.0 | Drawing Generation | ⬜ PLANNED | 2026-06-13 |
| v1.0.0 | Production Ready | ⬜ PLANNED | 2026-08-01 |

> **Note:** v0.5.0 AI Integration partially complete - AI provider abstraction (Ollama/OpenAI/Gemini) implemented in v0.2.2

---

## Active Sprint

**Current:** [v0.2.2 - UX Professional](current-sprint.md)  
**Next:** [v0.3.0 - Multi-Tenant Auth](next-sprint.md)

---

## Roadmap Phases

### Phase 1: Core Platform (v0.2.x)
**Duration:** v0.2.1 → v0.2.11 (2025-11-24 → 2026-02-07)  
**Goal:** Complete all essential engineering features for MBSE workflows

#### v0.2.1 - Logging & Monitoring ✅ DONE
- Loki + Grafana + Promtail
- WebSocket real-time logging
- DevConsole integration
- HTTP request/response logging

**Details:** Completed 2025-11-24

#### v0.2.2 - UX Professional
- Clickable navigation (tags → sidebar)
- Context menus (right-click actions)
- Command Palette (Ctrl+K)
- Keyboard shortcuts
- Professional polish

**Details:** [backlog/core-platform-v0.2.x.md](backlog/core-platform-v0.2.x.md#v022)

#### v0.2.3 - 3-Tier Asset Model
- Engineering Assets (design phase)
- Catalog Assets (procurement, vendors, specs)
- Physical Assets (as-built, serials, locations)
- Status Workflow (DESIGN → COMMISSION → OPERATE)

**Details:** [backlog/3-tier-asset-model.md](backlog/3-tier-asset-model.md)

#### v0.2.4 - Breakdown Structures
- FBS (Functional Breakdown)
- LBS (Location Breakdown)
- WBS (Work Breakdown / Packages)
- OBS (Organization / Disciplines)
- CBS (Cost Breakdown)
- PBS (Product Breakdown / Assembly)
- UI navigation between structures

**Details:** [backlog/breakdown-structures.md](backlog/breakdown-structures.md)

#### v0.2.5 - Search & Navigation
- MeiliSearch integration (self-hosted)
- Full-text search (10K+ assets)
- Filters (type, status, location, discipline)
- Recent searches, saved queries
- Search performance optimization

**Details:** [backlog/search-navigation.md](backlog/search-navigation.md)

#### v0.2.6 - Package Generation
- Excel generation (openpyxl)
- PDF generation (WeasyPrint)
- Standard templates: IN-P040, EL-M040, CA-P040, IO-P040
- Download queue with progress
- Template customization system

**Details:** [backlog/package-generation.md](backlog/package-generation.md)

#### v0.2.7 - Version History & Change Management
- Asset version history (per-asset tracking)
- Change tracking (who/when/why)
- Audit log (complete project history)
- Compare versions (diff view)
- Rollback capabilities

**Details:** [backlog/change-management.md](backlog/change-management.md#version-history)

#### v0.2.8 - Baselines & Impact Analysis
- Project baselines (freeze/snapshot)
- Baseline compare (project-level diff)
- Impact analysis engine
- Change request tracking
- Cost/schedule impact calculation

**Details:** [backlog/change-management.md](backlog/change-management.md#baselines-impact)

#### v0.2.9 - Rule Visualization
- 2D Graph view (ReactFlow)
- Rule dependencies display
- Interactive navigation
- Execution trace visualization
- Click to edit rules

**Details:** [backlog/rule-visualization-editor.md](backlog/rule-visualization-editor.md#visualization)

#### v0.2.10 - Visual Rule Editor
- Natural Language condition builder
- Form Builder mode
- Node-Based visual editor
- Code Mode (Monaco) for power users
- Action builder with templates
- Rule testing & simulation

**Details:** [backlog/rule-visualization-editor.md](backlog/rule-visualization-editor.md#editor)

#### v0.2.11 - Rule Templates Library
- 15+ predefined templates:
  - Equipment rules (Pump→Motor, Motor→Cable, etc.)
  - Property rules (Set Voltage, Enclosure, etc.)
  - Validation rules (HP match, Cable sizing, etc.)
  - Package rules (Auto-add to packages)
- Import/Export rules (JSON)
- Template customization
- Community template sharing (future)

**Details:** [backlog/rule-visualization-editor.md](backlog/rule-visualization-editor.md#templates)

#### v0.2.12 - Lifecycle Whiteboard
- Trident View (3 columns: Requirements, Manufacturer Model, Field Asset)
- Mining commissioning workflow statuses
- Compare modal (Req vs Manuf specs)
- Status change modal with dropdown
- Status history / audit trail
- Multi-criteria filters

**Details:** [backlog/lifecycle-whiteboard.md](backlog/lifecycle-whiteboard.md)

---

### Phase 2: Multi-Tenant & Security (v0.3.0)
**Duration:** 2 weeks (2026-02-07 → 2026-02-21)  
**Goal:** Enterprise authentication and multi-tenant architecture

- Azure AD integration + SSO
- RBAC (5 roles: SysAdmin, OrgAdmin, ProjectManager, Engineer, Viewer)
- Organization hierarchy (Org → Client → Project)
- User management UI
- Audit trail integration
- Session management

**Details:** [backlog/multi-tenant-auth.md](backlog/multi-tenant-auth.md)

---

### Phase 3: Background Processing (v0.4.0)
**Duration:** 3 weeks (2026-02-21 → 2026-03-14)  
**Goal:** Async processing for large imports and long-running operations

- Celery + Redis workers
- Async imports (1K-5K rows)
- Batch rule execution
- Scheduled jobs (backups, reports)
- Progress tracking (WebSocket)
- Job queue management UI

**Details:** [backlog/background-processing.md](backlog/background-processing.md)

---

### Phase 4: AI Integration (v0.5.0)
**Duration:** 4 weeks (2026-03-14 → 2026-04-11)  
**Goal:** Local AI assistance for navigation and documentation

- Ollama + LLaMA 70B (local, confidential)
- Navigation chatbot ("Show motors in Area 210")
- Rule explanation (natural language)
- Documentation search (embeddings)
- AI-powered validation suggestions

**Details:** [backlog/ai-strategy.md](backlog/ai-strategy.md)

---

### Phase 5: P&ID Intelligence (v0.6.0)
**Duration:** 4 weeks (2026-04-11 → 2026-05-09)  
**Goal:** P&ID ingestion and automated asset creation

- Claude Vision API integration
- Symbol recognition (YOLOv8 + custom training)
- Auto-create assets from drawings
- P&ID validation
- Instrumentation diagram parsing

**Details:** [backlog/pid-electrical-strategy.md](backlog/pid-electrical-strategy.md)

---

### Phase 6: Drawing Generation (v0.7.0)
**Duration:** 5 weeks (2026-05-09 → 2026-06-13)  
**Goal:** Automated P&ID and electrical drawing generation

- SVG/PDF P&ID generation
- DXF export (ezdxf)
- Auto-layout (Graphviz)
- Symbol library (ISA standards)
- Single-line diagrams
- Cable routing diagrams

**Details:** [backlog/pid-electrical-strategy.md](backlog/pid-electrical-strategy.md)

---

### Phase 7: Production Ready (v1.0.0)
**Duration:** 7 weeks (2026-06-13 → 2026-08-01)  
**Goal:** Production deployment readiness

- Full test coverage (>80%)
- Security audit
- Performance optimization
- Documentation complete
- Deployment guides
- Client training materials

---

## Key Strategic Decisions

### Database: PostgreSQL Only
- ✅ Full JSONB support for flexible schemas
- ✅ Proven performance at scale
- ✅ Rich ecosystem (PostGIS, full-text search)
- ❌ NO SQLite (dev or prod)

### UI: No Modals/Popups
- ✅ Side panels, inline expansion
- ✅ Page-based navigation
- ❌ NO modals unless absolutely necessary

### AI: Local-First
- ✅ Default: Ollama + LLaMA 70B (100% local, confidential)
- ✅ Fallback: Cloud AI (Gemini/GPT-4) for non-confidential only
- ✅ Hardware: RTX 3080 Ti sufficient

### Search: MeiliSearch
- ✅ Self-hosted, open source
- ✅ Optimized for 10K+ documents
- ✅ Fast typo-tolerant search
- ✅ Faceted filters

### Background Jobs: Celery
- ✅ Proven Python async framework
- ✅ Redis for broker and results
- ✅ Progress tracking via WebSocket
- ✅ Scheduled jobs support

---

## Folder Structure

```
.dev/roadmap/
├── README.md                     ← This file (overview)
├── current-sprint.md              ← Active sprint details
├── next-sprint.md                 ← Next sprint planning
└── backlog/                       ← Future features & strategies
    ├── core-platform-v0.2.x.md    ← v0.2.2-v0.2.11 detailed specs
    ├── 3-tier-asset-model.md      ← Engineering/Catalog/Physical
    ├── breakdown-structures.md    ← FBS/LBS/WBS/CBS/PBS/OBS
    ├── package-generation.md      ← Excel/PDF deliverables
    ├── search-navigation.md       ← MeiliSearch integration
    ├── change-management.md       ← Impact Analysis, Versioning, Baselines
    ├── rule-visualization-editor.md  ← Rule graph, visual editor, templates
    ├── lifecycle-whiteboard.md    ← Asset lifecycle tracking (NEW)
    ├── background-processing.md   ← Celery + Redis
    ├── multi-tenant-auth.md       ← Azure AD + RBAC
    ├── ai-strategy.md             ← Local AI integration
    ├── pid-electrical-strategy.md ← P&ID OCR + Drawing generation
    ├── technical-stack-planning.md ← Full tech stack
    └── ui-developer-features.md   ← Advanced UI features
```

---

## Quick Links

| Need | File |
|------|------|
| Current sprint | [current-sprint.md](current-sprint.md) |
| Next sprint | [next-sprint.md](next-sprint.md) |
| Core Platform v0.2.x | [backlog/core-platform-v0.2.x.md](backlog/core-platform-v0.2.x.md) |
| 3-Tier Assets | [backlog/3-tier-asset-model.md](backlog/3-tier-asset-model.md) |
| Breakdown Structures | [backlog/breakdown-structures.md](backlog/breakdown-structures.md) |
| Package Generation | [backlog/package-generation.md](backlog/package-generation.md) |
| Search & Navigation | [backlog/search-navigation.md](backlog/search-navigation.md) |
| Change Management | [backlog/change-management.md](backlog/change-management.md) |
| Rule Editor | [backlog/rule-visualization-editor.md](backlog/rule-visualization-editor.md) |
| Lifecycle Whiteboard | [backlog/lifecycle-whiteboard.md](backlog/lifecycle-whiteboard.md) |
| Background Jobs | [backlog/background-processing.md](backlog/background-processing.md) |
| Auth Planning | [backlog/multi-tenant-auth.md](backlog/multi-tenant-auth.md) |
| AI Planning | [backlog/ai-strategy.md](backlog/ai-strategy.md) |
| P&ID Planning | [backlog/pid-electrical-strategy.md](backlog/pid-electrical-strategy.md) |

---

**Updated:** 2025-11-28 (Added Lifecycle Whiteboard v0.2.12)
