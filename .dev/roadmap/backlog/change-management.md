# Change Management

**Versions:** v0.2.7 (Version History), v0.2.8 (Baselines & Impact Analysis)  
**Goal:** Track all changes, analyze impact, and create project snapshots

---

## Overview

SYNAPSE provides comprehensive change management capabilities:

| Feature | Purpose | Version |
|---------|---------|---------|
| **Version History** | Per-asset change tracking | v0.2.7 |
| **Audit Log** | Complete project history | v0.2.7 |
| **Compare Versions** |  Diff view for changes | v0.2.7 |
| **Rollback** | Undo changes | v0.2.7 |
| **Baselines** | Project snapshots (freeze) | v0.2.8 |
| **Baseline Compare** | Project-level diff | v0.2.8 |
| **Impact Analysis** | Predict change effects | v0.2.8 |
| **Change Requests** | CR tracking | v0.2.8 |

---

## Part 1: Version History & Audit (v0.2.7)

### Asset Version History

**Concept:** Every asset maintains complete change history

#### Example Timeline
```
ASSET: 210-M-001 (Motor)
─────────────────────────────────────────────────────────────

VERSION HISTORY:
═══════════════════════════════════════════════════════════

v4 (CURRENT) ─────────────────────────────────────────────
│ 2025-11-24 15:30 | admin@aurumax.com
│ Changed: rated_power: 100HP → 150HP
│ Reason: "Client requirement change - CR-2025-042"
│ Impact: 12 items affected
│ [View Details] [Compare with v3] [Rollback]
│
v3 ───────────────────────────────────────────────────────
│ 2025-11-20 10:15 | engineer@aurumax.com  
│ Changed: voltage: 480V → 600V
│ Reason: "Site standard update"
│ Impact: 3 items affected
│ [View Details] [Compare] [Rollback]
│
v2 ───────────────────────────────────────────────────────
│ 2025-11-15 14:00 | admin@aurumax.com
│ Changed: location_id: null → "Area 210"
│ Reason: "Initial placement"
│ [View Details] [Compare] [Rollback]
│
v1 (CREATED) ─────────────────────────────────────────────
│ 2025-11-10 09:00 | system
│ Created from: Rule "Pumps require motors"
│ Parent: 210-PP-001
│ Initial values: 100HP, 480V, TEFC
│ [View Details]
```

#### Compare View (Diff)
```
COMPARING: v3 → v4
─────────────────────────────────────────────────────────

PROPERTY          │ v3 (OLD)      │ v4 (NEW)
──────────────────┼───────────────┼───────────────
rated_power       │ 100 HP        │ 150 HP        ← CHANGED
voltage           │ 600V          │ 600V
efficiency        │ 95.4%         │ 96.2%         ← CHANGED
frame_size        │ 404T          │ 445T          ← CHANGED
weight            │ 850 lbs       │ 1,100 lbs     ← CHANGED
──────────────────┴───────────────┴───────────────

RELATED CHANGES:
├── Cable 210-M-001-PWR: v2 → v3
├── VFD 210-VFD-001: v1 → v2
└── Package EL-M040: regenerated
```

### Database Schema

```sql
-- Asset Versions
CREATE TABLE asset_versions (
    id UUID PRIMARY KEY,
    asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
    version_number INT NOT NULL,
    
    -- Snapshot (complete asset state at this version)
    data JSONB NOT NULL,
    
    -- Metadata
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT NOW(),
    change_reason TEXT,
    change_request_id UUID REFERENCES change_requests(id),
    
    -- Diff from previous version (for efficiency)
    changes JSONB,
    
    UNIQUE(asset_id, version_number)
);

-- Audit Log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    
    entity_type VARCHAR(50), -- ASSET, CABLE, RULE, etc.
    entity_id UUID,
    entity_identifier VARCHAR(100), -- Tag or name
    
    action VARCHAR(50), -- CREATE, MODIFY, DELETE, ROLLBACK, etc.
    
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT NOW(),
    
    old_values JSONB,
    new_values JSONB,
    change_summary TEXT,
    
    linked_cr_id UUID REFERENCES change_requests(id),
    
    ip_address INET,
    user_agent TEXT
);

-- Indexes
CREATE INDEX idx_versions_asset ON asset_versions(asset_id, version_number DESC);
CREATE INDEX idx_audit_project ON audit_log(project_id, changed_at DESC);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_user ON audit_log(changed_by);
CREATE INDEX idx_audit_cr ON audit_log(linked_cr_id);
```

