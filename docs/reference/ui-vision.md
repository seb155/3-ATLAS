# SYNAPSE UI Vision v2.0 - Engineering Workbench

**Updated:** 2025-11-22  
**Based on:** User feedback - Aras Innovator-style interface

---

## 🎯 Core Requirements

### 1. **Resizable & Collapsible Panels**
- Left sidebar (resizable, collapsible)
- Right sidebar (resizable, collapsible)
- Top toolbar (collapsible)
- Bottom panel (resizable, collapsible)
- Central work area (always visible)

### 2. **Multiple View Modes** (Toggle between)
- **Folded Tree** - Hierarchical collapse/expand
- **Flow Diagram** - Visual relationships (like ReactFlow)
- **AG Grid** - Spreadsheet with advanced filtering
- **Combined View** - Modern viz + Grid (Aras style)
- **3D View** - Spatial visualization (future)

### 3. **Advanced Search**
- **Global Search Bar** (top toolbar, always accessible)
- **Table Search** (per-grid filtering)
- **Autocomplete** with suggestions
- **Dropdown lists** for categorical fields
- **Wildcards:** `*` (any), `&` (AND), `|` (OR), `!` (NOT)
- **Search examples:**
  - `210-*` → All tags starting with 210
  - `MOTOR & APPROVED` → Approved motors
  - `!W/E` → Not with equipment

### 4. **Grid Features** (AG Grid or better)
- **Add/Remove Columns** - Drag & drop column manager
- **Column Presets:**
  - "Basic" (Tag, Type, Status)
  - "Engineering" (Tag, Type, HP, Voltage, Area)
  - "Package" (Tag, Package, Status, Cost)
  - "Custom" (save your own)
- **Filters:**
  - Quick filters (buttons: Show All, Approved Only, Errors Only)
  - Advanced filters (multi-condition builder)
  - **Filter Presets:**
    - "Ready for Review" (status=REVIEWED, package!=null)
    - "Missing Data" (warnings>0)
    - "Area 210" (area=210)
    - Save custom presets
- **Reorganization:**
  - Drag columns to reorder
  - Group by (Area, Type, Package)
  - Sort multi-column
  - Pin columns left/right

### 5. **Rule Visualization**
- **Flow Diagram** showing rule dependencies
- **Impact Graph** - "If I change this, what's affected?"
- **Rule Hierarchy** - Visual FIRM→COUNTRY→PROJECT→CLIENT

### 6. **Built for Engineers**
- Keyboard shortcuts everywhere
- No unnecessary clicks
- Fast bulk operations
- Excel-like feel
- Technical precision (no dumbed-down UX)

---

## 📐 Layout System - Resizable Workbench

