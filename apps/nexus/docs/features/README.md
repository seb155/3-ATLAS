# Nexus Features Overview

This directory contains detailed documentation for all Nexus features, organized by development phase.

## 📊 Development Phases

Nexus is being built in **6 phases**, each delivering a complete set of features:

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
  ✅        🏗️        📅        📅         📅         📅
Foundation  Notes    Tasks   Roadmap    Graph    AI+Collab
```

---

## Phase 1: Foundation ✅ **COMPLETE**

**Status:** Released (v0.1.0-alpha)
**Duration:** 1 day
**Completed:** 2025-11-27

### Summary

The foundation provides the technical infrastructure and UI shell for all future features.

### Features Delivered

| Feature | Description | Status |
|---------|-------------|--------|
| **Modern UI** | VSCode-inspired layout with sidebar, top bar, status bar | ✅ Complete |
| **Dark Theme** | Tailwind CSS 4 with elegant dark mode (light mode ready) | ✅ Complete |
| **Routing** | React Router with 6 pages (Dashboard, Notes, Tasks, Roadmap, Graph, Settings) | ✅ Complete |
| **State Management** | Zustand stores for global app state | ✅ Complete |
| **TypeScript** | Full type safety with strict mode enabled | ✅ Complete |
| **Build System** | Vite 7 with optimized production builds | ✅ Complete |

### Tech Stack

- **Frontend:** React 19, TypeScript 5.9, Vite 7
- **Styling:** Tailwind CSS 4
- **Routing:** React Router DOM 7
- **State:** Zustand 5
- **Icons:** Lucide React

**[📖 Read Full Documentation →](phase-1-foundation.md)**

---

## Phase 2: Notes/Wiki System 🏗️ **NEXT**

**Status:** Planning
**Target Start:** Week of 2025-12-02
**Duration:** 3-4 weeks
**Estimated Complete:** 2025-12-30

### Summary

Rich text note-taking system with hierarchical organization, wiki-style linking, and full-text search.

### Planned Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **TipTap Editor** | Rich text editor with markdown support | 🔴 Critical |
| **Note Tree** | Hierarchical sidebar with drag-drop organization | 🔴 Critical |
| **Wiki Links** | `[[note-name]]` syntax with autocomplete | 🔴 Critical |
| **Backlinks** | Panel showing all notes linking to current note | 🟡 High |
| **Full-Text Search** | Fast search across all notes (PostgreSQL tsvector) | 🟡 High |
| **Auto-Save** | Debounced auto-save every 2 seconds | 🟡 High |
| **Note Templates** | Pre-defined note structures | 🟢 Medium |
| **Tags** | Organize notes with tags | 🟢 Medium |

### Tech Stack Additions

- **Backend:** FastAPI, PostgreSQL, SQLAlchemy, Alembic
- **Editor:** TipTap (ProseMirror-based)
- **Auth:** JWT tokens
- **Search:** PostgreSQL full-text search

**[📖 Read Full Documentation →](phase-2-notes-wiki.md)**

---

## Phase 3: Task Management 📅

**Status:** Planned
**Target Start:** Q1 2026
**Duration:** 3-4 weeks
**Dependencies:** Phase 2 (backend, auth)

### Summary

Kanban-style task management with drag-drop boards, comments, and integration with notes.

### Planned Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **Kanban Board** | Drag-drop columns (Backlog → In Progress → Done) | 🔴 Critical |
| **Task CRUD** | Create, edit, delete tasks | 🔴 Critical |
| **Task Details** | Panel with description, assignees, due dates | 🟡 High |
| **Comments** | Discussion threads on tasks | 🟡 High |
| **Labels** | Color-coded task categorization | 🟡 High |
| **Note Links** | Link tasks to relevant notes | 🟡 High |
| **Task Search** | Filter and search tasks | 🟢 Medium |
| **Assignees** | Multi-user task assignment | 🟢 Medium |

### Tech Stack Additions

- **Drag-Drop:** @dnd-kit/core
- **State:** TanStack Query for server state

**[📖 Read Full Documentation →](phase-3-tasks.md)**

---

## Phase 4: Roadmap Planning 📅

**Status:** Planned
**Target Start:** Q1 2026
**Duration:** 2-3 weeks
**Dependencies:** Phase 3 (tasks)

### Summary

Gantt chart timeline for roadmap planning with milestones and task dependencies.

### Planned Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **Gantt Chart** | Timeline visualization of tasks and milestones | 🔴 Critical |
| **Milestones** | Major checkpoints with dates | 🔴 Critical |
| **Dependencies** | Task A blocks Task B relationships | 🟡 High |
| **Timeline View** | Monthly/quarterly views | 🟡 High |
| **Export** | Export roadmap to PDF/Excel | 🟢 Medium |
| **Slack Time** | Calculate buffer between tasks | 🟢 Medium |

### Tech Stack Additions

- **Gantt:** gantt-task-react or custom implementation
- **Export:** jsPDF, xlsx libraries

**[📖 Read Full Documentation →](phase-4-roadmap.md)**

---

## Phase 5: 3D Graph Visualization ⭐ **FLAGSHIP**

**Status:** Planned
**Target Start:** Q2 2026
**Duration:** 4-5 weeks
**Dependencies:** Phase 2 & 3 (notes + tasks for graph data)

### Summary

InfraNodus-inspired 3D force-directed graph with advanced network analytics.

### Planned Features

**Visualization:**
| Feature | Description | Priority |
|---------|-------------|----------|
| **2D Graph** | Force-directed layout in 2D | 🔴 Critical |
| **3D Graph** | WebGL-powered 3D visualization | 🔴 Critical |
| **Node Types** | Different visuals for notes, tasks, etc. | 🟡 High |
| **Interactive** | Pan, zoom, rotate, click nodes | 🟡 High |
| **Filters** | Show/hide node types, filter by tags | 🟡 High |

**Analytics (InfraNodus-style):**
| Feature | Description | Priority |
|---------|-------------|----------|
| **Betweenness Centrality** | Find bridge nodes connecting communities | 🟡 High |
| **Degree Centrality** | Find hub nodes with most connections | 🟡 High |
| **PageRank** | Identify most important nodes | 🟡 High |
| **Community Detection** | Louvain algorithm to find clusters | 🟡 High |
| **Gap Analysis** | Find missing connections | 🟢 Medium |
| **Path Finder** | Shortest path between two nodes | 🟢 Medium |

### Tech Stack Additions

- **Frontend:** react-force-graph-2d, react-force-graph-3d, three.js
- **Backend:** NetworkX (Python graph library)
- **Computation:** Background workers for heavy graph calculations

**[📖 Read Full Documentation →](phase-5-graph.md)**

---

## Phase 6: AI & Collaboration 📅

**Status:** Planned
**Target Start:** Q2 2026
**Duration:** 4-6 weeks
**Dependencies:** All previous phases

### Summary

Claude AI integration for intelligent assistance and real-time collaborative editing.

### Planned Features

**AI Integration:**
| Feature | Description | Priority |
|---------|-------------|----------|
| **AI Chat** | Claude-powered chatbot with project context | 🔴 Critical |
| **Inline Suggestions** | AI suggestions while editing | 🟡 High |
| **Semantic Search** | AI-powered search understanding intent | 🟡 High |
| **Auto-Summarize** | Generate summaries of notes/tasks | 🟢 Medium |
| **Smart Links** | AI suggests relevant connections | 🟢 Medium |

**Collaboration:**
| Feature | Description | Priority |
|---------|-------------|----------|
| **Real-Time Editing** | Multi-user collaborative editing (CRDT) | 🔴 Critical |
| **User Cursors** | See where others are editing | 🟡 High |
| **Presence** | See who's online | 🟡 High |
| **Comments** | Real-time comment threads | 🟡 High |
| **Activity Feed** | See recent changes by team | 🟢 Medium |

### Tech Stack Additions

- **AI:** Claude API (Anthropic)
- **Collaboration:** Yjs (CRDT library), TipTap-Yjs integration
- **WebSocket:** Real-time communication
- **Auth:** Multi-user support, permissions

**[📖 Read Full Documentation →](phase-6-ai-collab.md)**

---

## 📅 Timeline Overview

```
Nov 2025   Dec 2025   Jan 2026   Feb 2026   Mar 2026   Apr 2026   May 2026   Jun 2026
   |          |          |          |          |          |          |          |
   Phase 1✅  |----Phase 2----|----Phase 3----|--Phase 4--|----Phase 5----|--Phase 6--|
                                                                 ⭐
