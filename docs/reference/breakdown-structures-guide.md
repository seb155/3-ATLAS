# Breakdown Structures Guide

**How to organize assets using 6 different hierarchies**

---

## Overview

SYNAPSE provides **6 breakdown structures** to view the same assets from different perspectives:

| Structure | Question | Example Use |
|-----------|----------|-------------|
| **FBS** - Functional | **WHAT** does it do? | View all slurry transfer equipment |
| **LBS** - Location | **WHERE** is it? | View all equipment in Area 210 |
| **WBS** - Work/Package | **DELIVERABLE**? | View all assets in Motor Schedule |
| **OBS** - Organization | **WHO** owns it? | View all automation assets |
| **CBS** - Cost | **BUDGET**? | View all rotating equipment costs |
| **PBS** - Product | **ASSEMBLY**? | View pump assembly components |

**Key Feature:** Same asset appears in ALL relevant structures.

---

## FBS - Functional Breakdown

### What is it?

Organizes equipment by **process function** - what it does in the process.

### Example Hierarchy

```
Process
├── Crushing
│   ├── Primary Crushing
│   ├── Secondary Crushing
│   └── Screening
├── Pumping
│   ├── Slurry Transfer ← 210-PP-001 is here
│   ├── Water Supply
│   └── Chemical Dosing
├── Flotation
│   ├── Rougher Flotation
│   ├── Cleaner Flotation
│   └── Scavenger Flotation
└── Thickening
```

### When to Use

- **Process engineering** - View all equipment serving same function
- **Optimization** - Analyze crushing process separately from pumping
- **P&ID organization** - Group by process area
- **Rule execution** - Apply rules to all "Pumping" assets

### How to Navigate

1. Click **View By:** dropdown in sidebar
2. Select **FBS (Functional)**
3. Expand tree to find function
4. All assets serving that function are listed

---

## LBS - Location Breakdown

### What is it?

Organizes equipment by **physical location** - where it's installed.

### Example Hierarchy

```
GoldMine Site
├── Area 100 (Crushing)
├── Area 200 (Flotation)
│   ├── Building 210 (Pump House)
│   │   ├── Ground Floor
│   │   │   ├── Bay 1
│   │   │   ├── Bay 2
│   │   │   └── Bay 3 ← 210-PP-001 is here
│   │   └── Mezzanine
│   └── Building 220 (Control Room)
└── Area 300 (Tailings)
```

### When to Use

- **Cable routing** - Calculate lengths between locations
- **Installation planning** - Group work by building/area
- **Site access** - Find all equipment in specific location
- **Safety** - Identify equipment in hazardous areas
- **Construction progress** - Track completion by area

### How to Navigate

1. Select **LBS (Location)** from dropdown
2. Expand site → area → building → floor
3. View all assets at that location

---

## WBS - Work Breakdown (Packages)

### What is it?

Organizes assets by **engineering deliverable/package**.

### Example Hierarchy

```
Engineering Deliverables
├── Process Packages
│   ├── PKG-PR-P010 (Process Flow Diagrams)
│   └── PKG-PR-P020 (P&IDs)
├── Instrument Packages
│   ├── PKG-IN-P040 (Instrument Index) ← 210-FT-001 is here
│   ├── PKG-IN-P041 (Loop Diagrams)
│   └── PKG-IN-P042 (Installation Details)
├── Electrical Packages
│   ├── PKG-EL-M040 (Motor Schedule) ← 210-M-001 is here
│   ├── PKG-EL-V040 (VFD Schedule)
│   └── PKG-EL-L040 (Lighting Schedule)
└── Cable Packages
    ├── PKG-CA-P040 (Power Cable Schedule)
    └── PKG-CA-C040 (Control Cable Schedule)
```

### When to Use

- **Package generation** - Know which assets belong in each deliverable
- **Progress tracking** - "60% design complete" means all packages updated
- **Client submittals** - Generate specific package on demand
- **Revisions** - Track changes per package

### How to Navigate

1. Select **WBS (Work Packages)**
2. Expand package type (Instrument, Electrical, etc.)
3. Select specific package (PKG-IN-P040)
4. View all assets included in that package

---

## OBS - Organization Breakdown

### What is it?

Organizes assets by **responsible discipline/team** - who owns it.

### Example Hierarchy

```
Engineering Organization
├── Process
│   ├── Process Design
│   └── Process Safety
├── Mechanical
│   ├── Rotating Equipment
│   └── Static Equipment
├── Electrical
│   ├── Power Distribution ← 210-M-001 is here
│   ├── Lighting
│   └── Grounding
└── Automation
    ├── Field Instruments ← 210-FT-001 is here
    ├── Control Systems
    └── Communications
```

### When to Use

- **Workload distribution** - How many assets per discipline?
- **Approval workflows** - Route changes to responsible engineer
- **Resource planning** - Staffing requirements per discipline
- **Reporting** - Generate discipline-specific summaries

### How to Navigate

1. Select **OBS (Organization)**
2. Expand discipline (Electrical, Automation, etc.)
3. View all assets owned by that discipline

---

## CBS - Cost Breakdown

### What is it?

