# Control Architecture Planning (PLC & Panels)

**Version Window:** v0.2.6+ (extends into v0.4.0 Background Processing)  
**Goal:** Plan and represent the complete control architecture:
- PLC systems
- Panels (PCP – PLC Control Panel, RIO – Remote IO)
- IO modules and channels
- IO allocation per instrument/cable

This feature ties together:
- Instrument Index (IN‑P040)
- IO List (IO‑P040, by PLC)
- Cable Schedules (CA‑P040)
- LBS/Area breakdown for location‑based planning

---

## 1. Domain Concepts

### 1.1 PLC System

Logical control system for a project or area:
- Example: `PLC1` (Process Area 210), `PLC2` (Tailings)

**Attributes (conceptual):**
- `id` (UUID)
- `project_id`
- `name` (e.g. `PLC1`, `PLC1-CPU01`)
- `vendor` (Siemens, Rockwell, ABB, Schneider…)
- `cpu_model` (e.g. `CPU 1516F`, `1756-L85E`)
- `redundancy_mode` (`NONE`, `CPU_REDUNDANT`, `RING`)
- `network_segment` (control network identifier)
- `primary_area_id` (FK → LBS node for main area served)

### 1.2 Control Panel (PCP / RIO)

Physical panel housing PLC CPUs and/or IO modules:
- `PCP-210` – Main PLC panel in Area 210
- `RIO-210A`, `RIO-210B` – Remote IO panels in field

**Attributes (conceptual):**
- `id` (UUID)
- `project_id`
- `control_system_id` (FK → PLC System)
- `panel_tag` (e.g. `PCP-210`, `RIO-210A`)
- `panel_type` (`CPU`, `RIO`, `LOCAL_IO`, `MCC_IO`, …)
- `location_lbs_id` (FK → LBS node; physical area/building/room)
- `ip_rating`, `enclosure_type`, `heat_load_watts`
- `status` (`PLANNED`, `DESIGNED`, `INSTALLED`)

### 1.3 IO Module

An IO card (slot) inside a panel:
- Example: `SM 1231 AI 8x16 bit`, `1756-IB32`

**Attributes (conceptual):**
- `id` (UUID)
- `project_id`
- `panel_id` (FK → Control Panel)
- `slot_number` (0..N)
- `io_type` (`AI`, `AO`, `DI`, `DO`, `HART`, `RTD`)
- `channel_count` (8, 16, 32…)
- `used_channels` (computed)
- `vendor`, `module_model`
- `address_base` (rack/slot base address if needed)

### 1.4 IO Channel Allocation

One channel on an IO module, linked to an instrument signal:
- Example: `PLC1-CPU01 / PCP-210 / Slot 4 / CH 0` → `210-FT-001` PV

**Attributes (conceptual):**
- `id` (UUID)
- `module_id` (FK → IO Module)
- `channel_number` (0..N-1)
- `io_address` (string, e.g. `PLC1:AI.0`, `RACK1:S4:C0`)
- `asset_id` (FK → Asset – instrument or device)
- `signal_function` (`PV`, `SP`, `ZSO`, `ZSC`, `RUN_FB`, etc.)
- `signal_type` (`4-20mA`, `DI 24V`, `DO relay`, etc.)
- `range_min`, `range_max`, `engineering_units`
- `cable_id` (FK → Cable, optional)
- `is_spare` (bool, for spare channels)

These allocations provide the source data for IO‑P040 (IO List).

---

## 2. Target Database Schema (High-Level)

> NOTE: Actual table/field names will be refined during implementation. This is a planning schema.

