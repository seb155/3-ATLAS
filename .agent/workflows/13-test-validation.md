# Workflow: Test Validation

**Purpose:** Structured process for validating AI-generated code through auto tests + manual verification
**Version:** 1.0 (MVP-focused)
**Goal:** Ensure quality while maintaining velocity

---

## Overview

This workflow separates **automated validation** (AI-generated tests) from **manual validation** (user verification). Both are required before marking a feature as DONE.

---

## Phase 1: AI Generation

### AI Responsibilities
1. **Generate Code**
   - Backend code (endpoints, services, models)
   - Frontend code (components, stores, services)
   - Follow established patterns (see `docs/contributing/code-guidelines.md`)

2. **Generate Tests**
   - Backend: pytest tests with fixtures
   - Frontend: vitest tests with Testing Library
   - Target coverage: >70%

3. **Run Tests Automatically**
   ```bash
   # Backend
   cd apps/synapse/backend
   pytest tests/test_[feature].py --cov --alluredir=allure-results

   # Frontend
   cd apps/synapse/frontend
   npm run test -- [Component].test.tsx --coverage
   ```

4. **Log Results**
   - Update `.dev/testing/test-status.md`
   - Mark Auto Test column:
     - ✅ if all tests pass
     - ❌ if any test fails
   - Mark Manual Test column: ⚠️ (pending user validation)
   - Update Status: IN PROGRESS

### Output Artifacts
- Code committed to feature branch (or presented to user)
- Test results available (console output + Allure report if applicable)
- `.dev/testing/test-status.md` updated

---

## Phase 2: Auto-Validation (Automated Checks)

### Criteria for Auto-Pass
✅ **All tests pass** (exit code 0)
✅ **Coverage > 70%** (backend and frontend)
✅ **No linting errors** (eslint, flake8)
✅ **No type errors** (TypeScript strict, mypy if configured)

### Criteria for Auto-Fail
❌ **Any test fails** (exit code != 0)
❌ **Coverage < 70%**
❌ **Linting errors present**
❌ **Type errors present**

### If Auto-Pass
- AI: Updates `.dev/testing/test-status.md` (Auto Test: ✅)
- AI: Creates manual validation checklist for user
- Proceeds to Phase 3

### If Auto-Fail
- AI: Updates `.dev/testing/test-status.md` (Auto Test: ❌, Status: BLOCKED)
- AI: Analyzes failures
- AI: Fixes issues
- AI: Re-runs tests
- Repeats Phase 1

---

## Phase 3: Manual Validation (User Verification)

### Manual Test Checklist

#### 1. Functional Test
**Question:** Does the feature work as expected?

**Backend Checklist:**
- [ ] API endpoint responds correctly
- [ ] Data is saved to database
- [ ] Multi-tenancy filtering works (project_id)
- [ ] Authentication is enforced
- [ ] Error responses are appropriate (4xx, 5xx)

**Frontend Checklist:**
- [ ] Component renders correctly
- [ ] User interactions work (clicks, inputs, navigation)
- [ ] Data is fetched and displayed
- [ ] Loading states appear correctly
- [ ] Error states display properly

#### 2. Visual Test
**Question:** Does the UI look correct?

**Checklist:**
- [ ] Follows VSCode dark theme (if applicable)
- [ ] Spacing/padding consistent with other components
- [ ] No layout shifts or jumps
- [ ] Icons and text are aligned
- [ ] Responsive (works at different screen sizes)
- [ ] No visual glitches

#### 3. Edge Cases Test
**Question:** Does it handle edge cases gracefully?

**Checklist:**
- [ ] Empty state (no data)
- [ ] Large dataset (100+ items)
- [ ] Network error (API unavailable)
- [ ] Invalid input (wrong format, missing fields)
- [ ] Concurrent operations (race conditions)
- [ ] Browser refresh (state persists if needed)

#### 4. Performance Test
**Question:** Is it responsive and fast?

**Criteria:**
- [ ] < 5 seconds for data operations (import 100 items)
- [ ] < 10 seconds for rule execution (100 assets)
- [ ] < 3 seconds for package export
- [ ] No UI lag (smooth interactions)
- [ ] No memory leaks (dev tools profiler check)

### Recording Test Results

**Update `.dev/testing/test-status.md`:**
- If ALL tests pass → Manual Test: ✅ VALIDATED
- If ANY test fails → Manual Test: ❌ FAILED

**Update `.dev/journal/[today].md`:**
```markdown
### Manual Validation: [Feature Name]
- ✅ Functional: Works as expected
- ✅ Visual: Looks correct
- ❌ Edge Case: Fails with empty dataset (reported)
- ✅ Performance: < 5 seconds for 100 items

**Result:** FAILED (edge case issue)
**Action:** Created issue `.dev/issues/[feature]-empty-state.md`
```

---

## Phase 4: Issue Resolution (If Failed)

### If Manual Validation Fails

**User Actions:**
1. **Document the Issue**
   - Create `.dev/issues/[feature-name]-[issue].md`
   - Include:
     - What failed
     - Expected behavior
     - Actual behavior
     - Steps to reproduce
     - Screenshots/logs (if applicable)

2. **Update Status**
   - `.dev/testing/test-status.md`: Status → BLOCKED
   - `.dev/journal/[today].md`: Log issue

3. **Communicate to AI**
   - Share issue document
   - Provide clarifications if asked

**AI Actions:**
1. **Read Issue Document**
   - Understand what went wrong
   - Ask clarifying questions if needed

2. **Fix the Issue**
   - Modify code to address the problem
   - Update tests if needed
   - Re-run tests

3. **Repeat Phase 1**
   - Generate updated code
   - Run tests
   - Update test status

---

