# CORTEX - The Memory Engine

> **Version**: 0.5.0-dev
> **Status**: Development
> **Company**: Axoiq
> **Part of**: ATLAS (AI OS)

## Overview

**CORTEX** is the unified memory engine within ATLAS. It provides a CAG/RAG hybrid system for contextual intelligence across all AXIOM applications.

**CORTEX is a component of ATLAS**, not a standalone application. It serves as the "brain's memory" that connects:
- **NEXUS** (Knowledge Portal) - displays CORTEX data as 3D graph
- **SYNAPSE** (Engineering App) - sends events to CORTEX
- **APEX** (Enterprise Portal) - queries CORTEX for insights

### What CORTEX Is

- An **autonomous agent** that navigates any codebase (code + engineering/MBSE)
- A system that **plans, executes, and verifies** its own actions
- A tool that **actually modifies files** on disk
- An intelligent assistant with **temporal awareness** (understands time, versions, evolution)

### What CORTEX Is NOT

- A simple chatbot answering code questions
- An autocomplete tool (like Copilot)
- A wrapper around GPT-4

### The Key Analogy

Think of a very fast junior developer:
1. You give them repo access
2. You explain the task
3. They explore the code to understand it
4. They make a plan
5. They code
6. They test
7. If it fails, they fix it

**CORTEX does exactly that.**

---

## Architecture

### High-Level View

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              NEXUS (UI)                                  │
│                         Port 5173 - React                                │
│  Chat │ Context Builder │ Session History │ Graph 3D │ Settings         │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ REST/WebSocket
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         CORTEX ENGINE                                    │
│                    Port 7100 - FastAPI (Python)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ORCHESTRATOR (ReAct Loop: Think → Act → Observe → Repeat)              │
│  ├── JOB ENGINE    (queue, priority, retry, timeout)                    │
│  ├── RULE ENGINE   (validation, guards, policies)                       │
│  └── TRACE ENGINE  (audit log, replay, time-travel)                     │
│                                                                          │
│  CONTEXT MANAGER                                                         │
│  ├── Context Blocks (PROFILE, PROJECT, CLIENT, CODEBASE...)             │
│  ├── Memory: HOT(CAG) → WARM(RAG) → COLD(RAG full)                      │
│  └── Temporal Awareness (versions, evolution, snapshots)                │
│                                                                          │
│  AI ROUTER                                                               │
│  └── Claude │ Gemini │ OpenAI │ Ollama (local)                          │
│                                                                          │
│  TOOLS: read │ write │ edit │ search │ shell │ git                      │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SANDBOX MANAGER                                  │
│                         Port 7101                                        │
│  Pool: [Python] [Node] [Rust] [Custom...]                               │
│  Isolation │ Timeouts │ Resource limits │ Network policies              │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL INFRASTRUCTURE                              │
│  ai-sandbox: LiteLLM │ Ollama │ Langfuse                                │
│  FORGE: PostgreSQL │ Redis │ ChromaDB │ Grafana │ Loki                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Core Concepts

### 1. Context Blocks (Assemblable)

Modular context blocks that assemble based on the task:

```yaml
# Example: Personal Profile Block
type: PROFILE
name: "Dev Profile"
sensitivity: CONFIDENTIAL
content:
  preferences:
    language: "fr"
    code_style: "clean, minimal, typed"
  expertise: ["Python", "TypeScript", "Docker"]

# Example: Project Block
type: PROJECT
name: "AXIOM Platform"
sensitivity: INTERNAL
content:
  apps: ["SYNAPSE", "NEXUS", "APEX", "ATLAS", "CORTEX"]
  conventions:
    commit_style: "conventional"
```

**Automatic assembly via keywords/concepts:**

```
Task: "Fix the API users bug in SYNAPSE"

Assembled context:
[PROFILE: Dev] + [PROJECT: AXIOM] + [CODEBASE: synapse/backend] + [SESSION: Current]
```

### 2. Hybrid Memory (CAG + RAG)

| Level | Type | Content | Access |
|-------|------|---------|--------|
| **HOT** | CAG (Cache) | Session, recent files, task context | O(1) instant |
| **WARM** | Fast RAG | Project files, dependencies | Milliseconds |
| **COLD** | Full RAG | Entire codebase, Git history, docs | Seconds |