```
┌─────────────────────────────────────────────────────────────┐
│  🔍 Global Search [210-*]  │ Project: Greece │ [User ▼] │☰│ │ TOP TOOLBAR
├─────────────────────────────────────────────────────────────┤ (Collapsible)
│     │                                                 │     │
│  L  │              CENTRAL WORK AREA                  │  R  │
│  E  │                                                 │  I  │
│  F  │  ┌──────────────────────────────────────────┐  │  G  │
│  T  │  │ View Mode Selector:                      │  │  H  │
│     │  │ [Tree] [Flow] [Grid] [Combined] [3D]     │  │  T  │
│  S  │  ├──────────────────────────────────────────┤  │     │
│  I  │  │                                          │  │  S  │
│  D  │  │                                          │  │  I  │
│  E  │  │         Active View Content              │  │  D  │
│  B  │  │         (Changes based on mode)          │  │  E  │
│  A  │  │                                          │  │  B  │
│  R  │  │                                          │  │  A  │
│     │  │                                          │  │  R  │
│  ◄─►│  └──────────────────────────────────────────┘  │◄─► │
│     │                                                 │     │
│ 250px│              (Resizable handle)               │200px│
│ min  │                                                │ min │
├─────────────────────────────────────────────────────────────┤
│                    BOTTOM PANEL                             │ (Resizable)
│  Details / Properties / Logs / Version History              │ (Collapsible)
│                    ▲───────▼                                │
│                 (Resize handle)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 View Modes (Central Area)

### Mode 1: COMBINED VIEW (Default - Aras Style)

**Top 40%:** Modern Visualization  
**Bottom 60%:** AG Grid

```
┌──────────────────────────────────────────────────────────┐
│ VISUALIZATION PANE                                       │
│                                                          │
│  ┌─ 200 - Grinding ──────────────────────┐              │
│  │  ┌─ 210 - SAG Mill ────┐              │              │
│  │  │  ● 210-PP-001 (Pump)│──┐           │              │
│  │  │  ● 210-M-001 (Motor)│◄─┤           │              │
│  │  │  ● 210-VFD-001      │  └─ Rules    │              │
│  │  └─────────────────────┘   Applied    │              │
│  │  ┌─ 220 - Ball Mill ──────┐           │              │
│  │  │  ● 220-PP-001         │            │              │
│  │  └───────────────────────┘            │              │
│  └─────────────────────────────────────────┘            │
│                                                          │
├──────────────────────────────────────────────────────────┤ 
│ AG GRID PANE                                             │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Presets: [Basic] [Engineering▼] [Package] [Custom]│  │
│ │ Filters: [✓Show All] [ Approved Only] [Area: 210▼]│  │
│ ├────┬─────┬──────┬────┬───────┬──────┬────────┬────┤  │
│ │ #  │ Tag │ Type │ HP │Voltage│ Area │Package │Stat│  │
│ ├────┼─────┼──────┼────┼───────┼──────┼────────┼────┤  │
│ │ ✓  │210-P│PUMP  │100 │ 400V  │ 210  │IN-P040 │✅  │  │
│ │ ✓  │210-M│MOTOR │100 │ 400V  │ 210  │IN-P040 │🟡  │  │
│ │    │210-V│VFD   │100 │ 400V  │210   │IN-P001 │🔵  │  │
│ └────┴─────┴──────┴────┴───────┴──────┴────────┴────┘  │
│ [Column Manager] [Group By: Area▼] [Export]            │
└──────────────────────────────────────────────────────────┘
```

**Interaction:**
- Click node in viz → Highlights row in grid
- Select row in grid → Highlights node in viz
- **Synchronized selection**

---

### Mode 2: FLOW DIAGRAM VIEW

Full-screen flow diagram showing relationships:

```
┌──────────────────────────────────────────────────────────┐
│ [Zoom: 100%▼] [Fit] [Layout: Hierarchical▼] [Filter▼]   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│     ┌─────────┐                                         │
│     │210-PP-001│──── powered_by ────┐                   │
│     │  PUMP   │                     ↓                   │
│     └─────────┘              ┌──────────┐               │
│                              │210-M-001 │               │
│     ┌─────────┐              │  MOTOR   │               │
│     │210-LT   │── signal ──►│          │               │
│     │ LEVEL   │              └──────────┘               │
│     └─────────┘                     │                   │
│                                     │ controlled_by     │
│                              ┌──────────┐               │
│                              │210-VFD   │               │
│                              │   VFD    │               │
│                              └──────────┘               │
│                                     │                   │
│                                     ↓                   │
│                              ┌──────────┐               │
│                              │PLC-210-1 │               │
│                              │   PLC    │               │
│                              └──────────┘               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Features:**
- Click edge → Show rule that created relationship
- Drag to pan, scroll to zoom
- Right-click node → Context menu (Edit, Delete, Apply Rule, etc.)
- **Layouts:** Hierarchical, Force-directed, Circular, Tree

---

### Mode 3: TREE VIEW

Hierarchical tree with expand/collapse:

