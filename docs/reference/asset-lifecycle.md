# Asset Lifecycle Guide

**User Guide for the 3-Tier Asset Model & Lifecycle Whiteboard**

---

## Overview

SYNAPSE tracks equipment through its complete lifecycle using a **3-tier model**:

1. **Requirements** (Requis) - Design phase (what you NEED)
2. **Manufacturer Model** (Modèle Manufacturier) - Procurement phase (what you BUY)
3. **Field Asset** (Asset Terrain) - Construction/Operations phase (what you INSTALL)

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ REQUIREMENT │  ──► │ MANUFACTURER│  ──► │ FIELD ASSET │
│  (Design)   │      │   MODEL     │      │  (Terrain)  │
└─────────────┘      └─────────────┘      └─────────────┘
 "Ce qu'on veut"    "Ce qu'on achète"   "Ce qui est installé"
```

---

## Lifecycle Whiteboard (Vue Trident)

The Lifecycle Whiteboard provides a **3-column parallel view** to track assets through all phases:

```
┌──────────────────────────────────────────────────────────────────────────┐
│  ASSET LIFECYCLE BOARD                          [Filter ▼] [Search]      │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │   REQUIREMENTS  │  │  MANUFACTURER   │  │   FIELD ASSET   │          │
│  │   (Engineering) │  │     MODEL       │  │    (Terrain)    │          │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤          │
│  │                 │  │                 │  │                 │          │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │          │
│  │ │ LT-001      │ │  │ │ LT-001      │ │  │ │ LT-001      │ │          │
│  │ │ Level Trans │ │  │ │ Rosemount   │ │  │ │ Tank Farm   │ │          │
│  │ │ ✓ Approved  │ │  │ │ ✓ Validated │ │  │ │ ⚡ Testing  │ │          │
│  │ │ [Compare]   │ │  │ │ [Compare]   │ │  │ │ [History]   │ │          │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Key Features

- **Same Tag Across Phases:** LT-001 appears in all 3 columns when linked
- **Visual Status Badges:** Quick identification of asset state
- **Compare Button:** Side-by-side comparison of Requirement vs Manufacturer specs
- **History Button:** View complete status change timeline
- **Filters:** By phase, status, type, area, assigned user

---

## Requirements (Design Phase)

### What are Requirements?

Requirements represent your **design intent** - the equipment specifications needed to meet process requirements.

**Created from:**
- P&ID ingestion
- Manual entry
- Rule engine (e.g., pump creates motor automatically)

**Contains:**
- Tag number (e.g., `LT-001`)
- Type and subtype
- Service description
- Design properties (flow, pressure, power, etc.)
- Location (area, building)

### Review Workflow

| Status | Description |
|--------|-------------|
| `DRAFT` | Initial creation, incomplete |
| `NEED_REVIEW` | Ready for engineer review |
| `IN_REVIEW` | Currently being reviewed |
| `CHANGES_REQUESTED` | Modifications needed |
| `APPROVED` | Validated and approved |
| `REJECTED` | Not approved |

### Example

```
Tag: LT-001
Type: LEVEL_TRANSMITTER
Service: Tank 1 Level Measurement
Range: 0-10m
Accuracy: ±0.1%
Output: 4-20mA
Status: APPROVED
```

---

## Manufacturer Model (Procurement Phase)

### What are Manufacturer Models?

Manufacturer Models represent **vendor options** - specific manufacturer models that meet your engineering requirements.

**Created by:**
- Manual entry from vendor datasheets
- Vendor catalog search (future)
- Copy from previous project (future)

**Contains:**
- Vendor name (Emerson, ABB, Siemens, etc.)
- Model number and part number
- List price
- Lead time
- Datasheet link
- Technical specifications

### Review Workflow

Same as Requirements:
| Status | Description |
|--------|-------------|
| `DRAFT` | Initial entry |
| `NEED_REVIEW` | Ready for review |
| `IN_REVIEW` | Being reviewed |
| `CHANGES_REQUESTED` | Needs corrections |
| `VALIDATED` | Specs match requirements |
| `REJECTED` | Does not meet requirements |

### Example

```
Tag: LT-001
Vendor: Emerson
Model: Rosemount 5300
Part#: 5300-2C4ABCDEFG
Range: 0-15m (meets 0-10m requirement)
Accuracy: ±0.075% (exceeds requirement)
Price: $3,500
Lead Time: 6 weeks
Status: VALIDATED
```

---

## Field Asset (Terrain - Mining Commissioning)

### What are Field Assets?

Field Assets represent **actual installed equipment** - the real hardware on site in the mine.

**Created when:**
- Equipment arrives on site
- Installation begins