```sql
CREATE TABLE plc_systems (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    name VARCHAR(50),              -- "PLC1"
    vendor VARCHAR(100),
    cpu_model VARCHAR(100),
    redundancy_mode VARCHAR(20),   -- NONE, CPU_REDUNDANT, RING
    network_segment VARCHAR(50),
    primary_area_id VARCHAR(50),   -- FK to lbs_nodes.id
    notes TEXT
);

CREATE TABLE control_panels (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    plc_system_id UUID REFERENCES plc_systems(id),

    panel_tag VARCHAR(50),         -- "PCP-210", "RIO-210A"
    panel_type VARCHAR(20),        -- CPU, RIO, LOCAL_IO, MCC_IO
    location_lbs_id VARCHAR(50),   -- FK to lbs_nodes.id

    ip_rating VARCHAR(20),
    enclosure_type VARCHAR(50),    -- NEMA 12, NEMA 4X, etc.
    heat_load_watts DECIMAL(10,2),

    status VARCHAR(20) DEFAULT 'PLANNED',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE io_modules (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    panel_id UUID REFERENCES control_panels(id),

    slot_number INT,
    io_type VARCHAR(10),           -- AI, AO, DI, DO, RTD, HART
    channel_count INT,
    vendor VARCHAR(100),
    module_model VARCHAR(100),

    address_base VARCHAR(50),      -- e.g. "R1:S4"
    properties JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE io_channels (
    id UUID PRIMARY KEY,
    module_id UUID REFERENCES io_modules(id),
    channel_number INT,

    io_address VARCHAR(50),        -- "PLC1:AI.0", "R1:S4:C0"
    asset_id VARCHAR(50) REFERENCES assets(id),
    signal_function VARCHAR(20),   -- PV, ZSO, RUN_FB, etc.
    signal_type VARCHAR(50),       -- "4-20mA", "DI 24V", etc.
    range_min DECIMAL(12,4),
    range_max DECIMAL(12,4),
    engineering_units VARCHAR(20),

    cable_id UUID REFERENCES cables(id),
    is_spare BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 3. Planning Workflow

### 3.1 Compute IO Demand per Area

From existing assets and cables:
- Use `Asset.io_type`, discipline, and LBS location to calculate demand:
  - AI count per area
  - DI/DO count per area
  - AO / special IO (HART, RTD, pulse…)

Output example:
```text
Area 210 (Pump House)
- AI: 32 (process instruments)
- DI: 48 (valve feedbacks, motor statuses)
- DO: 24 (valve commands, motor starts)

Area 220 (Control Room)
- AI: 8 (panel instruments)
- DI: 16
- DO: 8
```

This drives how many PLC systems, panels, and IO modules are needed.

### 3.2 Define PLC Systems and Panels

User flow:
- Create one or more **PLC Systems** per plant/area (e.g. `PLC1` for Area 210).
- For each PLC System:
  - Define a CPU panel (`PCP-210` with type `CPU`).
  - Define 0..N RIO panels (`RIO-210A`, `RIO-210B`) in LBS locations.

SYNAPSE can:
- Suggest default mappings:
  - Area 210 → `PLC1` + `PCP-210` + `RIO-210A/B`.
  - Area 300 → `PLC2` + `PCP-300` + `RIO-300A`.

### 3.3 Auto‑Suggest IO Modules & Capacity

Based on IO demand and typical module capacities:
- Example assumptions:
  - AI module: 8 channels
  - DI module: 16 channels
  - DO module: 16 channels
  - **Design rule:** target ≈80% utilization (≈20% spare) per module and per panel

Algorithm (high level):
1. For each (Area, IO type), determine required channel count.
2. For each panel serving that area:
   - Calculate how many modules of each type are needed.
   - Respect target utilization threshold (auto‑add modules to maintain ≥20% spare capacity).
3. Create `io_modules` records and compute theoretical capacity vs used.

Output example:
```text
PCP-210 (CPU Panel)
- Slot 0: CPU
- Slot 1: DI16 (16 ch) – Planned
- Slot 2: DO16 (16 ch) – Planned

