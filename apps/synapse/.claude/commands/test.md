# SYNAPSE Test Command

This is an app-specific command that overrides the root `/test` command.
It runs SYNAPSE-specific test suites.

---

## What to do

Run the complete SYNAPSE test suite:

1. **Backend tests:**
   ```bash
   cd apps/synapse/backend
   pytest tests/ -v --cov=app
   ```

2. **Frontend tests:**
   ```bash
   cd apps/synapse/frontend
   npm run test
   ```

3. **Type checking:**
   ```bash
   cd apps/synapse/frontend
   npm run type-check
   ```

4. **Linting:**
   ```bash
   cd apps/synapse/backend
   ruff check app/ tests/

   cd apps/synapse/frontend
   npm run lint
   ```

Report results in this format:

```yaml
test_results:
  backend:
    pytest: PASS/FAIL
    coverage: XX%
    errors: []
  frontend:
    vitest: PASS/FAIL
    coverage: XX%
    errors: []
  lint:
    ruff: PASS/FAIL
    eslint: PASS/FAIL
```
