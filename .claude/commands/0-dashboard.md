---
description: Current session overview - tasks, tests, git status
---

# /0-dashboard

Vue d'ensemble de la session actuelle - tâches, tests, git.

**Format:** Current session focus (not full roadmap)

## What it shows

1. **Current sprint** - Active sprint and completion %
2. **Session stats** - Duration, tasks completed today
3. **Active task** - What you're working on now
4. **Next task** - What's coming up
5. **Tests status** - Backend/Frontend coverage
6. **Git status** - Local commits, push status

## Exemple

```text
User: /0-dashboard

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
3. Ship current work (/0-ship)
4. View full progress (/0-progress)
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

✅ **Use /0-dashboard when:**
- Check current session status
- See what's active right now
- Quick test status check
- Before `/0-ship`

❌ **Use /0-progress instead when:**
- Want roadmap overview
- See all phases
- Check overall project health
- Long-term planning

## Difference: Dashboard vs Progress

**Dashboard** = Current session
- Today's work
- Active tasks
- Right now status

**Progress** = Full roadmap
- All phases
- Long-term timeline
- Overall health

## Session Tracking

Dashboard tracks:
- **Micro-sessions:** Each time you start/stop work
- **Tasks completed:** From TodoWrite
- **Duration:** Total time working today
- **Git activity:** Commits, pushes

All stored in: `.claude/context/session-history.json`

## Quick Commands

From dashboard, you can jump to:
- `/0-ship` - Ship your work
- `/0-progress` - See full roadmap
- `/0-next` - Start next task
- `/test` - Run tests

---

**Tip:** Type `/0-dashboard` to check your current session status!