RIO-210A (Field Panel)
- Slot 1: AI8 (8 ch) – 7 used / 1 spare
- Slot 2: DI16 (16 ch) – 14 used / 2 spare
```

### 3.4 IO Channel Allocation per Instrument

For each instrument (Asset) and signal:
- Determine IO type (AI/DI/DO/AO) from `Asset.io_type` and properties.
- Choose appropriate `io_module`:
  - Prefer same area (via LBS).
  - Balance usage across modules.
- Allocate a channel:
  - Set `module_id`, `channel_number`, `io_address`.
  - Link to `asset_id` and `cable_id` if available.

Allocation modes:
- **Auto**: System assigns channels according to rules.
- **Manual override**: Engineer can reassign channel/address per signal.

This allocation is the data source for:
- IO‑P040 (IO List, grouped by PLC / panel).
- Panel IO occupancy reports.

---

## 4. UI Requirements

### 4.1 IO Planning View (Table)

New view under **Outputs / Automation**:

```text
PLC: PLC1-CPU01
Panel: PCP-210
────────────────────────────────────────────────────────────
Tag         | Signal | IO Type | Address   | Cable        | Area
210-FT-001  | PV     | AI      | AI.0      | 210-FT-001-S | Area 210
210-PT-001  | PV     | AI      | AI.1      | 210-PT-001-S | Area 210
210-PV-001  | ZSO    | DI      | DI.0      | 210-PV-001-C | Area 210
210-PV-001  | ZSC    | DI      | DI.1      | 210-PV-001-C | Area 210
```

Features:
- Group by PLC / panel / IO module.
- Show capacity bar per module (e.g. `14/16 channels used`).
- Filters by area, IO type, panel, status.

### 4.2 Panel Rack View

Visual representation of panel slots:

```text
PCP-210 (CPU Panel)
┌ Slot 0: CPU 1516F         ┐
├ Slot 1: DI16   [■■■■■■■■■■□□□□] 14/16
├ Slot 2: DO16   [■■■■■■■■□□□□□□] 10/16
└ Slot 3: SPARE              ┘
```

Interactions:
- Hover to see which tags are on each channel.
- Click module → focus IO Planning table filtered by that module.

### 4.3 IO Capacity Dashboard

Cards by area:

```text
Area 210 – Pump House
- PLCs: PLC1
- Panels: PCP-210, RIO-210A/B
- IO Demand vs Capacity:
  - AI: 32 / 40 (80%)
  - DI: 48 / 64 (75%)
  - DO: 24 / 32 (75%)
