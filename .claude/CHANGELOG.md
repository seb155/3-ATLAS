# Changelog

All notable changes to Atlas Agent Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-12-01

### Added
- **Workspace Navigation System for Monorepos**
  - `.dev-manifest.json` - Hierarchy manifest for each `.dev/` directory
  - Three context types: `parent`, `child`, `standalone`
  - Automatic parent/child relationship detection
  - Resource inheritance from parent to children
  - `workspace.md` navigation map for parent projects

- **New Templates**
  - `templates/dev/.dev-manifest-parent.json` - Parent project manifest
  - `templates/dev/.dev-manifest-child.json` - Child project manifest
  - `templates/dev/.dev-manifest-standalone.json` - Standalone project manifest
  - `templates/dev/workspace.template.md` - Workspace navigation map

- **New Rule**
  - `agents/rules/30-workspace-navigation.md` - AI navigation behavior for hierarchical workspaces

### Changed
- `commands/1-init-project.md` - Now creates `.dev-manifest.json` with auto-detection of context type
- `CLAUDE.md` - Added "Workspace Navigation (Monorepos)" section

### Projects Initialized
- **AXIOM** (parent + 7 children): synapse, nexus, atlas, apex, cortex, echo, forge
- **mechvision** (parent + 3 children): backend, frontend, forge
- **Personal projects** (4 standalone): FinDash, Pilote-Patrimoine, HomeAssistant, Homelab_MSH

### Technical
- Manifest schema version 1.0
- Relative paths for parent/child references
- `inherit_from_parent` array for selective resource sharing
- `shared_resources` object in parent manifests

---

## [1.2.0] - 2025-11-30

### Added
- **Visual Branding System**
  - `scripts/banner.sh` - Temple grec compact ASCII art au démarrage
  - Banner affiché automatiquement via SessionStart hook
- **Agent Tracking System**
  - `hooks/PreToolUse-Task.sh` - Track agent au lancement (push stack)
  - `hooks/SubagentStop.sh` - Pop agent à la fin (stack pattern)
  - État stocké dans `~/.claude/session-state.json`
  - Support des agents imbriqués (ATLAS → BACKEND → DEBUGGER)
- **StatusLine v2.0 avec Emojis**
  - Nouveau format: `🏛️ ATLAS │ 🧠 Opus │ 🏗️ AXIOM │ 🌿 main*3 │ 🔧 BACKEND │ 💰 $0.50 │ ⏱️ 12m`
  - Détection intelligente monorepo (projet + sous-dossier)
  - 11 projets avec emojis: AXIOM 🏗️, NEXUS 🧠, SYNAPSE ⚡, CORTEX 🔮, ATLAS 🏛️, FORGE 🔥, PRISM 💎, PERSO 👤, FINDASH 💰, HOMELAB 🖥️, HA 🏠
  - 16 agents avec emojis: ATLAS 🥇, GENESIS 🧬, BRAINSTORM 💡, BACKEND 🔧, FRONTEND 🎨, DEVOPS 🐳, DEBUGGER 🐛, etc.
  - Fallback sur nom de dossier pour projets inconnus (📁)

### Changed
- `hooks/SessionStart.sh` - Affiche banner + initialise agent state
- `hooks/SubagentStop.sh` - Implémente pop du stack agent
- `scripts/statusline.sh` - Nouveau format v2.0 avec emojis
- `settings.json` - Ajout PreToolUse hook pour Task tool

### Technical
- Scripts Bash compatibles Linux/WSL (pas de dépendance PowerShell)
- Requiert `jq` pour parsing JSON
- Pattern stack pour tracking agents imbriqués
- Conversion CRLF → LF automatique pour compatibilité WSL

---

## [1.1.0] - 2025-11-29

### Added
- **Session Management System**
  - Auto-documentation to `.dev/` folder
  - Session tracking with recovery support
  - Checkpoint system for context preservation
  - Backlog integration
- **Workflow Starter Commands (1-*)**
  - `/1-dev` - Start dev session with tracking
  - `/1-brainstorm` - Start brainstorm with auto-save
  - `/1-debug` - Start debug investigation
  - `/1-init-system` - Initialize Atlas in workspace
  - `/1-init-project` - Initialize `.dev/` structure
- **Session Commands**
  - `/0-checkpoint` - Create manual context checkpoint
  - `/9-archive` - Archive current session
- **Templates** (`templates/dev/`)
  - `current-session.template.md` - Active session tracking
  - `checkpoint.template.md` - Context snapshots
  - `hot-context.template.md` - Quick recovery reference
  - `journal-daily.template.md` - Daily activity logs
  - `backlog-item.template.md` - Backlog structure
- **Rules** (`agents/rules/`)
  - `auto-documentation.md` - When and what to auto-save
  - `session-management.md` - Session lifecycle management
- **Documentation** (`docs/`)
  - `session-management.md` - Complete guide
  - `commands-reference.md` - All commands reference
  - `templates-reference.md` - Templates guide

### Changed
- `agents/atlas.md` - Added Context Persistence Protocol
- `commands/0-new-session.md` - Now checks for active sessions
- `commands/0-resume.md` - Loads from session/checkpoint files
- `CLAUDE.md` - Added session management section
- `README.md` - Added workflow commands and session management docs

---

## [1.0.0] - 2025-11-29

### Added
- Initial release of Atlas Agent Framework
- **15+ Specialized Agents**
  - Core: ATLAS orchestrator, Workshop Facilitator, DevOps Manager
  - Orchestrators: Genesis, Brainstorm, System Architect
  - Builders: Backend, Frontend, DevOps, Docs
  - Planners: Debugger, Planner, UX Designer
- **Design Thinking Workshop System**
  - 5-phase process (Discovery, Problem Definition, Ideation, Validation, Specification)
  - Session recovery and progress tracking
  - Artifact generation
- **Unified Command Structure**
  - `0-*` commands for session start
  - `9-*` commands for session end
  - Standard commands for development workflows
- **Reusable Skills**
  - Infrastructure management (`zz-infra`)
  - API endpoint scaffolding (`zz-api-endpoint`)
  - React component generation (`zz-react-component`)
  - Docker service templates (`zz-docker-service`)
  - Optional Home Assistant MCP integration
- **Versioning System**
  - Semantic versioning with VERSION file
  - CHANGELOG following Keep a Changelog format
  - Conventional Commits integration
- **Session Tracking**
  - Unified timestamp format: `YYYY-MM-DD HH:MM`
  - Session JSON and activity log templates
  - Micro-session tracking
- **Git Workflow**
  - GitFlow branching model
  - Conventional Commits format
  - Private repos by default
- **Autopilot Permissions**
  - 60+ whitelisted development commands
  - Dangerous commands blocked (rm -rf /, format, etc.)

### Git Workflow
- Branch naming: `main`, `develop`, `feature/*`, `fix/*`, `release/*`, `hotfix/*`
- Commit format: `<type>(<scope>): <description>`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

[1.3.0]: https://github.com/seb155/atlas-agent-framework/releases/tag/v1.3.0
[1.2.0]: https://github.com/seb155/atlas-agent-framework/releases/tag/v1.2.0
[1.1.0]: https://github.com/seb155/atlas-agent-framework/releases/tag/v1.1.0
[1.0.0]: https://github.com/seb155/atlas-agent-framework/releases/tag/v1.0.0
