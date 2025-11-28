# Breakdown Structures

**Version:** v0.2.4  
**Goal:** Organize assets using multiple hierarchical structures for different views

---

## Overview

SYNAPSE supports 6 different breakdown structures to organize the same assets from different perspectives:

| Structure | Organizes By | Example |
|-----------|--------------|---------|
| **FBS** - Functional | WHAT it does | Process → Pumping → Slurry Transfer |
| **LBS** - Location | WHERE it is | Site → Area 210 → Building → Floor → Bay |
| **WBS** - Work/Package | DELIVERABLE | Packages → PKG-IN-P040 (Instruments) |
| **OBS** - Organization | WHO is responsible | Disciplines → Electrical → Power |
| **CBS** - Cost | BUDGET CATEGORY | CAPEX → Equipment → Rotating |
| **PBS** - Product | ASSEMBLY HIERARCHY | Pump Assembly → Pump → Seal → Impeller |

**Key Feature:** Same asset appears in ALL relevant structures (Multi-dimensional navigation)

---

## FBS - Functional Breakdown Structure

**Purpose:** Organize by **process function** (WHAT it does)

### Example: Mining Project
```
Process
├── Crushing
│   ├── Primary Crushing
│   ├── Secondary Crushing
│   └── Screening
├── Pumping
│   ├── Slurry Transfer
│   │   └── 210-PP-001 (Pump) ← Asset here
│   ├── Water Supply
│   └── Chemical Dosing
├── Flotation
│   ├── Rougher Flotation
│   ├── Cleaner Flotation
│   └── Scavenger Flotation
├── Thickening
└── Tailings Management
```

### Use Cases
- **Process engineering:** View all slurry transfer equipment
- **Optimization:** Analyze all crushing process assets together
- **Documentation:** Generate P&IDs grouped by process function
- **Rule execution:** Apply rules to all "Pumping" assets

### Schema
```json
{
  "id": "fbs-001",
  "type": "FBS",
  "code": "PROC-PUMP-SLURRY",
  "name": "Slurry Transfer",
  "parent_id": "fbs-pumping",
  "level": 3,
  "path": "/process/pumping/slurry-transfer",
  "metadata": {
    "process_type": "CONTINUOUS",
    "criticality": "HIGH"
  }
}
```

---

## LBS - Location Breakdown Structure

**Purpose:** Organize by **physical location** (WHERE it is)

### Example: Mining Site
```
GoldMine Site
├── Area 100 - Crushing Plant
│   ├── Building 110 - Primary Crusher
│   │   ├── Ground Floor
│   │   └── Maintenance Level
│   └── Building 120 - Secondary Crusher
├── Area 200 - Flotation
│   ├── Building 210 - Pump House
│   │   ├── Ground Floor
│   │   │   ├── Bay 1
│   │   │   ├── Bay 2
│   │   │   └── Bay 3
│   │   │       └── 210-PP-001 (Pump) ← Asset here
│   │   └── Mezzanine
│   ├── Building 220 - Control Room
│   └── Outdoor Area 230 - Tank Farm
├── Area 300 - Tailings
└── Area 400 - Utilities
    ├── Electrical Room
    ├── Compressor Room
    └── Workshop
```

### Use Cases
- **Cable routing:** Calculate cable lengths between locations
- **Installation:** Group work by building/area
- **Maintenance:** Access all equipment in Area 210
- **Safety:** Identify equipment in hazardous areas
- **Construction:** Track progress by area

### Schema
```json
{
  "id": "lbs-001",
  "type": "LBS",
  "code": "AREA-210-BAY-3",
  "name": "Bay 3",
  "parent_id": "lbs-210-ground",
  "level": 5,
  "path": "/goldmine/area-200/building-210/ground-floor/bay-3",
  "metadata": {
    "area_classification": "GENERAL",
    "access_restrictions": [],
    "coordinates": {"x": 1234, "y": 5678}
  }
}
```

