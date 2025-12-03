# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this agent framework.

## Atlas Agent Framework v2.2

This is a reusable Claude Code agent framework. Use it as `.claude/` in your projects.

### What's New in V2.2

- **Accurate Token Monitoring**: Real token counts from JSONL transcripts (not estimates!)
- **Token Breakdown**: Separate Input/Output/Cache tracking with Opus 4.5 pricing
- **Responsive Status Line**: Adapts to terminal width (Full/Standard/Compact/Ultra)
- **Tool Analytics**: `/0-analyze` identifies expensive patterns
- **Cache Savings**: Track savings from prompt caching (up to 90%!)

### What's New in V2.1

- **Layering System**: Projects can override framework components via `.atlas/`
- **Token Optimization**: `/0-tokens`, `/0-compact` commands
- **MCP Management**: `/0-mcp` for managing MCP servers
- **QA Tester Agent**: Automated testing with pytest/vitest
- **Context System**: Hot-files, thresholds, smart loading
- **Infrastructure Rules**: Traefik, Docker networking, URL registry

## Quick Start

Start every session with:
- `/0-session-start` - Full context load (first session of day)
- `/0-session-continue` - Quick continue existing session
- `/0-session-recover` - Recovery after /compact

End sessions with:
- `/9-git-ship` - Git workflow (test + commit + push)

**All commands support `[project-id]` argument:**
```bash
/0-session-continue echo      # Continue ECHO project
/0-session-start synapse      # Start SYNAPSE session
/9-git-ship mechvision        # Ship MechVision changes
```

## Available Commands

### Session Commands (0-session-*)
| Command | Purpose |
|---------|---------|
| `/0-session-start [project]` | Start new session |
| `/0-session-continue [project]` | Continue existing session |
| `/0-session-recover [project]` | Recovery after /compact |
| `/0-session-checkpoint` | Create context checkpoint |
| `/0-session-save` | Save before /compact |

### View Commands (0-view-*)
| Command | Purpose |
|---------|---------|
| `/0-view-status [project]` | Current session status |
| `/0-view-roadmap [project]` | Roadmap overview |
| `/0-view-backlog [project]` | Backlog management |
| `/0-view-projects` | All projects status |

### Workflow Starters (1-start-*)
| Command | Purpose |
|---------|---------|
| `/1-start-dev [project]` | Start dev session |
| `/1-start-brainstorm [project]` | Start brainstorm session |
| `/1-start-debug [project]` | Start debug session |
| `/1-init-system` | Init Atlas in workspace |
| `/1-init-project` | Init .dev/ in project |
| `/1-init-atlas` | Init .atlas/ layering structure |
| `/1-init-cli` | Init CLI customization |

### Token Management (UPDATED v2.2)
| Command | Purpose |
|---------|---------|
| `/0-tokens` | Dashboard with REAL token counts (Input/Output/Cache breakdown) |
| `/0-analyze` | Analyze tool usage patterns to optimize consumption |
| `/0-compact` | Compress context at 50% |
| `/0-mcp` | Manage MCP servers |

**Token Monitoring Features:**
- Real token counts from JSONL transcripts (not estimates!)
- Separate Input ($5/M) / Output ($25/M) / Cache ($0.50/M) tracking
- Responsive status line adapts to terminal width
- Cache savings calculator (up to 90% savings!)

See: `.claude/docs/token-monitoring.md`

### End Commands (9-*)
| Command | Purpose |
|---------|---------|
| `/9-git-ship [project]` | Git workflow (test + commit + push) |
| `/9-session-archive` | Archive current session |

### Other Commands
| Command | Purpose |
|---------|---------|
| `/0-workshop` | Design thinking session |

### Standard Commands
`app`, `architect`, `brainstorm`, `commit`, `debug`, `docs`, `genesis`, `implement`, `integrate`, `release`, `status`, `system`, `test`

