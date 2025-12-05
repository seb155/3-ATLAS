# /1-init-system

Initialize or update the Atlas Agent Framework in a workspace.

## Usage

```bash
/1-init-system              # Init in current workspace
/1-init-system [path]       # Init in specified workspace
```

---

## What It Does

1. Creates `.claude/` junction to `atlas-agent-framework`
2. Creates workspace-level `CLAUDE.md` if not exists
3. Validates the framework is properly linked
4. Shows available commands and agents

---

## Workflow

### Step 1: Check Existing Setup

```
Check for .claude/ in workspace root

IF .claude/ exists and is junction:
    "✅ Atlas déjà configuré"
    "Linked to: [target path]"

    1. Vérifier la configuration
    2. Mettre à jour le lien
    3. Réinitialiser complètement

IF .claude/ exists but is folder:
    "⚠️ Dossier .claude/ existant (pas un lien)"

    1. Backup et créer junction
    2. Fusionner avec atlas-framework
    3. Annuler

IF .claude/ not exists:
    → Proceed to Step 2
```

### Step 2: Locate Atlas Framework

```
Search for atlas-agent-framework in:
1. Parent directories
2. Common locations (D:\Projects, ~/Projects)
3. Ask user for path

IF found:
    "📁 Atlas trouvé: [path]"
ELSE:
    "Atlas framework non trouvé."
    "Indique le chemin vers atlas-agent-framework:"
```

### Step 3: Create Junction

**Windows (PowerShell):**
```powershell
cmd /c mklink /J ".claude" "[path-to-atlas]"
```

**Linux/macOS:**
```bash
ln -s "[path-to-atlas]" .claude
```

### Step 4: Validate Setup

```
Check:
- .claude/agents/ exists
- .claude/commands/ exists
- .claude/CLAUDE.md exists

IF all valid:
    "✅ Junction créée avec succès!"
ELSE:
    "⚠️ Structure incomplète dans atlas-framework"
```

### Step 5: Create Workspace CLAUDE.md

If no `CLAUDE.md` in workspace root:

```markdown
# CLAUDE.md

Workspace instructions for Claude Code.

## Workspace Overview

This workspace uses the Atlas Agent Framework.

## Quick Start

- `/0-new-session` - Full context load
- `/1-dev` - Start dev session
- `/1-brainstorm` - Start brainstorm
- `/9-ship` - Test, commit, push

## Projects

| Project | Path | Purpose |
|---------|------|---------|
| | | |

## Notes

[Add workspace-specific notes]
```

---

## Output

```
"🗺️ Atlas Agent Framework initialisé!"

Configuration:
├── .claude/ → [atlas-framework-path]
├── CLAUDE.md (workspace)
└── Framework version: [version]

Commandes disponibles:
├── 0-* (session management)
├── 1-* (workflow starters)
├── 9-* (finishers)
└── Standard commands

Agents disponibles:
├── ATLAS (orchestrator)
├── Builders (backend, frontend, devops, docs)
├── Planners (planner, debugger, ux-designer)
└── Orchestrators (genesis, brainstorm)

"Que veux-tu faire?"
1. Voir la liste complète des commandes
2. Initialiser un projet (/1-init-project)
3. Démarrer une session (/1-dev)
4. Lire la documentation
```

---

## Troubleshooting

### Junction Already Exists

```powershell
# Remove existing junction (Windows)
cmd /c rmdir ".claude"

# Then recreate
cmd /c mklink /J ".claude" "[path]"
```

### Permission Denied

On Windows, run PowerShell as Administrator or enable Developer Mode.

### Framework Not Found

Clone or download:
```bash
git clone https://github.com/seb155/atlas-agent-framework.git
```

---

## Related Commands

| Command | Purpose |
|---------|---------|
| `/1-init-project` | Init .dev/ in a project |
| `/0-new-session` | Start working |

---

## See Also

- `atlas-agent-framework/README.md`
- `atlas-agent-framework/CLAUDE.md`
