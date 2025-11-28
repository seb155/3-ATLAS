# Core Platform v0.2.x

Complete feature breakdown for v0.2.2 through v0.2.11.

**Goal:** Deliver all essential MBSE engineering features before moving to Multi-Tenant Auth.

---

## MVP Demo Scenario – CSV → IO → Panels

**Objective:** Have a single end‑to‑end story for v0.2.x demos, going from raw CSV to complete control architecture (instruments, cables, IO, PLCs, panels).

### Storyline (High Level)

1. **Import BBA Instrument List (CSV)**
   - Use the Modern Import Wizard to load a real `BBA-Instrument-List.csv` (≈100 instruments) into a project.
   - DevConsole V3 shows the **Import workflow** (jobs/steps, created/updated/errored rows).

2. **Rule Engine – Asset & Cable Generation**
   - Database‑driven rules auto‑create/enrich:
     - Engineering Assets (pumps, motors, instruments, etc.)
     - Power & signal cables (with tags, from/to, type, size placeholders)
   - DevConsole V3 shows the **Rule Engine workflow** with stats (rules executed, actions taken, errors).

3. **Instrument Index – IN‑P040**
   - From the same dataset, generate an **Instrument Index** package (IN‑P040):
     - Tag, Type, Service, Range, Output, Cable#, IO allocation (if available).
   - Use the Package Generation flow (v0.2.6) to export Excel/PDF, aligned with `package-generation.md`.

4. **IO Planning – IO‑P040 (by PLC)**
   - Plan IO signals per PLC / panel:
     - For each instrument: IO type (AI/AO/DI/DO), signal type, range, cable.
     - Automatic proposal of IO addresses per PLC (e.g. `PLC1:AI.0`, `PLC1:DI.5`).
   - Generate **IO‑P040 – IO List** grouped by PLC (Excel/PDF), consistent with the IO package spec.

5. **PLC & Panel Planning by Area**
   - For each **area** (via LBS / breakdown structures):
     - Plan PLC CPUs and RIO/PCP panels (e.g. PLC1‑CPU01 + PLC1‑RIO‑210A/B for Area 210).
     - Track IO capacity vs. usage per panel (e.g. “64/128 AI used”).
   - Provide a rack‑style view of panels (slots, cards, channels) with associated tags where possible.

6. **Cable & Package Overview**
   - Show **Cable Schedule** (CA‑P040) derived from generated cables.
   - Optionally include Motor Schedule (EL‑M040) as part of the same story.

### Mapping to v0.2.x Versions (Guidance)

- **v0.2.2 – UX Professional**
  - Make the end‑to‑end flow navigable and “demo‑ready” (sidebar, command palette, DevConsole integration, Import Wizard UX).
- **v0.2.3 – 3‑Tier Asset Model**
  - Ensure Engineering Assets created from CSV/rules fit into the 3‑Tier model and support later IO/PLC planning.
- **v0.2.4 – Breakdown Structures**
  - Use LBS/FBS to anchor PLCs and panels “by area” (e.g. Area 210 → PCP‑210, RIO‑210A/B).
- **v0.2.6 – Package Generation**
  - Deliver IN‑P040, CA‑P040, IO‑P040 packages in Excel/PDF, driven by the same underlying data.
- **Future sub‑feature: PLC & Panel Planning**
  - Detailed panel/rack planning (RIO/PCP) may span v0.2.6 and/or background‑processing phases when dealing with large IO counts.

---

## v0.2.2 - UX Professional

**Target:** 2025-11-29 (1 week)  
**Priority:** HIGH - Foundation for all future UI work

### Scope

