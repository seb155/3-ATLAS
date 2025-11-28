# Dev Environment & Owner Portal v0.1.x

**Scope:** Developer infrastructure, Owner dashboards, analytics database  
**Goal:** Give the technical owner a clear, visual view of health, tests, tech debt, and architecture checkpoints.

---

## Overview

This roadmap covers the **developer environment** and **Owner Portal** that sit around SYNAPSE:

- A dedicated **PostgreSQL analytics database** (`synapse_analytics`) with an `owner` schema.
- Structured tables for:
  - `owner.health_scorecards`
  - `owner.test_runs`
  - `owner.tech_debt_items`
  - `owner.architecture_checkpoints`
- A new **React Owner Portal** app, exposed via Traefik, focusing on:
  - Health scorecards per version/area
  - Test status and trends
  - Tech debt and review items
  - Architecture checkpoints timeline

---

## Version Map (Owner Environment)

- **v0.1.0 – Analytics DB Foundation**
- **v0.1.1 – Health Scorecards & Test Runs**
- **v0.1.2 – Tech Debt & Architecture Checkpoints**
- **v0.1.3 – Owner Portal React v1 (Read-Only)**
- **v0.1.4 – Owner Portal React v2 (Advanced UI)**

Target dates can be aligned with core platform versions (v0.2.x), but this stream is independent.

---

## v0.1.0 – Analytics DB Foundation

**Target:** TBA  
**Priority:** HIGH – base for all Owner dashboards

### Scope

- Create dedicated **PostgreSQL database**: `synapse_analytics`.
- Create **schema**: `owner`.
- Create base tables:
  - `owner.health_scorecards`
  - `owner.test_runs`
  - `owner.tech_debt_items`
  - `owner.architecture_checkpoints`
- Configure connections so:
  - Backend services (FastAPI) can read/write.
  - Grafana can read for dashboards.
  - CLI tools / AI scripts can write data via `psql` or simple scripts.

### Data Model (Initial Draft)

```sql
-- In database: synapse_analytics
CREATE SCHEMA IF NOT EXISTS owner;

CREATE TABLE owner.health_scorecards (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version TEXT NOT NULL,
    area TEXT NOT NULL, -- backend, frontend, infra, rule-engine, etc.
    reliability INTEGER NOT NULL,
    dx INTEGER NOT NULL,
    observability INTEGER NOT NULL,
    ux INTEGER NOT NULL,
    notes TEXT
);

CREATE TABLE owner.test_runs (
    id UUID PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    project TEXT NOT NULL,   -- synapse
    component TEXT NOT NULL, -- backend, frontend, e2e
    version TEXT NOT NULL,
    suite TEXT NOT NULL,     -- smoke, full, regression, etc.
    total INTEGER NOT NULL,
    passed INTEGER NOT NULL,
    failed INTEGER NOT NULL,
    skipped INTEGER NOT NULL,
    report_url TEXT,
    origin TEXT NOT NULL     -- ai, human, ci
);

CREATE TABLE owner.tech_debt_items (
    id UUID PRIMARY KEY,
    code TEXT NOT NULL,      -- CR-YYYYMMDD-XX
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    area TEXT NOT NULL,      -- backend, frontend, infra, docs, cross-cutting
    title TEXT NOT NULL,
    context TEXT,
    impact TEXT NOT NULL,    -- high, medium, low
    effort TEXT NOT NULL,    -- S, M, L
    risk TEXT NOT NULL,      -- high, medium, low
    type TEXT NOT NULL,      -- refactor, bug, dx, perf, arch
    status TEXT NOT NULL,    -- open, in_progress, done, wont_fix
    target_version TEXT,
    source_file TEXT         -- e.g. .dev/roadmap/backlog/core-platform-v0.2.x.md
);

CREATE TABLE owner.architecture_checkpoints (
    id UUID PRIMARY KEY,
    version TEXT NOT NULL,          -- v0.2.3, v0.3.0, etc.
    planned_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL,           -- planned, in_progress, done, skipped
    summary TEXT,
    main_risks TEXT,
    main_decisions TEXT
);
```

Indexes and constraints can be tuned later (e.g. composite indexes on `(version, area)`).

### Verification Plan

1. Start workspace Postgres (`workspace` stack).
2. Connect with `psql` to `synapse_analytics`.
3. Run the DDL above and verify tables exist.
4. Insert 1–2 sample rows in each table and query them back.

---

## v0.1.1 – Health Scorecards & Test Runs

**Target:** TBA  
**Priority:** HIGH – first visible Owner value

### Scope

- Define **standard scoring rubric** for:
  - Reliability, DX, Observability, UX (1–5 scale).
- Create simple **CLI/AI workflows**:
  - Record a health scorecard for a given version/area.
  - Record a test run summary after running backend/frontend tests.
- Connect Grafana to `synapse_analytics` and build:
  - **Health Scorecard dashboard** (per version, per area).
  - **Test Runs dashboard** (pass rate over time, by component).

### Verification Plan

1. Run at least one structured review and record a `health_scorecards` row.
2. Run backend tests and record a `test_runs` row.
3. Confirm both appear correctly in Grafana dashboards.

---

## v0.1.2 – Tech Debt & Architecture Checkpoints

**Target:** TBA  
**Priority:** MEDIUM – governance visibility

### Scope

- Define mapping from **Review Items (CR-YYYYMMDD-XX)** to `owner.tech_debt_items`.
- Build a small synchronization script:
  - Parse CR items from `.dev/roadmap/backlog/*.md`.
  - Upsert into `owner.tech_debt_items`.
- Record **architecture checkpoints** aligned with:
  - End of each minor version (v0.2.2 → v0.2.3, etc.).
  - Major architectural changes.
- Grafana dashboards:
  - Open tech debt items by area / target version.
  - Architecture checkpoint timeline (planned vs completed).

### Verification Plan

1. Create 3–5 CR items in backlog files and sync them.
2. Create architecture checkpoints for at least 2 versions.
3. Verify dashboards show correct counts and statuses.

---

## v0.1.3 – Owner Portal React v1 (Read-Only)

**Target:** TBA  
**Priority:** HIGH – first dedicated Owner UI

### Scope

- Create new **React app** (e.g. `apps/portal`):
  - Tech stack aligned with `apps/synapse` (React 19, TypeScript, Vite).
  - Simple layout with 3–4 main views:
    - Overview (health + tests summary per version).
    - Tech Debt (filtered list of open items).
    - Architecture Checkpoints (timeline).
- Backend:
  - Either reuse existing FastAPI backend or add a small BFF.
  - Read-only API endpoints that query `synapse_analytics.owner.*`.
- Infrastructure:
  - Expose via Traefik as `https://portal.localhost` (or similar).

### Verification Plan

1. Start Portal and navigate to each view.
2. Confirm data matches what is visible in Grafana.
3. Smoke test on desktop + laptop resolutions.

---

## v0.1.4 – Owner Portal React v2 (Advanced UI)

**Target:** TBA  
**Priority:** MEDIUM – polish and usability

### Scope

- Upgrade UI to **modern SaaS style**:
  - Glassmorphism, gradients, animations (subtle).
  - Responsive cards and grids.
  - Dark theme optimized.
- Features:
  - Filtering by version, area, impact, status.
  - Deep links from Portal back to:
    - Allure / ReportPortal.
    - Relevant backlog files and CR items.
  - Basic user preferences (default filters, last viewed version).

### Verification Plan

1. Perform UX pass focusing on Owner workflows.
2. Validate performance with realistic data volumes.
3. Ensure links between Portal, Grafana, and docs are consistent.