```
┌──────────────────────────────────────────────────────────┐
│ 🔍 Search in tree...  [Expand All] [Collapse All]        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ▼ 📂 200 - Grinding (85 assets)                         │
│     ▶ 📂 210 - SAG Mill (45 assets)                      │
│     ▼ 📂 220 - Ball Mill (40 assets)                     │
│        ▼ 📂 PUMPS (5)                                    │
│           □ 220-PP-001 (Centrifugal, 100HP) ✅ APPROVED  │
│           □ 220-PP-002 (Centrifugal, 75HP) 🟡 REVIEW    │
│           □ 220-PP-003 (Slurry, 150HP) 🔵 CREATED       │
│        ▶ 📂 MOTORS (5)                                   │
│        ▶ 📂 INSTRUMENTS (30)                             │
│                                                          │
│  ▶ 📂 300 - Flotation (150 assets)                       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Features:**
- Checkbox selection (multi-select with Ctrl/Shift)
- Drag & drop to reorganize
- Right-click → Context menu
- Icons for status (✅🟡🔵⚠️🔴)
- Count badges per folder

---

### Mode 4: 3D VIEW (Future - Phase 7)

3D spatial visualization of plant layout:

```
┌──────────────────────────────────────────────────────────┐
│ Controls: [Rotate] [Pan] [Zoom] [Perspective▼]           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│                    ╔═══════╗                            │
│                    ║ AREA  ║                            │
│                    ║  210  ║                            │
│                    ╚═══════╝                            │
│                       │                                 │
│           ┌───────────┼───────────┐                     │
│           │           │           │                     │
│        ┌──▼──┐    ┌──▼──┐    ┌──▼──┐                  │
│        │MILL │    │ MCC │    │ PLC │                  │
│        │ SAG │    │210-1│    │210-1│                  │
│        └─────┘    └─────┘    └─────┘                  │
│           │                      │                     │
│        [Cables shown as lines]   │                     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Use Case:** Spatial cable routing, equipment placement validation

---

## 🔍 Advanced Search System

### Global Search Bar (Top Toolbar)

```
┌──────────────────────────────────────────────────────────┐
│ 🔍 [Search: 210-* & MOTOR & !W/E                    ] 🔎│
│    └─ Autocomplete suggestions:                         │
│       • 210-M-001 (MOTOR, APPROVED)                     │
│       • 210-M-002 (MOTOR, REVIEW)                       │
│       • Search for: "210-* & MOTOR" (15 results)        │
│       • Filter: Area 210                                │
└──────────────────────────────────────────────────────────┘
```

**Operators:**
- `*` - Wildcard (any characters)
- `&` - AND logic
- `|` - OR logic
- `!` - NOT logic
- `""` - Exact phrase
- `field:value` - Field-specific (e.g., `status:APPROVED`)

**Examples:**
```
210-*                  → All tags in area 210
MOTOR & APPROVED       → Approved motors only
PUMP | TANK            → Pumps or tanks
!W/E                   → Not with equipment
voltage:400V           → 400V equipment
package:IN-P040        → Items in package IN-P040
created:today          → Created today
modified:>2025-11-20   → Modified after date
```

### Table Search (Per-Column)

```
AG Grid Header Row:
┌─────┬─────────────┬──────────────┬──────────────┐
│ Tag │ Type        │ Status       │ Package      │
│ 🔍  │ 🔍 [MOTOR]  │ 🔍 [APPROVE*]│ 🔍 [IN-P040] │
├─────┼─────────────┼──────────────┼──────────────┤
```

Each column has independent search with autocomplete dropdown.

---

## 🎨 Column Management

### Column Manager Panel (Right-click header or button)

```
┌─────────────────────────────────────────┐
│ Column Manager                    [Save]│
├─────────────────────────────────────────┤
│ ☑️ Tag                    [Pin Left]   │
│ ☑️ Type                   [Pin Left]   │
│ ☑️ HP                     [ ]          │
│ ☑️ Voltage                [ ]          │
│ ☑️ Area                   [ ]          │
│ ☑️ Package                [Pin Right]  │
│ ☑️ Status                 [Pin Right]  │
│ ☐ Created By                           │
│ ☐ Created Date                         │
│ ☐ Modified By                          │
│ ☐ Modified Date                        │
│ ☐ Version                              │
│ ☐ Serial Number (Physical only)        │
│                                        │
│ [Reset to Default] [Save as Preset]    │
└─────────────────────────────────────────┘
```

**Presets (Dropdown):**
- **Basic** - Tag, Type, Status (5 columns)
- **Engineering** - Tag, Type, HP, Voltage, RPM, Area (10 columns)
- **Package** - Tag, Package, Status, Cost, Deliverable (8 columns)
- **Procurement** - Tag, Manufacturer, Model, Price, Lead Time (7 columns)
- **Commission** - Tag, Serial, Install Date, Test Status (6 columns)
- **Custom-JF-2025** - Your saved preset

---

## 🎛️ Filter System

### Quick Filters (Buttons above grid)

```
[✓ Show All] [ Approved Only] [ Need Review] [ Errors Only]
[Area: All ▼] [Package: All ▼] [Type: All ▼]
```

