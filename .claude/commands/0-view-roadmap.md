---
description: Quick progress overview - roadmap, phases, last session (compact view)
---

# /0-view-roadmap

Affiche rapidement où on en est - roadmap, phases, dernière session.

**Format:** Ultra-compact (15-20 lignes max - tient dans un terminal)

## Usage

```bash
/0-view-roadmap              # Roadmap du projet courant
/0-view-roadmap echo         # Roadmap du projet ECHO
/0-view-roadmap synapse      # Roadmap du projet SYNAPSE
```

## Arguments

- `[project-id]` (optional): Identifiant du projet cible
  - Case-insensitive
  - Résolution via Rule 31 (project-resolution.md)

## What it shows

1. **MVP Sprint progress** - Overall timeline and deadline
2. **Phase progress** - Version-by-version completion with progress bars
3. **Last session recap** - Quick summary of last work session
4. **Next up** - Top 3 pending tasks

## Exemple

```text
User: /0-view-roadmap synapse

📂 Projet: SYNAPSE (MBSE Platform)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SYNAPSE Progress Report - 2025-11-28 15:30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 MVP Sprint: Week 2/4 ████████████░░░░░░░░ 60% → Dec 20

Phase Progress:
✅ v0.2.4 Templates & Export  ████████████████████ 100%
🔄 v0.2.5 Tests & Integration ████████░░░░░░░░░░░░  40%
⚠️  v0.3.0 Multi-Tenant       ░░░░░░░░░░░░░░░░░░░░   0%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Last Session: 2025-11-28 14:30 (45min)
✅ Template service, Package API, AssetHistory UI
✅ Documentation, Tests IN-P040/CA-P040 passing

Next Up:
1. Frontend integration (AssetHistory → AssetDetails)
2. UI Polish (export button)
3. Demo data creation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Que veux-tu faire?**
1. Continue next task  2. Ship current  3. Full details  4. Other
```

## Progress Bar Format

- 0-25%: ████░░░░░░░░░░░░░░░░ (4/20 blocks)
- 26-50%: ██████████░░░░░░░░░░ (10/20 blocks)
- 51-75%: ███████████████░░░░░ (15/20 blocks)
- 76-100%: ████████████████████ (20/20 blocks)

## Data Sources

- **Roadmap:** `.dev/roadmap/README.md`
- **Sprint:** `.dev/roadmap/current-sprint.md`
- **Last session:** `.dev/journal/YYYY-MM/latest.md`
- **Progress:** Calculate from completed vs total tasks

## Agent invoqué

- ATLAS (quick data aggregation)

## When to use

✅ **Use /0-view-roadmap when:**
- Want quick status overview
- Check overall project health
- See where you are in roadmap
- Before starting new task

❌ **Use /0-view-status instead when:**
- Want current session details
- Check today's work
- See active tasks only

---

**Tip:** Type `/0-view-roadmap [project]` to see project progress!

## See Also

- `/0-view-status` - Current session status
- `/0-view-backlog` - Backlog items
- `/0-view-projects` - All projects
