# Version History Reference

**Asset-level change tracking in SYNAPSE**

> **Detailed specs:** See [change-management.md](../../.dev/roadmap/backlog/change-management.md#version-history)

---

## What is Version History?

Every asset maintains a **complete change history** - like Git, but for engineering assets.

---

## Viewing History

1. Open asset (e.g., 210-M-001)
2. Click **[History]** tab
3. See all versions:

```
VERSION HISTORY: 210-M-001 (Motor)

v4 (CURRENT) ─────────────────────────────────
│ 2025-11-24 15:30 | admin@aurumax.com
│ Changed: rated_power: 100HP → 150HP
│ Reason: "Client requirement - CR-2025-042"
│ [Compare with v3] [Rollback]

v3 ───────────────────────────────────────────
│ 2025-11-20 10:15 | engineer@aurumax.com
│ Changed: voltage: 480V → 600V
│ Reason: "Site standard update"
│ [Compare] [Rollback]

v2 ───────────────────────────────────────────
│ 2025-11-15 14:00 | admin@aurumax.com
│ Changed: location → "Area 210"
│ [Compare] [Rollback]

v1 (CREATED) ─────────────────────────────────
│ 2025-11-10 09:00 | system
│ Created from: Rule "Pumps require motors"
│ Parent: 210-PP-001
```

---

## Comparing Versions

**Compare v3 vs v4:**

```
PROPERTY       │ v3 (OLD)  │ v4 (NEW)
───────────────┼───────────┼──────────
rated_power    │ 100 HP    │ 150 HP    ← CHANGED
voltage        │ 600V      │ 600V
efficiency     │ 95.4%     │ 96.2%     ← CHANGED
frame_size     │ 404T      │ 445T      ← CHANGED
```

---

## Rollback

**To undo a change:**

1. Open version history
2. Find previous version (e.g., v3)
3. Click **[Rollback]**
4. Confirm → Asset reverted to v3
5. New version created: v5 (copy of v3)

**Note:** Rollback creates new version, doesn't delete history.

---

## Audit Log

**Project-wide view:**

```
2025-11-24 15:30 | admin | MODIFY | 210-M-001 | HP: 100→150
2025-11-24 15:31 | system | AUTO | 210-M-001-PWR | Size: #4→#2
2025-11-24 15:32 | admin | REGEN | EL-M040 | Package updated
```

Filter by:
- User
- Date range
- Asset type
- Action type

---

## Best Practices

✅ **Add change reasons** - Helps future you understand why
✅ **Link to change requests** - CR numbers for traceability
✅ **Use baselines for milestones** - Snapshot before major changes

---

## Related Documentation

- [Change Management (Technical)](../../.dev/roadmap/backlog/change-management.md)
- [Creating Baselines](../workflows/creating-baselines.md)
- [Impact Analysis](impact-analysis.md)

---

**Updated:** 2025-11-24
