# Using Impact Analysis

**Step-by-step guide to analyzing change impacts**

---

## When to Use

Use impact analysis **before making changes** to:
- Understand downstream effects
- Calculate cost impacts
- Identify affected packages
- Prevent breaking dependencies

---

## Quick Start

### Step 1: Make a Change

1. Open asset (e.g., 210-M-001 Motor)
2. Modify property (HP: 100 → 150)
3. Click **[Save]**

### Step 2: Review Impact

System automatically shows impact:

```
⚠️ IMPACT ANALYSIS
─────────────────────────────────────

12 items will be affected by this change

DIRECT IMPACTS (3):
├── 🔌 Cable 210-M-001-PWR
│   Size: 3x#4 AWG → 3x#2 AWG
│   Cost: +$450
├── ⚡ VFD 210-VFD-001  
│   Rating: 100HP → 150HP
│   Cost: +$2,500
└── 🔧 MCC Bucket
    Breaker: 200A → 300A

INDIRECT IMPACTS (5):
├── 📦 Package EL-M040 (regenerate)
├── 📦 Package CA-P040 (regenerate)
├── 💰 Budget: +$2,950
├── 📋 Rule: "Soft starter required"
└── 🏗️ Foundation check needed

TOTAL COST: +$2,950
SCHEDULE: +2 weeks
```

### Step 3: Choose Action

```
┌─ Apply Changes? ────────────────┐
│                                  │
│ [Cancel] - Abort change          │
│ [Apply] - Change this asset only │
│ [Apply + Auto-Fix] - Update all  │
└──────────────────────────────────┘
```

**Cancel:** Nothing changes  
**Apply:** Only motor HP changes, manual fixes needed  
**Apply + Auto-Fix:** Motor + cable + VFD all updated ✅

---

## Advanced Usage

### Manual Review Mode

For critical changes:

1. Click **[Apply]** (not Auto-Fix)
2. Review each impact individually
3. Manually update as needed
4. More control, more work

### Impact Report Export

1. Click **[Export Impact Report]**
2. Choose format (PDF/Excel)
3. Share with team for approval
4. Apply changes after approval

---

## Best Practices

✅ **Always review impacts** before applying  
✅ **Use Auto-Fix** for routine changes (cable sizing)  
✅ **Manual review** for critical changes (voltage, HP)  
✅ **Export reports** for client approval  
✅ **Create baseline** before major changes

---

## Common Scenarios

### Scenario 1: Motor HP Increase

**Change:** 100HP → 150HP  
**Impacts:** Cable size, VFD rating, MCC breaker  
**Recommendation:** Use Auto-Fix ✅

### Scenario 2: Voltage Change

**Change:** 480V → 600V  
**Impacts:** ALL electrical components  
**Recommendation:** Manual review + baseline first ⚠️

### Scenario 3: Location Move

**Change:** Area 210 → Area 220  
**Impacts:** Cable lengths, trays, packages  
**Recommendation:** Review cable routes manually ⚠️

---

## Troubleshooting

**Q: Impact analysis takes too long**  
A: Large projects (5000+ assets) can take 10-20 seconds. Be patient.

**Q: Auto-Fix broke something**  
A: Use version history to rollback. Consider manual review next time.

**Q: Missing an impact**  
A: Some impacts require manual review (e.g., foundation loads).

---

## Related Documentation

- [Impact Analysis Reference](../reference/impact-analysis.md)
- [Change Management (Technical)](../../.dev/roadmap/backlog/change-management.md)
- [Creating Baselines](creating-baselines.md)

---

**Updated:** 2025-11-24
