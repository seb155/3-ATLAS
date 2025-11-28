# Automated Testing Guide

**Purpose**: Comprehensive guide to testing strategies for SYNAPSE

---

## Overview

SYNAPSE uses a modern testing stack:
- **Backend**: pytest + pytest-asyncio + pytest-cov
- **Frontend**: Vitest (planned) + @testing-library/react
- **E2E**: Playwright (future)

---

## Backend Testing (pytest)

### Setup

**Install Dependencies**:
```bash
pip install pytest pytest-asyncio pytest-cov
```

Already in `requirements.txt`:
```txt
pytest==9.0.1
pytest-asyncio==1.3.0
pytest-cov==6.0.0
```

---

### Running Tests

**All tests**:
```bash
# From backend directory
pytest

# Docker
docker exec synapse-backend pytest
```

**Specific file**:
```bash
pytest tests/test_workflow_engine.py
```

**With verbose output**:
```bash
pytest -v
```

**With coverage**:
```bash
pytest --cov=app --cov-report=html
```

**Watch mode** (re-run on file change):
```bash
pytest-watch
```

---

### Writing Tests

#### Test Structure

```python
import pytest
from app.services.my_service import my_function

@pytest.mark.asyncio
async def test_my_async_function():
    """Test description"""
    # Arrange
    input_data = {"key": "value"}
    
    # Act
    result = await my_function(input_data)
    
    # Assert
    assert result["status"] == "success"
```

#### Fixtures

Reusable test setup:

```python
@pytest.fixture
def sample_data():
    """Provide sample data for tests"""
    return {
        "user_id": "123",
        "name": "Test User"
    }

def test_with_fixture(sample_data):
    assert sample_data["user_id"] == "123"
```

#### Async Tests

Use `@pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_workflow_execution():
    workflow_id = workflow_engine.start_workflow("TEST", {})
    await workflow_engine.execute_workflow(workflow_id)
    assert workflow_id in results
```

#### Mocking

Mock external dependencies:

```python
# Mock WebSocket logger
class MockLogger:
    logs = []
    
    @staticmethod
    def log(data):
        MockLogger.logs.append(data)

@pytest.fixture
def mock_logger(monkeypatch):
    monkeypatch.setattr('app.services.action_logger.websocket_logger', MockLogger)
    yield
    MockLogger.logs = []
```

---

### Best Practices

#### 1. Test Organization

```
tests/
├── test_action_logger.py      # Unit tests for ActionLogger
├── test_workflow_engine.py    # Unit tests for WorkflowEngine
├── test_api_endpoints.py      # Integration tests for API
└── fixtures/
    └── conftest.py           # Shared fixtures
```

#### 2. Naming Convention

- Test files: `test_*.py`
- Test functions: `test_<what_it_tests>`
- Fixtures: `<resource>_fixture` or just `<resource>`

#### 3. AAA Pattern

```python
def test_action_completion():
    # Arrange: Set up test data
    action_id = action_logger.start_action("TEST", "Summary")
    
    # Act: Execute the function
    action_logger.complete_action(action_id, stats={"items": 10})
    
    # Assert: Verify results
    assert action_id not in action_logger.active_actions
```

#### 4. One Assertion Per Concept

```python
# ✅ Good: Clear, focused test
def test_workflow_starts():
    workflow_id = workflow_engine.start_workflow("TEST", {})
    assert workflow_id is not None

def test_workflow_creates_jobs():
    workflow_id = workflow_engine.start_workflow("TEST", {})
    assert len(workflow_engine.get_jobs(workflow_id)) > 0

# ❌ Bad: Multiple unrelated assertions
def test_workflow():
    workflow_id = workflow_engine.start_workflow("TEST", {})
    assert workflow_id is not None
    assert len(workflow_engine.get_jobs(workflow_id)) > 0
    assert workflow_engine.get_status(workflow_id) == "RUNNING"
```

---

## Frontend Testing (Vitest)

### Setup

**Install Dependencies**:
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

**Config** (`vitest.config.ts`):
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
})
```

---

### Running Tests

```bash
# Run all tests
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage

# UI mode (interactive)
npm run test:ui
```

---

### Writing Tests

#### Component Test

```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TimelinePanel } from './TimelinePanel'

