# 3-Tier Asset Model

**Version:** v0.2.3  
**Goal:** Support complete asset lifecycle from design through operations

---

## Overview

SYNAPSE uses a 3-tier asset model to track equipment through its complete lifecycle:

```
ENGINEERING ASSET          CATALOG ASSET              PHYSICAL ASSET
(What we DESIGN)    →     (What we BUY)         →    (What we INSTALL)
──────────────────        ──────────────────          ──────────────────
Tag: 210-PP-001           Vendor: Flowserve           Serial: FSV-2024-00123
Type: Centrifugal Pump    Model: 3196 LTX             Location: Area 210, Bay 3
Flow: 500 GPM             Part#: 3196-LTX-4x6-13      Install Date: 2025-03-15
Head: 150 ft              Price: $45,000              Condition: NEW
                          Lead Time: 12 weeks          Warranty: 2025-03-15 → 2027-03-15
```

---

## Tier 1: Engineering Assets

**Purpose:** Design phase - what we **need**

### Characteristics
- Created from P&ID ingestion or manual entry
- Contains design requirements (flow, pressure, power, etc.)
- Independent of vendor selection
- Used for calculations, cable sizing, rule execution
- Status: `DESIGN`

### Example
```json
{
  "id": "uuid-001",
  "tier": "ENGINEERING",
  "tag": "210-PP-001",
  "type": "PUMP",
  "subtype": "CENTRIFUGAL",
  "service": "Slurry Transfer",
  "properties": {
    "flow_gpm": 500,
    "head_ft": 150,
    "fluid": "Slurry",
    "temperature_f": 68,
    "npsh_available": 15
  },
  "status": "DESIGN"
}
```

### Workflow
1. Engineering Asset created (P&ID ingestion or manual)
2. Rule engine executes → creates child assets (motor, cables, etc.)
3. Engineer reviews, adjusts properties
4. Status remains `DESIGN` until procurement starts

---

## Tier 2: Catalog Assets

**Purpose:** Procurement phase - what we **buy**

### Characteristics
- Links to Engineering Asset (Many-to-One relationship)
- One Engineering Asset can have multiple Catalog options
- Contains vendor-specific information
- Used for procurement, budgeting, lead time tracking
- Status: `CATALOG`

### Example
```json
{
  "id": "uuid-cat-001",
  "tier": "CATALOG",
  "engineering_asset_id": "uuid-001",
  
  "vendor": "Flowserve",
  "model_number": "3196 LTX",
  "part_number": "3196-LTX-4x6-13",
  "list_price": 45000.00,
  "lead_time_weeks": 12,
  "datasheet_url": "https://flowserve.com/3196-ltx-datasheet.pdf",
  
  "is_selected": true,
  "status": "CATALOG"
}
```

### Workflow
1. Engineer searches vendor catalog
2. Creates Catalog Asset options (2-3 vendors for comparison)
3. Enters pricing, lead time, specs
4. Selects preferred vendor (`is_selected: true`)
5. Generates Purchase Order from selected Catalog Asset

---

## Tier 3: Physical Assets

**Purpose:** Construction/Operations phase - what we **install**

### Characteristics
- Links to both Catalog Asset (selected vendor) and Engineering Asset
- Contains as-built information
- Serial numbers, install dates, locations, commissioning data
- Used for maintenance, warranty tracking, operations
- Status: `INSTALLED`, `COMMISSIONED`, `OPERATING`, `MAINTENANCE`, `DECOMMISSIONED`

### Example
```json
{
  "id": "uuid-phy-001",
  "tier": "PHYSICAL",
  "engineering_asset_id": "uuid-001",
  "catalog_asset_id": "uuid-cat-001",
  
  "serial_number": "FSV-2024-00123",
  "install_location_detail": "Area 210, Pump House, Ground Floor, Bay 3",
  "install_date": "2025-03-15",
  "installed_by": "XYZ Construction",
  
  "commissioned_date": "2025-04-01",
  "warranty_start": "2025-04-01",
  "warranty_end": "2027-04-01",
  
  "status": "OPERATING",
  
  "qc_checks": [
    {
      "date": "2025-03-20",
      "inspector": "John Smith",
      "result": "PASS",
      "notes": "Foundation alignment verified"
    }
  ]
}
```

