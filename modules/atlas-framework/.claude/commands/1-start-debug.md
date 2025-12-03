---
description: Start debug session with tracking and documentation
---

# /1-start-debug

Start a debug session with tracking and documentation.

## Usage

```bash
/1-start-debug                     # Start in current project
/1-start-debug echo                # Start debug session on ECHO
/1-start-debug synapse api-error   # Start on SYNAPSE with error context
/1-start-debug [project] [error]   # General format
```

## Arguments

- `[project-id]` (optional): Identifiant du projet cible
  - Case-insensitive
  - Résolution via Rule 31 (project-resolution.md)
- `[error]` (optional): Error description or context

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
    "📋 Session active: [topic]"
    1. Mettre en pause et debugger
    2. Archiver et debugger
    3. Annuler
```

### Step 3: Create Debug Session

```
Create .dev/1-sessions/active/current-session.md

# Session: Debug - [Error/Issue]

**Started:** [timestamp]
**Type:** debug
**Branch:** [git branch]
**Status:** active

---

## Problem
[Error message or issue description]

## Context
- Error location: [file:line if known]
- Triggered by: [action that caused error]
- Frequency: [always / sometimes / once]

## Investigation
[Will be populated during debugging]

## Root Cause
[Will be populated when found]

## Fix
[Will be populated when resolved]

---

**Last updated:** [timestamp]
```

### Step 4: Start Investigation

```
Display:
"🐛 Session debug démarrée!"
"Project: [project name]"

"Décris l'erreur ou le problème:"

After description:
"Questions de diagnostic:"
1. Quand l'erreur se produit-elle?
2. Quel fichier/fonction est concerné?
3. Y a-t-il des logs disponibles?
```

---

## Debug Process

### Phase 1: Information Gathering

```
- Collect error message
- Check relevant logs
- Identify affected files
- Note recent changes (git log)
```

### Phase 2: Hypothesis

```
Update session file:

## Investigation

### Hypothesis 1: [Description]
- Evidence for: [...]
- Evidence against: [...]
- Status: testing | confirmed | rejected

### Hypothesis 2: [Description]
...
```

### Phase 3: Root Cause

```
## Root Cause

**Identified:** [timestamp]
**Description:** [What's causing the issue]
**Location:** [file:line]
**Why it happens:** [Explanation]
```

### Phase 4: Fix

```
## Fix

**Applied:** [timestamp]
**Solution:** [What was changed]
**Files modified:**
- [file1]
- [file2]

**Verification:**
- [ ] Error no longer occurs
- [ ] Tests pass
- [ ] No regressions
```

---

## End Session

When bug is fixed:

1. Document fix in session file
2. Append summary to journal
3. Suggest adding test case
4. Option to add to known issues

```
"✅ Bug résolu!"

"Root cause: [summary]"
"Fix: [summary]"

"Que veux-tu faire?"
1. Archiver et commiter le fix
2. Ajouter un test de régression
3. Documenter dans known issues
4. Continuer sur autre chose
```

---

## Auto-Documentation

Append to journal:

```markdown
### [HH:MM] Debug: [Issue]

**Problem:** [Description]
**Root Cause:** [What was wrong]
**Fix:** [What was changed]
**Duration:** [X min]
```

---

## See Also

- `/1-start-dev` - Switch to dev mode
- `/1-start-brainstorm` - Brainstorm session
- `/9-session-archive` - Archive session
- Rule 31 - Project ID resolution