**Flow:**
1. Search HOT first (instant)
2. If not found → WARM (milliseconds)
3. If still not found → COLD (seconds)

### 3. Temporal Awareness (Elephant Memory)

- **Version tracking**: History of context changes
- **Change detection**: "3 files changed since your last visit"
- **Evolution history**: How X evolved over time
- **Time-travel**: Return to project state at time T

### 4. Data Protection

| Level | Treatment |
|-------|-----------|
| **PUBLIC** | Sent to any cloud AI |
| **INTERNAL** | Trusted cloud AI only (Claude, Azure) |
| **CONFIDENTIAL** | Local AI only (Ollama) OR anonymized |
| **SECRET** | NEVER sent - local processing only |

**Mechanisms:**
- Automatic classification (sensitive patterns)
- Anonymization before sending (`john@company.com` → `[EMAIL_1]`)
- Routing by sensitivity
- Complete audit log

### 5. Multi-AI Router

Intelligent provider selection based on:
- **Cost**: Local=0$, Gemini=Low, Claude=High
- **Latency**: Local=Fast, API=Medium
- **Capability**: Claude=Complex, Gemini=Long context, Local=Simple

### 6. 3D Visualization (NEXUS)

Interactive 3D graph showing:
- **Nodes** = Context Blocks (size=tokens, color=type, opacity=relevance)
- **Edges** = Relations (thickness=strength)
- **Real-time animation** when agent works
- **Auto-extracted keywords/concepts**
- **Stats**: tokens, estimated cost, relevance score

---

## Technical Stack

### Backend (CORTEX Engine)

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Language | Python 3.11+ |
| Queue | Redis (via FORGE) |
| Database | PostgreSQL (via FORGE) |
| Vector DB | ChromaDB |
| Embeddings | nomic-embed-text (local) or OpenAI |

### AI Providers

| Provider | Use Case |
|----------|----------|
| Claude (Anthropic) | Complex reasoning, tool use |
| Gemini (Google) | Long context, cost-effective |
| OpenAI | Fallback, specific tasks |
| Ollama (Local) | Privacy-sensitive, free |

### Integration

- **LiteLLM** (from ai-sandbox): Unified proxy for all providers
- **Langfuse** (from ai-sandbox): Observability and tracing
- **NEXUS**: UI and 3D graph visualization

---

## Port Allocation

| Service | Port | Description |
|---------|------|-------------|
| cortex-engine | 7100 | Main FastAPI backend |
| cortex-sandbox | 7101 | Docker sandbox manager |

*In ATLAS range (7000-7999) as CORTEX is part of AI orchestration ecosystem*

---

## File Structure

```
apps/cortex/
├── README.md
├── docker-compose.yml
├── docker-compose.dev.yml
├── Dockerfile
│
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   │
│   │   ├── api/
│   │   │   ├── sessions.py         # Session management
│   │   │   ├── tasks.py            # Task submission
│   │   │   ├── context.py          # Context blocks CRUD
│   │   │   └── websocket.py        # Real-time updates
│   │   │
│   │   ├── core/
│   │   │   ├── config.py           # Settings
│   │   │   ├── database.py         # DB connection
│   │   │   └── security.py         # Data protection
│   │   │
│   │   ├── engine/
│   │   │   ├── orchestrator.py     # Main ReAct loop
│   │   │   ├── job_engine.py       # Job queue management
│   │   │   ├── rule_engine.py      # Validation rules
│   │   │   └── trace_engine.py     # Audit & replay
│   │   │
│   │   ├── context/
│   │   │   ├── manager.py          # Context assembly
│   │   │   ├── blocks.py           # Block definitions
│   │   │   ├── indexer.py          # Code indexing
│   │   │   ├── memory.py           # HOT/WARM/COLD cache
│   │   │   └── temporal.py         # Time-travel
│   │   │
│   │   ├── providers/
│   │   │   ├── base.py             # Abstract LLM interface
│   │   │   ├── claude.py           # Claude provider
│   │   │   ├── gemini.py           # Gemini provider
│   │   │   ├── openai.py           # OpenAI provider
│   │   │   └── ollama.py           # Local models
│   │   │
│   │   ├── tools/
│   │   │   ├── base.py             # Tool interface
│   │   │   ├── file_tools.py       # read/write/edit
│   │   │   ├── search_tools.py     # RAG search
│   │   │   ├── shell_tools.py      # Command execution
│   │   │   └── git_tools.py        # Git operations
│   │   │
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── session.py
│   │   │   ├── task.py
│   │   │   ├── context_block.py
│   │   │   └── trace.py
│   │   │
│   │   └── schemas/                # Pydantic schemas
│   │       ├── session.py
│   │       ├── task.py
│   │       └── context.py
│   │
│   └── tests/
│       ├── test_orchestrator.py
│       ├── test_context.py
│       └── test_tools.py
│
└── sandbox/
    ├── Dockerfile
    └── manager.py
```