```

**Key Milestones:**
- ✅ **M1:** Foundation Complete (2025-11-27)
- 🏗️ **M2:** Notes/Wiki MVP (2025-12-30)
- 📅 **M3:** Task Management (2026-01-31)
- 📅 **M4:** Roadmap Tools (2026-02-28)
- 📅 **M5:** 3D Graph Live ⭐ (2026-04-15)
- 📅 **M6:** AI + Collaboration (2026-06-15)

---

## 🎯 Feature Priority Legend

- 🔴 **Critical** - Must have for MVP
- 🟡 **High** - Should have for good UX
- 🟢 **Medium** - Nice to have, can be added later
- ⚪ **Low** - Future enhancement

---

## 📚 Feature Documentation Structure

Each phase has its own detailed documentation file:

```
features/
├── README.md                 # This file
├── phase-1-foundation.md     # UI foundation (complete)
├── phase-2-notes-wiki.md     # Notes & wiki system (next)
├── phase-3-tasks.md          # Task management
├── phase-4-roadmap.md        # Roadmap planning
├── phase-5-graph.md          # 3D graph visualization
└── phase-6-ai-collab.md      # AI & collaboration
```

Each file contains:
- Feature specifications
- User stories
- Technical implementation details
- API endpoints
- UI mockups/wireframes
- Testing requirements

---

## 🤔 Questions?

- **General questions:** [GitHub Discussions](https://github.com/seb155/Nexus/discussions)
- **Feature requests:** [GitHub Issues](https://github.com/seb155/Nexus/issues)
- **Implementation details:** See individual phase documentation

---

**[⬆ Back to Docs Home](../README.md)**

*Last Updated: 2025-11-27*
