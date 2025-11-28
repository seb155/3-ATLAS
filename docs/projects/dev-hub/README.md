# Dev Hub - Portail de Développement Unifié

**Unified Development Portal** - Notes, Wiki, Tasks, Roadmap, AI Chat & 3D Graph Visualization

---

## 🎯 Vision

**Dev Hub** est un portail de développement tout-en-un conçu pour centraliser:
- 📝 **Documentation** - Wiki hiérarchique avec éditeur riche
- ✅ **Tasks** - Kanban board + Gantt chart pour roadmap
- 🔗 **Connections** - Visualisation graph 2D/3D des liens entre notes et tâches
- 🤖 **AI Assistant** - Chat contextuel pour aide au développement
- 👥 **Collaboration** - Édition collaborative real-time
- 🔍 **Recherche** - Cmd+K universal search

**Inspirations:** Notion + Linear + TriliumNext + InfraNodus

---

## 🌟 Features Uniques

### 1. Graph 3D Visualization (InfraNodus-style)

Visualisez vos notes et tâches comme un réseau de connaissances:
- **2D View:** Force-directed graph traditionnel
- **3D View:** Navigation immersive WebGL avec Three.js
- **Filtres Avancés:**
  - Par type (notes, tasks, labels)
  - Par métriques (betweenness, degree, PageRank)
  - Par keywords et dates
- **Analytics:**
  - Community detection (Louvain algorithm)
  - Bridge nodes (betweenness centrality)
  - Hub nodes (most connected)
  - Gap analysis (missing connections)
- **Path Finding:** Shortest path entre 2 nodes
- **Time-Series:** Animation de croissance du réseau

### 2. AI-Powered Workflow

- **Context-Aware Chat:** L'AI connaît votre note actuelle, vos tâches, votre projet
- **Inline Suggestions:** Extraction automatique de tâches depuis notes
- **Smart Search:** Recherche sémantique (pas juste keyword)
- **Summarization:** Résumés automatiques de notes longues

### 3. Real-Time Collaboration

- **Collaborative Editing:** TipTap + Yjs CRDT
- **Multi-user Cursors:** Voir les autres utilisateurs en temps réel
- **Comments:** Discussion threads sur tasks et notes
- **Activity Feed:** Notifications de changements

---

## 📋 Cas d'Usage

### Pour Développeur Solo

**Workflow type:**
1. 🌅 **Matin:** Ouvre Dev Hub → Dashboard montre tâches du jour
2. 📝 **Travail:** Clique tâche → Ouvre note liée → Édite code + doc
3. 🔗 **Exploration:** Vue Graph 3D montre connexions entre features
4. 🤖 **Aide:** Chat AI pour clarifier algo ou suggérer refactoring
5. ✅ **Fin journée:** Drag task "Done" dans Kanban, log progrès

**Bénéfices:**
- Documentation à jour (wiki + code au même endroit)
- Pas de tâches oubliées (kanban visuel)
- Compréhension globale (graph view)

### Pour Équipe (2-5 personnes)

**Workflow collaboratif:**
1. 📋 **Planning Sprint:** Gantt chart pour roadmap, assign tasks
2. 📝 **Documentation:** Wiki partagé avec édition collaborative
3. 💬 **Discussion:** Comments threads sur tasks
4. 🔗 **Knowledge Sharing:** Graph view montre qui travaille sur quoi
5. 🔔 **Notifications:** Mentions @user → activity feed

**Bénéfices:**
- Pas de duplication de travail (real-time cursors)
- Onboarding rapide (wiki centralisé + graph overview)
- Communication asynchrone (comments vs meetings)

### Pour Project Manager

**Workflow de suivi:**
1. 📊 **Dashboard:** Metrics de progression (tasks done/todo)
2. 📈 **Gantt Chart:** Vue timeline des milestones
3. 🔗 **Graph Analytics:** Identifier bottlenecks (bridge nodes)
4. 📝 **Reports:** Export Markdown/PDF pour stakeholders

**Bénéfices:**
- Visibilité temps réel
- Identification risques (isolated tasks)
- Reporting automatisé

---

## 🏗️ Architecture

### Stack Technique

**Frontend:**
- React 19 + TypeScript
- Vite 7 (build tool)
- TanStack React Query (data fetching)
- Zustand (global state)
- shadcn/ui + Radix UI (components)
- Tailwind CSS (styling)

**Editor & Visualization:**
- **Rich Text:** TipTap (extensible editor)
- **Drag-Drop:** @dnd-kit (kanban)
- **Gantt:** gantt-task-react
- **Graph 2D:** react-force-graph-2d
- **Graph 3D:** react-force-graph-3d + Three.js
- **Collaboration:** Yjs (CRDT)

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL 15 (database)
- Redis (cache + Celery)
- Socket.io (WebSocket real-time)

**AI & Analytics:**
- Anthropic Claude API (AI chat)
- NetworkX (graph metrics)
- python-louvain (community detection)
- PostgreSQL tsvector (full-text search)

### Architecture Diagram