---

## Integration with ai-sandbox

CORTEX uses infrastructure from the `ai-sandbox` repository:

### Network Configuration

```yaml
# Both repos share the same Docker network
networks:
  axiom-ai-network:
    external: true
    name: axiom-ai-network

# ai-sandbox services available to CORTEX:
# - litellm:4000      (Unified LLM proxy)
# - ollama:11434      (Local models)
# - langfuse:3000     (Tracing)
# - chromadb:8000     (Vector DB) - if added
```

### Environment Setup

**Development (Windows laptop):**
- Both repos cloned locally
- Docker Desktop
- Shared Docker network `axiom-ai-network`
- Test with local models (Ollama) + Claude API

**Production (Linux server + Portainer):**
- Separate Docker stacks
- ai-sandbox = "AI Infra" stack
- AXIOM = "AXIOM Apps" stack
- Same Docker network for communication

---

## Development Phases

### Phase 0: Setup
- [ ] Create `apps/cortex/` file structure
- [ ] Configure shared Docker network
- [ ] Add ChromaDB to FORGE (optional)

### Phase 1: Core Engine (MVP)
- [ ] Orchestrator (ReAct loop)
- [ ] Essential tools (read/write/edit/search/shell)
- [ ] Claude provider
- [ ] CLI for testing

### Phase 2: Context System
- [ ] Context Blocks (data model)
- [ ] HOT cache (CAG)
- [ ] WARM/COLD cache (RAG with ChromaDB)
- [ ] Codebase indexing

### Phase 3: Job/Rule/Trace Engines
- [ ] Job queue (Redis-based)
- [ ] Rule engine for validation
- [ ] Trace engine for audit

### Phase 4: Memory & Temporal
- [ ] Temporal events tracking
- [ ] Snapshots & time-travel
- [ ] Change detection

### Phase 5: Multi-AI & Security
- [ ] Additional providers (Gemini, Ollama, OpenAI)
- [ ] Intelligent AI Router
- [ ] Security layer (classification, anonymization)

### Phase 6: NEXUS Integration
- [ ] REST API for NEXUS
- [ ] WebSocket real-time
- [ ] 3D Graph visualization

---

## Resources

### Repositories to Study

- [Aider](https://github.com/paul-gauthier/aider) - Reference CLI tool
- [OpenHands](https://github.com/All-Hands-AI/OpenHands) - Open source Devin clone
- [Continue](https://github.com/continuedev/continue) - VS Code extension
- [SWE-agent](https://github.com/princeton-nlp/SWE-agent) - Princeton research agent

### Documentation

- [Anthropic Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [ChromaDB](https://docs.trychroma.com/)
- [Tree-sitter](https://tree-sitter.github.io/tree-sitter/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)

### Papers

- "ReAct: Synergizing Reasoning and Acting in Language Models"
- "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"

---

## Related

- [ATLAS](./atlas.md) - Parent AI OS (CORTEX lives here)
- [NEXUS](./nexus.md) - UI and Knowledge Graph visualization
- [APEX](./apex.md) - Enterprise portal (uses CORTEX insights)
- [ai-sandbox](https://github.com/seb155/ai-sandbox) - LLM infrastructure
