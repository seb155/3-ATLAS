---
description: Rebuild Docker containers with pre-flight validation
---

# Docker Rebuild Protocol

**Purpose:** Safely rebuild Docker containers after code changes with validation checks

**When to use:** After modifying `.tsx`, `.ts`, `.py` files or build configurations

---

## Pre-Flight Checks (Prevent Broken Builds)

**IMPORTANT:** Run these checks BEFORE rebuilding to catch errors early.

### Frontend Pre-Flight

**A. TypeScript Compilation Check**
```bash
cd apps/synapse/frontend && npx tsc --noEmit
```

**Expected:** No errors
**If errors:** Fix TypeScript issues first

**B. Import Validation**
```bash
cd apps/synapse/frontend && npm run test src/test/imports.test.ts
```

**Expected:** All import tests PASS
**If FAIL:** Fix import paths (common cause of 500 errors)

**C. Frontend Tests**
```bash
cd apps/synapse/frontend && npm test
```

**Expected:** All tests PASS
**If FAIL:** Fix failing tests before rebuild

### Backend Pre-Flight

**A. Backend Tests**
```bash
docker exec synapse-backend-1 pytest apps/synapse/backend/tests/ -v
```

**Expected:** All tests PASS
**If FAIL:** Fix failing tests first

**B. Python Syntax Check**
```bash
docker exec synapse-backend-1 python -c "from app.main import app"
```

**Expected:** No errors
**If errors:** Fix Python syntax/import issues

---

## Pre-Flight Checklist

**Before proceeding to rebuild, verify:**
- [ ] TypeScript compilation successful (no errors)
- [ ] Import tests pass (prevents 500 errors)
- [ ] Frontend tests pass
- [ ] Backend tests pass
- [ ] No syntax errors

**If ANY check fails:** ❌ STOP and fix issues first
**If ALL checks pass:** ✅ Proceed to rebuild

---

## Rebuild Steps

### When to Rebuild

**✅ Rebuild required for:**
- `requirements.txt` changed (backend dependencies)
- `package.json` changed (frontend dependencies)
- Dockerfile modified
- `.env` variables added/changed
- `vite.config.ts` modified

**⏭️ NO rebuild for:**
- Code-only changes (`.py`, `.ts`, `.tsx`) - hot reload handles these
- Documentation changes (`.md` files)
- Test files (unless dependencies changed)

### Frontend Rebuild

```bash
# Rebuild frontend container
docker-compose -f apps/synapse/docker-compose.dev.yml up -d --build synapse-frontend

# Wait for build completion (CRITICAL)
docker logs synapse-frontend-1 --tail 50
```

**Expected:** `VITE v7.x.x ready in XXXms`

**If errors:**
- Check for import resolution errors (500 status)
- Check for "Module not found" errors
- Check for syntax errors

**Verify build success:**
```bash
docker logs synapse-frontend-1 | grep -i "error\|failed"
```

**If ANY errors found:**
- ❌ DO NOT notify user to test
- ✅ FIX errors first
- ✅ Re-run this workflow

**Wait for Vite readiness:**
- Allow 5-10 seconds for Vite dev server to stabilize
- Verify logs show "ready" status

### Backend Rebuild

```bash
# Rebuild backend container
docker-compose -f apps/synapse/docker-compose.dev.yml up -d --build synapse-backend

# Wait for build completion
docker logs synapse-backend-1 --tail 50
```

**Expected:** `Uvicorn running on http://0.0.0.0:8000`

**Verify backend health:**
```bash
docker exec synapse-backend-1 pytest apps/synapse/backend/tests/ -v
```

### Full Rebuild (Both)

```bash
# Rebuild all containers
docker-compose down
docker-compose up -d --build
```

**Wait 30-60 seconds** for all services to start

---

## Post-Rebuild Validation

**After rebuild completes:**

