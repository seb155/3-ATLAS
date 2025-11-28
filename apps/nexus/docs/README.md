# Nexus Documentation

Welcome to the Nexus documentation! This guide will help you navigate through all available documentation and find the information you need.

## 📚 Documentation Structure

```
docs/
├── README.md                    # This file - documentation navigation
├── getting-started.md           # Quick start guide for new users
├── vision.md                    # Project vision and philosophy
├── features/                    # Detailed feature documentation
│   ├── README.md               # Features overview
│   ├── phase-1-foundation.md   # Current: UI Foundation
│   ├── phase-2-notes-wiki.md   # Next: Notes & Wiki system
│   ├── phase-3-tasks.md        # Task Management
│   ├── phase-4-roadmap.md      # Roadmap & Gantt charts
│   ├── phase-5-graph.md        # 3D Graph Visualization
│   └── phase-6-ai-collab.md    # AI & Collaboration
├── architecture/               # Technical architecture
│   ├── README.md               # Architecture overview
│   ├── frontend.md             # Frontend architecture
│   ├── backend.md              # Backend architecture (Phase 2+)
│   ├── database.md             # Database schema (Phase 2+)
│   └── tech-stack.md           # Technology choices explained
├── developer-guide/            # For contributors
│   ├── README.md               # Developer guide overview
│   ├── setup.md                # Development environment setup
│   ├── code-style.md           # Coding standards
│   ├── testing.md              # Testing guidelines
│   └── deployment.md           # Deployment guide
└── api/                        # API documentation (Phase 2+)
    ├── README.md               # API overview
    └── endpoints/              # Endpoint documentation
```

---

## 🚀 Quick Navigation

### For New Users

Start here if you're new to Nexus:

1. **[Vision & Philosophy](vision.md)** - Understand what Nexus is and why it exists
2. **[Getting Started](getting-started.md)** - Install and run Nexus locally
3. **[Features Overview](features/README.md)** - Explore current and planned features

### For Developers

If you want to contribute or understand the codebase:

1. **[Developer Guide](developer-guide/README.md)** - Complete development guide
2. **[Architecture Overview](architecture/README.md)** - System architecture
3. **[Tech Stack](architecture/tech-stack.md)** - Technology choices explained
4. **[Code Style Guide](developer-guide/code-style.md)** - Coding standards

### For Project Managers

Understanding the roadmap and planning:

1. **[Features Roadmap](features/README.md)** - All phases and timelines
2. **[Current Sprint](../.dev/roadmap/current-sprint.md)** - What's being built now
3. **[Project State](../.dev/context/project-state.md)** - Current status

---

## 🎯 What is Nexus?

**Nexus** is a unified development portal that combines:
- **Notes & Wiki** (like Notion + Obsidian)
- **Task Management** (like Linear)
- **3D Graph Visualization** (like InfraNodus)
- **AI Assistant** (Claude-powered)
- **Real-time Collaboration** (multi-user editing)

### Why Nexus?

Most knowledge management tools excel at one thing:
- Notion → Great UI/UX but not graph-based
- Obsidian → Local-first but limited collaboration
- Linear → Perfect for tasks but not knowledge
- InfraNodus → Amazing graphs but not a full platform

**Nexus combines the best of all worlds** into a single, self-hosted platform with AI integration.

---

## 📖 Documentation by Topic

### Features & Functionality

| Topic | Document | Status |
|-------|----------|--------|
| **Foundation** | [Phase 1: Foundation](features/phase-1-foundation.md) | ✅ Complete |
| **Notes & Wiki** | [Phase 2: Notes/Wiki](features/phase-2-notes-wiki.md) | 📅 Next |
| **Task Management** | [Phase 3: Tasks](features/phase-3-tasks.md) | 📅 Q1 2026 |
| **Roadmap Tools** | [Phase 4: Roadmap](features/phase-4-roadmap.md) | 📅 Q1 2026 |
| **3D Graph** | [Phase 5: Graph Visualization](features/phase-5-graph.md) | 📅 Q2 2026 |
| **AI & Collaboration** | [Phase 6: AI & Collaboration](features/phase-6-ai-collab.md) | 📅 Q2 2026 |

### Technical Documentation

| Topic | Document | Audience |
|-------|----------|----------|
| **Frontend Architecture** | [architecture/frontend.md](architecture/frontend.md) | Developers |
| **Backend Architecture** | [architecture/backend.md](architecture/backend.md) | Developers |
| **Database Schema** | [architecture/database.md](architecture/database.md) | Developers |
| **Tech Stack Choices** | [architecture/tech-stack.md](architecture/tech-stack.md) | Everyone |
| **API Reference** | [api/README.md](api/README.md) | Developers |

### Development Guides

| Topic | Document | Audience |
|-------|----------|----------|
| **Environment Setup** | [developer-guide/setup.md](developer-guide/setup.md) | New contributors |
| **Code Style Guide** | [developer-guide/code-style.md](developer-guide/code-style.md) | Contributors |
| **Testing Guide** | [developer-guide/testing.md](developer-guide/testing.md) | Contributors |
| **Deployment** | [developer-guide/deployment.md](developer-guide/deployment.md) | DevOps |

---

## 🔍 Finding What You Need

### I want to...

**...understand the project vision**
→ Read [vision.md](vision.md)

**...install and run Nexus**
→ Follow [getting-started.md](getting-started.md)

**...know what features are available**
→ Check [features/README.md](features/README.md)

**...contribute code**
→ Start with [developer-guide/README.md](developer-guide/README.md)

**...understand the architecture**
→ Read [architecture/README.md](architecture/README.md)

**...see the API documentation**
→ Browse [api/README.md](api/README.md) *(Phase 2+)*

**...know what's being built now**
→ Check [../.dev/roadmap/current-sprint.md](../.dev/roadmap/current-sprint.md)

**...report a bug**
→ Open a [GitHub Issue](https://github.com/seb155/Nexus/issues)

**...suggest a feature**
→ Start a [GitHub Discussion](https://github.com/seb155/Nexus/discussions)

---

## 🤝 Contributing to Documentation

Documentation is a critical part of Nexus. If you find:
- Missing information
- Outdated content
- Unclear explanations
- Typos or errors

Please:
1. Open a [GitHub Issue](https://github.com/seb155/Nexus/issues)
2. Or submit a PR with improvements
3. Or start a [Discussion](https://github.com/seb155/Nexus/discussions)

### Documentation Standards

- Use clear, concise language
- Include code examples where relevant
- Add diagrams for complex concepts
- Keep navigation links up to date
- Follow markdown best practices

---

## 📅 Documentation Roadmap

### Current (v0.1.0)
- ✅ Getting started guide
- ✅ Vision document
- ✅ Features overview (all phases)
- ✅ Architecture documentation
- ✅ Developer guide

### Phase 2 (Notes/Wiki)
- [ ] API endpoint documentation
- [ ] Database schema diagrams
- [ ] TipTap editor guide
- [ ] Wiki links syntax guide

### Phase 3+ (Future)
- [ ] User guides for each feature
- [ ] Video tutorials
- [ ] Interactive demos
- [ ] Translation to other languages

---

## 🙋 Need Help?

- **Questions?** → [GitHub Discussions](https://github.com/seb155/Nexus/discussions)
- **Bugs?** → [GitHub Issues](https://github.com/seb155/Nexus/issues)
- **Chat?** → Join our community (coming soon)

---

**[⬆ Back to Top](#nexus-documentation)**

---

*Last Updated: 2025-11-27*
*Version: 0.1.0-alpha*
