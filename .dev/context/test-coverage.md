# Test Coverage Status

**Last Updated**: 2025-11-24  
**SYNAPSE Version**: v0.2.1

---

## Coverage Summary

| Layer | Tests | Coverage | Status |
|-------|-------|----------|--------|
| **Backend** | ✅ 3 tests | **8%** overall | 🟡 In Progress |
| **Frontend** | ✅ Setup | **0%** | 🟡 Partial |
| **E2E** | ❌ Not Setup | **0%** | 🔴 None |

**Note**: Backend coverage is 8% overall, but new services (WorkflowEngine, ActionLogger) have 78-90% coverage.

---

## Backend Tests (pytest)

### Status: 🟢 **ACTIVE**

**Framework**: pytest + pytest-asyncio + pytest-cov  
**Location**: `apps/synapse/backend/tests/`  
**Run**: `docker exec synapse-backend pytest -v`

#### Test Files

| File | Tests | Status | Coverage | Notes |
|------|-------|--------|----------|-------|
| `test_workflow_engine.py` | 3 | ✅ PASSING | - | ActionLogger, WorkflowEngine |
| `test_rules.py` | - | ✅ PASSING | - | Rule engine (existing) |
| `test_import.py` | - | ✅ PASSING | - | Import functionality (existing) |
| `test_export.py` | - | ✅ PASSING | - | Export functionality (existing) |
| `test_validation.py` | - | ✅ PASSING | - | Data validation (existing) |
| `test_rbac.py` | - | ✅ PASSING | - | Role-based access (existing) |
| `test_audit.py` | - | ✅ PASSING | - | Audit logging (existing) |
| `test_phase2_rules.py` | - | ✅ PASSING | - | Phase 2 rules (existing) |

#### Coverage Goals

| Component | Target | Current | Status |
|-----------|--------|---------|--------|
| ActionLogger | 90% | **78%** | 🟡 Good Progress |
| WorkflowEngine | 90% | **90%** | 🟢 Goal Met! |
| WebSocketManager | 85% | **39%** | 🔴 Needs Work |
| API Endpoints | 80% | **0%** | 🔴 None |
| Database Models | 85% | **0%** | 🔴 None |
| Utilities | 95% | **0%** | 🔴 None |
| **Overall App** | **80%** | **8%** | 🔴 Early Stage |

**Last Coverage Run**: 2025-11-24

**Notes**:
- WorkflowEngine has excellent coverage (90%) ✅
- ActionLogger coverage is good but needs improvement (78%)
- WebSocketManager is mocked in tests, needs dedicated tests
- Most of the app (models, API, core) has no tests yet

**Check Coverage**:
```bash
docker exec synapse-backend pytest --cov=app --cov-report=html
```

---

## Frontend Tests (Vitest)

### Status: 🟡 **PARTIAL SETUP**

**Framework**: Vitest + @testing-library/react  
**Location**: `apps/synapse/frontend/src/test/`  
**Run**: `npm run test` (from frontend directory)

#### Test Files

| File | Tests | Status | Coverage | Notes |
|------|-------|--------|----------|-------|
| `useLogStore.test.ts` | 3 | 🟡 Example | - | Store testing example |
| `DevConsole.test.tsx` | - | ⏸ Planned | - | DevConsole V3 |
| `SmartPayloadViewer.test.tsx` | - | ⏸ Planned | - | JSON viewer |
| `TimelinePanel.test.tsx` | - | ⏸ Planned | - | Timeline component |

#### Coverage Goals

| Component | Target | Current | Status |
|-----------|--------|---------|--------|
| UI Components | 70% | 0% | 🔴 None |
| Hooks/Stores | 80% | 0% | 🔴 None |
| Utilities | 95% | 0% | 🔴 None |

**Check Coverage**:
```bash
cd apps/synapse/frontend
npm run test:coverage
```

---

## E2E Tests (Playwright)

### Status: 🔴 **NOT SETUP**

**Framework**: Playwright (installed but not configured)  
**Location**: TBD  
**Run**: TBD

#### Planned Tests

| Test Suite | Priority | Status | Notes |
|------------|----------|--------|-------|
| DevConsole Workflow | High | ⏸ Planned | Open console, filter, navigate |
| Asset CRUD | High | ⏸ Planned | Create, read, update, delete assets |
| Rule Execution | Medium | ⏸ Planned | Execute rules, verify results |
| Import/Export | Medium | ⏸ Planned | Full import/export flow |

---

## Test Automation

### CI/CD Integration

**Status**: 🔴 **NOT SETUP**

**Planned**: GitHub Actions workflow to run tests on:
- Every pull request
- Every commit to main
- Pre-deployment

**Config**: `.github/workflows/tests.yml` (to be created)

---

## Next Steps

### Immediate (Week 1)
- [x] Run initial coverage report for backend (8% overall, WorkflowEngine 90%, ActionLogger 78%)
- [ ] Add dedicated tests for WebSocketManager (currently 39%)
- [ ] Write tests for DevConsole V3 components (frontend)
- [ ] Add tests for existing API endpoints (currently 0%)

### Short Term (Month 1)
- [ ] Achieve 80%+ coverage on ActionLogger service (currently 78%)
- [ ] Add tests for Models layer (currently 0%)
- [ ] Achieve 70%+ coverage on new frontend components
- [ ] Setup GitHub Actions CI/CD

### Long Term (Quarter 1)
- [ ] Achieve 80% overall backend coverage (currently 8%)
- [ ] Setup E2E testing with Playwright
- [ ] Implement automated visual regression testing

---

## How to Update This Document

1. **After adding new tests**: Update test file tables
2. **After running coverage**: Update coverage percentages
3. **Monthly**: Review and update status indicators
4. **Before releases**: Verify all critical paths are tested

---

## Quick Commands

```bash
# Backend - Run all tests
docker exec synapse-backend pytest -v

# Backend - Coverage report
docker exec synapse-backend pytest --cov=app --cov-report=term-missing

# Frontend - Run all tests
cd apps/synapse/frontend && npm run test

# Frontend - Coverage report
cd apps/synapse/frontend && npm run test:coverage

# Frontend - Interactive UI
cd apps/synapse/frontend && npm run test:ui
```

---

**Reference**: [`docs/developer-guide/08-testing.md`](../../docs/developer-guide/08-testing.md)
