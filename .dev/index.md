# AXIOM Development Index

> **Monorepo Structure & AI Context Loading**
>
> Version: 2.0 | Updated: 2025-11-30

---

## Session Start Workflow

### 1. Load Global Context (AI Runtime)

```
.dev/ai/
├── session-state.json      # Current session, last session summary
├── active-apps.json        # App registry with progress overview
├── owner-preferences.json  # Communication style, preferences
├── hot-files.json          # Recently modified files (auto-generated)
└── missing-info.json       # Questions needing owner input
```

### 2. Review Project Progress

**At session start, display:**

| App | Phase | Progress | Focus |
|:----|:------|:--------:|:------|
| SYNAPSE | MVP | 85% | Demo prep (Dec 20) |
| NEXUS | Phase 1.5 | 40% | Backend integration |
| CORTEX | Design | 10% | Architecture |
| APEX | Planning | 5% | Requirements |
| ATLAS | Active | 70% | Agent system |
| FORGE | Stable | 95% | Maintenance |

### 3. Choose App(s) to Work On

```
"Sur quelle(s) app(s) veux-tu travailler aujourd'hui?"
□ SYNAPSE    □ NEXUS    □ CORTEX    □ APEX    □ FORGE
```

### 4. Load App-Specific Context

After selection, load from `apps/{app}/.dev/ai/`:
- `app-state.json` - Current state, features, blockers
- `hot-files.json` - App-specific hot files

---

## Structure Monorepo

```
AXIOM/
├── .dev/                    # Global context
│   ├── ai/                  # 🤖 AI runtime files (JSON)
│   ├── context/             # Project state, credentials
│   ├── infra/               # 🔒 Infrastructure registry
│   ├── roadmap/             # Global roadmap
│   └── journal/             # Session logs
│
├── .claude/                 # AI agents system
│   ├── agents/              # Agent definitions
│   │   └── rules/           # 🔒 Mandatory rules
│   ├── commands/            # Slash commands
│   └── context/             # Claude-specific context
│
├── apps/
│   ├── synapse/.dev/        # SYNAPSE context
│   ├── nexus/.dev/          # NEXUS context
│   ├── cortex/.dev/         # CORTEX context
│   ├── apex/.dev/           # APEX context
│   └── atlas/.dev/          # ATLAS context
│
├── forge/.dev/              # FORGE infrastructure context
│
└── docs/                    # Documentation
    ├── context/             # Owner profile
    └── infrastructure/      # 🔒 Protected infra docs
```

---

## Protected Documents 🔒

**NEVER modify without owner validation:**

| Document | Path |
|:---------|:-----|
| Infrastructure Registry | `.dev/infra/registry.yml` |
| Architecture | `.dev/ARCHITECTURE.md` |
| Credentials | `.dev/context/credentials.md` |
| Agent Rules | `.claude/agents/rules/*.md` |
| Infra Docs | `docs/infrastructure/*.md` |

**Rule:** `.claude/agents/rules/20-protected-docs.md`

---

## Context Loading by Task

### Quick Question
```
Load: .dev/ai/session-state.json
```

### Development Session
```
Load:
  1. .dev/ai/*.json (global)
  2. apps/{app}/.dev/ai/*.json (app-specific)
  3. Relevant hot files
```

### Architecture Decision
```
Load:
  1. Global context
  2. .dev/ARCHITECTURE.md
  3. .dev/infra/registry.yml (read-only)
  4. Relevant app contexts
```

### Brainstorm/Whiteboard
```
Load:
  1. .dev/ai/owner-preferences.json
  2. docs/context/OWNER-PROFILE.md
  3. Relevant roadmap files
```

---

## Key Files Quick Reference

### Global State
| Need | File |
|:-----|:-----|
| Project status | `.dev/context/project-state.md` |
| Current sprint | `.dev/roadmap/current-sprint.md` |
| Infrastructure | `.dev/infra/registry.yml` 🔒 |
| Credentials | `.dev/context/credentials.md` 🔒 |
| Architecture | `.dev/ARCHITECTURE.md` 🔒 |

### AI Runtime
| Need | File |
|:-----|:-----|
| Session state | `.dev/ai/session-state.json` |
| App progress | `.dev/ai/active-apps.json` |
| Owner prefs | `.dev/ai/owner-preferences.json` |
| Hot files | `.dev/ai/hot-files.json` |
| Agent stats | `.dev/ai/agent-stats.json` |

### Per-App Context
| App | State File |
|:----|:-----------|
| SYNAPSE | `apps/synapse/.dev/ai/app-state.json` |
| NEXUS | `apps/nexus/.dev/ai/app-state.json` |
| CORTEX | `apps/cortex/.dev/ai/app-state.json` |
| APEX | `apps/apex/.dev/ai/app-state.json` |
| ATLAS | `apps/atlas/.dev/ai/app-state.json` |
| FORGE | `forge/.dev/ai/app-state.json` |

---

## Agent Rules

| Rule | File | Purpose |
|:-----|:-----|:--------|
| 10 | `10-traefik-routing.md` | Use domain names, not ports |
| 11 | `11-url-registry.md` | Centralized URL management |
| 12 | `12-docker-networking.md` | Docker DNS, no hardcoded IPs |
| 20 | `20-protected-docs.md` | Protected document policy |

---

## Commands Available

| Command | Mode | Purpose |
|:--------|:-----|:--------|
| `/0-new-session` | FULL | First session - full context |
| `/0-next` | QUICK | Continue work - minimal context |
| `/0-resume` | RECOVERY | After /compact |
| `/0-progress` | - | Roadmap overview |
| `/0-dashboard` | - | Session status |
| `/0-ship` | - | Git workflow (test+commit+push) |

---

## Documentation

| Category | Location |
|:---------|:---------|
| Getting Started | `docs/getting-started/` |
| Developer Guide | `docs/developer-guide/` |
| Infrastructure | `docs/infrastructure/` 🔒 |
| Reference | `docs/reference/` |
| Workflows | `docs/workflows/` |
| Owner Context | `docs/context/OWNER-PROFILE.md` |

---

## Archive

Obsolete files are archived in `.archive/YYYY-MM-DD/`

---

*Index updated for monorepo structure with AI-first context loading*
