---
description: Create manual checkpoint to preserve context
---

# /0-session-checkpoint

Crée un checkpoint manuel pour préserver le contexte avant des opérations risquées ou à des points stratégiques.

## Usage

```bash
/0-session-checkpoint              # Quick checkpoint
/0-session-checkpoint [note]       # Checkpoint with note
```

---

## When to Use

- Before major refactoring
- Before risky operations (migrations, deletions)
- At natural break points in complex work
- Before testing experimental approaches
- When context is reaching 70%+

---

## Workflow

### Step 1: Gather Context

```
Collect:
- Current session state
- Active tasks (from TodoWrite)
- Recent decisions made
- Files currently being worked on
- Git status and recent commits
```

### Step 2: Create Checkpoint

```
Create .dev/checkpoints/[timestamp]-checkpoint.md

# Checkpoint: [Note or "Manual Checkpoint"]

**Created:** YYYY-MM-DD HH:MM
**Session:** [current session topic]
**Context Level:** [estimated %]
**Branch:** [git branch]

---

## Context Summary

[What we're working on and current state]

## Active Tasks

From TodoWrite:
- [x] Completed task
- [ ] Pending task (in_progress)
- [ ] Pending task

## Recent Changes

From git:
- [commit hash] [message]
- [commit hash] [message]

## Hot Files

Files currently being modified:
- [file1] - [what's being done]
- [file2] - [what's being done]

## Key Decisions

Decisions made this session:
- [Decision 1]
- [Decision 2]

## Next Steps

What to do after resuming:
1. [Next action]
2. [Following action]

## Notes

[User's note if provided, or session context]

---

**Recovery command:** `/0-session-recover` then load this checkpoint
```

### Step 3: Update Hot Context

```
Update .dev/context/hot-context.md with:
- Latest checkpoint reference
- Current focus summary
```

### Step 4: Confirm

```
Display:
"💾 Checkpoint créé!"

Checkpoint: [timestamp]-checkpoint.md
Location: .dev/checkpoints/
Context saved: [summary]

"Pour restaurer: /0-session-recover et charger ce checkpoint"

"Que veux-tu faire?"
1. Continuer à travailler
2. Faire /compact maintenant
3. Voir le checkpoint créé
```

---

## Checkpoint Naming

Format: `YYYYMMDD-HHMM-checkpoint.md`

Examples:
- `20250129-1430-checkpoint.md`
- `20250129-1630-checkpoint.md`

---

## Auto-Checkpoints

Checkpoints are also created automatically:
- At session start (by `/1-start-dev`, `/1-start-brainstorm`, etc.)
- Before archiving (by `/9-session-archive`)
- At 70% context warning (by ATLAS)

---

## Recovery Flow

1. Session crashes or `/compact` used
2. User runs `/0-session-recover`
3. System checks `.dev/checkpoints/` for latest
4. Offers to load checkpoint context

---

## See Also

- `/0-session-recover` - Resume from checkpoint
- `/0-session-save` - Save before /compact
- `/1-start-dev` - Start new session (creates checkpoint)
