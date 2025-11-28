# Creating and Managing Baselines

**Step-by-step guide to project snapshots**

---

## What is a Baseline?

A **baseline** is a snapshot of your entire project at a specific point in time - like a "commit" in Git, but for your engineering project.

**Contains:**
- All assets (engineering, catalog, physical)
- All cables
- All rules
- All breakdown structures
- Package configurations

**Use Cases:**
- **Design milestones** - 30%, 60%, 90%, IFC
- **Client submittals** - Issued for Construction (IFC)
- **Change tracking** - Before/after major changes
- **Regulatory compliance** - Audit trail

---

## Creating a Baseline

### Step 1: Prepare Your Project

✅ **Before creating baseline:**
- All assets reviewed and validated
- All rules executed
- All packages generated
- No pending changes

### Step 2: Navigate to Baselines

1. Open project
2. Click **[Baselines]** in sidebar
3. Click **[+ Create Baseline]**

### Step 3: Fill Baseline Form

```
┌─ Create Baseline ─────────────────────────────────┐
│                                                    │
│ Name: *                                            │
│ [IFC Release                              ]        │
│                                                    │
│ Description:                                       │
│ [Issued for Construction - Final Design   ]        │
│ [based on client approval 2025-11-20      ]        │
│                                                    │
│ Include:                                           │
│ ☑️ All Engineering Assets (1,247)                  │
│ ☑️ All Catalog Assets (342)                        │
│ ☑️ All Physical Assets (0)                         │
│ ☑️  All Cables (892)                               │
│ ☑️ All Rules (14)                                  │
│ ☑️ All Breakdown Structures                        │
│                                                    │
│ Options:                                           │
│ ☑️ Lock baseline (prevent modifications)           │
│ ☐ Require approval before creation                │
│ ☑️ Generate change report vs BL-002                │
│                                                    │
│ [Cancel] [Create Baseline]                         │
└────────────────────────────────────────────────────┘
```

### Step 4: Review and Create

1. **Verify counts** - Make sure numbers look correct
2. **Check options** - Lock baseline if final
3. **Click [Create Baseline]**
4. **Wait** - System creates snapshot (2-5 seconds for 1000+ assets)

### Step 5: Confirm Creation

```
✅ Baseline Created Successfully!

BL-003 "IFC Release"
Created: 2025-11-24 10:15
Status: APPROVED
Assets: 1,247 | Cables: 892 | Rules: 14

[View Baseline] [Compare with Previous] [Export Report]
```

---

## Baseline Workflow

### Design Milestones

**Typical workflow for engineering project:**

```
┌─────────────────────────────────────────────────┐
│ 30% Design                                      │
│ - Basic layout complete                         │
│ - Major equipment selected                      │
│ └─ Create: BL-001 "30% Design"                  │
│                                                 │
│ 60% Design                                      │
│ - Detailed design                               │
│ - All equipment specified                       │
│ - Cable routes defined                          │
│ └─ Create: BL-002 "60% Design"                  │
│                                                 │
│ 90% Design                                      │
│ - Final review                                  │
│ - All packages generated                        │
│ └─ Create: BL-003 "90% Design"                  │
│                                                 │
│ IFC (Issued for Construction)                   │
│ - Client approved                               │
│ - Ready for construction                        │
│ └─ Create: BL-004 "IFC Release"                 │
└─────────────────────────────────────────────────┘
```

### Change Management

**When client requests change:**

1. **Create baseline** BEFORE making changes: "BL-005 Pre-CR-042"
2. **Make changes** per change request CR-042
3. **Create baseline** AFTER changes: "BL-006 Post-CR-042"
4. **Compare** BL-005 vs BL-006 to see impact
5. **Generate report** for client

---

## Comparing Baselines

### Simple Compare

1. Navigate to **[Baselines]**
2. Select two baselines (Ctrl+Click)
3. Click **[Compare]**

### Compare Results