```
┌─────────────────────────────────────────────┐
│  Frontend (React 19 + TypeScript)           │
│  ┌─────────────┬────────────┬──────────┐   │
│  │ Notes/Wiki  │ Kanban     │ Graph 3D │   │
│  │ (TipTap)    │ (dnd-kit)  │ (Three)  │   │
│  └─────────────┴────────────┴──────────┘   │
│  ┌──────────────────────────────────────┐   │
│  │ AI Chat Panel (streaming)            │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
                    ↕ REST API + WebSocket
┌─────────────────────────────────────────────┐
│  Backend (FastAPI)                          │
│  ┌───────────────────────────────────────┐  │
│  │ API Endpoints                         │  │
│  │ /notes, /tasks, /graph, /chat        │  │
│  └───────────────────────────────────────┘  │
│  ┌──────────┬─────────────┬────────────┐   │
│  │ Graph    │ AI Service  │ Yjs CRDT   │   │
│  │ Builder  │ (Claude)    │ Provider   │   │
│  └──────────┴─────────────┴────────────┘   │
└─────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────┐
│  PostgreSQL                                 │
│  ┌─────────┬────────┬──────────────────┐   │
│  │ notes   │ tasks  │ note_links       │   │
│  └─────────┴────────┴──────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## 📊 Comparaison vs SaaS

| Feature | Notion | Linear | Obsidian | Dev Hub |
|---------|--------|--------|----------|---------|
| **Wiki/Notes** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Task Management** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ |
| **Roadmap/Gantt** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ |
| **Graph 2D** | ❌ | ❌ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Graph 3D** | ❌ | ❌ | ❌ | ⭐⭐⭐⭐⭐ |
| **AI Chat** | ⭐⭐⭐ | ❌ | ⭐⭐ (plugins) | ⭐⭐⭐⭐ |
| **Real-time Collab** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ |
| **Self-hosted** | ❌ | ❌ | ✅ | ✅ |
| **AI Context (.md)** | ❌ | ❌ | ✅ | ✅ |
| **Cost** | $10/mo | $8/mo | Gratuit | Hosting |

**Verdict:**
- **Si besoin Graph 3D + Self-hosted + AI context:** Dev Hub est unique
- **Si besoin juste tasks + wiki:** Notion + Linear suffisent
- **Si solo offline:** Obsidian local suffit

---

## 🚀 Roadmap

### Phase 1: Fondations (2-3 semaines) ✅ Q4 2025

- [x] Database schema (notes, tasks, links)
- [x] shadcn/ui setup
- [x] Zustand stores
- [x] WebSocket infrastructure

### Phase 2: Wiki System (3-4 semaines) 🏗️ Q1 2026

- [ ] TipTap rich text editor
- [ ] Note tree sidebar (hierarchical)
- [ ] Wiki links `[[note]]` + backlinks
- [ ] Full-text search

### Phase 3: Task Management (3-4 semaines) 📅 Q1 2026

- [ ] Kanban board (drag-drop)
- [ ] Task detail panel
- [ ] Comments threads
- [ ] Labels + assignees

### Phase 4: Roadmap (2-3 semaines) 📅 Q1 2026

- [ ] Gantt chart component
- [ ] Milestones
- [ ] Timeline view

### Phase 5: Graph 2D/3D (4-5 semaines) 🎯 Q2 2026

- [ ] Graph 2D view (force-directed)
- [ ] Graph 3D view (WebGL + Three.js)
- [ ] Advanced filters (betweenness, degree, PageRank)
- [ ] Community detection (Louvain)
- [ ] Analytics panel
- [ ] Path finder
- [ ] Time-series animation

### Phase 6: AI + Collaboration (4-6 semaines) 🎯 Q2 2026

- [ ] AI chat sidebar (Claude API)
- [ ] Context injection (current note, project)
- [ ] Collaborative editor (TipTap + Yjs)
- [ ] Multi-user cursors
- [ ] Notifications

### Phase 7: Integrations (Future) 🔮

- [ ] Email sync (Outlook, Gmail)
- [ ] MS Teams integration
- [ ] GitHub integration
- [ ] Slack notifications

---

## 📚 Documentation

### Pour Utilisateurs

- [Getting Started](./getting-started.md) - Installation et premier projet
- [User Guide](./user-guide.md) - Guide complet des features
- [Graph Visualization Guide](./graph-guide.md) - Comment utiliser le graph 3D
- [AI Chat Guide](./ai-guide.md) - Maximiser l'AI assistant

### Pour Développeurs

- [Development Setup](./development-setup.md) - Setup environnement de dev
- [Architecture Overview](./architecture.md) - Architecture détaillée
- [API Reference](./api-reference.md) - Documentation API
- [Contributing](./contributing.md) - Comment contribuer

### Tutoriels

- [Create Your First Wiki](./tutorials/first-wiki.md)
- [Setup Kanban Workflow](./tutorials/kanban-workflow.md)
- [Visualize Knowledge Graph](./tutorials/knowledge-graph.md)
- [Collaborate in Real-Time](./tutorials/collaboration.md)

---

## 🤝 Contribuer

Dev Hub est développé en mode **open development**.

**Feedback & Issues:**
- GitHub Issues: `EPCB-Tools/issues`
- Discussions: `EPCB-Tools/discussions`

**Pull Requests:**
Voir [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 📝 License

MIT License - Voir [LICENSE](../../../LICENSE)

---

## 🙏 Credits

**Inspirations:**
- [Notion](https://notion.so) - Wiki & database UI/UX
- [Linear](https://linear.app) - Task management workflow
- [TriliumNext](https://github.com/TriliumNext/Notes) - Hierarchical notes
- [InfraNodus](https://infranodus.com) - Graph visualization & analytics
- [Obsidian](https://obsidian.md) - Local-first knowledge management

**Open Source Libraries:**
- [TipTap](https://tiptap.dev) - Extensible rich text editor
- [Yjs](https://yjs.dev) - CRDT for collaboration
- [NetworkX](https://networkx.org) - Graph algorithms
- [react-force-graph](https://github.com/vasturiano/react-force-graph) - Graph visualization
- [Three.js](https://threejs.org) - 3D rendering
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework

---

**Status:** 🏗️ In Development (Phase 1)
**Version:** 0.1.0-alpha
**Last Updated:** 2025-11-26