### Advanced Filter Builder

```
┌─────────────────────────────────────────────────────────┐
│ Advanced Filters                          [Save Preset] │
├─────────────────────────────────────────────────────────┤
│ Rule 1: [Type       ▼] [equals    ▼] [MOTOR    ▼] [×] │
│         [AND ▼]                                         │
│ Rule 2: [Voltage    ▼] [equals    ▼] [400V     ▼] [×] │
│         [AND ▼]                                         │
│ Rule 3: [Package    ▼] [not empty ▼] [         ▼] [×] │
│                                                         │
│ [+ Add Rule]   [Clear All]                             │
│                                                         │
│ Name: [Motors 400V with Package]  [Save as Preset]     │
└─────────────────────────────────────────────────────────┘
```

**Saved Filter Presets:**
- "Ready for Review" (status=REVIEWED, package!=null)
- "Missing Data" (warnings>0 OR errors>0)
- "Area 210 Instruments" (area=210, type IN [FT,PT,LT,TT])
- "VFDs without comm" (type=VFD, comm_protocol=null)
- "Orphan assets" (parent_id=null AND type!=AREA)

---

## 🔗 Rule Visualization

### Rule Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│ Rule Impact Visualization: "FIRM: Pumps require Motors" │
├──────────────────────────────────────────────────────────┤
│                                                          │
│    ┌──────────┐                                         │
│    │ CONDITION│                                         │
│    │ type=PUMP│                                         │
│    └────┬─────┘                                         │
│         │                                               │
│         ↓                                               │
│    ┌──────────┐      Creates      ┌──────────┐        │
│    │ ACTION   │──────────────────→│  MOTOR   │        │
│    │CREATE_M  │                    │ (child)  │        │
│    └──────────┘                    └────┬─────┘        │
│         │                                │              │
│         │ Triggers more rules            │              │
│         ↓                                ↓              │
│    ┌──────────┐                    ┌──────────┐        │
│    │FIRM: VFD │                    │FIRM: Cable│       │
│    │for Motors│                    │for Motors│        │
│    │>15HP     │                    │          │        │
│   └──────────┘                    └──────────┘        │
│                                                          │
│ Affected Assets: 15                                     │
│ Created Assets: 15 motors, 12 VFDs, 15 cables           │
└──────────────────────────────────────────────────────────┘
```

---

## 🎯 Keyboard Shortcuts (Engineering-Friendly)

```
Global:
Ctrl+K       → Global search
Ctrl+F       → Find in current view
Ctrl+/       → Show shortcuts help
Esc          → Close modals/panels

Grid:
Ctrl+A       → Select all
Ctrl+Click   → Multi-select toggle
Shift+Click  → Range select
Ctrl+C       → Copy selected
Ctrl+V       → Paste
Ctrl+Z       → Undo
Ctrl+Y       → Redo
Enter        → Edit cell
Tab          → Next cell
Shift+Tab    → Previous cell

Navigation:
Ctrl+1-5     → Switch view modes
Ctrl+Shift+L → Toggle left sidebar
Ctrl+Shift+R → Toggle right sidebar
Ctrl+Shift+B → Toggle bottom panel

Actions:
Ctrl+R       → Apply rule
Ctrl+E       → Export
Ctrl+S       → Save changes
F2           → Rename
Del          → Delete selected
```

---

## 📊 Panel Configurations (Save/Load)

### Workspace Presets

User can save panel layouts:

```
Presets:
├─ "Design Mode"
│  ├─ Left: FBS Tree (expanded)
│  ├─ Center: Combined View (tree + grid)
│  ├─ Right: Properties Panel
│  └─ Bottom: Version History
│
├─ "Package Review"
│  ├─ Left: Package List
│  ├─ Center: Grid only (full screen)
│  ├─ Right: Deliverables Checklist
│  └─ Bottom: Collapsed
│
├─ "Rule Development"
│  ├─ Left: Rule List
│  ├─ Center: Flow Diagram
│  ├─ Right: Rule Editor
│  └─ Bottom: Test Results
│
└─ "Compact" (Laptop)
   ├─ Left: Collapsed
   ├─ Center: Grid only
   ├─ Right: Collapsed
   └─ Bottom: Collapsed