**Contains:**
- Serial number (from equipment nameplate)
- As-built location (exact position)
- Install date and crew
- Commissioning data
- Test records

### Mining Commissioning Workflow

Field assets follow a **5-phase lifecycle** specific to mining operations:

```
LOGISTICS → PRE-INSTALL → INSTALLATION → COMMISSIONING → OPERATION
```

#### Phase 1: LOGISTICS (Approvisionnement)

| Status | Description |
|--------|-------------|
| `ORDERED` | PO émis au fournisseur |
| `FABRICATION` | En fabrication chez le manufacturier |
| `SHIPPED` | En transit vers le site |
| `RECEIVED` | Arrivé au site, inspection réception |
| `AT_WAREHOUSE` | Stocké, en attente d'installation |

#### Phase 2: PRE-INSTALLATION (Préparation)

| Status | Description |
|--------|-------------|
| `STORED` | En storage, protégé |
| `INSPECTED` | Inspection visuelle/dimensionnelle OK |
| `RELEASED` | Prêt pour installation (matériel complet) |
| `AT_LOCATION` | Transporté à l'emplacement final |

#### Phase 3: INSTALLATION (Montage)

| Status | Description |
|--------|-------------|
| `MECH_INSTALL` | Montage mécanique en cours |
| `MECH_COMPLETE` | Boulonnage, alignement fait |
| `ELEC_INSTALL` | Câblage en cours |
| `ELEC_COMPLETE` | Câblage terminé, méggé |
| `PIPING_COMPLETE` | Raccordements process faits |
| `INSTALL_COMPLETE` | Tout raccordé, punch list créée |
| `PUNCH_CLEAR` | Tous les items de punch list corrigés |

#### Phase 4: COMMISSIONING (Mise en service)

| Status | Description |
|--------|-------------|
| `PRE_COMM` | Vérifications avant énergisation |
| `COLD_COMM` | Tests sans procédé (dry run) |
| `HOT_COMM` | Tests avec procédé réel |
| `PERFORMANCE_TEST` | Validation des specs |
| `ACCEPTED` | Handover à l'opération |

#### Phase 5: OPERATION (Exploitation)

| Status | Description |
|--------|-------------|
| `READY` | Disponible mais pas en marche |
| `RUNNING` | En opération normale |
| `STANDBY` | Arrêt temporaire planifié |
| `MAINTENANCE` | Arrêt pour entretien |
| `BREAKDOWN` | Arrêt non planifié (panne) |
| `OUT_OF_SERVICE` | Retiré temporairement |
| `DECOMMISSIONED` | Retiré définitivement |

---

## Tests by Equipment Type

The **test type** is tracked separately from status, allowing flexibility per equipment:

| Equipment Type | Typical Tests |
|----------------|---------------|
| **Instrument** | Bump Test, Loop Test, Calibration, HART Check |
| **Motor** | Megger, Rotation Check, Vibration, Alignment |
| **Pump** | Pressure Test, Flow Test, NPSH, Seal Check |
| **Valve** | Stroke Test, Leak Test, Positioner Cal |
| **VFD** | Parameter Check, Speed Test, Ramp Test |
| **Conveyor** | Belt Tracking, Speed, E-Stop, Pull Cord |
| **Crusher** | No-Load, Loaded, CSS Check |

---

## Linking Assets (DB Architecture)

### Hybrid Approach

Assets use the **same tag** visually with **optional FK links** in the database:

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

**Search options:**
- By tag: `WHERE tag = 'LT-001'` → Returns all 3 phases
- By link: `WHERE requirement_id = 'uuid-001'` → Returns linked assets

### Supported Scenarios

| Scenario | How it Works |
|----------|--------------|
| 1 Req → 1 Manuf → 1 Field | Normal case, same tag, linked in DB |
| 1 Req → 2 Manuf (alternatives) | Same tag, 2 models point to same Req |
| Field without Req (legacy) | Tag exists, `requirement_id = NULL` |
| Req without Field (not installed yet) | Normal, Field will be created later |
| Model change | Update `model_id` on Field Asset |

---

## Compare Modal

Compare Requirements vs Manufacturer Model specs side-by-side:

