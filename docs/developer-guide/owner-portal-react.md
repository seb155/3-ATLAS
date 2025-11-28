# Owner Portal React App

**Purpose:** Dedicated web app for the technical owner to view health, tests, tech debt, and architecture checkpoints, with a polished SaaS-quality UI.

---

## Goals & Scope

- Read-only UI backed by `synapse_analytics.owner.*`.
- Fast, modern React experience (desktop + laptop), with clean dark SaaS styling (gradients + glassmorphism léger).
- Clear navigation: Overview, Health, Tests, Tech Debt, Architecture, Tools.
- Easy deep links to Allure, ReportPortal, Grafana, pgAdmin, Synapse UI/API, and backlog files.

Out of scope for now: writes/mutations; the Portal consumes data written by AI/CLI/scripts.

---

## Stack & Integration

- **App:** `apps/portal` (React 19, TypeScript, Vite).
- **UI:** TailwindCSS + optional shadcn/ui for consistent pro components.
- **State/Data:** React Query + axios/fetch clients.
- **Backend:** FastAPI (new module `owner_portal`) exposing read-only endpoints over `synapse_analytics.owner.*`.
- **Infra:** Docker + Traefik → `https://portal.localhost` (or `owner.localhost` during transition).
- **Auth:** Dev mode can be open; later align with Multi-Tenant Auth for production exposure.

---

## Data Sources (read-only)

- Database: `synapse_analytics`, schema `owner`.
  - `health_scorecards` (reliability, dx, observability, ux by version/area)
  - `test_runs` (totals, pass/fail, component, suite, report_url)
  - `tech_debt_items` (CR-YYYYMMDD-XX normalized)
  - `architecture_checkpoints` (planned/done, risks, decisions)
- No Elasticsearch required; Timescale optional in the future (tables already time-friendly).

---

## API Design (FastAPI, read-only)

Suggested endpoints (prefix `/owner`):
- `GET /health-scorecards?version=&area=` → aggregate/rows for charts.
- `GET /test-runs?version=&component=&limit=` → latest runs + pass rates.
- `GET /tech-debt-items?status=&impact=&area=&target_version=&limit=` → filterable table.
- `GET /architecture-checkpoints?version=` → timeline data.

Implementation notes:
- Separate DB connection string for `synapse_analytics`.
- Simple SQL/SQLAlchemy SELECTs; no business logic here.
- Pagination for tables (tech debt, test runs).

---

## UI / Pages

- **Overview**
  - Version selector (v0.2.2, v0.2.3, …).
  - Scorecards (Reliability, DX, Observability, UX averages).
  - Latest test runs per component with status.
  - Top 3 tech-debt items (High impact/risk) + links.

- **Health**
  - Charts by version/area (trend over time).
  - Drill-down per area with history.

- **Tests**
  - Timeline of test runs (pass rate).
  - Table of recent runs (component, suite, totals, report_url).
  - Quick links to Allure / ReportPortal.

- **Tech Debt**
  - Table with filters (area, impact, effort, status, target_version).
  - Row detail: context, type, link to source backlog file.

- **Architecture**
  - Timeline of checkpoints (planned/in_progress/done).
  - Detail: summary, main_risks, main_decisions.

- **Tools / Infra**
  - Cards linking to Synapse UI/API, Grafana, Loki, pgAdmin, Prisma, Homepage.
  - Simple service status pings (optional).

---

## UX & Design Direction

- Theme: dark SaaS, subtle gradients, glassmorphism léger, 12–16px radius, soft shadows.
- Typography: clean sans (Inter/Plus Jakarta/Manrope style), bold headings, readable body.
- Components: cards with hover feedback, skeleton loaders, clear empty states, toasts on errors.
- Responsiveness: desktop first (1440/1080), good on laptop (1366), acceptable on tablet widths.

---

## Project Structure (proposed)

```
apps/portal/
  package.json
  tsconfig.json
  vite.config.ts
  index.html
  src/
    app/            # layout, routing
    features/
      overview/
      health/
      tests/
      techdebt/
      architecture/
      infra/
    shared/
      api/          # axios clients, query keys
      components/   # cards, charts wrappers, layout
      config/       # env/config, routes, constants
      hooks/
      types/
    styles/         # tailwind, theme tokens
```

---

## Phasing (delivery roadmap)

1) **Skeleton & Infra**
   - Create `apps/portal` (Vite/React/TS), Tailwind setup, routing + layout shell.
   - Traefik labels + docker-compose entry; static build served by nginx or Vite preview in dev.
   - Overview page with mocked data.

2) **API Integration (read-only)**
   - FastAPI `owner_portal` endpoints hooked to `synapse_analytics.owner.*`.
   - React Query clients + types; replace mocks on Overview/Health/Tests.

3) **Tech Debt & Architecture**
   - Full table with filters for tech debt; checkpoint timeline.
   - Deep links to Allure/ReportPortal/backlog files.

4) **UX Pro Pass**
   - Final theme, gradients, glassmorphism, animations, keyboard shortcuts, skeletons/empty/error states.
   - Performance checks with realistic data volumes.

---

## Dev Workflow

- Start workspace (Postgres/Grafana/etc.), then Portal dev server (`npm run dev` in `apps/portal`).
- Use `.env` or config file for API base URL and external links (Allure, ReportPortal, Grafana).
- Keep Portal read-only; all writes happen via AI/CLI scripts to `synapse_analytics`.

## Docker / Traefik (preview)

- Build image from repo root:
  ```bash
  docker-compose -f workspace/docker-compose.yml -f workspace/docker-compose.traefik.yml -f workspace/docker-compose.owner-portal.yml build owner-portal
  docker-compose -f workspace/docker-compose.yml -f workspace/docker-compose.traefik.yml -f workspace/docker-compose.owner-portal.yml up -d owner-portal
  ```
- Default API base at build-time: `VITE_OWNER_API_BASE_URL=https://api.localhost` (override via build arg).
- Served at `https://portal.localhost` through Traefik (websecure entrypoint).