### Direct Model Access (NEW)
| Command | Purpose | Model |
|---------|---------|-------|
| `/opus [task]` | Maximum intelligence, no agent overhead | Opus 4.5 |
| `/sonnet [task]` | Balanced performance, no agent overhead | Sonnet 4.5 |

**Use these for:**
- `/opus` - Complex architecture, multi-system debugging, critical decisions
- `/sonnet` - Standard code tasks, quick questions, cost-conscious operations

**Key difference:** No response protocol (Recap/choices). Raw, direct answers.

## Agents

| Agent | Purpose | Model |
|-------|---------|-------|
| **ATLAS** | Main orchestrator | Opus |
| **GENESIS** | Meta-agent, system evolution | Opus |
| **BRAINSTORM** | Creative sessions | Opus |
| **SYSTEM-ARCHITECT** | AI governance | Opus |
| **DevOps Manager** | Infrastructure orchestration | Opus |
| **Workshop Facilitator** | Design thinking | Opus |
| **Backend Builder** | FastAPI, SQLAlchemy | Sonnet (quick: Haiku) |
| **Frontend Builder** | React, Zustand | Sonnet |
| **DevOps Builder** | Docker, configs | Haiku |
| **Doc Writer** | Documentation | Haiku |
| **Debugger** | Error analysis | Sonnet (quick: Haiku) |
| **Planner** | Task breakdown | Sonnet (quick: Haiku) |
| **UX Designer** | UI/UX design | Sonnet |
| **QA Tester** | Automated testing | Haiku |
| **OPUS-DIRECT** | Raw Opus access | Opus |
| **SONNET-DIRECT** | Raw Sonnet access | Sonnet |

### Model Selection

**Automatic routing** by ATLAS:
- **Haiku (quick)**: Simple errors, configs, docs, CRUD
- **Sonnet**: Code implementation, planning, design
- **Opus**: Orchestration, architecture, complex decisions
- **Direct**: User override via `/opus` or `/sonnet`

**Cost optimization target:**
- 70% tasks → Haiku/Sonnet (économique)
- 20% tasks → Sonnet (équilibré)
- 10% tasks → Opus (critique)

## Skills

| Skill | Purpose |
|-------|---------|
| `0-workshop` | Workshop actions |
| `zz-infra` | Infrastructure management |
| `zz-agent-draft` | Create new agents |
| `zz-api-endpoint` | API scaffolding |
| `zz-docker-service` | Docker services |
| `zz-react-component` | React components |
| `zz-backlog-manager` | Backlog management |
| `zz-init-cli` | CLI customization templates |

## Optional Skills

- `optional/homeassistant.md` - Home Assistant MCP integration (60 tools)

## Response Protocol

All agents interacting with humans MUST follow the unified response protocol.

**Reference:** `.claude/agents/rules/response-protocol.md`

### Standard Format

Every response ends with:

1. **Recap** - 2-4 bullet points summarizing actions
2. **Numbered choices** - 3-5 options with descriptions
3. **Input hint** - "Type a number (1-5) or write your request"

### Example

```markdown
[Agent response content...]

---

## Recap

- [done] Task completed
- [pending] Next step identified

---

## What do you want to do?

1. **Continue** - Next step
2. **Modify** - Change approach
3. **Details** - More information
4. **Something else** - Describe what you want

> Tip: Type a number (1-5) or write your request.
```

### AskUserQuestion Tool

Use for structured questions BEFORE starting work:
- Max 4 questions, 2-4 options each
- Use `multiSelect: true` for checkbox selection
- NOT for end-of-response choices (use text format)

## Session Management & Context Persistence

Atlas auto-documents work to `.dev/` to prevent context loss.

### Session Tracking

Active sessions are tracked in `.dev/1-sessions/active/current-session.md`

**Session Types:**
- `dev` - Development work (via `/1-start-dev`)
- `brainstorm` - Creative sessions (via `/1-start-brainstorm`)
- `debug` - Bug investigation (via `/1-start-debug`)

### Auto-Documentation Triggers