describe('TimelinePanel', () => {
  it('renders workflows', () => {
    const workflows = [
      { id: '1', summary: 'Import Gold Mine', status: 'COMPLETED' }
    ]
    
    render(<TimelinePanel workflows={workflows} />)
    
    expect(screen.getByText('Import Gold Mine')).toBeInTheDocument()
  })
  
  it('expands workflow on click', async () => {
    const { user } = render(<TimelinePanel workflows={workflows} />)
    
    await user.click(screen.getByText('Import Gold Mine'))
    
    expect(screen.getByText('Job 1')).toBeVisible()
  })
})
```

#### Hook Test

```typescript
import { renderHook, act } from '@testing-library/react'
import { useDevConsole } from './useDevConsole'

describe('useDevConsole', () => {
  it('filters logs by level', () => {
    const { result } = renderHook(() => useDevConsole())
    
    act(() => {
      result.current.setFilter('level', 'ERROR')
    })
    
    expect(result.current.filteredLogs).toHaveLength(0)
  })
})
```

---

## Test Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| Services (ActionLogger, WorkflowEngine) | 90%+ |
| API Endpoints | 80%+ |
| UI Components | 70%+ |
| Utilities | 95%+ |

**Check Coverage**:
```bash
# Backend
pytest --cov=app --cov-report=term-missing

# Frontend
npm run test:coverage
```

---

## CI/CD Integration

### GitHub Actions (Example)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm run test:coverage
```

---

## Debugging Tests

### Backend (pytest)

**Print debugging**:
```python
def test_something():
    result = my_function()
    print(f"Result: {result}")  # Will show in test output
    assert result == expected
```

**PDB (Python Debugger)**:
```python
def test_something():
    import pdb; pdb.set_trace()  # Breakpoint
    result = my_function()
    assert result == expected
```

**Verbose assertions**:
```bash
pytest -vv  # Very verbose
```

---

### Frontend (Vitest)

**Debug renders**:
```typescript
import { screen, debug } from '@testing-library/react'

it('renders component', () => {
  render(<MyComponent />)
  screen.debug()  # Prints DOM to console
})
```

**VS Code Debugging**:
Add to `.vscode/launch.json`:
```json
{
  "type": "node",
  "request": "launch",
  "name": "Debug Vitest Tests",
  "runtimeExecutable": "npm",
  "runtimeArgs": ["run", "test:debug"],
  "console": "integratedTerminal"
}
```

---

## Common Patterns

### Testing Async Operations

```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await async_function()
    assert result is not None
```

### Testing Error Handling

```python
def test_error_handling():
    with pytest.raises(ValueError, match="Invalid input"):
        my_function(invalid_data)
```

### Testing API Endpoints

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_assets():
    response = client.get("/api/v1/assets")
    assert response.status_code == 200
    assert len(response.json()) > 0
```

---

## Example: Complete Test File

```python
# File: tests/test_workflow_engine.py

import pytest
from app.services.action_logger import action_logger
from app.services.workflow_engine import workflow_engine

# Mock setup
mock_logs = []

def mock_websocket_log(log_dict):
    mock_logs.append(log_dict)

class MockWebSocketLogger:
    log = staticmethod(mock_websocket_log)

@pytest.fixture(autouse=True)
def setup_mocks():
    global mock_logs
    mock_logs = []
    
    import app.services.action_logger as action_logger_module
    action_logger_module.websocket_logger = MockWebSocketLogger
    
    action_logger.active_actions = {}
    yield
    mock_logs = []

@pytest.mark.asyncio
async def test_action_logger_lifecycle():
    """Test full lifecycle: Start -> Log -> Complete"""
    # Start
    action_id = action_logger.start_action("TEST", "Test Action")
    assert len(mock_logs) == 1
    
    # Log step
    action_logger.log_step(action_id, "Step 1")
    assert len(mock_logs) == 2
    
    # Complete
    action_logger.complete_action(action_id, stats={"items": 10})
    assert len(mock_logs) == 3
    assert mock_logs[2]["actionStatus"] == "COMPLETED"

@pytest.mark.asyncio
async def test_workflow_execution():
    """Test workflow with multiple jobs"""
    async def job1(job_id, params):
        return {"items": 5}
    
    workflow_engine.register_template("TEST_WORKFLOW", [
        {"name": "Job 1", "function": job1}
    ])
    
    workflow_id = workflow_engine.start_workflow("TEST_WORKFLOW", "Test", {})
    await workflow_engine.execute_workflow(workflow_id)
    
    assert mock_logs[-1]["actionStatus"] == "COMPLETED"
```

---

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Vitest Guide](https://vitest.dev/guide/)
- [Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

**Last Updated**: 2025-11-24
