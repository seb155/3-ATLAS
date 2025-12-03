# /1-init-project

Initialize a new project with the full `.dev/` structure for session tracking and documentation.

## Usage

```bash
/1-init-project              # Init in current directory
/1-init-project [path]       # Init in specified path
```

---

## What It Creates

```
project-root/
├── .dev/
│   ├── .dev-manifest.json   # [NEW] Hierarchy manifest
│   │
│   ├── 0-backlog/
│   │   ├── ideas.md
│   │   ├── bugs.md
│   │   └── features.md
│   │
│   ├── 1-sessions/
│   │   ├── active/
│   │   │   └── .gitkeep
│   │   └── archive/
│   │       └── .gitkeep
│   │
│   ├── context/
│   │   ├── project-state.md
│   │   ├── decisions.md
│   │   └── hot-context.md
│   │
│   ├── journal/
│   │   └── .gitkeep
│   │
│   ├── reports/
│   │   └── .gitkeep
│   │
│   └── checkpoints/
│       └── .gitkeep
│
├── workspace.md             # [PARENT ONLY] Navigation map
└── CLAUDE.md (if not exists)
```

---

## Manifest Context Detection

The command automatically detects the project context type:

### Detection Logic

```
IF parent ../.dev/.dev-manifest.json exists:
    → context_type: "child"
    → Set parent reference

ELIF has subdirectories with .dev/:
    → context_type: "parent"
    → Auto-detect children
    → Create workspace.md

ELSE:
    → context_type: "standalone"
```

### Manifest Examples

**Standalone:**
```json
{
  "version": "1.0",
  "context_type": "standalone",
  "project": {
    "id": "my-project",
    "name": "My Project",
    "path": "/path/to/project"
  }
}
```

**Child:**
```json
{
  "version": "1.0",
  "context_type": "child",
  "project": { ... },
  "parent": {
    "id": "parent-name",
    "path": "../.dev"
  },
  "inherit_from_parent": ["credentials", "infrastructure"]
}
```

**Parent:**
```json
{
  "version": "1.0",
  "context_type": "parent",
  "project": { ... },
  "children": [
    { "id": "app1", "path": "apps/app1/.dev" }
  ],
  "shared_resources": {
    "credentials": "context/credentials.md"
  }
}
```

---

## Workflow

### Step 1: Check Existing Structure

```
IF .dev/ exists:
    "⚠️ Structure .dev/ déjà existante"

    1. Fusionner (ajouter les fichiers manquants)
    2. Remplacer (backup + nouveau)
    3. Annuler
```

### Step 2: Create Structure

```
For each folder:
    Create if not exists
    Add .gitkeep for empty folders
```

### Step 3: Initialize Files

**project-state.md:**
```markdown
# Project State

**Project:** [Folder name]
**Initialized:** [timestamp]
**Status:** active

---

## Overview

[Project description - to be filled]

## Current Phase

[Current development phase]

## Key Files

| File | Purpose |
|------|---------|
| | |

## Tech Stack

- [To be documented]

---

**Last updated:** [timestamp]
```

**decisions.md:**
```markdown
# Architecture Decision Records

## Active Decisions

[No decisions recorded yet]

---

## Template

### [ADR-NNN] [Title]

**Date:** YYYY-MM-DD
**Status:** proposed | accepted | deprecated

**Context:** [Why this decision is needed]

**Decision:** [What was decided]

**Consequences:** [Impact and trade-offs]
```

**Backlog files (ideas.md, bugs.md, features.md):**
```markdown
# [Type] Backlog

## High Priority

[No items yet]

## Medium Priority

[No items yet]

## Low Priority

[No items yet]

---

## Template

### [Title]
**Added:** YYYY-MM-DD
**Priority:** high | medium | low
**Description:** [What and why]
```

### Step 4: Create CLAUDE.md (if not exists)

```markdown
# CLAUDE.md

Project-specific instructions for Claude Code.

## Project Overview

[Describe your project]

## Quick Commands

- `/1-dev` - Start development session
- `/1-brainstorm` - Start brainstorm session
- `/9-ship` - Test, commit, and push

## Tech Stack

[List your technologies]

## Development Notes

[Any special instructions]
```

---

## Output

```
"✅ Projet initialisé avec succès!"

Structure créée:
├── .dev/0-backlog/     (3 files)
├── .dev/1-sessions/    (2 folders)
├── .dev/context/       (3 files)
├── .dev/journal/       (ready)
├── .dev/reports/       (ready)
├── .dev/checkpoints/   (ready)
└── CLAUDE.md           (created/exists)

"Que veux-tu faire?"
1. Démarrer une session dev (/1-dev)
2. Documenter le projet (project-state.md)
3. Ajouter au git
4. Voir la structure complète
```

---

## Git Integration

If git repo exists, suggest:

```bash
# Add to .gitignore (optional)
.dev/1-sessions/active/
.dev/checkpoints/

# Or track everything
git add .dev/
git commit -m "chore: Initialize .dev/ structure for session tracking"
```

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `/1-init-system` | Init Atlas in workspace |
| `/1-dev` | Start dev session |

---

## See Also

- `.claude/templates/dev/` - All templates
- `.claude/agents/rules/session-management.md`
