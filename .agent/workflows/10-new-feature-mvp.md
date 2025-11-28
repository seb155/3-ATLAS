# Workflow: Nouvelle Feature MVP

**Purpose:** Structured workflow for implementing new features during MVP development
**Version:** 1.0 (MVP-focused)
**Target:** 80% solution fast, industry-standard patterns

---

## Phase 1: Planning (AI + User)

### AI Actions
1. **Understand Requirements**
   - Read user request carefully
   - Ask clarifying questions if ambiguous
   - Identify if backend, frontend, or both needed

2. **Generate Architecture Plan**
   - Propose component structure
   - Identify file locations (follow existing patterns)
   - List dependencies needed
   - Estimate complexity (Simple / Medium / Complex)

3. **Create Feature Plan Document**
   - Save to `.dev/roadmap/features/[feature-name].md`
   - Include: Overview, Files to create/modify, Dependencies, Tests needed
   - Share plan with user for approval

### User Actions
- [ ] Review architecture plan
- [ ] Approve or request changes
- [ ] Confirm priority (can delay if not MVP-critical)

### Output
- Feature plan document created
- User approval received
- Ready to implement

---

## Phase 2: Implementation (AI)

### Step 0: Git Branch Setup (OBLIGATOIRE)

**AVANT tout code, créer une branche de feature:**

```bash
# 1. Vérifier branche actuelle
git branch --show-current

# 2. Si sur main → Créer branche
git checkout main
git pull origin main
git checkout -b feat/<feature-name>

# 3. Confirmer
echo "Développement sur: $(git branch --show-current)"
```

**Convention de nommage:**
- Feature: `feat/<feature-name>` (ex: `feat/csv-import`)
- Bug fix: `fix/<bug-name>` (ex: `fix/login-404`)
- Refactor: `refactor/<description>` (ex: `refactor/api-structure`)

**⚠️ NE JAMAIS coder directement sur `main`!**

---

### Backend Implementation (if needed)

**Step 1: Database Model (if new)**
```python
# Location: apps/synapse/backend/app/models/[model_name].py
# Pattern: Follow existing models (models.py, cables.py, etc.)
# Requirements:
- Multi-tenancy (project_id column)
- UUID primary keys
- Timestamps (created_at, updated_at)
- Relationships properly defined
```

**Step 2: Pydantic Schemas**
```python
# Location: apps/synapse/backend/app/schemas/[schema_name].py
# Pattern: Request + Response models
# Requirements:
- serialize_by_alias = True
- Type hints on all fields
- Validation rules
```

**Step 3: API Endpoint**
```python
# Location: apps/synapse/backend/app/routers/[resource].py
# Pattern: Follow cables.py or assets.py
# Requirements:
- Multi-tenancy filter (project_id from X-Project-ID header)
- JWT authentication (current_user dependency)
- Type hints on all parameters and returns
- Error handling (custom exceptions)
- Logging (request/response to Loki)
- Trailing slash on collections
```

**Step 4: Service Layer (if complex logic)**
```python
# Location: apps/synapse/backend/app/services/[service_name].py
# Pattern: Follow rule_engine.py patterns
# Requirements:
- Separate business logic from routing
- Type hints
- Error handling
```

**Step 5: Alembic Migration**
```bash
# Command: docker exec synapse-backend-1 alembic revision -m "add [feature] table"
# Pattern: Never manual SQL, always Alembic
# Requirements:
- Upgrade AND downgrade functions
- Test migration before committing
```

**Step 6: Backend Tests**
```python
# Location: apps/synapse/backend/tests/test_[feature].py
# Pattern: pytest with fixtures
# Requirements:
- Test all endpoints (CRUD if applicable)
- Test multi-tenancy filtering
- Test error cases
- Coverage > 70%
```

### Frontend Implementation (if needed)

**Step 1: Type Definitions**
```typescript
# Location: apps/synapse/frontend/src/types/[feature].ts
# Pattern: Mirror backend Pydantic models
# Requirements:
- Interface for API responses
- Strict types (no 'any')
```

**Step 2: API Service**
```typescript
# Location: apps/synapse/frontend/src/services/[feature]Service.ts
# Pattern: Follow existing services (axiosConfig.ts patterns)
# Requirements:
- Include headers (Authorization, X-Project-ID)
- Trailing slash on collection URLs
- Error handling
- TypeScript return types
```

**Step 3: Zustand Store (if state needed)**
```typescript
# Location: apps/synapse/frontend/src/stores/use[Feature]Store.ts
# Pattern: Follow useAuthStore, useAppStore patterns
# Requirements:
- Type-safe state
- Actions for CRUD operations
- Loading/error states
```

**Step 4: React Component**
```typescript
# Location (choose appropriate):
- components/ui/          # Shadcn base components
- components/layout/      # Layout containers
- components/domain/      # Business components (reusable)
- components/features/    # Feature-specific

# Pattern: Follow existing components
# Requirements:
- TypeScript strict mode
- Props interface with JSDoc
- Shadcn/ui for UI elements
- TailwindCSS for styling (VSCode dark theme)
- Loading states
- Error boundaries
- No modals/popups (use pages, panels, inline)
```

**Step 5: Frontend Tests**
```typescript
# Location: apps/synapse/frontend/src/[component-path]/[Component].test.tsx
# Pattern: Vitest + Testing Library
# Requirements:
- Test rendering
- Test user interactions
- Test error states
- Coverage > 70%
```

### Auto-Run Tests
```bash
# Backend
cd apps/synapse/backend
pytest tests/test_[feature].py --alluredir=allure-results

# Frontend
cd apps/synapse/frontend
npm run test -- [Component].test.tsx
```

