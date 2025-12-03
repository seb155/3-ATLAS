---
description: Current session overview - tasks, tests, git status
---

# /0-view-status

Vue d'ensemble de la session actuelle - tâches, tests, git.

**Format:** Current session focus (not full roadmap)

## Usage

```bash
/0-view-status              # Status du projet courant
/0-view-status echo         # Status du projet ECHO
/0-view-status synapse      # Status du projet SYNAPSE
```

## Arguments

- `[project-id]` (optional): Identifiant du projet cible
  - Case-insensitive
  - Résolution via Rule 31 (project-resolution.md)

## What it shows

1. **Current sprint** - Active sprint and completion %
2. **Session stats** - Duration, tasks completed today
3. **Active task** - What you're working on now
4. **Next task** - What's coming up
5. **Tests status** - Backend/Frontend coverage
6. **Git status** - Local commits, push status

## Exemple

```text
User: /0-view-status echo

📂 Projet: ECHO (Voice Assistant)

ATLAS Dashboard - 2025-11-28 15:30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Sprint: MVP Week 2 (90% complete)
⏱️  Session: 2h 15min (3 micro-sessions)
✅ Completed today: 8 tasks
⚠️  Pending: 4 tasks

🔥 Active: Tests backend template_service
⏭️  Next: Frontend integration

🧪 Tests: ✅ Backend 84% | ⚠️ Frontend pending
📦 Git: 2 commits local, not pushed

**Que veux-tu faire?**
1. Continue active task
2. Start next task
3. Ship current work (/9-git-ship)
4. View full progress (/0-view-roadmap)
```

## Data Sources

- **Sprint:** `.dev/roadmap/current-sprint.md`
- **Session:** `.claude/context/session-history.json`
- **Tasks:** Current TodoWrite list
- **Tests:** Latest test run results
- **Git:** `git status`, `git log`

## Agent invoqué

- ATLAS (session tracking)

## When to use

✅ **Use /0-view-status when:**
- Check current session status
- See what's active right now
- Quick test status check
- Before `/9-git-ship`

❌ **Use /0-view-roadmap instead when:**
- Want roadmap overview
- See all phases
- Check overall project health
- Long-term planning

---

**Tip:** Type `/0-view-status [project]` to check session status!

## See Also

- `/0-view-roadmap` - Full roadmap view
- `/0-view-backlog` - Backlog items
- `/9-git-ship` - Ship your work
