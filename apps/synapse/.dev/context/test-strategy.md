# SYNAPSE - Test Strategy

> Adapted for MBSE/Engineering application with focus on integration tests

---

## Philosophy

**"Test what matters, not everything"**

For SYNAPSE, the critical paths are:
1. **Import → Process → Export** workflow
2. **Rule Engine** reliability
3. **Data integrity** (versioning, audit)

---

## Test Pyramid (Adjusted)

```
                    ┌─────────┐
                    │  E2E    │  ← 5% (smoke tests only)
                    │  Tests  │
                   ─┴─────────┴─
                  ┌─────────────┐
                  │ Integration │  ← 60% (PRIORITY)
                  │    Tests    │
                 ─┴─────────────┴─
                ┌─────────────────┐
                │   Unit Tests    │  ← 35% (critical logic only)
                └─────────────────┘
```

---

## Backend Tests

### Priority 1: Integration Tests (API)

```bash
# Run all integration tests
pytest tests/test_integration/ -v

# Test import workflow
pytest tests/test_integration/test_import_workflow.py

# Test rule engine
pytest tests/test_integration/test_rule_engine.py
```

**What to test:**
- Full import → rules → export workflow
- Rule engine with different rule types
- Asset versioning and rollback
- Package generation

### Priority 2: Service Tests

```bash
# Test specific services
pytest tests/test_services/ -v
```

**Critical services to test:**
- `rule_engine.py` - Rule evaluation
- `rule_execution_service.py` - CREATE_* actions
- `workflow_logger.py` - Event sourcing
- `template_service.py` - Excel generation

### Priority 3: Unit Tests

```bash
# Unit tests for utilities
pytest tests/test_utils/ -v
```

**What to unit test:**
- Cable sizing calculations
- Validation helpers
- Data transformers

---

## Frontend Tests

### Smoke Tests Only

```bash
# Run frontend tests
npm run test

# With coverage
npm run test:coverage
```

**What to test:**
- Components render without crashing
- Critical user flows (happy path)

**What NOT to test:**
- Every component variation
- CSS/styling
- Third-party library internals

---

## Coverage Targets

| Layer | Target | Rationale |
|:------|:------:|:----------|
| Backend Integration | 70% | Critical path coverage |
| Backend Services | 60% | Core business logic |
| Backend Utils | 50% | Helper functions |
| Frontend | 40% | Smoke tests sufficient |
| **Overall** | **60%** | Balanced for MVP |

---

## Test Commands Quick Reference

```bash
# === BACKEND ===

# All tests
cd apps/synapse/backend
pytest

# With coverage
pytest --cov=app --cov-report=html

# Single test file
pytest tests/test_rules.py

# Single test by name
pytest -k "test_create_motor"

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# === FRONTEND ===

# All tests
cd apps/synapse/frontend
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage

# Single file
npm run test -- DevConsole
```

---

## CI/CD Integration

```yaml
# .github/workflows/test.yml (example)
test-backend:
  - pytest --cov=app --cov-fail-under=60

test-frontend:
  - npm run test:coverage
```

---

## Demo Validation Tests

For the December 20 demo, these tests MUST pass:

- [ ] `test_import_csv_workflow` - Import 100 instruments
- [ ] `test_rule_create_motor` - Create motors for pumps
- [ ] `test_rule_create_cable` - Create cables with sizing
- [ ] `test_export_in_p040` - Generate Instrument Index
- [ ] `test_export_ca_p040` - Generate Cable Schedule
- [ ] `test_audit_trail` - Verify traceability

---

*Strategy aligned with owner preference: integration-focused testing*