---

## WBS - Work Breakdown Structure

**Purpose:** Organize by **engineering deliverable/package** (Work Package)

### Example: Engineering Packages
```
Engineering Deliverables
├── Process Packages
│   ├── PKG-PR-P010 - Process Flow Diagrams
│   └── PKG-PR-P020 - P&IDs
├── Instrument Packages
│   ├── PKG-IN-P040 - Instrument Index
│   │   └── 210-FT-001 (Flow Transmitter) ← Asset here
│   ├── PKG-IN-P041 - Loop Diagrams
│   └── PKG-IN-P042 - Installation Details
├── Electrical Packages
│   ├── PKG-EL-M040 - Motor Schedule
│   │   └── 210-M-001 (Motor) ← Asset here
│   ├── PKG-EL-V040 - VFD Schedule
│   └── PKG-EL-L040 - Lighting Schedule
├── Cable Packages
│   ├── PKG-CA-P040 - Power Cable Schedule
│   └── PKG-CA-C040 - Control Cable Schedule
├── IO Packages
│   └── PKG-IO-P040 - IO List (by PLC)
└── BOM Packages
    └── PKG-BID-LST - Bill of Materials
```

### Use Cases
- **Package generation:** Generate Excel/PDF deliverables
- **Progress tracking:** "60% design - all packages updated"
- **Revisions:** Track changes per package
- **Deliverable management:** Know which assets belong to which package

### Schema
```json
{
  "id": "wbs-001",
  "type": "WBS",
  "code": "PKG-IN-P040",
  "name": "Instrument Index",
  "parent_id": "wbs-instrument-packages",
  "level": 2,
  "path": "/engineering/instrument-packages/in-p040",
  "metadata": {
    "discipline": "AUTOMATION",
    "template": "EPCB-IN-P040-Template.xlsx",
    "revision": "B",
    "last_generated": "2025-11-20"
  }
}
```

---

## OBS - Organization Breakdown Structure

**Purpose:** Organize by **responsible discipline/team** (WHO owns it)

### Example: Engineering Disciplines
```
Engineering Organization
├── Process
│   ├── Process Design
│   └── Process Safety
├── Mechanical
│   ├── Rotating Equipment
│   └── Static Equipment
├── Electrical
│   ├── Power Distribution
│   │   └── 210-M-001 (Motor) ← Asset here
│   ├── Lighting
│   └── Grounding
├── Automation
│   ├── Field Instruments
│   │   └── 210-FT-001 (Flow Transmitter) ← Asset here
│   ├── Control Systems
│   │   ├── PLC Programming
│   │   └── SCADA
│   └── Communications
├── Civil/Structural
└── Piping
```

### Use Cases
- **Workload distribution:** How many assets per discipline?
- **Approval workflows:** Route changes to responsible discipline
- **Reporting:** Generate discipline-specific reports
- **Resource planning:** Staffing requirements per discipline

### Schema
```json
{
  "id": "obs-001",
  "type": "OBS",
  "code": "EL-PWR",
  "name": "Power Distribution",
  "parent_id": "obs-electrical",
  "level": 2,
  "path": "/engineering/electrical/power-distribution",
  "metadata": {
    "lead_engineer": "john.smith@aurumax.com",
    "team_size": 3,
    "budget_code": "EL-PWR-2025"
  }
}
```

---

## CBS - Cost Breakdown Structure

**Purpose:** Organize by **budget category** (CAPEX/OPEX tracking)