```
┌─────────────────────────────────────────────────────────────────┐
│  Compare: LT-001                                           [X]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────┐  ┌─────────────────────────┐      │
│  │     REQUIREMENT         │  │   MANUFACTURER MODEL    │      │
│  ├─────────────────────────┤  ├─────────────────────────┤      │
│  │ Range: 0-10m            │  │ Range: 0-15m        ✓   │      │
│  │ Accuracy: ±0.1%         │  │ Accuracy: ±0.075%   ✓   │      │
│  │ Output: 4-20mA          │  │ Output: 4-20mA      ✓   │      │
│  │ Power: 24VDC            │  │ Power: 24VDC        ✓   │      │
│  │ Material: SS316         │  │ Material: SS316L    ✓   │      │
│  │ Temp: -20 to 80°C       │  │ Temp: -40 to 100°C  ✓   │      │
│  │ IP Rating: IP67         │  │ IP Rating: IP68     ✓   │      │
│  └─────────────────────────┘  └─────────────────────────┘      │
│                                                                 │
│  ✓ All requirements met                                        │
│                                                                 │
│                              [Close]    [Export Comparison]     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Status History (Audit Trail)

Every status change is recorded with timestamp, user, and notes:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Status History: LT-001                                                [X]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ 2025-11-28 14:32 ─────────────────────────────────────────────────┐    │
│  │ COLD_COMM → HOT_COMM                                                │    │
│  │ By: Jean Tremblay                                                   │    │
│  │ Notes: Cold comm completed. Starting hot commissioning with slurry. │    │
│  │ Test: Loop Test - PASSED                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─ 2025-11-25 09:15 ─────────────────────────────────────────────────┐    │
│  │ PRE_COMM → COLD_COMM                                                │    │
│  │ By: Marie Gagnon                                                    │    │
│  │ Notes: Pre-comm checklist complete. All I/O verified.               │    │
│  │ Test: Bump Test - PASSED                                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  [Show All 12 entries...]                                                   │
│                                                                             │
│                                               [Export CSV]    [Close]       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Status Change Modal

Change status via dropdown with optional notes:

```
┌────────────────────────────────────────────────┐
│  Update Status: LT-001                    [X]  │
├────────────────────────────────────────────────┤
│                                                │
│  Current: COLD_COMM                            │
│                                                │
│  New Status:                                   │
│  ┌──────────────────────────────────────┐     │
│  │ HOT_COMM                           ▼ │     │
│  └──────────────────────────────────────┘     │
│                                                │
│  Test Type (optional):                         │
│  ┌──────────────────────────────────────┐     │
│  │ Loop Test                          ▼ │     │
│  └──────────────────────────────────────┘     │
│                                                │
│  Test Result:                                  │
│  ┌──────────────────────────────────────┐     │
│  │ PASSED                             ▼ │     │
│  └──────────────────────────────────────┘     │
│                                                │
│  Notes:                                        │
│  ┌──────────────────────────────────────┐     │
│  │ Loop test completed successfully.    │     │
│  │ Ready for SAT next week.             │     │
│  └──────────────────────────────────────┘     │
│                                                │
│           [Cancel]         [Save Changes]      │
└────────────────────────────────────────────────┘
```

---

## Filters

Filter assets by multiple criteria:

```
┌────────────────────────────────────────────────────────────────┐
│ Filters:                                                       │
│                                                                │
│ Phase:        [All ▼]  [Requirement] [Manufacturer] [Field]    │
│ Status:       [All ▼]  [Approved] [In Review] [Testing] ...    │
│ Type:         [All ▼]  [Instrument] [Motor] [Valve] [Pump]     │
│ Area:         [All ▼]  [Process] [Utilities] [Grinding]        │
│ Assigned To:  [All ▼]  [Jean] [Marie] [Unassigned]             │
│                                                                │
│ [Clear Filters]                           [Save as Preset ▼]   │
└────────────────────────────────────────────────────────────────┘
```

---

## Best Practices

### Requirements Phase

✅ **DO:**
- Use consistent tag numbering
- Fill in all required properties
- Apply rules early to create child assets
- Review auto-generated assets

❌ **DON'T:**
- Skip service descriptions
- Leave location blank
- Forget to run rules

### Manufacturer Model Phase

✅ **DO:**
- Get 2-3 vendor quotes minimum
- Record lead times accurately
- Attach datasheets
- Validate against requirements

❌ **DON'T:**
- Order without comparison
- Skip lead time entry
- Forget to compare specs

### Field Asset Phase

✅ **DO:**
- Record serial numbers immediately
- Document exact location
- Update status as work progresses
- Add test results with notes

❌ **DON'T:**
- Wait until end to update status
- Skip serial numbers
- Forget to record install date
- Leave tests undocumented

---

## Related Documentation

- [3-Tier Asset Model (Technical)](../../.dev/roadmap/backlog/3-tier-asset-model.md)
- [Lifecycle Whiteboard Spec](../../.dev/roadmap/backlog/lifecycle-whiteboard.md)

---

**Updated:** 2025-11-28 (Lifecycle Whiteboard feature added)