### Output
- Code committed to feature branch
- Tests run automatically (GitHub Actions if setup)
- Results logged to `.dev/testing/test-status.md`

---

## Phase 3: Validation (User)

### AI Actions
1. **Update Test Status**
   - Update `.dev/testing/test-status.md`
   - Mark auto tests (✅ if passed, ❌ if failed)
   - Mark manual tests as ⚠️ (requires user validation)

2. **Create Validation Checklist**
   - List manual tests to perform
   - Include edge cases to try
   - Note performance expectations

### User Actions
- [ ] **Functional Test:** Does feature work as expected?
- [ ] **Visual Test:** Does UI look correct?
- [ ] **Edge Cases:** Try to break it
- [ ] **Performance:** Is it responsive? (no lag)

### If Pass:
1. Update `.dev/testing/test-status.md` (Manual Test → ✅ VALIDATED)
2. Update `.dev/journal/[today].md` (log completion)
3. Signal AI to proceed to Phase 4

### If Fail:
1. Update `.dev/testing/test-status.md` (Manual Test → ❌ BLOCKED)
2. Create issue in `.dev/issues/[feature-name]-issue.md` with details:
   - What failed
   - Expected behavior
   - Actual behavior
   - Screenshots/logs if applicable
3. AI fixes based on feedback
4. Repeat Phase 2

---

## Phase 4: Documentation (AI)

### Update Documentation
1. **CHANGELOG.md**
   ```markdown
   ### [Unreleased]
   #### Added
   - [Brief description of feature]
   ```

2. **Feature Documentation** (if user-facing)
   - Location: `docs/user-guide/[feature].md`
   - Include: Screenshots, usage examples, limitations

3. **API Documentation** (if new endpoints)
   - FastAPI auto-generates from docstrings
   - Ensure docstrings are complete

### Git Commit (Conventional Commits)
```bash
# Format: <type>: <subject>
# Types: feat, fix, docs, refactor, test, chore

git add .
git commit -m "feat: implement [feature name]

- Backend: [list changes]
- Frontend: [list changes]
- Tests: [coverage %]

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 5: Integration (Auto)

### Pre-Commit (Husky - if setup)
- Run lint-staged
- Run quick tests
- Check TypeScript types

### CI Pipeline (GitHub Actions - if setup)
- Run full backend tests (pytest)
- Run full frontend tests (vitest)
- Upload Allure results
- Check coverage (>70% required)

### Semantic Release (if setup)
- Detects conventional commit
- Auto-bumps version (feat: minor, fix: patch)
- Updates CHANGELOG.md
- Creates git tag

### Deployment (future)
- Deploy to staging (Proxmox)
- Smoke tests

---

## Workflow Decision Tree

**Is this a new feature?**
- Yes → Use this workflow
- No (bug fix) → Use simplified flow (skip planning, focus on fix)

**Is this MVP-critical?**
- Yes → High priority, follow all phases
- No → Defer to backlog

**Backend or Frontend?**
- Backend only → Skip frontend steps
- Frontend only → Skip backend steps
- Both → Complete both sections

**Complex or Simple?**
- Complex (>3 files, new patterns) → Full planning phase
- Simple (1-2 files, existing patterns) → Quick approval, implement

---

## Example Usage

**User Request:** "Add CSV import for BBA data"

**Phase 1 (Planning):**
- AI: "This requires backend endpoint (POST /api/v1/import/csv), CSV parser, Alembic migration (import_log table), frontend upload component (CSVImportPanel.tsx). Estimated complexity: Medium. Proceed?"
- User: "Yes, proceed"

**Phase 2 (Implementation):**
- AI: Creates endpoint, parser, migration, component, tests
- AI: Runs pytest and vitest
- AI: Updates test-status.md (Auto Test: ✅, Manual Test: ⚠️)

**Phase 3 (Validation):**
- User: Tests CSV import with real BBA.csv (100 instruments)
- User: Verifies project_id filtering, error handling, progress bar
- User: Updates test-status.md (Manual Test: ✅ VALIDATED)

**Phase 4 (Documentation):**
- AI: Updates CHANGELOG.md
- AI: Git commit: "feat: implement CSV import for BBA data"

**Phase 5 (Integration):**
- Husky: Runs pre-commit tests (pass)
- GitHub Actions: Runs CI pipeline (pass)
- Semantic Release: Bumps version to v0.2.3

**Result:** Feature complete, tested, documented, integrated

---

## Checklist Template

Copy this to feature plan document:

```markdown
## Implementation Checklist

### Backend
- [ ] Database model created (if needed)
- [ ] Alembic migration created
- [ ] Pydantic schemas created
- [ ] API endpoint implemented
- [ ] Service layer implemented (if needed)
- [ ] Tests written (>70% coverage)
- [ ] Tests passing

### Frontend
- [ ] Type definitions created
- [ ] API service created
- [ ] Zustand store created (if needed)
- [ ] Component implemented
- [ ] Tests written (>70% coverage)
- [ ] Tests passing

### Documentation
- [ ] CHANGELOG.md updated
- [ ] Feature docs created (if user-facing)
- [ ] API docstrings complete

### Validation
- [ ] Auto tests passing
- [ ] Manual validation complete
- [ ] Edge cases tested
- [ ] Performance acceptable

### Integration
- [ ] Conventional commit created
- [ ] CI pipeline passing
- [ ] Version bumped (auto)
```

---

**Version:** 1.0
**Last Updated:** 2025-11-25
**Next Review:** After MVP Week 1 completion
