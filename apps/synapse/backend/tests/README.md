# Backend Tests

Quick reference for running tests in SYNAPSE backend.

## Quick Start

```bash
# Run all tests
docker exec synapse-backend pytest

# Run with verbose output
docker exec synapse-backend pytest -v

# Run specific test file
docker exec synapse-backend pytest tests/test_workflow_engine.py

# Run with coverage
docker exec synapse-backend pytest --cov=app --cov-report=html
```

## Test Files

- `test_workflow_engine.py` - Tests for ActionLogger and WorkflowEngine
- `test_rules.py` - Rule engine tests
- `test_import.py` - Import functionality tests
- `test_export.py` - Export functionality tests

## Writing New Tests

See [`docs/developer-guide/08-testing.md`](../../docs/developer-guide/08-testing.md) for comprehensive guide.

**Quick template**:

```python
import pytest
from app.services.my_service import my_function

@pytest.mark.asyncio
async def test_my_feature():
    """Test description"""
    # Arrange
    input_data = {"key": "value"}
    
    # Act
    result = await my_function(input_data)
    
    # Assert
    assert result["status"] == "success"
```

## Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Services | 90%+ | - |
| API Endpoints | 80%+ | - |
| Utilities | 95%+ | - |

Run `pytest --cov` to check current coverage.

## CI/CD

Tests run automatically on:
- Every commit (GitHub Actions - planned)
- Before deployment

## Troubleshooting

**Tests not found?**
```bash
# Make sure you're in the right directory
cd apps/synapse/backend
pytest
```

**Import errors?**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**Async warnings?**
- Make sure to use `@pytest.mark.asyncio` for async tests
- Check that pytest-asyncio is installed

---

**Full Documentation**: [`docs/developer-guide/08-testing.md`](../../docs/developer-guide/08-testing.md)