### Audit Log View

```
AUDIT LOG: Project GoldMine
─────────────────────────────────────────────────────────

Filter: [All Users ▼] [All Actions ▼] [Last 7 days ▼]

2025-11-24 15:30 | admin@aurumax.com
├── Action: MODIFY
├── Asset: 210-M-001
├── Change: rated_power: 100 → 150
├── Linked CR: CR-2025-042
└── IP: 192.168.1.100

2025-11-24 15:31 | system
├── Action: AUTO_UPDATE
├── Asset: 210-M-001-PWR (Cable)
├── Change: size: 3x#4 → 3x#2 AWG
├── Triggered by: Rule "Cable sizing for motors"
└── Parent change: 210-M-001

2025-11-24 15:32 | admin@aurumax.com
├── Action: REGENERATE
├── Package: EL-M040
├── Result: SUCCESS
└── Download: EL-M040_Rev3.xlsx

[Export Audit Log] [Advanced Filters]
```

---

## Part 2: Baselines & Impact Analysis (v0.2.8)

### Project Baselines

**Concept:** Baseline = Snapshot of entire project at a moment in time (like Git commit for engineering)

#### Baseline Workflow

```
PROJECT: GoldMine Phase 1
─────────────────────────────────────────────────────────

BASELINES:
═══════════════════════════════════════════════════════

📌 BL-003 "IFC Release" (CURRENT) ────────────────────
│ Date: 2025-11-24
│ Status: APPROVED
│ Assets: 1,247 | Cables: 892 | Rules: 14
│ Created by: Project Manager
│ Approved by: Client Rep
│ [View] [Compare with BL-002] [Export]
│
📌 BL-002 "60% Design" ───────────────────────────────
│ Date: 2025-10-15
│ Status: SUPERSEDED
│ Assets: 1,102 | Cables: 756 | Rules: 12
│ [View] [Compare] [Export]
│
📌 BL-001 "30% Design" ───────────────────────────────
│ Date: 2025-09-01
│ Status: SUPERSEDED
│ Assets: 423 | Cables: 0 | Rules: 8
│ [View] [Compare] [Export]
│
═══════════════════════════════════════════════════════
[+ Create New Baseline]
```

#### Creating a Baseline

```
CREATE BASELINE
═══════════════════════════════════════════════════════

Name: IFC Release
Description: Issued for Construction - Final Design
Date: 2025-11-24

Include:
☑️ All Engineering Assets (1,247)
☑️ All Cables (892)
☑️ All Rules (14)
☑️ All Packages (12)
☑️ Location Structure
☑️ Functional Structure

Options:
☑️ Lock baseline (prevent modifications)
☐ Require approval before unlock
☑️ Generate change report vs previous baseline

[Cancel] [Create Baseline]
```

#### Baseline Compare (Project-Level Diff)

```
COMPARING: BL-002 (60%) → BL-003 (IFC)
─────────────────────────────────────────────────────────

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
│ Mechanical      │ 10    │ 2       │ 8        │ 18      │
└─────────────────┴───────┴─────────┴──────────┴─────────┘

SIGNIFICANT CHANGES:
├── 🆕 NEW: Area 220 added (45 assets)
├── ❌ DELETED: 210-PP-003 (cancelled by client)
├── ⚠️ MODIFIED: All motors upgraded to 600V
└── 📦 NEW PACKAGES: IO-P040, VFD Schedule

[Export Change Report] [Export Full Comparison]
```

### Database Schema

