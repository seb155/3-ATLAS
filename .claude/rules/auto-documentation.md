---
name: auto-documentation-rules
description: Auto-documentation triggers and format standards for preventing context loss
type: rule
---

# Auto-Documentation Rules

## Overview

This rule defines when and how agents automatically document their work to prevent context loss during auto-compacting.

**Key Principle:** Save on major tasks only, not every response.

---

## Auto-Save Triggers

### SAVE - Major Events

| Event | Action | Target File |
|-------|--------|-------------|
| **Brainstorm session ends** | Save insights and decisions | `.dev/journal/YYYY-MM/YYYY-MM-DD.md` |
| **TodoWrite initial setup** | Log task list created | `.dev/journal/YYYY-MM/YYYY-MM-DD.md` |
| **Major task completed** | Update project state | `.dev/context/project-state.md` |
| **Architectural decision** | Create/append ADR | `.dev/context/decisions.md` |
| **Report generated** | Save full report | `.dev/reports/YYYY-MM-DD-HHMM-[type].md` |
| **Context at 70%** | Create checkpoint | `.dev/checkpoints/YYYY-MM-DD-HHMM.md` |
| **Session ends** | Update hot context | `.dev/context/hot-context.md` |
| **Workshop phase complete** | Update session file | `.dev/1-sessions/active/current-session.md` |

### DO NOT SAVE

- Simple Recap responses (too frequent)
- Short Q&A exchanges
- Minor code changes
- File reads without action
- Navigation/exploration

---

## Format Standards

### Journal Entry

```markdown
### [HH:MM] [Event Type]

**Context:** [Brief context]
**Action:** [What was done]
**Outcome:** [Result]
**Files:** [Files affected, if any]
```

### Decision Entry

```markdown
### [ADR-NNN] [Decision Title]

**Date:** YYYY-MM-DD HH:MM
**Status:** proposed | accepted | deprecated
**Context:** [Why this decision was needed]
**Decision:** [What was decided]
**Consequences:** [Impact of the decision]
```

---

## Implementation

### For All Agents

After completing a major task:

1. Check if event matches SAVE triggers
2. If yes, append to appropriate file
3. Use timestamp format: `YYYY-MM-DD HH:MM`
4. Follow user's language (English or French)

### For ATLAS Orchestrator

Additionally monitor:
- Context usage percentage
- Session duration
- TodoWrite changes

### Checkpoint Creation

When creating checkpoint:

1. Copy current TodoWrite state
2. Run `git diff --stat`
3. List hot files being worked on
4. Document open questions
5. Define clear next steps

---

## File Paths

All paths relative to project root:

```
.dev/
├── 0-backlog/           # Backlog items
├── 1-sessions/          # Session tracking
│   ├── active/          # Current session
│   └── archive/         # Completed sessions
├── context/             # State files
│   ├── project-state.md
│   ├── decisions.md
│   └── hot-context.md
├── journal/             # Daily logs
│   └── YYYY-MM/
├── reports/             # Generated reports
└── checkpoints/         # Context snapshots
```

---

## Language

Documentation follows user's conversation language:
- If user writes in French → document in French
- If user writes in English → document in English
- Technical terms can remain in English
