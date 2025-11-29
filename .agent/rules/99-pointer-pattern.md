# Token Optimization Protocol

**Purpose:** Maintain low cognitive load for AI context by using pointer pattern.

## Core Principle: "Pointer Pattern"

**IF** information exists in `docs/` or `.dev/` (Source of Truth),
**THEN** do NOT duplicate it in `.agent/rules/`.
**INSTEAD** write: "See `docs/.../filename.md` for details."

### Example

**BAD (duplicates docs):**
```markdown
# Rule File
Database tables:
- assets (UUID, tag, description, type, properties)
- cables (UUID, from_asset, to_asset, cable_type)
```

**GOOD (pointer pattern):**
```markdown
# Rule File
**Database schema:** See `docs/developer-guide/01-project-structure.md`
```

**Savings:** ~80 tokens

## Compression Rules

### 1. The "Imperative" Rule
- BAD: "When you are ready, you should verify that the containers are running." (14 tokens)
- GOOD: "Verify containers are UP." (5 tokens)

### 2. The "Header" Rule
Delete "Introduction", "Context", or "Purpose" headers if filename is self-explanatory.

### 3. The "100-Line" Rule
If a rule file exceeds 100 lines:
1. Split into sub-concepts (if conditional)
2. Compress text aggressively (if always_on)
3. Use pointer pattern

## Trigger Decision Matrix

| Criteria | Trigger |
|----------|---------|
| Security / Credentials | `always_on` |
| Identity / Role | `always_on` |
| Global Constraints (Naming, DB) | `always_on` |
| Applies to >50% of prompts | `always_on` |
| Specific Task / Workflow | `on_demand` |
| Reference / Lookup Data | `on_demand` |
| Rare Edge Cases | `manual` |

## Pointer Targets (Source of Truth)

**Documentation (`docs/`):**
- Getting Started: `docs/getting-started/`
- Developer Guides: `docs/developer-guide/`
- Code Standards: `docs/contributing/code-guidelines.md`

**Dev Tracking (`.dev/`):**
- Project State: `.dev/context/project-state.md`
- Current Sprint: `.dev/roadmap/current-sprint.md`
- Decisions (ADR): `.dev/decisions/`
- Daily Log: `.dev/journal/YYYY-MM/YYYY-MM-DD.md`

**Code:**
- Backend: `apps/synapse/backend/app/`
- Frontend: `apps/synapse/frontend/src/`

**Rule:** Reference these, don't duplicate.