```sql
-- Project Baselines
CREATE TABLE project_baselines (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    
    code VARCHAR(20) UNIQUE NOT NULL, -- BL-001, BL-002, etc.
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Snapshot (complete project state)
    snapshot_data JSONB NOT NULL,
    
    -- Summary stats
    asset_count INT,
    cable_count INT,
    rule_count INT,
    package_count INT,
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    
    -- Status
    status VARCHAR(20) DEFAULT 'DRAFT', -- DRAFT, APPROVED, SUPERSEDED
    is_locked BOOLEAN DEFAULT FALSE
);

-- Change Requests
CREATE TABLE change_requests (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    
    cr_number VARCHAR(20) UNIQUE NOT NULL, -- CR-2025-042
    title VARCHAR(200) NOT NULL,
    description TEXT,
    
    requested_by VARCHAR(100),
    requested_date DATE DEFAULT CURRENT_DATE,
    
    -- Impact estimates
    cost_impact DECIMAL(12,2),
    schedule_impact_days INT,
    
    -- Status workflow
    status VARCHAR(20) DEFAULT 'PENDING',
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    implemented_by UUID REFERENCES users(id),
    implemented_at TIMESTAMP,
    
    -- Links
    affected_assets UUID[],
    baseline_before UUID REFERENCES project_baselines(id),
    baseline_after UUID REFERENCES project_baselines(id)
);
```

---

### Impact Analysis

**Concept:** When changing anything, show everything that will be affected

#### Example: Changing Motor HP

```
USER: Change 210-M-001 from 100HP → 150HP
─────────────────────────────────────────────────────────

IMPACT ANALYSIS:
═══════════════════════════════════════════════════════

⚠️  IMPACT SUMMARY: 12 items affected
─────────────────────────────────────────────────────────

DIRECT IMPACTS (3):
├── 🔌 Cable 210-M-001-PWR
│   └── Size: 3x#4 AWG → 3x#2 AWG (recalculate)
│   └── Cost: +$450
│
├── ⚡ VFD 210-VFD-001
│   └── Rating: 100HP → 150HP (upgrade required)
│   └── Cost: +$2,500
│
└── 🔧 MCC Bucket
    └── Breaker: 200A → 300A (upgrade required)

INDIRECT IMPACTS (5):
├── 📦 Package EL-M040 (Motor Schedule)
│   └── Regenerate required
│
├── 📦 Package CA-P040 (Cable Schedule)  
│   └── Regenerate required
│
├── 💰 CBS: Electrical Budget
│   └── +$2,950 (total impact)
│
├── 📋 Rule: "Motors >125HP require reduced voltage starter"
│   └── NEW RULE APPLIES → Create soft starter?
│
└── 🏗️ Physical: Installation
    └── Foundation may need reinforcement

DOWNSTREAM (4):
├── 210-PP-001 (Pump) - Parent asset updated timestamp
├── Area 210 - Equipment list changed
├── IO Allocation - No change (same signals)
└── P&ID - May need revision

═══════════════════════════════════════════════════════
TOTAL COST IMPACT: +$2,950
TOTAL SCHEDULE IMPACT: +2 weeks (procurement)

[Cancel] [Apply Changes] [Apply + Auto-Fix]
═══════════════════════════════════════════════════════
```

#### Impact Analysis Engine

```python
class ImpactAnalyzer:
    def analyze_property_change(
        self, 
        asset_id: UUID, 
        property_name: str,
        old_value: Any,
        new_value: Any
    ) -> ImpactReport:
        """
        Analyze impact of property change
        """
        impacts = []
        
        # 1. Direct: Child assets (cables, VFDs, etc.)
        children = get_child_assets(asset_id)
        for child in children:
            impact = analyze_child_impact(child, property_name, new_value)
            impacts.append(impact)
        
        # 2. Direct: Rules that may now apply/unapply
        rules = get_affected_rules(asset_id, property_name, new_value)
        for rule in rules:
            impact = analyze_rule_impact(rule, asset_id)
            impacts.append(impact)
        
        # 3. Indirect: Packages containing this asset
        packages = get_packages_containing(asset_id)
        for pkg in packages:
            impacts.append({
                "type": "PACKAGE",
                "entity": pkg,
                "action": "REGENERATE",
                "reason": f"{property_name} changed"
            })
        
        # 4. Indirect: Cost structure
        if property_name in COST_AFFECTING_PROPS:
            cost_impact = calculate_cost_impact(asset_id, old_value, new_value)
            impacts.append(cost_impact)
        
        # 5. Downstream: Parent assets (timestamp update)
        parent = get_parent_asset(asset_id)
        if parent:
            impacts.append({
                "type": "PARENT",
                "entity": parent,
                "action": "UPDATE_TIMESTAMP"
            })
        
        return ImpactReport(
            total_count=len(impacts),
            direct=filter_direct(impacts),
            indirect=filter_indirect(impacts),
            downstream=filter_downstream(impacts),
            cost_impact=sum_cost_impacts(impacts),
            schedule_impact=max_schedule_impacts(impacts)
        )
```

