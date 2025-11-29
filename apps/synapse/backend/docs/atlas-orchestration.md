# Atlas Orchestration System

**Version:** v0.2.5
**Status:** Production Ready
**Last Updated:** 2025-11-28

---

## Overview

Le système Atlas Orchestration fournit un point d'entrée unique pour toutes les sessions de développement avec Claude Code, avec 3 modes de session optimisés et workflow automation.

### Key Features

- ✅ **ATLAS Agent** - Orchestrateur principal avec consciousness complète
- ✅ **3 Session Modes** - FULL, QUICK, RECOVERY
- ✅ **Command Naming `/0-*`** - Tri alphabétique pour quick access
- ✅ **Choix Numérotés** - Réponses systématiques avec options 1,2,3,4
- ✅ **Auto-documentation** - Via `/docs` automatique
- ✅ **Git Workflow** - Tests + commit + version bump + push
- ✅ **Progress Tracking** - Compact views (progress + dashboard)
- ✅ **Smart Context** - Hot files, session history, task queue

---

## Quick Start

### First Session of the Day

```bash
/0-new-session
```

**What happens:**
- Charge TOUT le contexte (project-state, journal, tests, git)
- Vérifie Docker, services, environnement
- Propose roadmap complet
- Affiche sprint actuel et priorités

### Continue Next Task

```bash
/0-next
```

**What happens:**
- Lit dernier journal "Next Session" uniquement
- Charge contexte minimal pour la tâche
- Skip vérifications environnement
- Démarre directement sur prochaine tâche

### After /compact During Work

```bash
/0-resume
```

**What happens:**
- Reconstruit contexte depuis compact summary
- Retrouve todo list active
- Valide dernière tâche completed
- Reprend exactement où c'était rendu

---

## All `/0-*` Commands

Type `/0` to see all principal commands:

```bash
/0-new-session    # Mode FULL - Nouvelle session complète
/0-next           # Mode QUICK - Prochaine tâche rapide
/0-resume         # Mode RECOVERY - Après /compact
/0-progress       # Roadmap overview compact
/0-dashboard      # Session actuelle overview
/0-ship           # Git workflow automatisé
```

---

## Architecture

```
Atlas Orchestration System
│
├── Point d'entrée: .claude/agents/atlas.md
│   ├── Consciousness: Peut utiliser /commands et agents
│   ├── Always: Propose choix numérotés (1,2,3,4)
│   └── Modes: FULL, QUICK, RECOVERY
│
├── Session Commands (.claude/commands/)
│   ├── /0-new-session → Mode FULL
│   ├── /0-next → Mode QUICK
│   └── /0-resume → Mode RECOVERY
│
├── Workflow Commands
│   ├── /0-progress → Roadmap overview
│   ├── /0-dashboard → Session overview
│   └── /0-ship → Git push + versioning
│
└── Tracking Files
    ├── session-history.json → Session stats
    ├── task-queue.md → Task management
    └── hot-files.json → Smart context loading
```

---

## Session Modes

### FULL Mode (via /0-new-session)

**Use case:** Première session du jour ou après pause longue

**Actions:**
- Charge TOUT le contexte
- Vérifie Docker, env, git
- Propose roadmap complet
- Affiche sprint actuel et priorités

**Example:**
```
User: /0-new-session

ATLAS: "Bonjour! Je charge le contexte...

**Environnement**
- OS: Windows 11
- Docker: forge-postgres, forge-redis (healthy)
- Mode: Development

**Sprint**: MVP Week 2 (90% complete)
**En cours**: Tests backend template_service

**Que veux-tu faire?**
1. Continuer tests (recommandé)
2. Voir roadmap complet
3. Autre tâche
4. Voir dashboard (/0-dashboard)"
```

### QUICK Mode (via /0-next)

**Use case:** Continuer travail en cours, enchaîner tâches

**Actions:**
- Lit dernier journal "Next Session" uniquement
- Charge contexte minimal pour la tâche
- Skip vérifications environnement
- Démarre directement sur prochaine tâche

**Example:**
```
User: /0-next

ATLAS: "Reprenant session précédente...

**Dernière session:** 2025-11-28 14:30 (45min)
**Prochaine tâche:** Tests backend template_service

**Contexte chargé:**
- apps/synapse/backend/app/services/template_service.py
- apps/synapse/backend/tests/ (structure)

**Que veux-tu faire?**
1. Démarrer tests IN-P040 (recommandé)
2. Voir plan complet
3. Changer de tâche
4. Autre chose"
```

### RECOVERY Mode (via /0-resume)

**Use case:** Après /compact en plein développement

**Actions:**
- Reconstruit contexte depuis compact summary
- Retrouve todo list active
- Valide dernière tâche completed
- Reprend exactement où c'était rendu

**Example:**
```
User: /0-resume

ATLAS: "Reconstruction session après compact...

**Compact timestamp:** 2025-11-28 15:45
**Tâche en cours:** Créer AssetHistory.tsx component

**Todo list retrouvée:**
- ✅ Create component structure
- 🔄 Add version timeline UI (IN PROGRESS)
- ⚠️ Add diff viewer
- ⚠️ Add rollback button

**Que veux-tu faire?**
1. Continuer version timeline UI
2. Voir le diff depuis compact
3. Commiter travail actuel
4. Autre chose"
```

---

## Workflow Commands

### /0-progress - Roadmap Overview

**Format:** Ultra-compact (15-20 lignes - tient dans terminal)

**Shows:**
- MVP Sprint progress with deadline
- Phase-by-phase completion (progress bars)
- Last session recap
- Top 3 next tasks

