# SYNAPSE - Test Status

> Last updated: 2025-11-30

---

## Current Coverage

| Component | Coverage | Target | Status |
|:----------|:--------:|:------:|:------:|
| Backend Integration | ~40% | 70% | 🔴 |
| Backend Services | ~50% | 60% | 🟡 |
| Backend Utils | ~30% | 50% | 🔴 |
| Frontend | ~20% | 40% | 🔴 |
| **Overall** | **~35%** | **60%** | 🔴 |

---

## Test Inventory

### Backend Tests

| Test File | Tests | Passing | Status |
|:----------|:-----:|:-------:|:------:|
| `test_rules.py` | 12 | ? | Needs run |
| `test_assets.py` | 8 | ? | Needs run |
| `test_import.py` | 5 | ? | Needs run |
| `test_workflow.py` | 6 | ? | Needs run |

### Frontend Tests

| Component | Tests | Passing | Status |
|:----------|:-----:|:-------:|:------:|
| DevConsole | 2 | ? | Needs run |
| AssetHistory | 1 | ? | Needs run |

---

## Critical Tests for Demo

| Test | Purpose | Status |
|:-----|:--------|:------:|
| Import CSV workflow | Verify import works | ⬜ TODO |
| Rule CREATE_CHILD | Verify motor creation | ⬜ TODO |
| Rule CREATE_CABLE | Verify cable creation | ⬜ TODO |
| Export IN-P040 | Verify Excel generation | ⬜ TODO |
| Export CA-P040 | Verify Excel generation | ⬜ TODO |
| Asset versioning | Verify audit trail | ⬜ TODO |

---

## Next Actions

1. [ ] Run full test suite and update status
2. [ ] Add missing integration tests
3. [ ] Fix failing tests
4. [ ] Achieve 60% coverage target

---

## Commands

```bash
# Run all tests
cd apps/synapse/backend
pytest

# With coverage report
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

*Update this file after each test run*
