# Task Queue

**Last Updated:** 2025-12-03 14:50

---

## In Progress

- [ ] [TASK-002] **Finaliser migration monorepo + import historique** (Started: 2025-12-03)
  - **Contexte:** Session avec Claude Opus - Architecture AI Ecosystem
  - **Branch:** `claude/ai-ecosystem-architecture-01PpZTSnLJPMtxh15tmyUh4p`
  - **À faire sur machine locale:**
    1. `git checkout claude/ai-ecosystem-architecture-01PpZTSnLJPMtxh15tmyUh4p && git pull`
    2. `./scripts/migration/import-all-history.sh` (importe historique atlas-framework + nexus)
    3. Merger la branche dans main
  - **Docs créés:** `.dev/design/ai-ecosystem-architecture.md`, `.dev/design/monorepo-pure-architecture.md`

## Next Up (Priority)

1. [ ] Frontend integration AssetHistory → AssetDetails
2. [ ] UI Polish - Package export button
3. [ ] Demo data creation

## Backlog

- [ ] CI/CD setup (GitHub Actions)
- [ ] User documentation

---

## Completed (Recent)

- [x] [TASK-001] Complete Atlas orchestration system (2025-11-28 17:00)
- [x] Test infrastructure assessment - Backend 111 tests, Frontend 73 tests (2025-11-29 14:00)
- [x] Create .claude/agents/atlas.md (2025-11-28 15:45)
- [x] Create all /0-*.md commands (2025-11-28 16:20)
- [x] Create tracking files - session-history, task-queue, hot-files (2025-11-28 16:30)
- [x] Update project-state.md to v0.2.5 (2025-11-28 16:45)
- [x] Create journal entry 2025-11-28-atlas-orchestration.md (2025-11-28 17:00)

---

## Task Format

```markdown
- [ ] [TASK-XXX] Description (Started: YYYY-MM-DD HH:MM)
```

**States:**
- `[ ]` Pending
- `[x]` Completed
- Removed if no longer relevant

---

## Usage

**Add task:**
```markdown
- [ ] [TASK-XXX] New task description
```

**Complete task:**
```markdown
- [x] [TASK-XXX] Task description (Completed: YYYY-MM-DD HH:MM)
```

**Move to "Completed (Recent)":** Keep last 10-15 for reference