**Example:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AXIOM Progress Report - 2025-11-28 15:30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 MVP Sprint: Week 2/4 ████████████░░░░░░░░ 60% → Dec 20

Phase Progress:
✅ v0.2.5 Atlas Orchestration ████████████████████ 100%
✅ v0.2.4 Templates & Export  ████████████████████ 100%
🔄 v0.2.6 Tests & Integration ████████░░░░░░░░░░░░  40%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Last Session: 2025-11-28 15:30 (1h30)
✅ Atlas orchestration, 6 commands, tracking files

Next Up:
1. Test workflows complets
2. Frontend integration AssetHistory
3. UI Polish export button
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### /0-dashboard - Session Overview

**Format:** Current session focus

**Shows:**
- Current sprint completion
- Session duration & tasks completed today
- Active task & next task
- Tests status (backend/frontend)
- Git status (commits, push status)

**Example:**
```
ATLAS Dashboard - 2025-11-28 17:00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Sprint: MVP Week 2 (95% complete)
⏱️  Session: 1h 30min
✅ Completed: 12 tasks

🔥 Active: Documentation Atlas
⏭️  Next: Test workflows

🧪 Tests: ✅ Backend 84% | ⚠️ Frontend pending
📦 Git: 14 files modified, not pushed
```

### /0-ship - Git Workflow

**Actions:**
1. Run all tests (backend + frontend)
2. Check linting
3. Verify build succeeds
4. Parse commits for version bump
5. Stage, commit, tag, push
6. Auto-documentation via `/docs`

**Conventional Commits:**
- `feat:` → minor version (0.x.0)
- `fix:` → patch version (0.0.x)
- `BREAKING CHANGE:` → major version (x.0.0)

---

## Tracking Files

### session-history.json

Track all development sessions:

```json
{
  "sessions": [
    {
      "id": "2025-11-28-1530",
      "mode": "FULL",
      "command": "/0-new-session",
      "started_at": "2025-11-28 15:30",
      "ended_at": "2025-11-28 17:00",
      "duration_minutes": 90,
      "tasks_completed": 12,
      "commits": 3
    }
  ],
  "stats": {
    "total_sessions": 42,
    "avg_duration_minutes": 38,
    "most_used_mode": "QUICK"
  }
}
```

### task-queue.md

Prioritized task management:

```markdown
## In Progress
- [ ] [TASK-001] Tests backend (Started: 2025-11-28 15:30)

## Next Up (Priority)
1. [ ] Frontend integration
2. [ ] UI Polish
3. [ ] Demo data

## Backlog
- [ ] CI/CD setup
```

### hot-files.json

Smart context loading:

```json
{
  "hot_files": [
    {
      "path": "d:\\Projects\\AXIOM\\.claude\\agents\\atlas.md",
      "frequency": 15,
      "last_modified": "2025-11-28 15:45",
      "priority": "high"
    }
  ]
}
```

---

## Best Practices

### 1. Always Start with Atlas

**First session:**
```bash
/0-new-session
```

**Resume work:**
```bash
/0-next
```

**After compact:**
```bash
/0-resume
```

### 2. Use Progress Tracking

Check progress anytime:
```bash
/0-progress     # Full roadmap
/0-dashboard    # Current session
```

### 3. Ship with Confidence

```bash
/0-ship         # Runs tests, bumps version, pushes
```

### 4. Let Atlas Propose Choices

Atlas ALWAYS ends responses with numbered choices:
```
**Que veux-tu faire?**
1. [Action principale]
2. [Alternative 1]
3. [Alternative 2]
4. Autre chose
```

Just type the number!

---

## Timestamp Format

**Complete guide:** [.agent/rules/07-timestamp-format.md](d:\Projects\AXIOM\.agent\rules\07-timestamp-format.md)

**ALWAYS use:** `YYYY-MM-DD HH:MM`

Example: `2025-11-28 14:30`

**Time ranges:** `[YYYY-MM-DD HH:MM] - [YYYY-MM-DD HH:MM]`
Example: `[2025-11-28 09:00] - [2025-11-28 12:30]`

Never:
- Just date: `2025-11-28`
- Just time: `14:30`
- Short time ranges: `[HH:MM]-[HH:MM]`
- Other formats: `11/28/2025 2:30 PM`

---

## Success Metrics

### Before Atlas
- Commandes dispersées
- Setup manuel à chaque session
- Documentation oubliée
- Pas de tracking progression

### After Atlas
- Type `/0` → 6 commandes principales
- 3 modes optimisés
- Auto-documentation
- Full tracking (session + task + files)

### ROI
- Après 10 sessions: ROI positif
- Réduction 30-50% temps setup
- 0 oublis documentation

---

## Troubleshooting

### Issue: Command not found

**Solution:** Ensure you're in plan mode exit or check `.claude/commands/` directory exists

### Issue: Atlas doesn't propose numbered choices

**Solution:** Check `.claude/agents/atlas.md` loaded correctly

### Issue: Timestamps wrong format

**Solution:** Always use `YYYY-MM-DD HH:MM` format. For time ranges, use `[YYYY-MM-DD HH:MM] - [YYYY-MM-DD HH:MM]`. See [.agent/rules/07-timestamp-format.md](d:\Projects\AXIOM\.agent\rules\07-timestamp-format.md) for complete guide

---

## See Also

- [CLAUDE.md](../../../CLAUDE.md) - AI Orchestration overview
- [project-state.md](../../../.dev/context/project-state.md) - Current project state
- [session-template.md](../../../.dev/journal/session-template.md) - Journal template

---

**Last Updated:** 2025-11-28
**Version:** v0.2.5
**Author:** AXIOM Development Team
