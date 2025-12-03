---
description: Start development session with session tracking
---

# /1-start-dev

Start a development session with session tracking and context recovery.

## Usage

```bash
/1-start-dev                    # Start in current project
/1-start-dev echo               # Start dev session on ECHO
/1-start-dev synapse tests      # Start on SYNAPSE with topic "tests"
/1-start-dev [project] [topic]  # General format
```

## Arguments

- `[project-id]` (optional): Identifiant du projet cible
  - Case-insensitive
  - Résolution via Rule 31 (project-resolution.md)
- `[topic]` (optional): Session topic description

---

## Workflow

### Step 1: Resolve Project (if argument)

```
IF project-id provided:
    Resolve via Rule 31
    Change context to target project
    Display: "📂 Projet: [name] ([path])"
```

### Step 2: Check Active Session

```
Read .dev/1-sessions/active/current-session.md

IF EXISTS:
    Display:
    "📋 Session active trouvée!"
    "Topic: [topic from file]"
    "Started: [timestamp]"
    "Last updated: [timestamp]"
    "Progress: [X/Y tasks]"

    "Que veux-tu faire?"
    1. Continuer cette session
    2. Archiver et commencer une nouvelle
    3. Voir les détails de la session

IF NOT EXISTS:
    → Go to Step 3
```

### Step 3: Check Backlog

```
Read .dev/0-backlog/bugs.md (high priority first)
Read .dev/0-backlog/features.md (ready items)

IF urgent items found:
    Display:
    "📌 Items prioritaires dans le backlog:"
    "- [BUG/HIGH] [description]"
    "- [FEATURE/READY] [description]"

    "Veux-tu travailler sur un de ces items?"
```

### Step 4: Create Session

```
Create .dev/1-sessions/active/current-session.md

Content:
# Session: [Topic or "Dev Session"]

**Started:** [current timestamp]
**Type:** dev
**Branch:** [git branch]
**Status:** active

---

## Objective
[User's stated objective or from backlog item]

## Context
[Key files, relevant project state]

## Progress
- [ ] [First task]

## Next Steps
1. [First action]

---

**Last updated:** [timestamp]
```

### Step 5: Load Context

```
Read in order:
1. .dev/context/hot-context.md
2. .dev/context/project-state.md
3. Recent journal entries if relevant

Display summary:
"📦 Contexte chargé:"
"- [Current focus from hot-context]"
"- [Recent activity summary]"
```

### Step 6: Start Working

```
Display:
"🚀 Session dev démarrée!"
"Project: [project name]"
"Topic: [topic]"
"Branch: [branch]"

"Que veux-tu faire?"
1. [Suggested action based on context]
2. Voir le backlog complet
3. Continuer sur [last task]
4. Autre chose
```

---

## During Session

Update `.dev/1-sessions/active/current-session.md`:
- After completing tasks
- When making key decisions
- When blockers appear

---

## End Session

Use `/9-session-archive` to properly close the session, or it will persist for recovery.

---

## Recovery

If context is lost:
1. `/1-start-dev` will detect the active session
2. Offer to continue from where you left off
3. Load context from session file

---

## See Also

- `/1-start-brainstorm` - Creative session
- `/1-start-debug` - Debug session
- `/9-session-archive` - Archive current session
- `/0-session-checkpoint` - Create checkpoint
- Rule 31 - Project ID resolution