```

Helps spot overloaded or under‑utilized panels.

---

## 5. Integration with Existing Features

### 5.1 Breakdown Structures (v0.2.4)

- Use LBS nodes (`lbs_nodes`) to anchor panels physically.
- IO Demand per area computed from assets linked to LBS.

### 5.2 Package Generation (v0.2.6)

- IN‑P040 (Instrument Index):
  - Uses IO allocation to show Cable#, IO Address columns when available.
- IO‑P040 (IO List):
  - Generated directly from `io_channels` and `io_modules`.
  - Grouped by PLC, panel, module.
- CA‑P040 (Cable Schedule):
  - Link `cable_id` in `io_channels` for traceability from IO to cable.

### 5.3 DevConsole & Workflow Engine

- Long‑running allocation / re‑allocation operations:
  - Run via `WorkflowEngine` with steps:
    - “Compute IO demand”
    - “Create modules & panels”
    - “Allocate channels”
  - All steps logged via `ActionLogger` for full visibility.

### 5.4 Background Processing (v0.4.0+)

For large projects (1000+ IO points):
- Move allocation jobs to Celery workers.
- UI shows job progress; DevConsole shows workflow execution details.

---

## 6. Verification & Validation

### 6.1 Unit Tests (Backend)

- IO demand calculation per area:
  - Given a set of assets and LBS nodes, counts per IO type are correct.
- Module capacity planning:
  - For given demand and module sizes, module counts are as expected.
- IO allocation:
  - All signals are assigned to valid channels.
  - No channel over‑allocation.
  - Area preference respected when possible.

### 6.2 Integration Tests

- End‑to‑end with a sample project:
  - Import instrument list + rules generate assets/cables.
  - Run PLC & Panel planning.
  - Generate IO‑P040, IN‑P040, CA‑P040 and manually check coherence on a small set.

### 6.3 Manual Validation

- Review with an automation engineer:
  - Panel layouts look realistic.
  - IO distribution matches typical EPC practice.
  - Spare channels (≈20%) intentionally reserved at module and panel level.

---

## 7. Design Rules & Typical Architectures

### 7.1 Spare Capacity Rule (20%)

Baseline engineering rule:
- Plan IO capacity so that:
  - Each **module** has ~20% spare channels (e.g. ≤12/16 or ≤6/8 used).
  - Each **panel** (sum of modules) maintains ~20% spare IO overall per IO type.
- Allocation engine must:
  - Prefer filling modules up to the 80% mark, then start a new module.
  - Never exceed 100% per module; raise a warning if free capacity <10%.

This rule aligns with common EPC practice for growth and late‑stage changes.

### 7.2 Rockwell‑Based Reference Design (PlantPAx)

Assumptions for the initial template set:
- **Platform:** Rockwell ControlLogix / CompactLogix with PlantPAx libraries.
- **Network:** EtherNet/IP for PLCs, RIO, and intelligent MCCs.

Reference patterns:
- Large systems:
  - `ControlLogix` CPU in `PCP-xxx` (control room).
  - Multiple `RIO-xxx` panels (field) with EtherNet/IP adapters and IO cards.
- Smaller / area‑level systems:
  - `CompactLogix` CPU in a smaller `PCP-xxx` or combined CPU+RIO panel.

Panel templates (conceptual examples):
- **PCP – PLC Control Panel (Control Room)**
  - 2‑door, 800–1000 mm wide, 600–800 mm deep.
  - ControlLogix rack with:
    - Slot 0: CPU
    - Slot 1: EtherNet/IP comms
    - Slot 2–N: local IO or comms as needed
  - 20–30% spare rack slots reserved where possible.

- **RIO – Remote IO Panel (Field)**
  - 2‑door enclosure, similar footprint for standardization.
  - EtherNet/IP adapter + IO cards (AI/DI/DO).
  - Designed to host current IO demand + ≥20% spare IO per type.

The planning engine can use these templates as defaults for:
- Typical maximum IO per panel before suggesting a new panel.
- Default module mix (e.g. ratio of DI/DO/AI cards per area).

### 7.3 Intelligent MCCs (EtherNet/IP)

Assumptions:
- MCCs are smart devices on EtherNet/IP (Rockwell CENTERLINE or similar).
- Many motor starters/feeds expose:
  - Status (RUN, TRIP, HEALTH) as EtherNet/IP data.
  - Commands (START/STOP/RESET) over EtherNet/IP.

Implications for IO planning:
- **Fewer hardwired DO/DI** to panels for motors:
  - Logical IO points are modeled in the IO list but mapped to MCC devices / add‑on instructions instead of physical IO channels.
- IO planning must support:
  - “Soft IO” mapping: Tag/function allocated to an MCC data point, not a panel channel.
  - Clear separation in IO‑P040 between:
    - Hardwired IO (panel/channel).
    - Networked IO (MCC / EtherNet/IP).

### 7.4 Network Topology & Site Scale (Small Gold Mine)

Assumed physical context:
- Site size: approx. **400m x 400m** (small gold mine).
- Process areas: crushing, grinding, leaching, tailings, utilities (modeled via LBS and P&IDs).

Control network layers:
- **Plant Control Ring (Fiber)**:
  - Redundant **fiber ring** interconnecting main buildings (e.g. control room, pump house, MCC rooms).
  - Connects:
    - PLC CPU panels (PCP‑xxx).
    - Core network switches.
    - Intelligent MCCs (EtherNet/IP).
  - Represented at `plc_system` / `control_panels` level via `network_segment` and/or properties.

- **Building/Area Copper Network**:
  - Inside each building/area, copper (Ethernet over copper) from local switches to:
    - RIO panels in the field.
    - Local HMI panels / operator stations if any.
  - Shorter runs (tens of meters) within each building, still tied to the same `network_segment`.

- **PLC–RIO IO Ring (Copper)**:
  - Each PLC system has its own **remote IO copper “ring”** topology inside the area:
    - EtherNet/IP or similar industrial Ethernet daisy‑chain/ring from PCP‑xxx to RIO‑xxx panels.
    - Follows the physical path of the process (e.g. along leach tanks, pump skids).
  - Planning should:
    - Prefer grouping RIO panels along the process path in LBS (e.g. Leach Area, Neutralization Area).
    - Avoid unrealistic distances for copper (max recommended segment lengths).

Implications for IO & P&ID‑driven distribution:
- P&IDs + LBS define **process “clusters”** (e.g. leaching train, reagent dosing, tailings pumps).
- For each cluster:
  - Assign it to a **primary PLC system** and a **subset of RIO panels** on the PLC’s copper IO ring.
  - Ensure IO density and distances are reasonable for a 400m x 400m site.
- This ensures:
  - Clean mapping from process (P&ID) → area (LBS) → PLC/RIO on FO/copper rings.
  - An IO & panel layout that looks realistic for a small gold mine.


---

**Updated:** 2025-11-25
