# Impact Analysis Reference

**Understanding change impact in SYNAPSE**

> **Detailed specs:** See [change-management.md](../../.dev/roadmap/backlog/change-management.md#impact-analysis)

---

## What is Impact Analysis?

When you modify an asset property, SYNAPSE calculates **all downstream effects**:

- Direct impacts (child assets, cables)
- Indirect impacts (packages, budgets)
- Downstream (parent assets, timestamps)

---

## Example

**Change:** Motor HP from 100 → 150

**Impact Analysis Shows:**

```
⚠️ IMPACT SUMMARY: 12 items affected

DIRECT (3):
├── Cable 210-M-001-PWR: Size 3x#4 → 3x#2 AWG (+$450)
├── VFD 210-VFD-001: Rating 100HP → 150HP (+$2,500)
└── MCC Bucket: Breaker 200A → 300A

INDIRECT (5):
├── Package EL-M040: Regenerate required
├── Package CA-P040: Regenerate required
├── CBS Budget: +$2,950
├── Rule "Motors >125HP need soft starter": NOW APPLIES
└── Foundation: May need reinforcement

TOTAL COST: +$2,950
SCHEDULE: +2 weeks (procurement)
```

---

## How It Works

1. **You make change** → System calculates impacts
2. **Review impacts** → See all affected items
3. **Choose action:**
   - Cancel (abort change)
   - Apply (change only)
   - Apply + Auto-Fix (change + update children)

---

## Impact Types

| Type | Description | Example |
|------|-------------|---------|
| **Direct** | Child assets | Motor HP ↑ → Cable size ↑ |
| **Indirect** | Packages, budgets | Package regenerate |
| **Downstream** | Parent timestamps | Parent "modified" date |

---

## Related Documentation

- [Change Management (Technical)](../../.dev/roadmap/backlog/change-management.md)
- [Using Impact Analysis](../workflows/using-impact-analysis.md)
- [Creating Baselines](../workflows/creating-baselines.md)

---

**Updated:** 2025-11-24
