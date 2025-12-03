<div align="center">

# 🌐 Nexus

**Knowledge Graph Portal**

*Your development brain - visualized in 3D*

[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue?logo=typescript)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-19-61dafb?logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-7-646cff?logo=vite)](https://vitejs.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Features](#-features) • [Getting Started](#-getting-started) • [Tech Stack](#-tech-stack) • [Roadmap](#-roadmap) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🎯 Overview

**Nexus** is the Knowledge Portal of the AXIOM platform. It combines the best features of Notion, Linear, Obsidian, and InfraNodus into a single, self-hosted platform. Think of it as your **second brain** for development - but with superpowers.

### Relationship with CORTEX

NEXUS serves as the **UI layer for CORTEX** (the memory engine in ATLAS):
- NEXUS has its own data (notes, wiki, tasks)
- NEXUS also visualizes CORTEX's knowledge graph in 3D
- CORTEX provides AI context for NEXUS features

```
┌──────────────────────────────────────────┐
│              NEXUS (UI)                  │
│  ┌────────────────────────────────────┐ │
│  │  Own Data: Notes, Wiki, Tasks      │ │
│  └────────────────────────────────────┘ │
│                  +                       │
│  ┌────────────────────────────────────┐ │
│  │  CORTEX Interface:                 │ │
│  │  - 3D Graph Visualization          │ │
│  │  - AI Chat                         │ │
│  │  - Context Blocks                  │ │
│  └────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

### Why Nexus?

- 📝 **Notes & Wiki** - TipTap-powered rich text editor with hierarchical organization
- ✅ **Task Management** - Kanban boards and Gantt charts for project planning
- 🌐 **3D Graph Visualization** - Visualize CORTEX's knowledge network in stunning 3D
- 🤖 **AI Assistant** - CORTEX-powered chatbot with full project context
- 👥 **Real-time Collaboration** - Work together with multi-user editing
- 🔒 **Self-Hosted** - Your data stays on your servers
- 🎨 **Beautiful UI** - VSCode-inspired dark theme (light mode too!)

---

## ✨ Features

### Current (v0.2.0) ✅

| Feature | Status | Description |
|---------|--------|-------------|
| **Modern UI** | ✅ Complete | VSCode-like layout with sidebar, tabs, and status bar |
| **Theme System** | ✅ Complete | Dynamic light/dark themes (13 pre-built themes) |
| **Visual Polish** | ✅ Complete | Vercel/Linear-quality design with animations |
| **Component Library** | ✅ Complete | Badge, Button, Card, StatCard, Skeleton components |
| **Routing** | ✅ Complete | React Router with 6 enhanced pages |
| **State Management** | ✅ Complete | Zustand for global state |
| **TypeScript** | ✅ Complete | Full type safety with strict mode |
| **Drawing & Whiteboarding** | ✅ Complete | Excalidraw integration with library support |

### Drawing & Whiteboarding (Excalidraw)

NEXUS integrates Excalidraw for powerful whiteboard and diagramming capabilities:

- **Library Support**: Browse and install shapes from [libraries.excalidraw.com](https://libraries.excalidraw.com)
- **Advanced UX**: Collapsible sidebar, fullscreen mode (F key), inline rename
- **Persistence**: Auto-save drawings, localStorage for libraries and UI state
- **Integration**: Use drawings in notes via TipTap blocks
- **Collaboration Ready**: Backend sync preparation for real-time collaboration

See [docs/EXCALIDRAW-INTEGRATION.md](docs/EXCALIDRAW-INTEGRATION.md) for detailed documentation.

### Planned Features 🚀

**📝 Phase 2: Notes/Wiki (3-4 weeks)**
- TipTap rich text editor
- Hierarchical note tree
- Wiki-style links [[note-name]]
- Backlinks panel
- Full-text search

**✅ Phase 3: Task Management (3-4 weeks)**
- Drag-and-drop Kanban board
- Task detail panel
- Comments and labels
- Link tasks to notes

**📊 Phase 4: Roadmap (2-3 weeks)**
- Gantt chart timeline
- Milestones and dependencies

**🌐 Phase 5: 3D Graph Visualization (4-5 weeks) ⭐**
- 2D/3D force-directed graph
- InfraNodus-style analytics
- Community detection
- Path finding

**🤖 Phase 6: AI & Collaboration (4-6 weeks)**
- Claude API chatbot
- Real-time collaborative editing (Yjs)
- Multi-user cursors

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Git

### Quick Start

```bash
# Clone repository
git clone https://github.com/seb155/Nexus.git
cd Nexus

# Install dependencies
cd frontend
npm install

# Start dev server
npm run dev
```

🎉 Open http://localhost:5173

---

## 🛠️ Tech Stack

**Frontend:** React 19 • TypeScript 5.9 • Vite 7 • Tailwind CSS 4 • Zustand • React Router 7

**Future:** FastAPI • PostgreSQL • Redis • TipTap • Three.js • NetworkX • Claude API • Yjs

---

## 🗺️ Roadmap

```
Phase 1: Foundation           ✅ Complete (2025-11-27 AM)
Phase 1.5: Visual Polish      ✅ Complete (2025-11-27 PM)
Phase 2: Notes/Wiki           🏗️ Next (3-4 weeks)
Phase 3: Task Management      📅 Q1 2026
Phase 4: Roadmap              📅 Q1 2026
Phase 5: 3D Graph ⭐          📅 Q2 2026
Phase 6: AI & Collaboration   📅 Q2 2026
```

See [.dev/roadmap/README.md](.dev/roadmap/README.md) for details.

---

## 📚 Documentation

**Comprehensive documentation is available in the [docs/](docs/) directory:**

### For Users

- **[📖 Documentation Home](docs/README.md)** - Start here for navigation
- **[🎯 Vision & Philosophy](docs/vision.md)** - Understanding Nexus
- **[🚀 Getting Started](docs/getting-started.md)** - Installation & first steps
- **[✨ Features Overview](docs/features/)** - Detailed feature documentation

### For Developers

- **[👨‍💻 Developer Guide](docs/developer-guide/)** - Contributing to Nexus
- **[🏗️ Architecture](docs/architecture/)** - Technical architecture
- **[📝 Code Style Guide](CONTRIBUTING.md)** - Coding standards
- **[🧪 Testing Guide](docs/developer-guide/testing.md)** - Testing strategies

### Quick Links

| I want to... | Go to... |
|--------------|----------|
| Understand the project vision | [docs/vision.md](docs/vision.md) |
| Install and run Nexus | [docs/getting-started.md](docs/getting-started.md) |
| Learn about features | [docs/features/](docs/features/) |
| Contribute code | [docs/developer-guide/](docs/developer-guide/) |
| Understand architecture | [docs/architecture/](docs/architecture/) |

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
git checkout -b feature/amazing-feature
git commit -m 'feat: add amazing feature'
git push origin feature/amazing-feature
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Credits

**Inspired by:** Notion • Linear • Obsidian • InfraNodus

**Built with:** React • Vite • Tailwind CSS • FastAPI

---

<div align="center">

**[⬆ Back to Top](#-nexus)**

Made with ❤️ by the Nexus Team

⭐ Star us on GitHub!

</div>
