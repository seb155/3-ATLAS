---
trigger: glob
globs: *.py, *.ts, *.tsx
description: When to run tests and when to rebuild Docker containers
---

# Testing & Build Triggers

**Purpose:** Define when to run tests and when to rebuild Docker after code changes.

---

## When to Run Tests

### ✅ ALWAYS Run Tests After:

1. **Modifying Backend Code** (`.py` files in `apps/synapse/backend/app/`)
   - Services, models, API endpoints, middleware
   - **Exception**: Documentation-only changes (comments, docstrings)

2. **Creating or Modifying Tests**
   - New test files (`test_*.py`, `*.test.ts`, `*.test.tsx`)
   - Changes to existing test files

3. **Modifying Frontend Logic** (`.ts`, `.tsx` files)
   - Stores (Zustand), hooks, utilities, components
   - **Exception**: Pure UI styling changes (CSS only)

4. **Before Creating a Walkthrough Artifact**
   - Verify all tests pass before documenting work completion

5. **User Explicitly Requests**
   - "Run tests", "Check if tests pass", "Verify tests", etc.

### ⏭️ SKIP Tests When:

1. **Documentation Only Changes**
   - `.md` files only
   - Comments/docstrings only
   - No code logic changed

2. **Configuration Changes** (unless they affect test setup)
   - `.gitignore`, `.env.example`
   - Docker configs (unless affecting test environment)

3. **Pure Styling Changes**
   - CSS/Tailwind classes only
   - No logic or behavior changes

4. **Already Run Recently**
   - Tests were run < 5 minutes ago for the same code
   - No new changes since last test run

---

## How to Run Tests

**Command:** `/13-test-validation` (comprehensive workflow)

**What it does:**
1. Runs backend tests (`pytest`)
2. Runs frontend tests (`npm test`)
3. Reports coverage
4. Updates test tracking in `.dev/testing/test-status.md`

**Quick commands:**
```bash
# Backend tests
docker exec synapse-backend-1 pytest apps/synapse/backend/tests/

# Frontend tests
cd apps/synapse/frontend && npm test
```

**Remember:** When in doubt, RUN TESTS. It's better to run tests unnecessarily than to miss a regression.

---

## When to Rebuild Docker

### 🔨 ALWAYS Rebuild Docker After:

1. **Backend dependency changes**
   - `requirements.txt` modified
   - New Python packages added

2. **Frontend dependency changes**
   - `package.json` modified
   - New NPM packages added

3. **Dockerfile changes**
   - Backend or frontend Dockerfile modified
   - Docker Compose configuration changed

4. **Environment variable changes**
   - `.env` file modified (new variables, changed values)

5. **Build configuration changes**
   - `vite.config.ts` modified
   - `tsconfig.json` modified (affects build)

### ⏭️ NO Rebuild Needed For:

1. **Code-only changes** (`.py`, `.ts`, `.tsx`)
   - Hot reload handles these
   - Just save and refresh browser

2. **Documentation changes** (`.md`)

3. **Test files** (unless dependencies changed)

---

## Rebuild Workflow

**IMPORTANT:** If you modify code (`.tsx`, `.ts`, `.py`):

1. ✅ Run `/14-docker-rebuild` IMMEDIATELY
2. ✅ Wait for build to finish
3. ✅ THEN ask user to test
4. ❌ NEVER ask user to test without rebuild first

**Command:** `/14-docker-rebuild` (includes pre-flight validation)

**Quick rebuild commands:**
```bash
# Backend only
docker-compose down && docker-compose up -d --build synapse-backend

# Frontend only
docker-compose down && docker-compose up -d --build synapse-frontend

# Full rebuild
docker-compose down && docker-compose up -d --build
```

---

## Testing + Build Decision Matrix

| Change Type | Run Tests? | Rebuild Docker? |
|-------------|-----------|-----------------|
| Backend `.py` logic | ✅ Yes | ❌ No (hot reload) |
| Frontend `.tsx` logic | ✅ Yes | ❌ No (hot reload) |
| `requirements.txt` | ✅ Yes | ✅ Yes (backend) |
| `package.json` | ✅ Yes | ✅ Yes (frontend) |
| Dockerfile | ⏭️ Skip | ✅ Yes (affected service) |
| `.env` changes | ⏭️ Skip | ✅ Yes (full rebuild) |
| Documentation `.md` | ⏭️ Skip | ❌ No |
| CSS/Tailwind only | ⏭️ Skip | ❌ No (hot reload) |
| Test files | ✅ Yes | ❌ No |

---

## Automation (Post-MVP)

**Week 4 Setup:**
- Husky pre-commit hooks → Auto-run tests before commit
- GitHub Actions CI → Auto-run tests on push
- Docker Compose watch → Auto-rebuild on dependency changes

---

## References

**Full workflows:**
- Tests: `/13-test-validation` (comprehensive workflow)
- Docker rebuild: `/14-docker-rebuild` (with pre-flight checks)
- Test tracking: `.dev/testing/test-status.md`
