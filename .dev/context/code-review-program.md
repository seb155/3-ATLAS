---
description: Structured code & architecture review program
---

# Code & Architecture Review Program

**Purpose:** Provide a repeatable, professional process to:
- Analyze the codebase (backend, frontend, infrastructure)
- Capture risks, opportunities, and refactoring ideas
- Convert them into **roadmap-ready** recommendations with timing and method

This is the process to follow for **deep reviews** (like the SYNAPSE analysis we just did), not for day‑to‑day PR review.

---

## 1. When to Run a Review

Run a structured review when:
- ✅ End of a minor version (e.g. v0.2.2 → v0.2.3)
- ✅ Before adding a major feature (rule editor, background jobs, P&ID, etc.)
- ✅ After a large refactor or architecture change
- ✅ When recurring pain points appear (bugs, performance, DX friction)

Cadence suggestion:
- **Light review:** Every 1–2 weeks (focus on the active sprint scope)
- **Deep review:** At major roadmap milestones (end of v0.2.x, before v0.3.0, etc.)

---

## 2. Review Types

Choose ONE primary type per session:

- **Feature Review**
  - Scope: A single feature or module (e.g. Import CSV, Rule Engine, DevConsole)
  - Goal: Validate design, API boundaries, and implementation quality

- **Cross‑Cutting Review**
  - Scope: One concern across the stack (e.g. logging, error handling, auth, testing)
  - Goal: Ensure consistency and reuse patterns across services and UI

- **Architecture Checkpoint**
  - Scope: Global structure (DB model, services, UI layout, workflows)
  - Goal: Confirm that current direction still supports the roadmap (scale, maintainability)

---

## 3. Standard Review Workflow

Use this 7‑step workflow for every structured review (human or AI‑assisted).

### Step 1 – Define Objective & Scope

Write a short statement:
- **Objective:** What are we trying to validate or improve?
- **Scope:** Files / domains / features included (and explicitly excluded)
- **Target version:** Which roadmap version should receive the recommendations (e.g. v0.2.3, v0.4.0)?

Log this in the daily journal (`.dev/journal/YYYY-MM/YYYY-MM-DD.md`).

### Step 2 – Load Context

Always load:
- `.dev/context/project-state.md`
- `.dev/roadmap/README.md` + relevant backlog file(s)
- Any domain‑specific references:
  - Rule Engine → `docs/reference/rule-engine.md`, `.dev/roadmap/backlog/core-platform-v0.2.x.md`
  - DevConsole → `docs/reference/devconsole-v3.md`
  - Workflow Engine → `docs/developer-guide/workflow-engine.md`

For AI sessions: run the smart resume script (`.dev/scripts/smart-resume-enhanced.ps1`) where possible.

### Step 3 – Explore Code (Backend + Frontend)

For the chosen scope:
- Identify **entry points** (API endpoints, React pages, services)
- Follow the main path end‑to‑end:
  - HTTP → service → model → DB → logs
  - UI view → store → service → response handling → DevConsole/logs
- Note any smells or complexity (duplication, tight coupling, unclear naming, missing tests)

### Step 4 – Reconstruct the Product Flow

Summarize in plain language:
- What is the **real user story** behind this code?
- What are the **main flows** (happy path + 1–2 key error paths)?
- How this relates to the roadmap (which version / feature name)?

This step ensures recommendations stay product‑driven, not purely technical.

### Step 5 – Capture Findings

Group findings into 4 buckets:
- **Strengths** – patterns to keep and replicate
- **Risks** – potential bugs, correctness issues, security concerns
- **Complexity / DX** – things that make changes or onboarding harder
- **Opportunities** – refactors, abstractions, tests, or tooling that would unlock speed and quality

Use short bullets; avoid long essays.

### Step 6 – Convert to Roadmap Recommendations

For each important finding, create a **Review Item** with fields:

```text
ID: CR-YYYYMMDD-XX
Area: Backend | Frontend | Infra | Docs | Cross-cutting
Title: Short, action-oriented title
Context: 1–3 lines (what and where)
Impact: High | Medium | Low      (business / reliability / DX)
Effort: S | M | L                 (estimated)
Risk: Low | Medium | High         (if we do NOTHING)
Type: Refactor | Bug | DX | Perf | Arch
Proposed Target: v0.2.x / v0.3.0 / later
Suggested Location: backlog file or sprint (e.g. `.dev/roadmap/backlog/core-platform-v0.2.x.md`)
```

Then:
- If it aligns with an existing backlog spec → **attach it there** (extend that file)
- If it’s a new theme → create a new backlog entry (e.g. `code-health-v0.2.x.md`) and link from `DOCUMENTATION-INDEX.md`

### Step 7 – Log & Track

At the end of the review:
- Add a short **summary section** to the journal of the day:
  - Reviewed area, main risks, count of Review Items created
- Optionally add a short note to `project-state.md` if it changes priorities for the next sprint
- Ensure each Review Item is linked from a roadmap/backlog file (no “orphan” ideas)

---

## 4. Example Review Session (Template)

Use this template in `.dev/journal/YYYY-MM/YYYY-MM-DD.md` when you run a structured review:

```markdown
## Code & Architecture Review – [Area]

**Objective**
- Validate [feature / module] for [reliability / UX / maintainability]

**Scope**
- Backend: [files, modules, endpoints]
- Frontend: [pages, stores, components]
- Excluded: [out of scope]

**Key Observations**
- Strengths:
  - [...]
- Risks:
  - [...]
- Complexity / DX:
  - [...]
- Opportunities:
  - [...]

**Review Items Created**
- CR-YYYYMMDD-01 – [Title] → Proposed: v0.2.3 (core-platform-v0.2.x.md)
- CR-YYYYMMDD-02 – [Title] → Proposed: v0.4.0 (background-processing.md)
```

---

## 5. AI-Assisted Reviews (Optional)

When using an AI assistant for this program:
- Always start from this document + `project-state.md`
- Explicitly state the **scope** and **target version(s)** for recommendations
- Ask the AI to:
  - Produce **Review Items** in the format above
  - Propose where to place them in `.dev/roadmap/backlog/*.md`
  - Keep suggestions **incremental** (fit into existing roadmap, not redesign everything)

The human owner remains responsible for:
- Accepting or rejecting each Review Item
- Deciding final target version
- Updating backlog and sprint files