### Workflow
1. Equipment arrives on site
2. Create Physical Asset with serial number
3. Track installation progress
4. Record QC checks
5. Commission equipment (status → `COMMISSIONED`)
6. Handover to operations (status → `OPERATING`)

---

## Status Workflow

### Complete Lifecycle
```
DESIGN → PROCURE → FABRICATION → SHIPPED → INSTALLED → TESTED → COMMISSIONED → OPERATING
  ↑                                                                                    ↓
  └────────────────────────── MAINTENANCE ←──────────────────────────────────────────┘
```

### Status Transitions

| From | To | Trigger | Notes |
|------|-----|---------|-------|
| `DESIGN` | `PROCURE` | Catalog Asset selected | Ready to order |
| `PROCURE` | `FABRICATION` | PO issued | Vendor starts manufacturing |
| `FABRICATION` | `SHIPPED` | Equipment leaves factory | In transit |
| `SHIPPED` | `INSTALLED` | Equipment arrives + installed | Physical Asset created |
| `INSTALLED` | `TESTED` | Installation QC complete | Pre-commissioning |
| `TESTED` | `COMMISSIONED` | Commissioning complete | Ready for operations |
| `COMMISSIONED` | `OPERATING` | Handover to operations | Normal operation |
| `OPERATING` | `MAINTENANCE` | Scheduled/unscheduled work | Temporarily offline |
| `MAINTENANCE` | `OPERATING` | Maintenance complete | Return to service |
| `*` | `DECOMMISSIONED` | Permanent removal | End of life |

### Status History Tracking
Every status change is recorded:
```sql
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

Example history:
```
2025-11-10 09:00 | system        | NULL     → DESIGN        | Created from P&ID
2025-11-15 14:00 | admin         | DESIGN   → PROCURE       | Flowserve selected
2025-11-20 10:00 | procurement   | PROCURE  → FABRICATION   | PO-2025-001 issued
2025-02-15 08:00 | procurement   | FABRICATION → SHIPPED    | Tracking# ABC123
2025-03-15 12:00 | construction  | SHIPPED  → INSTALLED     | Install complete
2025-03-20 14:00 | qc_inspector  | INSTALLED → TESTED       | All checks passed
2025-04-01 09:00 | commissioning | TESTED   → COMMISSIONED  | Commissioning complete
2025-04-05 08:00 | operations    | COMMISSIONED → OPERATING | Handover complete
```

---

## Relationships

### Engineering → Catalog (One-to-Many)
One Engineering Asset can have multiple Catalog options:
```
210-PP-001 (Engineering)
├── Flowserve 3196 LTX - $45,000 (SELECTED)
├── ABB FPX 4x6 - $38,000
└── KSB Etanorm - $41,000
```

### Catalog → Physical (One-to-Many)
One Catalog Asset can have multiple Physical instances (spare pumps):
```
Flowserve 3196 LTX (Catalog)
├── Serial FSV-2024-00123 (Area 210)
├── Serial FSV-2024-00124 (Area 220) - Installed spare
└── Serial FSV-2024-00125 (Warehouse) - Warehouse spare
```

### Engineering ← Physical (Many-to-One)
Multiple Physical Assets can reference same Engineering Asset:
```
210-PP-001 (Engineering)
└── Physical Assets:
    ├── FSV-2024-00123 (Primary)
    └── FSV-2024-00124 (Installed spare)
```

---

## UI/UX

### Asset Detail Panel - Multi-Tab
```
┌─ 210-PP-001 - Centrifugal Pump ─────────────────────────────────┐
│                                                                  │
│ [Engineering] [Catalog] [Physical] [History] [Relationships]     │
│                                                                  │
│ ───────────────────────── ENGINEERING ─────────────────────────  │
│                                                                  │
│ Tag:         210-PP-001                                          │
│ Type:        PUMP → CENTRIFUGAL                                  │
│ Service:     Slurry Transfer                                     │
│ Status:      DESIGN                                              │
│                                                                  │
│ Design Properties:                                               │
│ Flow:        500 GPM                                             │
│ Head:        150 ft                                              │
│ Fluid:       Slurry (SG 1.4)                                     │
│ Temperature: 68°F                                                │
│ NPSH Avail:  15 ft                                               │
│                                                                  │
│ [Edit Properties] [Run Rules] [Generate Cable]                   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

