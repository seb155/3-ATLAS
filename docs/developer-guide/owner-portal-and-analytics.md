# Owner Analytics & Portal

**Purpose:** Give the technical owner a clear, visual view of SYNAPSE health, tests, tech debt, and architecture checkpoints, using PostgreSQL only.

---

## 1. Architecture Overview

The Owner analytics stack is intentionally simple and professional:

- **Database:** `synapse_analytics` (PostgreSQL), with an `owner` schema.
- **Data sources:**
  - AI/CLI scripts after reviews and test runs.
  - Synchronization scripts from `.dev/roadmap/backlog/*.md` (Review Items).
- **Consumers:**
  - Grafana dashboards (health, tests, tech debt, checkpoints).
  - Owner Portal React app (`apps/portal`, planned).

Nothing depends on Elasticsearch or other external data stores. Future use of Timescale is possible, but not required.

---

## 2. Database: synapse_analytics / owner schema

**Database:** `synapse_analytics`  
**Schema:** `owner`

Tables:
- `owner.health_scorecards` – health scores per version and area.
- `owner.test_runs` – aggregated test runs (backend, frontend, e2e).
- `owner.tech_debt_items` – normalized view of Review Items (CR-YYYYMMDD-XX).
- `owner.architecture_checkpoints` – checkpoints around minor/major versions.

See `.dev/roadmap/backlog/dev-environment-owner-portal.md` (v0.1.0) for the current DDL.

---

## 3. Data Flow & Responsibilities

**Technical Owner (human):**
- Decides *when* to run reviews and checkpoints.
- Chooses scores (reliability, DX, observability, UX).
- Approves which Review Items become tech debt targets for specific versions.

**AI / CLI tools:**
- After a review:
  - Insert a row into `owner.health_scorecards`.
  - Insert/update rows in `owner.tech_debt_items`.
- After running tests:
  - Insert a row into `owner.test_runs` with totals and links (Allure/ReportPortal).
- Around roadmap milestones:
  - Insert/update `owner.architecture_checkpoints` with status and notes.

**Dashboards (Grafana / Portal):**
- Read from `synapse_analytics.owner.*` in read-only mode.
- Present data as:
  - Scorecards per version.
  - Test trends over time.
  - Tech debt by area and target version.
  - Checkpoint timelines.

---

## 4. Owner Portal React (Planned)

**App:** `apps/portal` (planned)  
**Stack:** React 19, TypeScript, Vite (aligned with `apps/synapse`)

Main views:
- **Overview:** Health + tests per version (high-level).
- **Tech Debt:** Filterable list of open items (by area, impact, target version).
- **Architecture:** Timeline of checkpoints and key decisions.

Data access:
- Read-only API endpoints (FastAPI or a small BFF) querying `synapse_analytics.owner.*`.
- No direct writes from the Portal; writes are driven by reviews, tests, and scripts.

---

## 5. Usage Pattern for the Technical Owner

Typical cycle:

1. **Plan**
   - Set objectives in `.dev/context/project-state.md` and relevant backlog files.
2. **Review**
   - Run a structured review following `.dev/context/code-review-program.md`.
   - Decide scores and key Review Items.
3. **Record**
   - Ask AI/CLI to:
     - Record health scorecards and test runs.
     - Sync Review Items into `tech_debt_items`.
     - Update architecture checkpoints if needed.
4. **Inspect**
   - Use Grafana and the Owner Portal to:
     - Check overall health of the platform.
     - See where tech debt is accumulating.
     - Verify architecture checkpoints are on track.

This keeps the technical owner at the “governance” level, while AI and tools handle the heavy lifting.