### Example: Project Budget
```
Project Budget
├── CAPEX
│   ├── Equipment
│   │   ├── Rotating Equipment
│   │   │   └── 210-PP-001 (Pump) ← Asset here ($45,000)
│   │   ├── Static Equipment
│   │   ├── Electrical Equipment
│   │   │   └── 210-M-001 (Motor) ← Asset here ($12,000)
│   │   └── Instrumentation
│   ├── Bulk Materials
│   │   ├── Cable
│   │   ├── Conduit
│   │   ├── Cable Tray
│   │   └── Terminals
│   ├── Installation
│   │   ├── Mechanical Installation
│   │   ├── Electrical Installation
│   │   └── Commissioning
│   └── Engineering
├── OPEX
│   ├── Maintenance
│   │   ├── Preventive Maintenance
│   │   └── Corrective Maintenance
│   └── Spares
└── Contingency
```

### Use Cases
- **Budget tracking:** Total CAPEX by category
- **Cost estimation:** Predict project cost
- **Change orders:** Impact of scope changes on budget
- **Procurement:** Track spending by category

### Schema
```json
{
  "id": "cbs-001",
  "type": "CBS",
  "code": "CAPEX-EQ-ROT",
  "name": "Rotating Equipment",
  "parent_id": "cbs-capex-equipment",
  "level": 3,
  "path": "/budget/capex/equipment/rotating",
  "metadata": {
    "budget_allocated": 500000,
    "budget_spent": 245000,
    "budget_committed": 180000,
    "budget_remaining": 75000
  }
}
```

---

## PBS - Product Breakdown Structure

**Purpose:** Organize by **assembly hierarchy** (Parent → Child components)

### Example: Pump Assembly
```
210-PP-001 (Pump Assembly)
├── 210-PP-001-PUMP (Pump)
│   ├── 210-PP-001-CASING (Casing)
│   ├── 210-PP-001-IMPELLER (Impeller)
│   ├── 210-PP-001-SHAFT (Shaft)
│   └── 210-PP-001-SEAL (Mechanical Seal)
│       ├── 210-PP-001-SEAL-STAT (Stationary Ring)
│       └── 210-PP-001-SEAL-ROT (Rotating Ring)
├── 210-M-001 (Motor)
│   ├── 210-M-001-STATOR (Stator)
│   ├── 210-M-001-ROTOR (Rotor)
│   ├── 210-M-001-BEARING-DE (Drive End Bearing)
│   └── 210-M-001-BEARING-NDE (Non-Drive End Bearing)
├── 210-PP-001-COUPLING (Coupling)
├── 210-PP-001-BASEPLATE (Baseplate)
└── 210-PP-001-GUARD (Coupling Guard)
```

### Use Cases
- **Spares management:** Identify replaceable components
- **Maintenance:** Track component failures
- **BOM generation:** Complete bill of materials
- **3D modeling:** Assembly structure for CAD

### Schema
```json
{
  "id": "pbs-001",
  "type": "PBS",
  "code": "210-PP-001-SEAL",
  "name": "Mechanical Seal",
  "parent_id": "pbs-210-pp-001-pump",
  "level": 3,
  "path": "/assemblies/210-pp-001/pump/seal",
  "metadata": {
    "component_type": "CONSUMABLE",
    "mtbf_hours": 8760,
    "spare_qty": 2,
    "vendor": "John Crane"
  }
}
```

---

## Multi-Dimensional Navigation

**Key Feature:** Same asset exists in ALL relevant structures

### Example: 210-PP-001 (Pump)

```
┌─────────────────────────────────────────────────────────────┐
│ Asset: 210-PP-001 (Centrifugal Pump)                        │
│                                                              │
│ This asset appears in:                                       │
│                                                              │
│ FBS:  Process → Pumping → Slurry Transfer                   │
│ LBS:  GoldMine → Area 210 → Building 210 → Ground → Bay 3   │
│ WBS:  Engineering → Process Packages → PKG-PR-P020          │
│ OBS:  Engineering → Process → Process Design                │
│ CBS:  CAPEX → Equipment → Rotating Equipment                │
│ PBS:  210-PP-001 Assembly → 210-PP-001-PUMP                 │
│                                                              │
│ [Switch View] [Show in Tree]                                 │
└─────────────────────────────────────────────────────────────┘
```

