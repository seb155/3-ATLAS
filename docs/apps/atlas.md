# ATLAS - AI Operating System

> **A**I **T**eam **L**ayered **A**ssistance **S**ystem

## Overview

ATLAS is the **AI Operating System** at the heart of AXIOM. It's not just an application - it's the intelligent system that powers and connects everything.

**ATLAS contains:**
- **CORTEX** - Memory Engine (CAG/RAG hybrid)
- **Agents** - Claude Code framework (18+ specialized agents)
- **ECHO** - Voice input tool (planned)
- **Note_synch** - TriliumNext sync (started)

---

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        ATLAS (AI OS)                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  CORTEX (Memory)  │  Agents  │  ECHO  │  Note_synch      │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   ┌──────────┐         ┌──────────┐         ┌──────────┐
   │   APEX   │         │  NEXUS   │         │ SYNAPSE  │
   └──────────┘         └──────────┘         └──────────┘
```

---

## Components

### CORTEX - Memory Engine

The unified memory system with 3 layers:

| Layer | Type | Content | Speed |
|:---|:---|:---|:---|
| **HOT** | CAG (Cache) | Session, recent, task context | Instant |
| **WARM** | RAG Fast | Project files, dependencies | Fast |
| **COLD** | RAG Full | All codebase, git history, docs | Slower |

**Features:**
- Context Blocks (assemblable via keywords)
- Temporal Awareness (version tracking, change detection)
- Multi-AI Router (Claude, Gemini, Ollama)
- Data protection (classification + anonymization)

See [CORTEX Documentation](./cortex.md) for details.

### Agents - Claude Code Framework

The AI agents system currently active in Claude Code:

```
┌─────────────────────── ORCHESTRATORS (Opus) ───────────────────┐
│  ATLAS (Main)  │  GENESIS (Meta)  │  BRAINSTORM  │  ARCHITECT  │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────── SPECIALISTS ────────────────────────────┐
│ BUILDERS          │ VALIDATORS      │ TRACKERS     │ PLANNERS  │
│ • Backend         │ • QA-Tester     │ • Dev-Tracker│ • Debugger│
│ • Frontend        │ • Issue-Reporter│ • Git-Manager│ • Planner │
│ • DevOps          │                 │              │ • UX      │
└────────────────────────────────────────────────────────────────┘
```

**Commands:**
- `/0-new-session` - Start new session (full context)
- `/0-next` - Continue next task
- `/0-resume` - Resume after /compact
- `/0-progress` - View roadmap
- `/0-ship` - Git workflow

### ECHO - Voice Input (Planned)

Voice notes → Whisper transcription → CORTEX memory

### Note_synch - Trilium Integration (Started)

Bidirectional sync with TriliumNext notes → CORTEX memory

---

## Status

| Component | Status |
|:---|:---:|
| **Agents** | ✅ Active |
| **CORTEX** | 🚧 Development |
| **ECHO** | 🚧 Development |
| **Note_synch** | 🏗️ Started |

---

## Integration Points

ATLAS connects all AXIOM applications:

| Application | Integration |
|-------------|-------------|
| **APEX** | Uses ATLAS for app orchestration and AI insights |
| **NEXUS** | Displays CORTEX memory as 3D graph |
| **SYNAPSE** | Sends engineering events to CORTEX |
| **FORGE** | Vector storage, caching, infrastructure |

---

## Port Allocation

| Service | Port |
|---------|------|
| CORTEX Engine | 7100 |
| CORTEX Sandbox | 7101 |

*In CORTEX range (7000-7999)*

---

## Files

| Path | Purpose |
|:---|:---|
| `.claude/agents/` | Agent definitions |
| `.claude/commands/` | Slash commands |
| `.claude/skills/` | Reusable skills |
| `.claude/context/` | Session context |
| `apps/cortex/` | CORTEX backend |
| `apps/atlas/` | ATLAS (placeholder for future UI) |

---

## Technology Considerations

| Component | Technology |
|-----------|------------|
| LLM Providers | Claude API, Gemini, OpenAI, Ollama |
| Embeddings | nomic-embed-text (local), OpenAI |
| Vector Store | ChromaDB |
| Orchestration | Custom (ReAct loop) |
| Queue | Redis |
| Database | PostgreSQL |

---

## Related Documentation

- [CORTEX](./cortex.md) - Memory engine details
- [NEXUS](./nexus.md) - Knowledge portal (CORTEX UI)
- [APEX](./apex.md) - Enterprise portal
- [AI Agents Guide](../developer-guide/ai-agents-overview.md)