Organizes assets by **budget category** - for cost tracking.

### Example Hierarchy

```
Project Budget
├── CAPEX
│   ├── Equipment
│   │   ├── Rotating Equipment ← 210-PP-001 is here ($45,000)
│   │   ├── Static Equipment
│   │   ├── Electrical Equipment ← 210-M-001 is here ($12,000)
│   │   └── Instrumentation
│   ├── Bulk Materials
│   │   ├── Cable
│   │   ├── Conduit
│   │   └── Cable Tray
│   └── Installation
└── OPEX
    ├── Maintenance
    └── Spares
```

### When to Use

- **Budget tracking** - Total spending by category
- **Cost estimation** - Predict project cost
- **Change orders** - Calculate impact on budget
- **Procurement** - Track commitments vs. budget

### How to Navigate

1. Select **CBS (Cost)**
2. Expand budget tree (CAPEX → Equipment → Rotating)
3. View total cost for that category
4. List all assets contributing to cost

---

## PBS - Product Breakdown (Assembly)

### What is it?

Organizes assets by **assembly hierarchy** - parent/child components.

### Example Hierarchy

```
210-PP-001 (Pump Assembly)
├── 210-PP-001-PUMP (Pump)
│   ├── 210-PP-001-CASING (Casing)
│   ├── 210-PP-001-IMPELLER (Impeller)
│   ├── 210-PP-001-SHAFT (Shaft)
│   └── 210-PP-001-SEAL (Mechanical Seal)
├── 210-M-001 (Motor)
│   ├── 210-M-001-STATOR
│   ├── 210-M-001-ROTOR
│   └── 210-M-001-BEARING-DE
├── 210-PP-001-COUPLING
└── 210-PP-001-BASEPLATE
```

### When to Use

- **Spares management** - Identify replaceable components
- **Maintenance** - Track component failures
- **BOM generation** - Complete bill of materials
- **3D modeling** - Assembly structure for CAD

### How to Navigate

1. Select **PBS (Product)**
2. Expand assembly (210-PP-001)
3. View all components in assembly
4. Click component to see details

---

## Multi-Dimensional Navigation

### Example: Finding 210-PP-001 (Pump)

The same pump appears in ALL structures:

```
FBS:  Process → Pumping → Slurry Transfer
LBS:  GoldMine → Area 210 → Building 210 → Bay 3
WBS:  Engineering → Process Packages → PKG-PR-P020
OBS:  Engineering → Process → Process Design
CBS:  CAPEX → Equipment → Rotating
PBS:  210-PP-001 Assembly → 210-PP-001-PUMP
```

### Switching Structures

```
┌─ View By: [LBS ▼] ──────────────────────┐
│                                          │
│ 📍 Location (LBS):                       │
│ ├─ Area 210                              │
│ │  └─ Bay 3 (12 assets)                  │
│ │     └─ 210-PP-001 ← CURRENT            │
│                                          │
│ Click dropdown → Switch to FBS           │
│                                          │
│ ⚙️ Functional (FBS):                     │
│ ├─ Pumping                               │
│ │  └─ Slurry Transfer (8 assets)         │
│ │     └─ 210-PP-001 ← SAME ASSET         │
└──────────────────────────────────────────┘
```

**Result:** Different perspective, same asset!

---

## Best Practices

### Which Structure to Use?

**During Design:**
- Start with **LBS** (most intuitive)
- Use **FBS** for process grouping
- Use **WBS** to organize deliverables

**During Procurement:**
- Use **CBS** for budget tracking
- Use **WBS** for package generation

**During Construction:**
- Use **LBS** for installation planning
- Use **PBS** for assembly tracking

**During Operations:**
- Use **LBS** for maintenance routes
- Use **PBS** for spare parts
- Use **OBS** for work assignment

### Setting Up Structures

1. **Start with LBS** - Create location hierarchy first (most used)
2. **Add FBS** - Define process functions
3. **Add WBS** - Define deliverable packages
4. **Optional:** Add OBS, CBS, PBS as needed

### Linking Assets

**Automatic:**
- LBS: Set asset location → Auto-linked
- OBS: Asset type → Discipline mapping
- WBS: Package rules auto-assign

**Manual:**
- Right-click asset → **Link to Structure**
- Select structure type and node
- Save

---

## Common Questions

**Q: Can an asset be in multiple locations?**  
A: No, one LBS location only. Use PBS for components at different locations.

**Q: Can I create custom structures?**  
A: Not yet (v0.2.4). Future versions may support custom hierarchies.

**Q: How do I move an asset to a different structure node?**  
A: Right-click asset → **Change Structure Link** → Select new node.

**Q: What if I delete a structure node?**  
A: Assets are unlinked but not deleted. Re-link them to a new node.

**Q: Can I export a structure as Excel?**  
A: Yes! Right-click structure node → **Export to Excel**.

---

## Related Documentation

- [Breakdown Structures (Technical)](../../.dev/roadmap/backlog/breakdown-structures.md)
- [Database Schema](database-schema.md)
- [Asset Lifecycle Guide](asset-lifecycle.md)

---

**Updated:** 2025-11-24