### UI Implementation

**Sidebar with Structure Switcher:**
```
┌─ View By: [LBS ▼] ────────────────────────────────┐
│                                                    │
│ 📍 Location (LBS):                                 │
│ ├─📂 GoldMine Site                                 │
│ │  ├─📂 Area 100                                   │
│ │  ├─📂 Area 200                                   │
│ │  │  ├─📂 Building 210 (45 assets)                │
│ │  │  │  ├─📂 Ground Floor                         │
│ │  │  │  │  ├─📂 Bay 1                             │
│ │  │  │  │  ├─📂 Bay 2                             │
│ │  │  │  │  └─📂 Bay 3 (12 assets)                 │
│ │  │  │  │     ├─📦 210-PP-001 ← SELECTED          │
│ │  │  │  │     ├─📦 210-M-001                      │
│ │  │  │  │     └─📦 210-VFD-001                    │
│ │  │  │  └─📂 Mezzanine                            │
│ │  │  └─📂 Building 220                            │
│ │  └─📂 Area 300                                   │
└────────────────────────────────────────────────────┘

User clicks dropdown → Switch to FBS:

┌─ View By: [FBS ▼] ────────────────────────────────┐
│                                                    │
│ ⚙️ Functional (FBS):                               │
│ ├─📂 Process                                       │
│ │  ├─📂 Crushing                                   │
│ │  ├─📂 Pumping                                    │
│ │  │  ├─📂 Slurry Transfer (8 assets)              │
│ │  │  │  └─📦 210-PP-001 ← SAME ASSET              │
│ │  │  ├─📂 Water Supply                            │
│ │  │  └─📂 Chemical Dosing                         │
│ │  └─📂 Flotation                                  │
└────────────────────────────────────────────────────┘
```

---

## Database Schema

### Generic Breakdown Structure Table
```sql
CREATE TABLE breakdown_structures (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    
    type VARCHAR(20) NOT NULL, -- FBS, LBS, WBS, OBS, CBS, PBS
    code VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    
    parent_id UUID REFERENCES breakdown_structures(id) ON DELETE CASCADE,
    level INT NOT NULL,
    path TEXT NOT NULL, -- Materialized path: /area-200/building-210/bay-3
    
    metadata JSONB, -- Type-specific fields
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(project_id, type, code)
);

-- Asset to Structure Links (Many-to-Many)
CREATE TABLE asset_structure_links (
    id UUID PRIMARY KEY,
    asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
    structure_id UUID REFERENCES breakdown_structures(id) ON DELETE CASCADE,
    structure_type VARCHAR(20) NOT NULL,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(asset_id, structure_id)
);

-- Indexes
CREATE INDEX idx_breakdown_project ON breakdown_structures(project_id, type);
CREATE INDEX idx_breakdown_parent ON breakdown_structures(parent_id);
CREATE INDEX idx_breakdown_path ON breakdown_structures(path);
CREATE INDEX idx_asset_links_asset ON asset_structure_links(asset_id);
CREATE INDEX idx_asset_links_structure ON asset_structure_links(structure_id);
CREATE INDEX idx_asset_links_type ON asset_structure_links(structure_type);
```

### Example Data