Click [Catalog] tab:

┌─ 210-PP-001 - Catalog Options ──────────────────────────────────┐
│                                                                  │
│ [Engineering] [Catalog] [Physical] [History] [Relationships]     │
│                                                                  │
│ ─────────────────────────── CATALOG ────────────────────────────  │
│                                                                  │
│ Vendor Options:                                                  │
│                                                                  │
│ ┌─ ✓ Flowserve 3196 LTX (SELECTED) ─────────────────────────┐   │
│ │ Model:      3196 LTX                                       │   │
│ │ Part#:      3196-LTX-4x6-13                                │   │
│ │ Price:      $45,000                                        │   │
│ │ Lead Time:  12 weeks                                       │   │
│ │ Datasheet:  [Download PDF]                                 │   │
│ │ [Edit] [Unselect]                                          │   │
│ └────────────────────────────────────────────────────────────┘   │
│                                                                  │
│ ┌─ ABB FPX 4x6 ──────────────────────────────────────────────┐   │
│ │ Model:      FPX 4x6                                        │   │
│ │ Part#:      FPX-4x6-13                                     │   │
│ │ Price:      $38,000                                        │   │
│ │ Lead Time:  8 weeks                                        │   │
│ │ [Select] [Edit] [Delete]                                   │   │
│ └────────────────────────────────────────────────────────────┘   │
│                                                                  │
│ [+ Add Vendor Option]                                            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

Click [Physical] tab:

┌─ 210-PP-001 - Physical Assets ──────────────────────────────────┐
│                                                                  │
│ [Engineering] [Catalog] [Physical] [History] [Relationships]     │
│                                                                  │
│ ──────────────────────────── PHYSICAL ─────────────────────────  │
│                                                                  │
│ Installed Units:                                                 │
│                                                                  │
│ ┌─ FSV-2024-00123 (Primary) ────────────────────────────────┐   │
│ │ Serial:      FSV-2024-00123                                │   │
│ │ Location:    Area 210, Pump House, Ground Floor, Bay 3     │   │
│ │ Installed:   2025-03-15 by XYZ Construction                │   │
│ │ Commissioned: 2025-04-01                                   │   │
│ │ Status:      OPERATING                                     │   │
│ │ Warranty:    2025-04-01 → 2027-04-01                       │   │
│ │                                                            │   │
│ │ QC Checks: 3 PASSED                                        │   │
│ │ [View Details] [Edit]                                      │   │
│ └────────────────────────────────────────────────────────────┘   │
│                                                                  │
│ ┌─ FSV-2024-00124 (Installed Spare) ────────────────────────┐   │
│ │ Serial:      FSV-2024-00124                                │   │
│ │ Location:    Area 220, Warehouse                           │   │
│ │ Installed:   2025-03-20                                    │   │
│ │ Status:      STANDBY                                       │   │
│ │ [View Details] [Edit]                                      │   │
│ └────────────────────────────────────────────────────────────┘   │
│                                                                  │
│ [+ Add Physical Asset]                                           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Use Cases

### Use Case 1: New Project - Design Phase
1. Engineer imports P&ID
2. System creates Engineering Assets
3. Rule engine creates child assets (motors, cables)
4. Engineer reviews, adjusts properties
5. All assets remain in `DESIGN` status

### Use Case 2: Procurement
1. Engineer searches vendor catalogs
2. Creates 2-3 Catalog Asset options per Engineering Asset
3. Compares pricing, lead times
4. Selects preferred vendor
5. Procurement generates PO from selected Catalog Asset

### Use Case 3: Construction
1. Equipment arrives on site
2. Create Physical Asset with serial number
3. Track install progress → QC checks
4. Commission equipment
5. Handover to operations

### Use Case 4: Spares Management
1. Engineering Asset: 210-PP-001
2. Catalog Asset: Flowserve 3196 LTX (selected)
3. Physical Assets:
   - FSV-2024-00123 (Primary - OPERATING)
   - FSV-2024-00124 (Installed spare - STANDBY)
   - FSV-2024-00125 (Warehouse spare - STORAGE)

### Use Case 5: Maintenance
1. Primary pump fails
2. Update status: OPERATING → MAINTENANCE
3. Swap with installed spare
4. Installed spare: STANDBY → OPERATING
5. Repair primary pump
6. Primary pump: MAINTENANCE → STANDBY

