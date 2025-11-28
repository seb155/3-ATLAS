# Lifecycle Whiteboard

**Version:** v0.3.x (Post-MVP)
**Priority:** HIGH
**Status:** SPEC COMPLETE
**Created:** 2025-11-28
**Brainstorming Session:** 2025-11-28

---

## Overview

Visual whiteboard for tracking asset lifecycle through 3 phases:
1. **Requirements** (Requis) - Engineering specifications
2. **Manufacturer Model** (Modèle Manufacturier) - Vendor equipment
3. **Field Asset** (Asset Terrain) - Installed equipment in the mine

---

## Design Decisions (Brainstorming 2025-11-28)

### UI: Option B - Vue Trident (3 Colonnes Parallèles)

Selected for:
- Clear visual link between 3 phases
- Compact view
- Same tag visible across columns
- Easy to compare phases

```
┌──────────────────────────────────────────────────────────────────────────┐
│  ASSET LIFECYCLE BOARD                          [Filter ▼] [Search]      │
├──────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │   REQUIREMENTS  │  │  MANUFACTURER   │  │   FIELD ASSET   │          │
│  │   (Engineering) │  │     MODEL       │  │    (Terrain)    │          │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤          │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │          │
│  │ │ LT-001      │ │  │ │ LT-001      │ │  │ │ LT-001      │ │          │
│  │ │ ✓ Approved  │ │  │ │ ✓ Validated │ │  │ │ ⚡ Testing  │ │          │
│  │ │ [Compare]   │ │  │ │ [Compare]   │ │  │ │ [History]   │ │          │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
└──────────────────────────────────────────────────────────────────────────┘
```

### DB: Hybrid Approach (Same Tag + FK Links)

Selected for:
- Same tag visible to user (LT-001 everywhere)
- Optional FK links for data integrity
- Flexible: can search by tag OR by relationship
- Supports edge cases (legacy assets, alternatives)

```sql
Table: assets
┌──────────────────────────────────────────────────────────────────┐
│ id       │ tag    │ phase              │ requirement_id │ model_id │
├──────────┼────────┼────────────────────┼────────────────┼──────────┤
│ uuid-001 │ LT-001 │ REQUIREMENT        │ NULL           │ NULL     │
│ uuid-002 │ LT-001 │ MANUFACTURER_MODEL │ uuid-001       │ NULL     │
│ uuid-003 │ LT-001 │ FIELD_ASSET        │ uuid-001       │ uuid-002 │
└──────────────────────────────────────────────────────────────────┘
```

### Status Change: Modal with Dropdown

Selected for:
- Clear UI, no accidental changes
- Space for notes and test results
- Audit trail integration

---

## Scope

### Core Features

1. **Trident View (3 Columns)**
   - Requirement column with review statuses
   - Manufacturer Model column with validation statuses
   - Field Asset column with mining commissioning statuses
   - Cards showing tag, description, status badge

2. **Status Management**
   - Modal for status change (dropdown)
   - Optional test type selection
   - Optional test result (PASSED/FAILED)
   - Notes field
   - Automatic audit trail

3. **Compare Modal**
   - Side-by-side Requirement vs Manufacturer specs
   - Visual indicators for met/unmet requirements
   - Export comparison button

4. **Status History**
   - Timeline view of all status changes
   - User, timestamp, notes for each change
   - Export to CSV

5. **Filters**
   - By phase (Req/Manuf/Field)
   - By status
   - By equipment type
   - By area
   - By assigned user
   - Save filter presets

---

## Status Definitions

### Requirements & Manufacturer Model (Review Workflow)

| Status | Description |
|--------|-------------|
| `DRAFT` | Initial creation |
| `NEED_REVIEW` | Ready for review |
| `IN_REVIEW` | Being reviewed |
| `CHANGES_REQUESTED` | Modifications needed |
| `APPROVED` / `VALIDATED` | Approved |
| `REJECTED` | Not approved |

### Field Asset (Mining Commissioning Workflow)

#### Phase 1: LOGISTICS
| Status | Description |
|--------|-------------|
| `ORDERED` | PO émis |
| `FABRICATION` | En fabrication |
| `SHIPPED` | En transit |
| `RECEIVED` | Arrivé au site |
| `AT_WAREHOUSE` | Stocké |

#### Phase 2: PRE-INSTALLATION
| Status | Description |
|--------|-------------|
| `STORED` | En storage |
| `INSPECTED` | Inspection OK |
| `RELEASED` | Prêt pour installation |
| `AT_LOCATION` | À l'emplacement final |

#### Phase 3: INSTALLATION
| Status | Description |
|--------|-------------|
| `MECH_INSTALL` | Montage méca en cours |
| `MECH_COMPLETE` | Méca terminé |
| `ELEC_INSTALL` | Câblage en cours |
| `ELEC_COMPLETE` | Câblage terminé |
| `PIPING_COMPLETE` | Tuyauterie OK |
| `INSTALL_COMPLETE` | Installation complète |
| `PUNCH_CLEAR` | Punch list vidée |

