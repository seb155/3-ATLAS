# Testing with ReportPortal

**ReportPortal** is a centralized test reporting dashboard with AI-powered analytics for test execution tracking, flaky test detection, and historical trend analysis.

---

## Quick Access

**UI:** http://localhost:8080
**Default Login:** `default` / `superadmin` / `erebus`
**RabbitMQ Management:** http://localhost:15672 (rabbitmq / rabbitmq)
**OpenSearch:** http://localhost:9200

---

## Architecture

ReportPortal is integrated into the `workspace/` infrastructure:

```
workspace/docker-compose.yml
├── reportportal-rabbitmq      (Message queue)
├── reportportal-opensearch    (Search/analytics engine)
├── reportportal-migrations    (Database schema)
├── reportportal-api           (Backend API)
├── reportportal-ui            (Web interface)
├── reportportal-analyzer      (ML flaky test detection)
└── reportportal-jobs          (Background tasks)
```

**Database:** Shares `forge-postgres` (database: `reportportal`)

---

## Resource Requirements

**RAM:** ~4-6 GB total
- OpenSearch: ~512MB-1GB
- API: ~1GB
- Analyzer: ~512MB
- Other services: ~1GB combined

**Disk:** ~10-20 GB (30 days history)

**Startup Time:** ~2-3 minutes (first time)

---

## Backend Testing (pytest)

### Setup

1. **Install dependencies:**
   ```bash
   cd apps/synapse/backend
   docker exec -it synapse-backend pip install -r requirements.txt
   ```

2. **Get API token:**
   - Login to ReportPortal: http://localhost:8080
   - Go to: Profile (top-right) → API Keys
   - Copy your token

3. **Run tests with ReportPortal:**
   ```bash
   # Using default project config
   pytest --reportportal

   # With custom token (recommended for CI/CD)
   export RP_UUID="your-api-token"
   pytest --reportportal
   ```

### Configuration

**File:** `apps/synapse/backend/pytest.ini`

```ini
[reportportal]
rp_endpoint = http://localhost:8080
rp_project = synapse
rp_launch_name = SYNAPSE Backend Tests
rp_launch_description = Automated backend tests for SYNAPSE platform
rp_launch_attributes = backend python fastapi
```

**Environment Variables (optional):**
```bash
export RP_UUID="your-api-token"       # API key
export RP_LAUNCH="Custom Launch Name" # Override launch name
export RP_LAUNCH_DESCRIPTION="..."    # Override description
```

---

## Frontend E2E Testing (Playwright)

### Setup

1. **Install dependencies:**
   ```bash
   cd apps/synapse/frontend
   npm install
   ```

2. **Run tests with ReportPortal:**
   ```bash
   # Enable ReportPortal via environment variable
   RP_ENABLED=true npx playwright test

   # With custom token
   RP_ENABLED=true RP_TOKEN="your-api-token" npx playwright test

   # Without ReportPortal (default HTML reporter)
   npx playwright test
   ```

### Configuration

**File:** `apps/synapse/frontend/playwright.config.ts`

The config automatically detects `RP_ENABLED` environment variable:
- `RP_ENABLED=true` → Reports to ReportPortal + HTML
- Not set → HTML only (default)

**Default Token:** Uses superadmin token (hard-coded for dev)
**Production:** Set `RP_TOKEN` environment variable

---

## Frontend Unit Tests (Vitest)

**Note:** ReportPortal does NOT have official Vitest support yet.

**Workaround Options:**
1. **Use built-in reporters** (recommended for now):
   ```bash
   npm run test          # Default reporter
   npm run test:ui       # Visual UI
   npm run test:coverage # Coverage report
   ```

2. **Export to JUnit XML** → Import to ReportPortal manually:
   ```bash
   # Add to vitest.config.ts
   reporters: ['default', 'junit']
   outputFile: './test-results/junit.xml'
   ```

3. **Future:** Watch for `@reportportal/agent-js-vitest` package

---

## First Time Setup

### 1. Start ReportPortal

```powershell
# Start all services (including ReportPortal)
.\dev.ps1
```

Wait ~2-3 minutes for all services to be healthy.

### 2. Initial Login

1. Navigate to: http://localhost:8080
2. Login with:
   - **Project:** `default`
   - **Login:** `superadmin`
   - **Password:** `erebus`

### 3. Create SYNAPSE Project

1. Click **Administration** (top menu)
2. Click **Projects** → **Add New Project**
3. Fill in:
   - **Project Name:** `synapse`
   - **Project Type:** Internal
   - **Description:** SYNAPSE MBSE Platform Tests
4. Click **Add**

### 4. Get Your API Token

1. Click your profile (top-right) → **Profile**
2. Go to **API Keys** tab
3. Click **Generate API Key**
4. Copy and save the token

### 5. Update Backend Config (Optional)

If you want to use your personal token instead of default:

```bash
# Add to .env or export
export RP_UUID="your-copied-token"
```

---

## Running Tests

### Backend (pytest)

```bash
# Terminal 1: Ensure backend is running
cd apps/synapse
docker-compose -f docker-compose.dev.yml up

# Terminal 2: Run tests
cd apps/synapse/backend
docker exec -it synapse-backend pytest --reportportal
```

**View Results:**
1. Go to http://localhost:8080
2. Click **Launches** (left menu)
3. Select your launch: "SYNAPSE Backend Tests"