```
COMPARING: BL-002 (60% Design) → BL-003 (90% Design)
═══════════════════════════════════════════════════════

SUMMARY:
├── Assets: 1,102 → 1,247 (+145 new, -12 deleted, +89 modified)
├── Cables: 756 → 892 (+136 new)
├── Rules: 12 → 14 (+2 new)
└── Packages: 8 → 12 (+4 new)

CHANGES BY DISCIPLINE:
┌─────────────────┬───────┬─────────┬──────────┬─────────┐
│ Discipline      │ Added │ Deleted │ Modified │ Total   │
├─────────────────┼───────┼─────────┼──────────┼─────────┤
│ Process         │ 12    │ 2       │ 8        │ 18      │
│ Electrical      │ 45    │ 5       │ 32       │ 77      │
│ Automation      │ 78    │ 3       │ 41       │ 119     │
└─────────────────┴───────┴─────────┴──────────┴─────────┘

SIGNIFICANT CHANGES:
├── 🆕 NEW: Area 220 added (45 assets)
├── ❌ DELETED: 210-PP-003 (cancelled by client)
├── ⚠️ MODIFIED: All motors upgraded to 600V
└── 📦 NEW PACKAGES: IO-P040, VFD Schedule

[Export Summary (PDF)] [Export Detailed (Excel)] [Close]
```

### Exporting Comparison

**PDF Summary** - For management/client:
- High-level summary
- Key changes highlighted
- Total counts

**Excel Detailed** - For engineering team:
- Complete asset list with changes
- Line-by-line comparison
- Formulas for analysis

---

## Approving Baselines

### Workflow

**For formal projects requiring approval:**

1. Engineer creates baseline (Status: DRAFT)
2. Engineer requests approval
3. Project Manager reviews
4. PM approves (Status: APPROVED)
5. Baseline locked automatically

### Approval UI

```
┌─ Baseline Approval Request ───────────────────────┐
│                                                    │
│ BL-004 "IFC Release"                               │
│ Created by: engineer@aurumax.com                   │
│ Created: 2025-11-24 10:15                          │
│                                                    │
│ Changes since BL-003:                              │
│ - 15 assets modified                               │
│ - 3 rules added                                    │
│ - All packages regenerated                         │
│                                                    │
│ Approval Notes:                                    │
│ [Client approved via email 2025-11-20    ]         │
│ [All comments addressed                  ]         │
│                                                    │
│ [Reject] [Approve]                                 │
└────────────────────────────────────────────────────┘
```

---

## Baseline Status

### Status Workflow

```
DRAFT → PENDING_APPROVAL → APPROVED → SUPERSEDED
│                                  │
└──────── REJECTED ────────────────┘
```

| Status | Meaning | Actions Available |
|--------|---------|-------------------|
| **DRAFT** | Created, not submitted | Edit, Delete, Submit |
| **PENDING_APPROVAL** | Awaiting PM approval | Approve, Reject |
| **APPROVED** | Locked, official | Compare, Export, Supersede |
| **REJECTED** | Not approved | Edit, Resubmit, Delete |
| **SUPERSEDED** | Replaced by newer baseline | View only, Compare |

---

## Best Practices

### Naming Conventions

✅ **Good names:**
- "30% Design"
- "IFC Release"
- "Pre-CR-042 Voltage Change"
- "Post-Client Review 2025-11-20"

❌ **Bad names:**
- "Baseline 1"
- "Test"
- "Final" (then you make another "Final-Final")

### When to Create

**Create baseline:**
- ✅ Before major design milestones (30%, 60%, 90%)
- ✅ Before client submittals (IFC, bidding packages)
- ✅ Before implementing change requests
- ✅ After completing major rework

**Don't create baseline:**
- ❌ After every small change
- ❌ While work is in progress
- ❌ For testing/debugging

### Description Tips

Good descriptions help future you:
```
✅ Good:
"IFC Release - Client approved 2025-11-20. 
Includes voltage change (480V→600V) and Area 220 additions."

❌ Bad:
"Final version"
```

---

## Troubleshooting

**Problem:** Baseline creation takes too long  
**Solution:** Baseline size scales with project size. For 5000+ assets, expect 20-30 seconds.

**Problem:** Can't delete baseline  
**Solution:** Locked baselines can't be deleted. Unlock first (requires admin role).

**Problem:** Compare shows too many changes  
**Solution:** Filter by discipline or area in detailed Excel export.

**Problem:** Lost track of which baseline is current  
**Solution:** Most recent APPROVED baseline is marked (CURRENT).

---

## Related Documentation

- [Change Management (Technical)](../../.dev/roadmap/backlog/change-management.md#baselines-impact)
- [Impact Analysis Guide](../reference/impact-analysis.md)
- [Version History Guide](../reference/version-history.md)

---

**Updated:** 2025-11-24