#### Phase 4: COMMISSIONING
| Status | Description |
|--------|-------------|
| `PRE_COMM` | Pré-commissioning |
| `COLD_COMM` | Commissioning à froid |
| `HOT_COMM` | Commissioning à chaud |
| `PERFORMANCE_TEST` | Test de performance |
| `ACCEPTED` | Accepté |

#### Phase 5: OPERATION
| Status | Description |
|--------|-------------|
| `READY` | Prêt |
| `RUNNING` | En marche |
| `STANDBY` | En attente |
| `MAINTENANCE` | En maintenance |
| `BREAKDOWN` | En panne |
| `OUT_OF_SERVICE` | Hors service |
| `DECOMMISSIONED` | Décommissionné |

---

## Test Types by Equipment

| Equipment | Tests |
|-----------|-------|
| Instrument | Bump Test, Loop Test, Calibration, HART Check |
| Motor | Megger, Rotation, Vibration, Alignment |
| Pump | Pressure, Flow, NPSH, Seal Check |
| Valve | Stroke, Leak, Positioner Cal |
| VFD | Parameters, Speed, Ramp |
| Conveyor | Belt Tracking, Speed, E-Stop, Pull Cord |
| Crusher | No-Load, Loaded, CSS Check |

---

## Technical Implementation

### Backend

#### New/Modified Tables

```sql
-- Add to assets table
ALTER TABLE assets ADD COLUMN phase VARCHAR(20) DEFAULT 'REQUIREMENT';
ALTER TABLE assets ADD COLUMN field_status VARCHAR(30);
ALTER TABLE assets ADD COLUMN review_status VARCHAR(20) DEFAULT 'DRAFT';
ALTER TABLE assets ADD COLUMN requirement_id UUID REFERENCES assets(id);
ALTER TABLE assets ADD COLUMN model_id UUID REFERENCES assets(id);
ALTER TABLE assets ADD COLUMN assigned_to UUID REFERENCES users(id);

-- Status history table
CREATE TABLE asset_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    old_status VARCHAR(30),
    new_status VARCHAR(30) NOT NULL,
    test_type VARCHAR(50),
    test_result VARCHAR(20),
    notes TEXT,
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT NOW(),
    project_id UUID NOT NULL REFERENCES projects(id)
);

CREATE INDEX idx_status_history_asset ON asset_status_history(asset_id, changed_at DESC);
CREATE INDEX idx_status_history_project ON asset_status_history(project_id);
```

#### New Endpoints

```
GET    /api/v1/lifecycle/board              Get all assets grouped by phase
GET    /api/v1/lifecycle/assets/{id}        Get asset with linked assets
POST   /api/v1/lifecycle/assets/{id}/status Change status (creates history)
GET    /api/v1/lifecycle/assets/{id}/history Get status history
GET    /api/v1/lifecycle/compare/{req_id}/{model_id}  Compare specs
POST   /api/v1/lifecycle/link               Link assets (req → model → field)
```

### Frontend

#### New Components

```
src/components/lifecycle/
├── LifecycleBoard.tsx          # Main 3-column view
├── LifecycleColumn.tsx         # Single column (Req/Manuf/Field)
├── AssetCard.tsx               # Card in column
├── StatusChangeModal.tsx       # Dropdown status change
├── CompareModal.tsx            # Side-by-side comparison
├── StatusHistoryModal.tsx      # Timeline view
├── LifecycleFilters.tsx        # Filter bar
└── index.ts
```

#### New Store

```typescript
// src/store/useLifecycleStore.ts
interface LifecycleState {
  assets: LifecycleAsset[];
  filters: LifecycleFilters;
  selectedAssetId: string | null;

  // Actions
  fetchBoard: () => Promise<void>;
  changeStatus: (assetId: string, newStatus: string, notes?: string) => Promise<void>;
  getLinkedAssets: (assetId: string) => LifecycleAsset[];
  setFilters: (filters: Partial<LifecycleFilters>) => void;
}
```

### New Route

```typescript
// Add to App.tsx routes
<Route path="/lifecycle" element={<LifecycleBoard />} />
```

### Activity Bar Integration

Add new icon in AppLayout.tsx activity bar for Lifecycle Board.

---

## Dependencies

**Blocked by:**
- v0.2.3: 3-Tier Asset Model (DB schema changes)

**Blocks:**
- Nothing (can be developed in parallel after v0.2.3)

---

## Estimation

| Task | Effort |
|------|--------|
| DB schema + migrations | 2h |
| Backend endpoints | 4h |
| Status history table + API | 2h |
| LifecycleBoard component | 4h |
| AssetCard component | 2h |
| StatusChangeModal | 2h |
| CompareModal | 3h |
| StatusHistoryModal | 2h |
| Filters + Store | 3h |
| Tests (backend + frontend) | 4h |
| **Total** | **~28h (3-4 days)** |

---

## Related Documentation

- [Asset Lifecycle Guide](../../../docs/reference/asset-lifecycle.md) - User documentation
- [3-Tier Asset Model](./3-tier-asset-model.md) - Technical foundation

---

**Created:** 2025-11-28
**Status:** Ready for implementation (post-MVP)
