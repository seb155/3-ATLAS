# Phase 1: Enhanced Rule Engine - Deployment Guide

## 📋 Overview

This guide outlines deploying Phase 1 of the Enhanced Rule Engine, including:
- Database models with enforcement and conflict tracking
- Migration script for new columns
- Enhanced rule engine with conflict detection
- API endpoints for conflict detection
- Unit tests

---

## 🔧 Prerequisites

- Python 3.9+
- PostgreSQL database
- Backend requirements installed: `pip install -r backend/requirements.txt`

---

## 📦 Deployment Steps

### 1. Run Database Migration

```bash
cd backend
alembic upgrade head
```

**What this does:**
- Adds `category`, `is_enforced`, `overrides_rule_id`, `conflicts_with` columns to `rule_definitions` table
- Creates indexes on new columns

**Migration file:** `backend/alembic/versions/a1b2c3d4e5f6_add_rule_enforcement_and_conflict_tracking.py`

---

### 2. Seed Baseline Rules

```bash
cd backend
python3 -m app.scripts.seed_baseline_rules
```

**What this does:**
- Creates 10+ FIRM baseline rules (Automation, Electrical)
- Creates 4 COUNTRY rules (Canada CEC, Brazil ABNT, Greece IEC)
- Marks electrical codes as `is_enforced=True`

**Output:**
```
=== SEEDING BASELINE ENGINEERING RULES ===
🏢 Seeding FIRM Baseline Rules...
  + Created rule: PlantPAX: One PLC per Area
  + Created rule: PlantPAX: CPC Cabinet per Area
  ...
✅ 10 FIRM rules seeded successfully

🌍 Seeding COUNTRY Electrical Code Rules...
  + Created rule: CEC - Motor Voltage Standard
  ...
✅ 4 COUNTRY rules seeded successfully

Total Rules: 14
```

---

### 3. Test Rule Engine

Run unit tests:

```bash
cd backend
pytest app/tests/test_enhanced_rule_engine.py -v
```

**Tests included:**
- ✅ Conflict detection between rules
- ✅ Enforcement violations (enforced rules cannot be overridden)
- ✅ Priority hierarchy (CLIENT > PROJECT > COUNTRY > FIRM)
- ✅ Property extraction from rule actions

---

### 4. Verify API Endpoints

Start the backend server:

```bash
cd backend
uvicorn app.main:app --reload
```

Test the conflict detection endpoint:

```bash
curl http://localhost:8000/api/rules/conflicts/{project_id}
```

**Expected response:**
```json
{
  "project_id": "...",
  "total_rules": 14,
  "conflicts_count": 2,
  "enforcement_violations_count": 0,
  "conflicts": [
    {
      "winning_rule": {
        "id": "rule-xxx",
        "name": "Canada CEC Voltage",
        "source": "COUNTRY",
        "priority": 30
      },
      "overridden_rule": {
        "id": "rule-yyy",
        "name": "FIRM Default Voltage",
        "source": "FIRM",
        "priority": 10
      },
      "status": "valid_override"
    }
  ],
  "enforcement_violations": []
}
```

---

## 🔍 Verification Checklist

- [ ] Migration applied successfully (no errors)
- [ ] 14+ baseline rules created in database
- [ ] All unit tests pass
- [ ] Backend starts without errors
- [ ] `/api/rules` endpoint returns rules list
- [ ] `/api/rules/conflicts/{project_id}` detects conflicts
- [ ] Enforced rules cannot be overridden (test with CLIENT rule trying to override COUNTRY enforced rule)

---

## 🛠️ Key Files Modified/Created

### Database Models
- ✅ `backend/app/models/rules.py` - Added `is_enforced`, `category`, `conflicts_with`, `overrides_rule_id`

### Migration
- ✅ `backend/alembic/versions/a1b2c3d4e5f6_add_rule_enforcement_and_conflict_tracking.py`

### Enhanced Rule Engine
- ✅ `backend/app/services/enhanced_rule_engine.py` - New file
  - `RuleConflictResolver` class
  - `EnhancedRuleEngine` class
  - Conflict detection logic
  - Enforcement validation

### API Endpoints
- ✅ `backend/app/api/endpoints/rules.py` - Added `/conflicts/{project_id}` endpoint

### Seed Script
- ✅ `backend/app/scripts/seed_baseline_rules.py` - Updated with `is_enforced`, `category`

### Unit Tests
- ✅ `backend/app/tests/test_enhanced_rule_engine.py` - New file
  - 15+ test cases covering conflict detection and enforcement

---

## 📖 Usage Examples

### Example 1: Enforced Rule Blocks Higher Priority

**Scenario:** Greece project has IEC 60364 electrical code (enforced). Client tries to override.

```python
# COUNTRY rule (enforced)
{
  "name": "IEC 60364 - Motor Voltage",
  "source": "COUNTRY",
  "priority": 30,
  "is_enforced": True,  # Legal requirement
  "action": {"set_property": {"voltage": "400V"}}
}

# CLIENT rule (higher priority but blocked)
{
  "name": "CLIENT Custom Voltage",
  "source": "CLIENT",
  "priority": 100,
  "is_enforced": False,
  "action": {"set_property": {"voltage": "690V"}}
}
```

**Result:**
- Conflict detected
- CLIENT rule is **blocked** because COUNTRY rule is enforced
- Motors get 400V (IEC code respected)
- API returns `enforcement_violation`

---

### Example 2: Valid Override (No Enforcement)

**Scenario:** PROJECT rule overrides FIRM baseline.

```python
# FIRM rule
{
  "name": "FIRM Default PLC",
  "source": "FIRM",
  "priority": 10,
  "is_enforced": False,
  "action": {"create_child": {"type": "PLC", "manufacturer": "Rockwell"}}
}

# PROJECT rule
{
  "name": "PROJECT Siemens Preference",
  "source": "PROJECT",
  "priority": 50,
  "is_enforced": False,
  "action": {"create_child": {"type": "PLC", "manufacturer": "Siemens"}}
}
```

**Result:**
- Conflict detected
- PROJECT rule wins (priority 50 > 10)
- FIRM rule is overridden (allowed, not enforced)
- Status: `valid_override`

---

## 🐛 Troubleshooting

### Migration fails with "column already exists"

**Solution:** Column may have been added manually. Check with:
```sql
\d rule_definitions
```

If columns exist, mark migration as applied:
```bash
alembic stamp a1b2c3d4e5f6
```

### Seed script reports errors

**Solution:** Check database connection in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/epcb_tools
```

### Unit tests fail

**Solution:** Install pytest:
```bash
pip install pytest pytest-mock
```

---

## ✅ Success Criteria

Phase 1 is complete when:

1. ✅ Database has 14+ baseline rules
2. ✅ Enforced rules cannot be overridden
3. ✅ Conflicts detected correctly
4. ✅ API endpoint `/api/rules/conflicts/{project_id}` works
5. ✅ All unit tests pass
6. ✅ Re-running rules is idempotent (no duplicates)

---

## 🚀 Next Steps (Phase 2)

- Frontend UI for conflict visualization
- Manual conflict resolution interface
- Project-specific hierarchy customization
- Rule versioning and rollback

---

**Deployed:** Phase 1  
**Date:** 2025-11-21  
**Status:** ✅ Ready for Testing