```

**Quick Switch:** Dropdown in top toolbar to switch workspaces.

---

## 🎨 UI Components Library

### Modern Components to Use:
- **Layout:** `react-grid-layout` or `react-mosaic` (resizable panels)
- **Grid:** AG Grid Enterprise (best for engineers)
- **Tree:** `react-complex-tree` or `rc-tree` (performant)
- **Flow:** `ReactFlow` (node-based diagrams)
- **3D:** `Three.js` + `@react-three/fiber` (future)
- **Search:** `cmdk` (command palette style)
- **Autocomplete:** `downshift` or `react-select`

---

## 🚀 Implementation Priority

**Phase 2 (Current):**
- ✅ Basic grid (AG Grid)
- ✅ Simple layout (no resize yet)

**Phase 3:**
- ➕ Resizable panels (`react-grid-layout`)
- ➕ Combined view (tree + grid)
- ➕ Column management
- ➕ Basic search

**Phase 4:**
- ➕ Flow diagram (ReactFlow)
- ➕ Advanced filters with presets
- ➕ Workspace presets

**Phase 5:**
- ➕ Global search with wildcards
- ➕ Rule visualization
- ➕ Keyboard shortcuts

**Phase 6:**
- ➕ 3D view (exploratory)

---

## ✅ Success Criteria

UI is successful if engineer can:
- [ ] Resize/collapse any panel to their preference
- [ ] Switch between tree/flow/grid views in 1 click
- [ ] Find any asset with global search in <5 seconds
- [ ] Apply filter preset and see results instantly
- [ ] Add/remove columns without opening settings
- [ ] See rule impact visually before applying
- [ ] Work entirely with keyboard (no mouse needed)
- [ ] Save workspace layout and restore next session

---

**This is a professional engineering tool, not a consumer app.**

---

## 🔗 Clickable Navigation System

### Entity Linking (Everywhere)

**Principle:** Every reference to an asset, rule, package, or DB entity is a clickable link.

**Visual Style:**
- Asset tags: `<a class="asset-link">210-M-001</a>` (blue underline on hover)
- Rules: `<a class="rule-link">FIRM: Motors for Pumps</a>` (teal underline)
- Packages: `<a class="package-link">IN-P040</a>` (purple underline)

**Click Actions:**

| Entity Type | Click Action | Example |
|-------------|--------------|---------|
| Asset Tag | Open asset detail sidebar | Click `210-M-001` → Sidebar shows motor details |
| Rule Name | Open rule editor modal | Click `FIRM: Motors` → Rule JSON editor |
| Package | Navigate to package view | Click `IN-P040` → WBS tab, IN-P040 selected |
| User | Show user profile tooltip | Hover `JF` → Tooltip: "Jean-François, last edit: 2h ago" |
| Location | Navigate to LBS view | Click `MCC-210-MCC1` → LBS tab, MCC expanded |
| File/Drawing | Open file viewer | Click `P&ID-210.pdf` → PDF viewer modal |

**Context Menu (Right-Click):**
```
Right-click on "210-M-001"
├─ Open in New Tab
├─ View Relationships (graph)
├─ Edit Properties
├─ View Version History
├─ Copy Tag
└─ Go to Location (LBS view)
```

**Examples in UI:**

**Grid Cell:**
```
Tag: [210-M-001] ← Clickable
Parent: [210-PP-001] ← Clickable
Package: [IN-P040] ← Clickable
Created by: [FIRM: Motors for Pumps] ← Clickable (rule)
```

**Sidebar Detail:**
```
Asset: 210-M-001
Parent: 210-PP-001 [→]
Children:
  - 210-M-001-PWR (Cable) [→]
  - 210-M-001-VFD (VFD) [→]
