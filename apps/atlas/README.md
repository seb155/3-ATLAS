# ATLAS - AI Operating System

> **A**I **T**eam **L**ayered **A**ssistance **S**ystem

ATLAS is the intelligent operating system at the heart of AXIOM. It's not just an application - it's the AI OS that powers and connects everything.

## Status

**Phase:** Active (Agents system running)
**CORTEX:** Development

## What is ATLAS?

ATLAS is the central nervous system of AXIOM, containing:

```
┌────────────────────────────────────────────────────────────────┐
│                        ATLAS (AI OS)                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  CORTEX (Memory)  │  Agents  │  ECHO  │  Note_synch      │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

## Components

| Component | Status | Description |
|:---|:---:|:---|
| **CORTEX** | 🚧 Dev | Memory engine - CAG/RAG hybrid |
| **Agents** | ✅ Active | Claude Code framework (18+ agents) |
| **ECHO** | 🚧 Dev | Voice → Transcription → Memory |
| **Note_synch** | 🏗️ Started | TriliumNext → Memory |

### CORTEX - Memory Engine

CORTEX is the unified memory system with 3 layers:

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

### ECHO - Voice Input

Voice notes → Whisper transcription → CORTEX memory

### Note_synch - Trilium Integration

Bidirectional sync with TriliumNext notes → CORTEX memory

## Integration Points

ATLAS connects all AXIOM applications:

```
         APEX                    NEXUS
        (Apps)                (Knowledge)
           │                        │
           └────────┬───────────────┘
                    │
              ┌─────▼─────┐
              │   ATLAS   │
              │   (OS)    │
              │     │     │
              │  CORTEX   │
              └─────┬─────┘
                    │
              ┌─────▼─────┐
              │  SYNAPSE  │
              │ (+ future)│
              └───────────┘
```

- **APEX**: Enterprise portal uses ATLAS for app orchestration
- **NEXUS**: Knowledge portal displays CORTEX memory as 3D graph
- **SYNAPSE**: Engineering app sends events to CORTEX

## Ports

| Service | Port |
|:---|:---:|
| CORTEX Engine | 7100 |
| CORTEX Sandbox | 7101 |

## Files

| Path | Purpose |
|:---|:---|
| `.claude/agents/` | Agent definitions |
| `.claude/commands/` | Slash commands |
| `.claude/skills/` | Reusable skills |
| `apps/cortex/` | CORTEX backend |

---

*The AI OS at the heart of AXIOM Platform by AXoiq*
