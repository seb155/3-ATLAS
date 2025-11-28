---
description: Code quality standards and validation rules
---

# Code Quality Validation Rules

**Purpose**: Enforce quality standards before deployment

---

## Rule 1: Always Validate Before Rebuild

### When Making Code Changes

**REQUIRED sequence**:
1. Make changes to `.ts`, `.tsx`, `.py` files
2. **RUN VALIDATION** (`/09-pre-commit-validation`)
3. **CHECK OUTPUT** - all tests must pass
4. **ONLY THEN** run `/07-docker-rebuild`

**FORBIDDEN**:
- Rebuilding without validation
- Assuming tests pass
- Skipping import/syntax checks

---

## Rule 2: Check Logs After Rebuild

### After Every Rebuild

**MUST do**:
```bash
docker logs synapse-frontend-1 --tail 50
```

**Look for**:
- ✅ "VITE v7.x.x ready" = SUCCESS
- ❌ "500 Internal Server Error" = IMPORT ERROR
- ❌ "Failed to resolve import" = PATH ERROR
- ❌ "Module not found" = MISSING DEPENDENCY

**Action**:
- If ❌ found: FIX immediately, re-validate, rebuild
- If ✅ only: Proceed to notify user

---

## Rule 3: Import Path Validation

### For Components in Subfolders

**Example structure**:
```
src/
├── components/
│   ├── MyComponent.tsx          # Use: import from '../store/'
│   └── SubFolder/
│       └── NestedComponent.tsx  # Use: import from '../../store/'
```

**Rule**: Count directory levels up to find target

**Common mistake**:
```typescript
// ❌ WRONG - from SubFolder/
import { useStore } from '../store/useStore'  // Only goes up 1 level

// ✅ CORRECT - from SubFolder/
import { useStore } from '../../store/useStore'  // Goes up 2 levels
```

**Prevention**: Run import validation tests

---

## Rule 4: Test Coverage Requirements

### When Adding New Files

**Frontend**:
- [ ] Create `[ComponentName].test.tsx` or `[filename].test.ts`
- [ ] Add to `src/test/imports.test.ts` if exported
- [ ] Verify tests pass before commit

**Backend**:
- [ ] Create `test_[module_name].py`
- [ ] Add tests for new services/endpoints
- [ ] Maintain 80%+ coverage

---

## Rule 5: Error Detection Before User Testing

### Never Ask User to Test If

- ❌ Build logs show errors
- ❌ Tests are failing
- ❌ Import validation fails
- ❌ Vite dev server not "ready"

### Always Verify

- ✅ All validation checks pass
- ✅ Logs show success
- ✅ Tests pass
- ✅ Dev server ready

---

## Automated Checks (AI Agent Must Run)

### Before Notify User

**Frontend changes**:
```bash
# 1. Build logs check
docker logs synapse-frontend-1 --tail 50 | grep -i "ready\|error"

# 2. Import validation
docker exec synapse-frontend-1 npm run test src/test/imports.test.ts

# 3. Quick smoke test
docker exec synapse-frontend-1 npm run test
```

**Backend changes**:
```bash
# 1. Unit tests
docker exec synapse-backend pytest tests/ -v

# 2. Import check
docker exec synapse-backend python -c "import app.main"
```

**Decision tree**:
```
All checks pass?
├─ YES → Notify user ✅
└─ NO  → Fix issues, repeat validation ❌
```

---

## Common Validation Failures

### 1. Import Path Error (500)
**Symptom**: `Failed to resolve import "../store/..."`  
**Fix**: Correct relative path depth  
**Test**: `npm run test src/test/imports.test.ts`

### 2. Missing Dependency
**Symptom**: `Cannot find module 'package-name'`  
**Fix**: Add to `package.json` / `requirements.txt`  
**Test**: Check imports in validation

### 3. TypeScript Error
**Symptom**: Type mismatch, undefined property  
**Fix**: Fix type definitions  
**Test**: `npx tsc --noEmit`

---

## Integration with Workflows

**Standard flow**:
1. Code changes
2. `/09-pre-commit-validation` ← VALIDATE
3. `/07-docker-rebuild` ← REBUILD
4. Check logs ← VERIFY
5. Notify user ← ONLY IF ALL PASS

**Short circuit on failure**: Stop at first failure, fix, restart from step 2.

---

## Exceptions

**Skip validation for**:
- Pure documentation changes
- README updates
- Comments/docstrings only
- Configuration with no code impact