Location: MCC-210-MCC1 [→]
Created by Rule: FIRM: Motors for Pumps [Edit]
```

---

## 🛠️ Developer Console (Built-in DevTools)

### Purpose
- Monitor system logs in real-time
- Debug rule execution
- Trace API calls
- Help AI debug issues
- Assist developers

### Layout

**Bottom Panel Toggle:**
```
[Console] [Network] [Rules Trace] [DB Queries] [Errors]
```

**Console Tab:**
```
┌──────────────────────────────────────────────────────┐
│ [Clear] [Levels: ✓Info ✓Warn ✓Error ✓Debug] [Export]│
├──────────────────────────────────────────────────────┤
│ 16:42:01 ℹ️  [API] GET /api/v1/assets/ → 200 (45ms) │
│ 16:42:03 ⚠️  [Rule] Motor voltage missing, using 400V│
│ 16:42:05 ✅ [Rule] Created 5 motors from rule FIRM:01│
│ 16:42:07 ❌ [Error] Cable sizing failed: Invalid HP  │
│          ↳ Stack trace: cable_sizing.py:145         │
│          ↳ Asset: 210-M-999 [View] [Retry]          │
│ 16:42:10 🔧 [Debug] RuleExecutor: 3 rules matched    │
│          ↳ FIRM: Motors (prio 10)                   │
│          ↳ COUNTRY-GR: 400V (prio 30)               │
│          ↳ PROJECT: PlantPAX (prio 50)              │
└──────────────────────────────────────────────────────┘
```

**Network Tab:**
```
┌──────────────────────────────────────────────────────┐
│ Method │ URL                    │ Status │ Time      │
├────────┼────────────────────────┼────────┼───────────┤
│ GET    │ /api/v1/assets/        │ 200    │ 45ms      │
│ POST   │ /api/v1/rules/execute  │ 201    │ 230ms     │
│ GET    │ /api/v1/cables/        │ 200    │ 32ms      │
└──────────────────────────────────────────────────────┘
Click row → Show request/response details
```

**Rules Trace Tab:**
```
┌──────────────────────────────────────────────────────┐
│ Rule Execution Trace for: 210-PP-001                 │
├──────────────────────────────────────────────────────┤
│ 1. Condition Matched: type=PUMP ✅                   │
│ 2. Action: CREATE_CHILD (Motor)                      │
│    ↳ Created: 210-M-001 [View]                       │
│ 3. Triggered: FIRM: VFD for Motors >15HP             │
│    ↳ Condition: HP > 15 ✅ (HP=100)                  │
│    ↳ Created: 210-VFD-001 [View]                     │
│ 4. Triggered: FIRM: Create Power Cable                │
│    ↳ Calculating cable size...                       │
│    ↳ CEC Table 2: 3x #2 AWG + 1x #6 AWG ground       │
│    ↳ Created: 210-M-001-PWR [View]                   │
│                                                       │
│ Total: 3 assets created in 230ms                     │
└──────────────────────────────────────────────────────┘
```

**DB Queries Tab:**
```
┌──────────────────────────────────────────────────────┐
│ SQL Query Log                          [Show Explain]│
├──────────────────────────────────────────────────────┤
│ SELECT * FROM assets WHERE area='210' (15ms, 45 rows)│
│ INSERT INTO cables (...) VALUES (...) (8ms)          │
│ UPDATE assets SET status='APPROVED' WHERE... (12ms)  │
└──────────────────────────────────────────────────────┘
Click query → Show full SQL + execution plan
```

**Errors Tab:**
```
┌──────────────────────────────────────────────────────┐
│ Recent Errors                          [Clear All]   │
├──────────────────────────────────────────────────────┤
│ ❌ Cable Sizing Error (3 occurrences)                │
│    Last: 2 minutes ago                               │
│    Asset: 210-M-999 [View]                           │
│    Error: Invalid HP value (null)                    │
│    Stack: cable_sizing.py:145                        │
│    [Copy Error] [Report Issue]                       │
└──────────────────────────────────────────────────────┘
```

### AI Debugging Helper

**Special logging for AI:**
```javascript
// Enhanced logging with context for AI
console.aiDebug({
  action: "rule_execution",
  asset_id: "210-M-001",
  rule_id: "rule-firm-001",
  context: {
    asset_type: "MOTOR",
    properties: { hp: 100, voltage: "400V" },
    triggered_rules: ["rule-firm-vfd", "rule-firm-cable"]
  },
  result: "success",
  created_assets: ["210-VFD-001", "210-M-001-PWR"]
});
```

AI can query logs via API:
```
GET /api/v1/debug/logs?action=rule_execution&asset_id=210-M-001
```

---

## 🗄️ Raw Database Viewer

### Purpose
- View/edit database directly (admin/dev mode)
- Debug data issues
- Export raw data
- Inspect relationships

### Implementation Options (All Opensource)

**Option 1: Adminer (Recommended)**
- Single PHP file (~500KB)
- Supports PostgreSQL
- Web UI for DB management
- **License:** Apache 2.0 (Free)

**Option 2: pgAdmin Web**
- Full PostgreSQL admin
- More features, heavier
- **License:** PostgreSQL License (Free)

**Option 3: Custom React Component**
- Built with AG Grid + PostgreSQL introspection
- Fully integrated in app
- **License:** Opensource (our code)

### Proposed: Embedded Adminer

**Access:**
```
Top Menu → Admin → Database Viewer
or
http://localhost:3000/admin/db
```

**Features:**
- View all tables (assets, cables, rules, etc.)
- Execute SQL queries
- Edit data inline
- Export to CSV/JSON
- View foreign keys and relationships

**Security:**
- Only accessible in development mode
- Or admin users with `DB_ADMIN` role
- Read-only mode for non-admins

**Screenshot Mock:**
```
┌──────────────────────────────────────────────────────┐
│ Database: synapse_db                    [Adminer 4.8]│
├──────────────────────────────────────────────────────┤
│ Tables:                                              │
│ ☑️ assets (487 rows)                                 │
│ ☑️ cables (234 rows)                                 │
│ ☑️ rules (45 rows)                                   │
│ ☑️ packages (11 rows)                                │
│                                                       │
│ SQL Query:                                           │
│ SELECT * FROM assets WHERE area='210' LIMIT 100      │
│ [Execute] [Export CSV]                               │
│                                                       │
│ Results: (45 rows in 12ms)                           │
│ ┌────┬──────────┬──────┬────────┬────────┐          │
│ │ id │ tag      │ type │ area   │ status │          │
│ ├────┼──────────┼──────┼────────┼────────┤          │
│ │ 1  │210-PP-001│ PUMP │ 210    │APPROVED│          │
│ │ 2  │210-M-001 │MOTOR │ 210    │CREATED │          │
└──────────────────────────────────────────────────────┘
```

---

## 🤖 AI Chatbot Integration

### Purpose
- Help navigate: "Show me all motors in area 210"
- Answer questions: "What's the voltage for Greece?"
- Guide workflow: "How do I create a package?"
- Debug: "Why didn't cable generate?"

### Implementation (Opensource)

**Option 1: OpenAI API (Paid but flexible)**
- GPT-4 with custom instructions
- Access to app data via API
- **Cost:** Pay per use (~$0.01/1K tokens)

**Option 2: Ollama (Self-hosted, Free)**
- Run LLaMA 3 / Mistral locally
- No API costs
- **License:** Opensource
- **Requirement:** GPU or good CPU

**Option 3: Hybrid**
- Ollama for basic queries (free)
- GPT-4 for complex reasoning (paid)

### Proposed: Hybrid Approach

**UI Position:**
```
Bottom-right floating button: [💬 Ask AI]
Click → Chatbot sidebar opens
```

**Chat Interface:**
```
┌──────────────────────────────────────┐
│ SYNAPSE AI Assistant       [−][×]    │
├──────────────────────────────────────┤
│                                      │
│ 👤 Show me all motors in area 210    │
│                                      │
│ 🤖 Found 12 motors in area 210:      │
│    • 210-M-001 (100HP, APPROVED) [→] │
│    • 210-M-002 (75HP, REVIEW) [→]    │
│    • 210-M-003 (50HP, CREATED) [→]   │
│    ... (9 more)                      │
│                                      │
│    [Show in Grid] [Export List]      │
│                                      │
│ 👤 Why wasn't cable created for M-003│
│                                      │
│ 🤖 Cable not created because:        │
│    ❌ Motor voltage is NULL           │
│    ✅ Fix: Set voltage to 400V        │
│                                      │
│    [Auto-Fix] [Show Rule]            │
│                                      │
├──────────────────────────────────────┤
│ [Type your question...]        [Send]│
└──────────────────────────────────────┘
```

### Data Access for AI

**API Endpoints for AI:**
```
GET /api/v1/ai/query
POST /api/v1/ai/execute-action