#### Clickable Navigation
- All asset tags become clickable links
- Click → Opens sidebar with asset details
- Context preserved (don't lose current view)
- Browser history support (back button works)

#### Context Menus (Right-Click)
Standard actions on any asset/cable/rule:
- Copy Tag
- Edit Properties
- View Relationships
- Show in Graph (future)
- Run Rules
- Rollback Last Action
- Delete

#### Command Palette (Ctrl+K)
Quick actions accessible via keyboard:
```
Ctrl+K → Command Palette opens

Commands:
├── Go to Asset...          (g a)
├── Go to Rule...           (g r)
├── Generate Package...     (g p)
├── Run Rules on Selection  (r r)
├── Export to Excel...      (e x)
├── Open DevConsole         (d c)
└── Search Documentation    (? ?)
```

#### Keyboard Shortcuts
| Shortcut | Action |
|---------|--------|
| `Ctrl+K` | Command Palette |
| `Ctrl+B` | Toggle sidebar |
| `Ctrl+\` | Toggle DevConsole |
| `Escape` | Close panels |
| `/` | Focus search |
| `?` | Show shortcuts |

#### Professional Polish
- Consistent spacing, colors, typography
- Loading states for all async operations
- Error boundaries with user-friendly messages
- Toast notifications (success/error/info)
- Smooth transitions, micro-animations

### Technical Details

**Frontend:**
- Command Palette: `cmdk` library (React)
- Context Menus: `@radix-ui/dropdown-menu`
- Keyboard shortcuts: Global event listeners
- Toast: `react-hot-toast`

**Backend:**
- No backend changes required

### Verification Plan

1. Manual testing:
   - Click every tag in Asset/Cable/Rule grids
   - Right-click every entity type
   - Test all keyboard shortcuts
   - Verify command palette search
   - Test on multiple screen sizes

2. Frontend tests:
   ```bash
   cd apps/synapse/frontend
   npm run test -- CommandPalette.test.tsx
   npm run test -- ContextMenu.test.tsx
   ```

---

## v0.2.3 - 3-Tier Asset Model

**Target:** 2025-12-06 (1 week)  
**Priority:** HIGH - Required for procurement workflows

### Scope

#### Engineering Assets (Existing, Enriched)
Current assets become "Engineering Assets":
- Tag, Type, Service Description
- Design properties (flow, pressure, power, etc.)
- Status: DESIGN

#### Catalog Assets (NEW)
Procurement and vendor information:
- Vendor (Flowserve, ABB, Siemens, etc.)
- Model Number
- Part Number
- List Price
- Lead Time
- Datasheet URL
- Status: CATALOG

Link to Engineering Asset (Many-to-One):
- One Engineering Asset can have multiple Catalog options
- Engineer selects preferred vendor

#### Physical Assets (NEW)
As-built, installed equipment:
- Serial Number
- Install Location (detailed)
- Install Date
- Crew/Contractor
- QC Checks
- Warranty Start/End
- Status: INSTALLED, COMMISSIONED, OPERATING

Links:
- Physical → Catalog (selected vendor)
- Physical → Engineering (design basis)

#### Status Workflow
```
DESIGN → PROCURE → FABRICATION → SHIPPED → INSTALLED → TESTED → COMMISSIONED → OPERATING
```

Each status transition tracked with:
- Date/Time
- User
- Notes

### Database Schema

```sql
-- Engineering Assets (existing table enriched)
ALTER TABLE assets ADD COLUMN asset_tier VARCHAR(20) DEFAULT 'ENGINEERING';
ALTER TABLE assets ADD COLUMN status VARCHAR(20) DEFAULT 'DESIGN';

-- Catalog Assets (NEW)
CREATE TABLE catalog_assets (
    id UUID PRIMARY KEY,
    engineering_asset_id UUID REFERENCES assets(id),
    
    vendor VARCHAR(100),
    model_number VARCHAR(100),
    part_number VARCHAR(100),
    list_price DECIMAL(12,2),
    lead_time_weeks INT,
    datasheet_url TEXT,
    
    is_selected BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Physical Assets (NEW)
CREATE TABLE physical_assets (
    id UUID PRIMARY KEY,
    catalog_asset_id UUID REFERENCES catalog_assets(id),
    engineering_asset_id UUID REFERENCES assets(id),
    
    serial_number VARCHAR(100),
    install_location_detail TEXT,
    install_date DATE,
    installed_by VARCHAR(100),
    
    status VARCHAR(20) DEFAULT 'FABRICATION',
    commissioned_date DATE,
    warranty_start DATE,
    warranty_end DATE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Status History (NEW)
CREATE TABLE asset_status_history (
    id UUID PRIMARY KEY,
    asset_id UUID,
    asset_tier VARCHAR(20),
    
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT NOW(),
    notes TEXT
);
```

### UI Changes

**Asset Detail Panel:**
```
┌─ 210-PP-001 (Pump) ────────────────────────────┐
│                                                 │
│ Tabs:                                           │
│ [Engineering] [Catalog] [Physical] [History]    │
│                                                 │
│ ENGINEERING (Current View):                     │
│ - Design properties (flow, head, etc.)          │
│ - Rules applied                                 │
│ - Related assets                                │
│                                                 │
│ CATALOG (NEW):                                  │
│ Vendor Options:                                 │
│ ✓ Flowserve 3196 LTX - $45,000 (Selected)      │
│   ABB FPX 4x6 - $38,000                         │
│   KSB Etanorm - $41,000                         │
│                                                 │
│ PHYSICAL (NEW):                                 │
│ Serial: FSV-2024-00123                          │
│ Location: Area 210, Pump House, Bay 3          │
│ Installed: 2025-03-15                           │
│ Status: COMMISSIONED                            │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Verification Plan

1. Database migration:
   ```bash
   docker exec synapse-backend-1 alembic upgrade head
   docker exec synapse-backend-1 pytest tests/test_3tier_assets.py
   ```

2. API tests:
   ```bash
   curl -X POST http://localhost:8001/api/v1/catalog-assets \
     -H "Content-Type: application/json" \
     -d '{"engineering_asset_id":"...","vendor":"Flowserve",...}'
   ```

3. Frontend:
   - Create Engineering Asset
   - Add 2 Catalog options
   - Select one
   - Create Physical Asset
   - Verify all tabs display correctly

---

## v0.2.4 - Breakdown Structures

**Target:** 2025-12-13 (1 week)  
**Priority:** HIGH - Essential for project organization

### Scope

Implement 6 breakdown structures for organizing assets:

#### FBS - Functional Breakdown Structure
Organize by **WHAT** it does:
```
Process
├── Pumping
│   ├── Slurry Transfer
│   ├── Water Supply
│   └── Chemical Dosing
├── Mixing
└── Separation
```

#### LBS - Location Breakdown Structure
Organize by **WHERE** it is:
```
GoldMine Site
├── Area 100 (Crushing)
├── Area 200 (Flotation)
│   ├── Building 210 (Pump House)
│   │   ├── Ground Floor
│   │   │   ├── Bay 1
│   │   │   ├── Bay 2
│   │   │   └── Bay 3
│   │   └── Mezzanine
│   └── Building 220 (Control Room)
└── Area 300 (Tailings)
```

#### WBS - Work Breakdown Structure
Organize by **DELIVERABLE** (Package):
```
Packages
├── PKG-IN-P040 (Instruments)
├── PKG-EL-M040 (Motors)
├── PKG-CA-P040 (Cables)
└── PKG-IO-P040 (IO Lists)
```

#### OBS - Organization Breakdown Structure
Organize by **WHO** is responsible:
```
Disciplines
├── Process
├── Mechanical
├── Electrical
│   ├── Power Distribution
│   └── Lighting
└── Automation
    ├── Field Instruments
    └── Control Systems
```

#### CBS - Cost Breakdown Structure
Organize by **BUDGET CATEGORY**:
```
Budget
├── CAPEX
│   ├── Equipment
│   │   ├── Rotating (Pumps, Fans, etc.)
│   │   ├── Static (Tanks, Vessels, etc.)
│   │   └── Electrical (Motors, VFDs, etc.)
│   └── Bulk
│       ├── Cable
│       ├── Conduit
│       └── Installation
└── OPEX
    ├── Maintenance
    └── Spares
```

#### PBS - Product Breakdown Structure
Organize by **ASSEMBLY HIERARCHY**:
```
210-PP-001 (Pump Assembly)
├── 210-PP-001-PUMP (Pump)
├── 210-PP-001-SEAL (Mechanical Seal)
├── 210-PP-001-COUPLG (Coupling)
├── 210-PP-001-IMPELLER (Impeller)
└── 210-M-001 (Motor)
    ├── 210-M-001-BEARING (Bearings)
    └── 210-M-001-FAN (Cooling Fan)
```

### Database Schema

```sql
-- Generic Breakdown Structure
CREATE TABLE breakdown_structures (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    
    type VARCHAR(20), -- FBS, LBS, WBS, OBS, CBS, PBS
    name VARCHAR(100),
    code VARCHAR(50),
    parent_id UUID REFERENCES breakdown_structures(id),
    
    level INT,
    path TEXT, -- Materialized path: /100/110/111
    
    metadata JSONB, -- Type-specific data
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Asset to Structure mapping
CREATE TABLE asset_structure_links (
    id UUID PRIMARY KEY,
    asset_id UUID REFERENCES assets(id),
    structure_id UUID REFERENCES breakdown_structures(id),
    structure_type VARCHAR(20), -- FBS, LBS, WBS, etc.
    
    UNIQUE(asset_id, structure_type)
);
```

### UI Navigation

**Sidebar Structure Switcher:**
```
┌─ View By: [LBS ▼] ────────────────────┐
│ Options: FBS, LBS, WBS, OBS, CBS, PBS │
│                                        │
│ 📍 Location (LBS):                     │
│ ├─📂 GoldMine Site                     │
│ │  ├─📂 Area 100                       │
│ │  ├─📂 Area 200                       │
│ │  │  ├─📂 Building 210 (45 assets)    │
│ │  │  │  └─📦 210-PP-001 ←clicked      │
│ │  │  └─📂 Building 220                │
│ │  └─📂 Area 300                       │
└────────────────────────────────────────┘

Switch to FBS:
┌─ View By: [FBS ▼] ────────────────────┐
│                                        │
│ ⚙️ Functional (FBS):                   │
│ ├─📂 Process                           │
│ │  ├─📂 Pumping                        │
│ │  │  ├─📂 Slurry Transfer             │
│ │  │  │  └─📦 210-PP-001 ←same asset   │
│ │  │  └─📂 Water Supply                │
│ │  └─📂 Mixing                         │
└────────────────────────────────────────┘
```

### Verification Plan

1. Database:
   ```bash
   docker exec synapse-backend-1 alembic upgrade head
   docker exec synapse-backend-1 pytest tests/test_breakdown_structures.py
   ```

2. Frontend:
   - Create LBS hierarchy
   - Create FBS hierarchy
   - Link asset to both
   - Switch between views
   - Verify same asset appears in both trees

---

## Remaining Versions (v0.2.5-v0.2.11)

See detailed specs in separate backlog files:
- [search-navigation.md](search-navigation.md) - v0.2.5
- [package-generation.md](package-generation.md) - v0.2.6
- [change-management.md](change-management.md) - v0.2.7, v0.2.8
- [rule-visualization-editor.md](rule-visualization-editor.md) - v0.2.9, v0.2.10, v0.2.11

---

**Updated:** 2025-11-24