```sql
-- LBS: GoldMine Site → Area 200 → Building 210 → Ground Floor → Bay 3
INSERT INTO breakdown_structures VALUES
  ('lbs-site', 'proj-001', 'LBS', 'SITE', 'GoldMine Site', NULL, 1, '/goldmine', '{}'),
  ('lbs-200', 'proj-001', 'LBS', 'AREA-200', 'Area 200', 'lbs-site', 2, '/goldmine/area-200', '{}'),
  ('lbs-210', 'proj-001', 'LBS', 'B-210', 'Building 210', 'lbs-200', 3, '/goldmine/area-200/building-210', '{}'),
  ('lbs-210-gf', 'proj-001', 'LBS', 'GF', 'Ground Floor', 'lbs-210', 4, '/goldmine/area-200/building-210/ground-floor', '{}'),
  ('lbs-bay3', 'proj-001', 'LBS', 'BAY-3', 'Bay 3', 'lbs-210-gf', 5, '/goldmine/area-200/building-210/ground-floor/bay-3', '{}');

-- FBS: Process → Pumping → Slurry Transfer
INSERT INTO breakdown_structures VALUES
  ('fbs-proc', 'proj-001', 'FBS', 'PROCESS', 'Process', NULL, 1, '/process', '{}'),
  ('fbs-pump', 'proj-001', 'FBS', 'PUMPING', 'Pumping', 'fbs-proc', 2, '/process/pumping', '{}'),
  ('fbs-slurry', 'proj-001', 'FBS', 'SLURRY', 'Slurry Transfer', 'fbs-pump', 3, '/process/pumping/slurry-transfer', '{}');

-- Link asset 210-PP-001 to both LBS and FBS
INSERT INTO asset_structure_links VALUES
  (uuid(), 'asset-210-pp-001', 'lbs-bay3', 'LBS'),
  (uuid(), 'asset-210-pp-001', 'fbs-slurry', 'FBS');
```

---

## API Endpoints

```
# Breakdown Structures
POST   /api/v1/breakdown-structures                 Create structure node
GET    /api/v1/breakdown-structures/{id}            Get node details
PUT    /api/v1/breakdown-structures/{id}            Update node
DELETE /api/v1/breakdown-structures/{id}            Delete node
GET    /api/v1/breakdown-structures?type=LBS        List all nodes by type
GET    /api/v1/breakdown-structures/{id}/children   Get child nodes
POST   /api/v1/breakdown-structures/{id}/move       Move node to new parent

# Asset Links
POST   /api/v1/assets/{id}/link-structure           Link asset to structure
DELETE /api/v1/assets/{id}/unlink-structure         Unlink asset
GET    /api/v1/assets/{id}/structures               Get all structure links for asset
GET    /api/v1/breakdown-structures/{id}/assets     Get all assets in this structure node
```

---

## Use Case: Multi-Structure Navigation

**Scenario:** Engineer viewing 210-PP-001

1. **Default view:** LBS (Location)
   - Path: GoldMine → Area 200 → Building 210 → Ground Floor → Bay 3
   - Shows: All 12 assets in Bay 3

2. **Switch to FBS:**
   - Path: Process → Pumping → Slurry Transfer
   - Shows: All 8 slurry transfer pumps (across all areas)

3. **Switch to WBS:**
   - Path: Engineering → Process Packages → PKG-PR-P020
   - Shows: All assets in this P&ID package

4. **Switch to OBS:**
   - Path: Engineering → Process → Process Design
   - Shows: All process-owned assets

5. **Switch to CBS:**
   - Path: CAPEX → Equipment → Rotating
   - Shows: All rotating equipment with costs

6. **Switch to PBS:**
   - Path: 210-PP-001 Assembly → Pump
   - Shows: All components of this pump assembly

---

## Migration Strategy

1. **Create structure definitions first:**
   ```bash
   POST /api/v1/breakdown-structures
   # Create full hierarchy for each type (LBS, FBS, etc.)
   ```

2. **Link existing assets:**
   ```bash
   POST /api/v1/assets/{id}/link-structure
   # Link each asset to relevant structures
   ```

3. **Gradual adoption:**
   - Start with LBS (most intuitive for users)
   - Add FBS and WBS as needed
   - OBS/CBS/PBS optional (advanced use)

## Future Enhancements

### v0.3.0+
- Import structures from Excel
- Auto-link assets based on rules (tag pattern → structure)
- Structure templates (common LBS/FBS patterns)
- Cross-project structure reuse

---

**Updated:** 2025-11-24