Example:
POST /api/v1/ai/query
{
  "question": "Show motors in area 210",
  "context": {
    "current_view": "FBS",
    "selected_area": "210"
  }
}

Response:
{
  "answer": "Found 12 motors in area 210",
  "results": [
    { "id": "...", "tag": "210-M-001", ... }
  ],
  "actions": [
    { "label": "Show in Grid", "action": "navigate", "target": "grid", "filter": "area=210&type=MOTOR" }
  ]
}
```

### AI Capabilities

**Navigation:**
- "Go to package IN-P040"
- "Show me area 210 on the LBS tree"
- "Find all approved motors"

**Data Queries:**
- "How many instruments need review?"
- "What's the total cable length for area 210?"
- "Which packages are incomplete?"

**Explanations:**
- "Why was VFD created for this motor?"
- "Explain the FIRM: Motors rule"
- "What happens when I approve this asset?"

**Actions:**
- "Apply FIRM: Motors rule to all pumps"
- "Generate BID LST for IN-P040"
- "Change all area 210 motors to 400V"

**Debug:**
- "Why didn't cable generate?"
- "Show me the rule execution trace for 210-PP-001"
- "What errors occurred in the last hour?"

### AI Context System

AI has access to:
- Current user state (view, selection, filters)
- Database schema and relationships
- Rule definitions (can explain rules)
- Recent actions (can reference history)
- Error logs (can help debug)

**Example Context:**
```json
{
  "user": {
    "current_view": "FBS",
    "selected_area": "210",
    "filters": { "status": "APPROVED" }
  },
  "data_access": {
    "assets_count": 487,
    "recent_changes": [
      { "asset": "210-M-001", "action": "created", "timestamp": "2m ago" }
    ]
  },
  "permissions": ["read", "write", "execute_rules"]
}
```

---

## 🌐 Full Opensource Stack

### Current Stack (All Free/Opensource)

| Component | Technology | License | Cost |
|-----------|------------|---------|------|
| **Frontend** | React 19 | MIT | Free |
| **UI Components** | AG Grid Community | MIT | Free |
| **Flow Diagrams** | ReactFlow | MIT | Free |
| **Panels** | react-grid-layout | MIT | Free |
| **Backend** | FastAPI (Python) | MIT | Free |
| **Database** | PostgreSQL | PostgreSQL | Free |
| **ORM** | SQLAlchemy | MIT | Free |
| **Auth** | FastAPI JWT | MIT | Free |
| **DB Viewer** | Adminer | Apache 2.0 | Free |
| **AI (Local)** | Ollama + LLaMA 3 | Apache 2.0 | Free |
| **AI (Cloud)** | OpenAI API | Proprietary | Paid |

### Recommended Additions (Opensource)

| Component | Technology | License | Purpose |
|-----------|------------|---------|---------|
| **Search** | MeiliSearch | MIT | Fast asset search |
| **Caching** | Redis | BSD | Performance |
| **Queue** | Celery + Redis | BSD | Background jobs |
| **Monitoring** | Grafana | AGPL | System monitoring |
| **Logs** | Loki | AGPL | Log aggregation |

### Avoiding Paid Licenses

**❌ Do NOT use:**
- AG Grid Enterprise ($999/dev/year)
- Tableau ($70/user/month)
- Jira ($10/user/month)
- Confluence ($10/user/month)

**✅ Use instead:**
- AG Grid Community (free)
- Grafana (free)
- GitHub Issues (free)
- Markdown docs (free)

---

## 🎯 Updated Success Criteria

UI is successful if:
- [ ] Every entity reference is clickable and navigable
- [ ] Developer console shows real-time logs and traces
- [ ] Raw DB viewer accessible for debugging
- [ ] AI chatbot can answer 80%+ of common questions
- [ ] AI can navigate user to correct location
- [ ] Full stack remains opensource (no paid licenses)
- [ ] AI has proper context for debugging help

---

## 📊 Implementation Priority (Updated)

**Phase 2 (Current):**
- ✅ Basic grid
- ✅ Simple layout

**Phase 3:**
- ➕ Resizable panels
- ➕ Combined view
- ➕ **Clickable entity links**
- ➕ **Basic dev console (logs)**

**Phase 4:**
- ➕ Flow diagram
- ➕ Advanced filters
- ➕ **Full dev console (network, rules trace)**

**Phase 5:**
- ➕ Global search
- ➕ **DB viewer (Adminer)**
- ➕ **AI chatbot (basic navigation)**

**Phase 6:**
- ➕ **AI chatbot (advanced actions)**
- ➕ 3D view (exploratory)

---

**This is a professional engineering tool with developer-first features.**

