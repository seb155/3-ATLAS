---
trigger: model_decision
description: Naming conventions for rules, assets, and code.
---

# Naming Conventions

**Rule:** Rule names MUST use spaces/colons, NEVER underscores.

## Rule Names

**Format:** `{SOURCE}: {Description}` or `{SOURCE}-{ID}: {Description}`

**Examples:**
- `FIRM: Centrifugal Pumps require Electric Motor`
- `COUNTRY-CA: 600V Standard Voltage`
- `PROJECT-GoldMine: Use ABB Motors`
- `CLIENT-AuruMax: Siemens PLC Only`

**Forbidden:**
- `firm_motor_rule` (No underscores)
- `country_ca_voltage` (No snake_case)

## Code Naming

**Backend (Python):**
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`

**Frontend (TypeScript):**
- Files: `PascalCase.tsx` (components), `camelCase.ts` (utils)
- Components: `PascalCase`
- Functions/variables: `camelCase`

**Database:**
- Tables: `plural_snake_case` (assets, rule_definitions)
- Columns: `snake_case`

**Full guide:** See `docs/contributing/code-guidelines.md`