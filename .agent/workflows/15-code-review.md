---
description: Code review checklist
---

# Code Review

**Goal:** Ensure quality before merging.

## 1. Automated Checks

**Backend:**
```bash
docker exec synapse-backend-1 pytest
docker exec synapse-backend-1 mypy app/
```

**Frontend:**
```bash
cd apps/synapse/frontend
npm run type-check
npm run lint
```

**Both pass?** ✅ Continue

## 2. Code Quality

**Check:**
- [ ] Follows naming conventions (see `.agent/rules/01-naming-conventions.md`)
- [ ] Type hints (backend) / TypeScript (frontend)
- [ ] No console.log / print statements (unless logging)
- [ ] Error handling present
- [ ] No hardcoded values (use env vars/config)

## 3. Architecture

**Check:**
- [ ] Follows project structure (`docs/developer-guide/01-project-structure.md`)
- [ ] Uses existing patterns
- [ ] No duplication
- [ ] Multi-tenancy respected (filter by project_id)

## 4. Database

**If DB changes:**
- [ ] Migration present
- [ ] Migration reversible
- [ ] Pydantic schemas updated
- [ ] No breaking changes (or documented)

## 5. Documentation

**Check:**
- [ ] Code comments (why, not what)
- [ ] Updated relevant `docs/` if needed
- [ ] ADR if architectural decision (`.dev/decisions/`)
- [ ] Logged in `.dev/journal/`

## 6. Testing

**Check:**
- [ ] Tests added for new features
- [ ] Edge cases covered
- [ ] Tests pass

## 7. Review

**Approve if:**
- All checks pass
- Code is readable
- No security issues
- Performance acceptable

**See:** `docs/contributing/code-guidelines.md` for full standards