- Brainstorm session end
- Task list completion
- Architectural decisions
- 70% context warning
- Session end (via `/9-session-archive`)

### Recovery Flow

If session crashes or `/compact` used:
1. `/0-session-recover` or `/1-start-dev` detects active session
2. Loads from session file + checkpoint + hot-context
3. Offers to continue or start fresh

### Project Structure (.dev/)

```
project/
└── .dev/
    ├── .dev-manifest.json  # Hierarchy manifest (NEW)
    ├── 0-backlog/          # Ideas, bugs, features
    ├── 1-sessions/         # Active + archive
    ├── context/            # Project state, hot-context
    ├── journal/            # Daily logs
    ├── checkpoints/        # Manual checkpoints
    └── reports/            # Generated reports
```

**Reference:** `.claude/agents/rules/session-management.md`

## Workspace Navigation (Monorepos)

Atlas supports hierarchical `.dev/` structures for monorepos and multi-project workspaces.

### Context Types

| Type | Description |
|------|-------------|
| `parent` | Monorepo root with children projects |
| `child` | Sub-project within a parent |
| `standalone` | Independent project |

### Manifest System

Each `.dev/` contains a `.dev-manifest.json` declaring:
- Project identity (id, name, path)
- Context type (parent/child/standalone)
- Parent reference (for children)
- Children list (for parents)
- Shared resources (credentials, infrastructure)

### Parent Projects

Parents have a `workspace.md` showing navigation map:

```
AXIOM/ (parent)
├── apps/synapse/.dev/   → SYNAPSE [MVP 85%]
├── apps/nexus/.dev/     → NEXUS [Phase 1.5 40%]
└── forge/.dev/          → FORGE [Stable 95%]
```

### Resource Inheritance

Children inherit shared resources from parent:
```json
{
  "inherit_from_parent": ["credentials", "infrastructure"]
}
```

**Templates:** `.claude/templates/dev/.dev-manifest-*.json`
**Reference:** `.claude/agents/rules/30-workspace-navigation.md`

## CLI Customization

Status line Powerline affichant en bas du CLI:

```
 Model  Project  Git  Agent  Context%  Cost  Tokens
```

### Setup

```bash
/1-init-cli    # Initialize/repair CLI customization
```

### Components

| File | Purpose |
|------|---------|
| `~/.claude/settings.json` | StatusLine + Hooks config |
| `~/.claude/atlas-agent.ps1` | Agent detection |
| `~/.claude/detect-project.ps1` | Project detection |
| `~/.claude/hooks/track-agent.ps1` | Agent tracking hook |
| `~/.config/ccstatusline/settings.json` | Powerline widgets |

### Requirements

- JetBrainsMono Nerd Font (`winget install DEVCOM.JetBrainsMonoNerdFont`)
- Windows Terminal configured with Nerd Font

**Reference:** `.claude/docs/cli-customization.md`

## Layering System (NEW in V2.1)

Projects can override framework components via `.atlas/` directory.

### Project Structure with Layering

```
my-project/
├── .claude -> atlas-framework/.claude  # Symlink to framework
├── .atlas/                              # Project-specific layer
│   ├── atlas.config.json               # Configuration
│   ├── agents/                         # Project-specific agents
│   ├── overrides/                      # Override framework components
│   ├── commands/                       # Project-specific commands
│   └── runtime/                        # Sessions, checkpoints
└── .dev/                               # Project context (unchanged)
```

### Resolution Priority

```
Priority 3 (highest): .atlas/agents/{name}.md      # Local
Priority 2:           .atlas/overrides/{name}.md   # Override
Priority 1 (base):    .claude/agents/{name}.md     # Framework
```

### Setup Layering

```bash
/1-init-atlas              # Auto-detect project type
/1-init-atlas standalone   # Force standalone
/1-init-atlas child        # For monorepo sub-project
/1-init-atlas parent       # For monorepo root
```

**Reference:** `.claude/agents/rules/40-layering.md`
