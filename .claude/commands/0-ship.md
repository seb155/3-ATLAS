---
description: Git workflow - commit, version bump, push with tests validation
---

# /0-ship

Workflow Git automatisé avec vérification tests et versioning.

## Actions

1. **Vérifications pré-push**
   - ✅ Tests backend passent? (pytest)
   - ✅ Tests frontend passent? (vitest)
   - ✅ Linting OK? (ruff, eslint)
   - ✅ Build réussit?

2. **Git status**
   - Fichiers modifiés
   - Fichiers non-trackés
   - Commits locaux non-pushés

3. **Version bump** (si applicable)
   - Parse commits (conventional commits)
   - Détermine: patch/minor/major
   - Update package.json, pyproject.toml

4. **Git operations**
   - Stage changements
   - Commit (si nécessaire)
   - Tag version (si bump)
   - Push to remote

5. **Documentation update**
   - Utilise `/docs` automatiquement
   - Update CHANGELOG.md
   - Update project-state.md

## Agent invoqué

- ATLAS
- GIT-MANAGER (si disponible)

## Options

```bash
/0-ship              # Full workflow
/0-ship --skip-tests # Skip tests (use with caution)
/0-ship --dry-run    # Show what would happen
```

## Conventional Commits Version Bump

**Rules:**
- `feat:` → minor version (0.x.0)
- `fix:` → patch version (0.0.x)
- `BREAKING CHANGE:` → major version (x.0.0)
- `chore:`, `docs:`, `style:` → no bump

**Example:**
```
Commits:
- feat: Add template export system
- fix: Handle null asset properties

→ Version bump: v0.2.4 → v0.2.5 (minor)
```

## Exemple

```text
User: /0-ship

ATLAS: "Démarrage workflow Git...

**Tests:**
✅ Backend tests: 142 passed, coverage 84%
✅ Frontend tests: 89 passed
✅ Linting: No errors
✅ Build: Success

**Git status:**
- 6 fichiers modifiés
- 2 commits locaux (non-pushés)

**Commits analysis:**
- feat: Add template export system
- fix: Handle null asset properties

**Version bump suggérée:** v0.2.4 → v0.2.5 (minor)

**Que veux-tu faire?**
1. Ship avec version bump (recommandé)
2. Ship sans version bump
3. Dry-run (voir les commandes)
4. Annuler"
```

## Auto-documentation

Après `/0-ship`, ATLAS met automatiquement à jour:
- `.dev/context/project-state.md` (version, recent changes)
- `.dev/journal/YYYY-MM/YYYY-MM-DD-HH-MM.md` (session summary - filename exception)
- `CHANGELOG.md` (if version bump)

**Note:** Filename format `YYYY-MM-DD-HH-MM` is an allowed filesystem exception. All content inside files must use `YYYY-MM-DD HH:MM` format (see [.agent/rules/07-timestamp-format.md](d:\Projects\AXIOM\.agent\rules\07-timestamp-format.md))

## When to use

✅ **Use /0-ship when:**
- Tests passent
- Ready to push to remote
- Want version bump
- End of feature/sprint

❌ **Don't use /0-ship when:**
- Tests failing
- Work in progress
- Not ready for remote
- Experimental changes

## Safety checks

Before push, `/0-ship` verifies:
1. All tests pass (backend + frontend)
2. No linting errors
3. Build succeeds
4. Git status clean (or intentional changes)

If any check fails → Abort with error message

---

**Tip:** Type `/0-ship` when ready to deliver your work!
