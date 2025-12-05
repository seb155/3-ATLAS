---
name: session-management-rules
description: Session lifecycle rules - creating, tracking, and recovering sessions
type: rule
---

# Session Management Rules

## Overview

This rule defines how sessions are created, tracked, and recovered across the Atlas framework.

---

## Session Types

| Type | Command | Purpose |
|------|---------|---------|
| **dev** | `/1-start-dev` | Development work session |
| **brainstorm** | `/1-start-brainstorm` | Creative exploration, whiteboarding |
| **debug** | `/1-start-debug` | Bug investigation and fixing |
| **workshop** | `/0-workshop` | Design Thinking 5-phase workshop |

---

## Cross-Project Targeting

Commands accept optional `[project-id]` to target a specific project:

```bash
/0-session-continue echo           # Continue ECHO session
/1-start-dev synapse tests         # Start dev on SYNAPSE with topic
/0-view-status mechvision          # View MechVision status
/9-git-ship echo                   # Ship ECHO changes
```

**Resolution:** See Rule 31 (project-resolution.md)

**Priority when no argument:**
1. Current directory if has `.dev/`
2. Active session in workspace
3. Ask user which project

---

## Session Lifecycle

### 1. Starting a Session

When any `/1-start-*` command is invoked:

```
1. Check .dev/1-sessions/active/current-session.md
   ├── EXISTS → Show session info
   │            → Offer: (1) Continue (2) Archive + New
   └── EMPTY  → Create new session file

2. Check .dev/0-backlog/ for urgent items
   → Display any high-priority items

3. Create/Update current-session.md
   - Set Started timestamp
   - Set Type (dev/brainstorm/debug)
   - Set Status: active
   - Set Branch from git

4. Load context
   - Read .dev/context/hot-context.md
   - Read recent journal if exists
   - Load project-state.md

5. Start workflow
```

### 2. During Session

**Update current-session.md when:**
- Progress is made on tasks
- Key decisions are made
- New blockers are discovered
- Objectives change

**Format for updates:**
```markdown
## Progress
- [x] Completed item (YYYY-MM-DD HH:MM)
- [ ] In progress item
- [ ] Pending item

## Key Decisions
- [New decision] (YYYY-MM-DD HH:MM)
```

### 3. Ending a Session

When `/9-session-archive` or session naturally ends:

```
1. Update current-session.md
   - Set Status: completed
   - Add completion timestamp

2. Copy to archive
   .dev/1-sessions/active/current-session.md
   → .dev/1-sessions/archive/YYYY-MM-DD-[topic].md

3. Update hot-context.md
   - Summarize what was accomplished
   - Note any open items
   - Set next steps

4. Clear active folder
   - Remove current-session.md from active/
```

---

## Recovery Flow

### After Context Loss / Crash

```
User runs /0-session-recover or /1-start-dev
    ↓
Check .dev/1-sessions/active/current-session.md
    ↓
IF EXISTS:
    "📋 Session active trouvée!"
    "Topic: [topic]"
    "Started: [timestamp]"
    "Status: [status]"

    "Que veux-tu faire?"
    1. Continuer cette session
    2. Archiver et en créer une nouvelle
    3. Voir les détails
    ↓
IF CONTINUE:
    Read current-session.md
    Read hot-context.md
    Resume where left off
```

### Recovery Priority Order

1. `.dev/1-sessions/active/current-session.md` (if exists)
2. `.dev/context/hot-context.md` (always)
3. `.dev/checkpoints/` (latest checkpoint)
4. `.dev/journal/YYYY-MM/latest.md` (recent activity)
5. `.dev/context/project-state.md` (global state)

---

## Command Naming Convention

| Prefix | Purpose | Examples |
|--------|---------|----------|
| `0-session-*` | Session management | `0-session-start`, `0-session-continue`, `0-session-recover` |
| `0-view-*` | View commands | `0-view-status`, `0-view-roadmap`, `0-view-backlog` |
| `1-start-*` | Workflow starters | `1-start-dev`, `1-start-brainstorm`, `1-start-debug` |
| `9-*` | Session finishers | `9-git-ship`, `9-session-archive` |
| `zz-*` | Agent-internal | `zz-infra`, `zz-api-endpoint` |

---

## Backlog Integration

### Checking Backlog on Session Start

```
Read .dev/0-backlog/
├── ideas.md      → Show new ideas if any
├── bugs.md       → Show critical bugs (high priority)
└── features.md   → Show ready features

Display:
"📌 Backlog items trouvés:"
"- [BUG] Critical: [description]"
"- [FEATURE] Ready: [description]"
```

### Adding to Backlog

During session, if item discovered but not for now:

```markdown
# In .dev/0-backlog/ideas.md (or bugs.md, features.md)

## [Title]
**Added:** YYYY-MM-DD HH:MM
**Priority:** high | medium | low
**Description:** [What and why]
**Context:** [Related to current work]
```

---

## File Templates

All templates in `.claude/templates/dev/`:
- `current-session.template.md`
- `journal-daily.template.md`
- `checkpoint.template.md`
- `hot-context.template.md`
- `backlog-item.template.md`