---

## Workflows

### Workflow 1: Making a change with Impact Analysis

1. User modifies property (e.g., Motor HP: 100 → 150)
2. System calculates impacts (1-2 seconds)
3. Modal displays Impact Analysis summary
4. User reviews:
   - Direct impacts (cables, VFDs, MCCs)
   - Indirect impacts (packages, budget)
   - Downstream (parent assets, P&IDs)
5. User chooses:
   - **Cancel** - Abort change
   - **Apply** - Apply change only
   - **Apply + Auto-Fix** - Apply + update cables/VFDs automatically

### Workflow 2: Creating a Baseline

1. User clicks "Create Baseline"
2. Enters name and description
3. Selects what to include (assets, cables, rules, etc.)
4. System creates snapshot (2-5 seconds for 1000+ assets)
5. Baseline saved with status: DRAFT
6. User requests approval
7. Approver reviews, approves
8. Baseline status → APPROVED
9. Baseline is locked (no edits)

### Workflow 3: Comparing Baselines

1. User selects two baselines
2. Clicks "Compare"
3. System generates diff report:
   - Added/deleted/modified counts
   - Changes by discipline
   - Significant changes highlighted
4. User exports:
   - Summary PDF (executive level)
   - Detailed Excel (engineering level)

### Workflow 4: Change Request Management

1. Client requests change: "Upgrade all pumps to 150HP"
2. Project Manager creates CR-2025-042
3. Engineer analyzes impact:
   - Affects 8 pumps
   - Cost impact: +$24,000
   - Schedule impact: +2 weeks
4. PM submits for approval
5. Client approves
6. Engineer implements changes
7. System links all edits to CR-2025-042
8. New baseline created: "BL-004 - Post CR-042"

---

## API Endpoints

```
# Version History
GET    /api/v1/assets/{id}/versions           List all versions
GET    /api/v1/assets/{id}/versions/{version}  Get specific version
POST   /api/v1/assets/{id}/rollback/{version}  Rollback to version
GET    /api/v1/assets/{id}/compare/{v1}/{v2}   Compare two versions

# Audit Log
GET    /api/v1/projects/{id}/audit-log         Get audit log (paginated)
GET    /api/v1/audit-log?user={user}           Filter by user
GET    /api/v1/audit-log?cr={cr_id}            Filter by change request

# Baselines
POST   /api/v1/baselines                       Create baseline
GET    /api/v1/baselines/{id}                  Get baseline
PUT    /api/v1/baselines/{id}                  Update baseline
POST   /api/v1/baselines/{id}/approve          Approve baseline
POST   /api/v1/baselines/{id}/lock             Lock baseline
GET    /api/v1/baselines/{id1}/compare/{id2}   Compare baselines

# Impact Analysis
POST   /api/v1/impact-analysis                 Analyze change impact
POST   /api/v1/assets/{id}/analyze-change      Analyze property change

# Change Requests
POST   /api/v1/change-requests                 Create CR
GET    /api/v1/change-requests/{id}            Get CR
PUT    /api/v1/change-requests/{id}            Update CR
POST   /api/v1/change-requests/{id}/approve    Approve CR
POST   /api/v1/change-requests/{id}/implement  Mark implemented
GET    /api/v1/projects/{id}/change-requests   List all CRs
```

---

## Verification Plan

### Database
```bash
docker exec synapse-backend-1 alembic upgrade head
docker exec synapse-backend-1 pytest tests/test_version_history.py
docker exec synapse-backend-1 pytest tests/test_impact_analysis.py
docker exec synapse-backend-1 pytest tests/test_baselines.py
```

### Frontend Tests
```bash
cd apps/synapse/frontend
npm run test -- VersionHistory.test.tsx
npm run test -- ImpactAnalysis.test.tsx
npm run test -- BaselineCompare.test.tsx
```

### Manual Testing
1. Create asset with properties
2. Modify property → Verify version created
3. View version history → Verify timeline
4. Compare v1 vs v2 → Verify diff display
5. Rollback to v1 → Verify property restored
6. Create baseline → Verify snapshot
7. Make changes → Create new baseline
8. Compare baselines → Verify diff report

---

**Updated:** 2025-11-24