## Phase 5: Completion (If Passed)

### If Manual Validation Passes

**User Actions:**
1. **Update Test Status**
   - `.dev/testing/test-status.md`: Manual Test → ✅ VALIDATED, Status → DONE
   - `.dev/journal/[today].md`: Log completion

2. **Approve Merge** (if feature branch)
   - Review final code
   - Approve pull request or signal AI to merge

**AI Actions:**
1. **Update Documentation**
   - CHANGELOG.md entry
   - Feature docs (if user-facing)

2. **Create Git Commit**
   ```bash
   git commit -m "feat: [feature name]

   - Implementation details
   - Tests: [coverage %]

   🤖 Generated with Claude Code
   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

3. **Merge to Develop**
   - Merge feature branch to develop
   - Trigger CI/CD pipeline (if configured)

---

## Phase 6: Integration (Automated)

### CI/CD Pipeline (GitHub Actions - if configured)

**Triggers:**
- On push to develop
- On pull request to main

**Steps:**
1. **Run Full Test Suite**
   - Backend: pytest with all tests
   - Frontend: vitest with all tests
   - Upload Allure results

2. **Check Quality Gates**
   - Coverage > 70%
   - No linting errors
   - No type errors

3. **Semantic Release** (if configured)
   - Detect conventional commit
   - Bump version (feat: minor, fix: patch)
   - Update CHANGELOG.md
   - Create git tag

4. **Deploy** (future)
   - Deploy to staging (Proxmox)
   - Run smoke tests

---

## Workflow Diagram

```
┌─────────────────┐
│ Phase 1:        │
│ AI Generation   │
│ - Code          │
│ - Tests         │
│ - Run Tests     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Phase 2:        │
│ Auto-Validation │
│ - Tests pass?   │
│ - Coverage OK?  │
│ - No errors?    │
└────────┬────────┘
         │
         ├─ ❌ Failed ───→ Fix & Retry (Phase 1)
         │
         ↓ ✅ Passed
┌─────────────────┐
│ Phase 3:        │
│ Manual          │
│ Validation      │
│ - Functional    │
│ - Visual        │
│ - Edge Cases    │
│ - Performance   │
└────────┬────────┘
         │
         ├─ ❌ Failed ───→ Create Issue (Phase 4) ───→ Fix (Phase 1)
         │
         ↓ ✅ Passed
┌─────────────────┐
│ Phase 5:        │
│ Completion      │
│ - Update docs   │
│ - Git commit    │
│ - Merge         │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Phase 6:        │
│ Integration     │
│ - CI/CD         │
│ - Semantic      │
│   Release       │
│ - Deploy        │
└─────────────────┘
```

---

## Test Status Tracking Example

### Before Implementation
```markdown
| Feature | Component | Auto Test | Manual Test | Status |
|---------|-----------|-----------|-------------|--------|
| CSV Import | POST /api/v1/import/csv | ⚠️ Pending | ⚠️ Pending | TODO |
```

### After AI Generation (Tests Pass)
```markdown
| Feature | Component | Auto Test | Manual Test | Status |
|---------|-----------|-----------|-------------|--------|
| CSV Import | POST /api/v1/import/csv | ✅ pytest | ⚠️ Pending | IN PROGRESS |
```

### After Manual Validation (Failed)
```markdown
| Feature | Component | Auto Test | Manual Test | Status |
|---------|-----------|-----------|-------------|--------|
| CSV Import | POST /api/v1/import/csv | ✅ pytest | ❌ Failed | BLOCKED |
```
**Issue:** `.dev/issues/csv-import-empty-file.md`

### After Fix & Re-Validation (Passed)
```markdown
| Feature | Component | Auto Test | Manual Test | Status |
|---------|-----------|-----------|-------------|--------|
| CSV Import | POST /api/v1/import/csv | ✅ pytest | ✅ Validated | DONE |
```

---

## Best Practices

### For AI
1. **Always run tests before presenting code**
2. **Update test-status.md immediately after test run**
3. **Provide clear manual test checklist**
4. **Don't skip auto tests even if "simple" feature**

### For User
1. **Don't skip manual validation (even if auto tests pass)**
2. **Test edge cases (where bugs hide)**
3. **Document issues clearly (helps AI fix faster)**
4. **Update test-status.md promptly**

### For Both
1. **Coverage > 70% is minimum, not target**
2. **Manual validation is NOT optional**
3. **Issues should be fixed same day (maintain velocity)**
4. **Celebrate DONE status (motivation)**

---

## Issue Template

When creating `.dev/issues/[feature]-[issue].md`:

```markdown
# Issue: [Brief Description]

**Feature:** [Feature Name]
**Component:** [Component/File Name]
**Discovered:** [YYYY-MM-DD]
**Severity:** [Critical / High / Medium / Low]

---

## Problem Description

[Clear description of what went wrong]

---

## Expected Behavior

[What should happen]

---

## Actual Behavior

[What actually happened]

---

## Steps to Reproduce

1. [Step 1]
2. [Step 2]
3. [Step 3]
4. [Observe issue]

---

## Environment

- Browser: [Chrome 120 / Firefox 121 / etc.]
- OS: [Windows 11 / macOS / Linux]
- Screen Size: [1920x1080 / etc.]

---

## Screenshots/Logs

[Paste screenshots or relevant log output]

---

## Suggested Fix

[If user has idea for fix]

---

## Status

- [ ] Issue reported
- [ ] AI working on fix
- [ ] Fix implemented
- [ ] Re-tested (auto)
- [ ] Re-validated (manual)
- [ ] Issue resolved
```

---

**Version:** 1.0
**Last Updated:** 2025-11-25
**Next Review:** After MVP Week 1 completion