- [ ] All containers running (`docker ps`)
- [ ] Backend healthy (http://localhost:8001/health)
- [ ] Frontend loaded (http://localhost:4000)
- [ ] No errors in logs (`docker-compose logs -f`)
- [ ] Vite dev server shows "ready"

---

## Inform User

**ONLY inform user if ALL checks pass:**

```
✅ Rebuild complete! Changes are live.

- Frontend: Vite dev server ready
- Backend: API running on port 8001
- Tests: All passing

Please hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)

What changed:
- [List specific changes made]
```

**NEVER ask user to test without:**
1. ✅ Pre-flight checks passed
2. ✅ Rebuild completed successfully
3. ✅ Post-rebuild validation passed
4. ✅ No errors in logs

---

## Quick Check (Fast Validation)

For quick validation before rebuild:

```bash
# Frontend imports only (fastest check)
cd apps/synapse/frontend && npm run test src/test/imports.test.ts

# Backend unit tests only
docker exec synapse-backend-1 pytest apps/synapse/backend/tests/test_workflow_engine.py -v
```

---

## Common Errors & Fixes

### 500 Internal Server Error (Frontend)
**Cause:** Import path incorrect (e.g., `../store/` instead of `../../store/`)
**Fix:** Check relative import paths
**Prevention:** Run import validation tests

### Module not found
**Cause:** Missing dependency or wrong path
**Fix:** Check import statement and file location
**Prevention:** Import validation tests

### Vite transform errors
**Cause:** Syntax error or invalid TypeScript
**Fix:** Check TypeScript errors in IDE
**Prevention:** Type-check with `npx tsc --noEmit` before commit

### Container won't start
**Cause:** Port conflict or previous container not stopped
**Fix:** `docker-compose down && docker-compose up -d`

### Changes not visible after rebuild
**Cause:** Browser cache or didn't use `--build` flag
**Fix:** Hard refresh (Ctrl+F5) or use `docker-compose up -d --build --force-recreate`

---

## Critical Notes

- **`docker restart` does NOT apply code changes** - always use `--build`
- **CHECK LOGS** - don't assume build success
- **RUN TESTS** - catch import/syntax errors early
- **Hard refresh required** after rebuild (Ctrl+F5 in browser)
- **Skip this workflow** for documentation-only changes

---

## Troubleshooting

**If rebuild fails:**
1. Check Docker logs: `docker logs synapse-frontend-1` or `synapse-backend-1`
2. Verify containers are running: `docker ps`
3. Check disk space: `docker system df`
4. Try clean rebuild: `docker-compose down -v && docker-compose up -d --build`

**If tests fail after rebuild:**
1. Check test logs for specific failures
2. Verify database migrations applied: `docker exec synapse-backend-1 alembic current`
3. Check environment variables: `docker exec synapse-backend-1 env | grep SYNAPSE`

---

## Typical Workflow

```
1. Make code changes
   └─> Modify .tsx, .ts, .py files

2. Run pre-flight checks
   └─> TypeScript compilation
   └─> Import validation
   └─> Tests

3. If pre-flight passes → Rebuild Docker
   └─> Use --build flag
   └─> Wait for completion
   └─> Check logs for errors

4. Post-rebuild validation
   └─> Verify containers running
   └─> Check API health
   └─> Run tests

5. Inform user (ONLY if all checks pass)
   └─> Tell user to hard refresh
   └─> Mention what changed
```

---

## When to Skip

**Skip this workflow for:**
- Documentation changes only (`.md` files)
- Configuration files that don't affect code build
- README updates
- Comments-only changes

**For code changes without dependency updates:**
- Hot reload handles `.tsx`, `.ts`, `.py` changes automatically
- Just save file and refresh browser (Ctrl+F5)

---

## Integration with Other Workflows

**Related workflows:**
- Before rebuild: Check `/05-testing-triggers` rule (when to rebuild)
- After rebuild: Use `/13-test-validation` for full validation
- Feature work: `/10-new-feature-mvp` includes rebuild steps

---

**Version:** 1.0 (Merged from 07-docker-rebuild + 09-pre-commit-validation)
**Last Updated:** 2025-11-25
**Related:** `/05-testing-triggers`, `/13-test-validation`, `/03-docker-troubleshoot`