---

## Database Schema

```sql
-- Engineering Assets (existing table, enriched)
ALTER TABLE assets 
ADD COLUMN asset_tier VARCHAR(20) DEFAULT 'ENGINEERING',
ADD COLUMN status VARCHAR(20) DEFAULT 'DESIGN';

-- Catalog Assets (NEW)
CREATE TABLE catalog_assets (
    id UUID PRIMARY KEY,
    engineering_asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
    
    vendor VARCHAR(100) NOT NULL,
    model_number VARCHAR(100),
    part_number VARCHAR(100),
    list_price DECIMAL(12,2),
    lead_time_weeks INT,
    datasheet_url TEXT,
    specifications JSONB,
    
    is_selected BOOLEAN DEFAULT FALSE,
    
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Physical Assets (NEW)
CREATE TABLE physical_assets (
    id UUID PRIMARY KEY,
    catalog_asset_id UUID REFERENCES catalog_assets(id),
    engineering_asset_id UUID REFERENCES assets(id),
    
    serial_number VARCHAR(100) UNIQUE,
    install_location_detail TEXT,
    install_date DATE,
    installed_by VARCHAR(100),
    
    status VARCHAR(20) DEFAULT 'FABRICATION',
    commissioned_date DATE,
    warranty_start DATE,
    warranty_end DATE,
    
    qc_checks JSONB,
    maintenance_history JSONB,
    
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Status History (NEW)
CREATE TABLE asset_status_history (
    id UUID PRIMARY KEY,
    asset_id UUID NOT NULL,
    asset_tier VARCHAR(20) NOT NULL,
    
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT NOW(),
    notes TEXT
);

-- Indexes
CREATE INDEX idx_catalog_engineering ON catalog_assets(engineering_asset_id);
CREATE INDEX idx_catalog_selected ON catalog_assets(is_selected) WHERE is_selected = TRUE;
CREATE INDEX idx_physical_catalog ON physical_assets(catalog_asset_id);
CREATE INDEX idx_physical_engineering ON physical_assets(engineering_asset_id);
CREATE INDEX idx_physical_serial ON physical_assets(serial_number);
CREATE INDEX idx_status_history_asset ON asset_status_history(asset_id, changed_at DESC);
```

---

## API Endpoints

### Catalog Assets
```
POST   /api/v1/catalog-assets              Create catalog option
GET    /api/v1/catalog-assets/{id}         Get catalog asset
PUT    /api/v1/catalog-assets/{id}         Update catalog asset
DELETE /api/v1/catalog-assets/{id}         Delete catalog option
POST   /api/v1/catalog-assets/{id}/select  Select this vendor
GET    /api/v1/engineering-assets/{id}/catalog  List all catalog options
```

### Physical Assets
```
POST   /api/v1/physical-assets             Create physical asset
GET    /api/v1/physical-assets/{id}        Get physical asset
PUT    /api/v1/physical-assets/{id}        Update physical asset
DELETE /api/v1/physical-assets/{id}        Delete physical asset
POST   /api/v1/physical-assets/{id}/status Change status
POST   /api/v1/physical-assets/{id}/qc     Add QC check
GET    /api/v1/engineering-assets/{id}/physical  List all physical instances
```

### Status History
```
GET    /api/v1/assets/{id}/status-history  Get status history
POST   /api/v1/assets/{id}/status          Change status (creates history)
```

---

## Migration Strategy

1. **Database migration:**
   ```bash
   alembic revision -m "Add 3-tier asset model"
   alembic upgrade head
   ```

2. **Existing assets:**
   - All existing assets become Engineering Assets
   - `asset_tier = 'ENGINEERING'`
   - `status = 'DESIGN'`

3. **Backwards compatibility:**
   - Existing API endpoints still work
   - New endpoints for Catalog/Physical

4. **Gradual adoption:**
   - Users can continue using Engineering Assets only
   - Catalog/Physical tiers are optional
   - Full adoption during procurement/construction phases

---

## Future Enhancements

### v0.4.0+
- Vendor catalog integration (import vendor data)
- Automated purchase order generation
- Shipping tracking integration
- Mobile app for field QC checks
- Predictive maintenance (OPERATING → MAINTENANCE forecasting)

---

**Updated:** 2025-11-24