### Frontend E2E (Playwright)

```bash
# Terminal 1: Ensure frontend is running
cd apps/synapse
docker-compose -f docker-compose.dev.yml up

# Terminal 2: Run E2E tests
cd apps/synapse/frontend
RP_ENABLED=true npx playwright test
```

**View Results:**
1. Go to http://localhost:8080
2. Click **Launches** (left menu)
3. Select your launch: "SYNAPSE E2E Tests"

---

## Understanding ReportPortal UI

### Dashboard

**Widgets:**
- **Launch Statistics:** Pass/fail rates over time
- **Failed Cases Trend:** Track flaky tests
- **Test Cases Growth:** Total test count
- **Passing Rate:** Success percentage

### Launches

**Launch:** A single test execution (e.g., "SYNAPSE Backend Tests - 2025-11-24 14:30")

**Attributes:**
- Filter by: `backend`, `frontend`, `python`, `playwright`
- Custom tags from your tests

**Actions:**
- View logs and screenshots
- Compare runs
- Mark as baseline
- Export to PDF

### Filters

Create custom filters:
```
Example: Failed Backend Tests (Last 7 Days)
- Attribute: backend
- Status: Failed
- Date: Last 7 days
```

### Auto-Analyzer

**Purpose:** ML-powered detection of:
- Flaky tests (pass/fail randomly)
- Similar failures (group by root cause)
- Known issues (match to existing bugs)

**Activation:**
1. Go to **Project Settings** → **Auto-Analysis**
2. Enable **Auto-Analysis Mode**
3. Select **Strategy:** Recommend "All launches"

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests with ReportPortal

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start ReportPortal
        run: docker-compose -f workspace/docker-compose.yml up -d
      - name: Wait for ReportPortal
        run: |
          timeout 300 bash -c 'until curl -f http://localhost:8080; do sleep 5; done'
      - name: Run Backend Tests
        env:
          RP_UUID: ${{ secrets.RP_API_TOKEN }}
        run: |
          cd apps/synapse/backend
          pytest --reportportal

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start ReportPortal
        run: docker-compose -f workspace/docker-compose.yml up -d
      - name: Install dependencies
        run: cd apps/synapse/frontend && npm ci
      - name: Run E2E Tests
        env:
          RP_ENABLED: true
          RP_TOKEN: ${{ secrets.RP_API_TOKEN }}
        run: cd apps/synapse/frontend && npx playwright test
```

**Secrets to add:**
- `RP_API_TOKEN`: Your ReportPortal API key

---

## Troubleshooting

### ReportPortal UI not loading

```bash
# Check service health
docker ps --filter "name=reportportal"

# Check logs
docker logs reportportal-ui
docker logs reportportal-api
docker logs reportportal-opensearch

# Common issue: OpenSearch needs more memory
# Edit workspace/docker-compose.yml:
#   OPENSEARCH_JAVA_OPTS: "-Xms1g -Xmx1g"  # Increase if you have RAM
```

### Pytest not sending to ReportPortal

```bash
# Verify pytest-reportportal is installed
docker exec -it synapse-backend pip show pytest-reportportal

# Check network connectivity
docker exec -it synapse-backend curl http://reportportal-ui:8080

# Enable debug logging
pytest --reportportal -o log_cli=true -o log_cli_level=DEBUG
```

### Playwright tests not appearing

```bash
# Verify reporter is installed
cd apps/synapse/frontend
npm list @reportportal/agent-js-playwright

# Check environment variable
echo $RP_ENABLED  # Should be "true"

# Test API connectivity
curl http://localhost:8080/api/v1/synapse
```

### OpenSearch failing to start

```powershell
# Windows/WSL2: Increase vm.max_map_count
wsl -d docker-desktop
sysctl -w vm.max_map_count=262144

# Or add to Docker Desktop settings:
# Settings → Resources → WSL Integration → Advanced
```

### Database migration errors

```bash
# Reset ReportPortal database
docker exec -it forge-postgres psql -U postgres -c "DROP DATABASE reportportal;"
docker exec -it forge-postgres psql -U postgres -c "CREATE DATABASE reportportal;"

# Restart migrations
docker-compose -f workspace/docker-compose.yml restart reportportal-migrations
```

---

## Cleanup & Maintenance

### Disk Space Management

ReportPortal stores **all test runs** indefinitely by default.

**Clean old launches:**
1. Go to **Launches**
2. Filter by date: `> 30 days ago`
3. Select all → **Actions** → **Delete**

**Auto-cleanup (Recommended):**
1. Go to **Project Settings** → **General**
2. Set **Keep launches:** `30 days`
3. Set **Keep logs:** `15 days`
4. Click **Save**

### Full Reset

```bash
# Stop all services
docker-compose -f workspace/docker-compose.yml down

# Remove volumes (WARNING: deletes ALL data)
docker volume rm workspace_rabbitmq-data
docker volume rm workspace_opensearch-data
docker volume prune

# Restart
.\dev.ps1
```

---

## Resources

**Official Docs:** https://reportportal.io/docs
**API Docs:** http://localhost:8080/api
**GitHub:** https://github.com/reportportal

**Integrations:**
- pytest-reportportal: https://github.com/reportportal/agent-python-pytest
- agent-js-playwright: https://github.com/reportportal/agent-js-playwright

---

**Updated:** 2025-11-24
