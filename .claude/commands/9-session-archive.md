---
description: Archive current session and move to archive
---

# /9-session-archive

Archive the current session and move it to the session archive.

## Usage

```bash
/9-session-archive              # Archive current session
/9-session-archive [summary]    # Archive with custom summary
```

---

## Purpose

- Properly close an active session
- Preserve session history for reference
- Clear the active session slot
- Update journal with session summary
- Prepare for next session

---

## Workflow

### Step 1: Check Active Session

```
Read .dev/1-sessions/active/current-session.md

IF NOT EXISTS:
    "ℹ️ Aucune session active à archiver"

    "Que veux-tu faire?"
    1. Démarrer une nouvelle session (/1-start-dev)
    2. Voir les sessions archivées
    3. Annuler

IF EXISTS:
    Display session summary
    → Continue to Step 2
```

### Step 2: Summarize Session

```
Display:
"📋 Session à archiver:"
"Topic: [topic]"
"Started: [timestamp]"
"Duration: [X heures]"
"Tasks completed: [X/Y]"

"Résumé automatique:"
- [Key accomplishment 1]
- [Key accomplishment 2]
- [Key decision made]

"Ce résumé est-il correct?"
1. Oui, archiver
2. Modifier le résumé
3. Annuler
```

### Step 3: Create Archive Entry

```
Move to: .dev/1-sessions/archive/YYYY-MM/[session-id].md

Add header:
# [Archived] Session: [Topic]

**Archived:** [timestamp]
**Original Start:** [start timestamp]
**Duration:** [X hours]
**Status:** completed | abandoned | paused

---

[Original session content]

---

## Archive Summary

[Final summary of what was accomplished]
```

### Step 4: Update Journal

```
Append to .dev/journal/YYYY-MM/YYYY-MM-DD.md:

### [HH:MM] Session Archived: [Topic]

**Duration:** [X hours]
**Status:** [completed/abandoned]

**Summary:**
- [Key accomplishment 1]
- [Key accomplishment 2]

**Files Modified:**
- [file1]
- [file2]
```

### Step 5: Update Backlog

```
IF session had incomplete tasks:
    Offer to add to backlog:

    "⚠️ Tasks incomplètes détectées:"
    - [ ] Task 1
    - [ ] Task 2

    "Ajouter au backlog?"
    1. Oui, ajouter comme features
    2. Oui, ajouter comme bugs
    3. Non, ignorer
```

### Step 6: Clean Up

```
1. Delete .dev/1-sessions/active/current-session.md
2. Update .dev/context/hot-context.md (clear current focus)
3. Create final checkpoint if significant work done
```

### Step 7: Confirm

```
Display:
"✅ Session archivée!"

Archive: .dev/1-sessions/archive/YYYY-MM/[session-id].md
Journal updated: .dev/journal/YYYY-MM/YYYY-MM-DD.md

"Que veux-tu faire?"
1. Démarrer une nouvelle session (/1-start-dev)
2. Faire un commit (/9-git-ship)
3. Voir l'archive
4. Terminer pour aujourd'hui
```

---

## Archive Structure

```
.dev/1-sessions/
├── active/
│   └── current-session.md (cleared after archive)
└── archive/
    ├── 2025-01/
    │   ├── 20250115-1030-auth-refactor.md
    │   └── 20250118-1400-api-design.md
    └── 2025-02/
        └── 20250201-0900-bugfixes.md
```

---

## Session ID Format

`YYYYMMDD-HHMM-[topic-slug].md`

Examples:
- `20250129-1430-user-auth.md`
- `20250129-1630-api-refactor.md`
- `20250130-0900-brainstorm-v2.md`

---

## Abandon vs Complete

**Completed:** All tasks done or consciously closed
- Status: `completed`
- Journal: Normal entry

**Abandoned:** Session stopped due to priority change
- Status: `abandoned`
- Journal: Note reason
- Backlog: Offer to add incomplete tasks

**Paused:** Temporary stop, plan to resume
- Status: `paused`
- Keep in active? Optional
- Hot-context: Updated with pause reason

---

## See Also

- `/1-start-dev` - Start new session
- `/9-git-ship` - Commit and push
- `/0-session-checkpoint` - Create checkpoint without archiving
