# Rule Visualization & Editor

**Versions:** v0.2.9 (Visualization), v0.2.10 (Visual Editor), v0.2.11 (Templates)  
**Goal:** Visual rule management with graph view, drag-drop editor, and template library

---

## Overview

SYNAPSE provides a modern visual interface for rule management:

| Version | Feature | Description |
|---------|---------|-------------|
| **v0.2.9** | Rule Visualization | 2D graph view of rule dependencies |
| **v0.2.10** | Visual Rule Editor | Drag-drop condition/action builder |
| **v0.2.11** | Rule Templates | 15+ predefined templates |

---

## Part 1: Rule Visualization (v0.2.9)

### 2D Rule Graph (ReactFlow)

**Concept:** Visualize rules as a directed graph showing dependencies and execution flow

#### Example View

```
RULE GRAPH VIEW (ReactFlow)
═══════════════════════════════════════════════════════════════════

                    ┌─────────────────────┐
                    │ 🎯 TRIGGER          │
                    │ Asset Created       │
                    │ Type = PUMP         │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │ ⚙️ RULE-001     │ │ ⚙️ RULE-002     │ │ ⚙️ RULE-003     │
    │ Create Motor    │ │ Set Voltage     │ │ Create Seal     │
    │ Priority: 10    │ │ Priority: 10    │ │ Priority: 10    │
    │ ✅ Active       │ │ ✅ Active       │ │ ⏸️ Disabled     │
    └────────┬────────┘ └────────┬────────┘ └─────────────────┘
             │                   │
             ▼                   │
    ┌─────────────────┐          │
    │ 🔌 RULE-004     │          │
    │ Create Cable    │◄─────────┘
    │ Priority: 20    │
    │ Depends on:     │
    │ Motor + Voltage │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ 📦 RULE-005     │
    │ Add to Package  │
    │ Priority: 30    │
    │ EL-M040         │
    └─────────────────┘

═══════════════════════════════════════════════════════════════════
[2D View] [List View] [+ Add Rule] [Run Selected]
```

### Interactive Features

**Hover Over Node:**
```
┌─ RULE-001: Pumps require Motor ─────────────────────┐
│ Condition:                                           │
│   asset.type == "PUMP"                               │
│                                                      │
│ Action:                                              │
│   CREATE_CHILD: MOTOR                                │
│   - rated_power = {{parent.required_hp}}            │
│   - voltage = {{project.standard_voltage}}          │
│                                                      │
│ Triggered: 45 times                                  │
│ Last run: 2025-11-24 15:30                           │
│                                                      │
│ [Edit] [View History] [Test]                         │
└──────────────────────────────────────────────────────┘
```

**Click Node → Opens Detail Panel:**
```
┌─ Rule Details: RULE-001 ─────────────────────────────┐
│                                                       │
│ Name: Pumps require Motor                            │
│ Priority: FIRM (10)                                   │
│ Status: ✅ Active                                     │
│                                                       │
│ Condition (Natural Language):                         │
│ "When asset type is PUMP"                            │
│                                                       │
│ Action:                                               │
│ CREATE_CHILD: MOTOR                                   │
│ - Tag pattern: {{parent.tag}}-M-001                  │
│ - HP: {{parent.required_hp}}                         │
│ - Voltage: {{project.standard_voltage}}              │
│                                                       │
│ Execution History (Last 10):                          │
│ ├─ 2025-11-24 15:30 - 210-PP-001 → Created 210-M-001│
│ ├─ 2025-11-23 14:15 - 210-PP-002 → Created 210-M-002│
│ └─ 2025-11-22 10:00 - 220-PP-001 → Created 220-M-001│
│                                                       │
│ [Edit Rule] [Disable] [Delete] [View Code]           │
└───────────────────────────────────────────────────────┘
```

### Execution Trace Visualization

**Live execution overlay on graph:**
```
USER: Create asset 210-PP-001 (Pump)
───────────────────────────────────────────────────────

RULE GRAPH (Live Execution):
═══════════════════════════════════════════════════════

                    ┌─────────────────────┐
                    │ 🎯 TRIGGER          │ ✅ MATCHED
                    │ Asset Created: PUMP │
                    └──────────┬──────────┘
                               │ ✅ Executing...
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │ ⚙️ RULE-001     │ │ ⚙️ RULE-002     │ │ ⚙️ RULE-003     │
    │ ✅ EXECUTED     │ │ ✅ EXECUTED     │ │ ⏭️ SKIPPED      │
    │ Created Motor   │ │ Set 600V        │ │ (disabled)      │
    └────────┬────────┘ └────────┬────────┘ └─────────────────┘
             │                   │
             ▼                   │
    ┌─────────────────┐          │
    │ 🔌 RULE-004     │          │
    │ ⏳ RUNNING...   │◄─────────┘
    │ Creating cable  │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ 📦 RULE-005     │
    │ ⏱️ PENDING      │
    └─────────────────┘

Execution Log:
├─ RULE-001: ✅ Created 210-M-001 (12ms)
├─ RULE-002: ✅ Set voltage=600V (3ms)
├─ RULE-004: ⏳ Creating cable... (current)
└─ RULE-005: ⏱️ Waiting...
```

### ReactFlow Implementation

```typescript
// apps/synapse/frontend/src/components/RuleGraph.tsx

import React from 'react';
import ReactFlow, { 
  Node, 
  Edge, 
  Background,
  Controls,
  MiniMap
} from 'reactflow';
import 'reactflow/dist/style.css';

interface RuleGraphProps {
  rules: Rule[];
}

export function RuleGraph({ rules }: RuleGraphProps) {
  const { nodes, edges } = useMemo(() => {
    // Convert rules to ReactFlow nodes
    const nodes: Node[] = rules.map(rule => ({
      id: rule.id,
      type: 'ruleNode',
      position: calculatePosition(rule), // Auto-layout
      data: {
        rule,
        status: rule.is_active ? 'active' : 'disabled',
        type: getRuleType(rule),
      }
    }));
    
    // Create edges based on dependencies
    const edges: Edge[] = [];
    for (const rule of rules) {
      for (const depId of rule.dependencies) {
        edges.push({
          id: `${depId}-${rule.id}`,
          source: depId,
          target: rule.id,
          animated: true,
          style: { stroke: '#366092' }
        });
      }
    }
    
    return { nodes, edges };
  }, [rules]);
  
  return (
    <div className="rule-graph" style={{height: '600px'}}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={{ruleNode: RuleNode}}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}

// Custom Rule Node Component
function RuleNode({ data }: { data: any }) {
  const { rule, status } = data;
  
  return (
    <div className={`rule-node ${status}`}>
      <div className="rule-icon">
        {getIcon(rule.action_type)}
      </div>
      <div className="rule-name">{rule.name}</div>
      <div className="rule-priority">Priority: {rule.priority}</div>
      <div className="rule-status">
        {status === 'active' ? '✅' : '⏸️'}
      </div>
    </div>
  );
}
```

---

## Part 2: Visual Rule Editor (v0.2.10)

### Node-Based Editor (ReactFlow)

**Concept:** Drag-and-drop interface for condition and action building

#### Condition Builder

```
CONDITION BUILDER (Node-Based)
═══════════════════════════════════════════════════════════════════

┌─── CONDITION ────────────────────────────────────────────────────┐
│                                                                  │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐         │
│  │ 📦 Asset   │      │ 🔗 AND     │      │ ✓ Result   │         │
│  │            │─────▶│            │─────▶│            │         │
│  │ type=MOTOR │      │            │      │ MATCH      │         │
│  └────────────┘      │            │      └────────────┘         │
│                      │            │                              │
│  ┌────────────┐      │            │                              │
│  │ 📊 Property│─────▶│            │                              │
│  │            │      └────────────┘                              │
│  │ HP > 75    │                                                  │
│  └────────────┘                                                  │
│                                                                  │
│  [+ Add Condition] [Switch to Form] [Switch to Code]             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

#### Action Builder

```
ACTION BUILDER (Node-Based)
═══════════════════════════════════════════════════════════════════

┌─── ACTION ───────────────────────────────────────────────────────┐
│                                                                  │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐         │
│  │ ➕ Create  │      │ 📝 Set     │      │ 🔗 Link    │         │
│  │            │─────▶│            │─────▶│            │         │
│  │ type=VFD   │      │ rating=HP  │      │ parent=    │         │
│  │            │      │ voltage=   │      │ MOTOR      │         │
│  └────────────┘      │ from_motor │      └────────────┘         │
│                      └────────────┘                              │
│                                                                  │
│  [+ Add Action] [Switch to Form] [Switch to Code]                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Form Builder Mode

```
CONDITION BUILDER (Form Mode)
═══════════════════════════════════════════════════════════════════

┌─ Condition Group (AND) ──────────────────────────────────────────┐
│                                                                   │
│  ┌─ Condition 1 ───────────────────────────────────────────────┐ │
│  │ Field: [type ▼]  Operator: [equals ▼]  Value: [MOTOR    ]   │ │
│  │                                               [× Remove]    │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─ Condition 2 ───────────────────────────────────────────────┐ │
│  │ Field: [rated_power ▼] Operator: [> ▼]  Value: [75      ]   │ │
│  │                                               [× Remove]    │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  [+ Add Condition]  [+ Add OR Group]                              │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Natural Language Mode

```
CONDITION BUILDER (Natural Language Mode)
═══════════════════════════════════════════════════════════════════

"When [asset type ▼] is [MOTOR ▼] 
 AND [property ▼] [rated_power ▼] is [greater than ▼] [75] HP
 AND [property ▼] [voltage ▼] is [equals ▼] [600] V"

[+ Add Condition]

═══════════════════════════════════════════════════════════════════
Preview: asset.type == "MOTOR" && asset.rated_power > 75 && asset.voltage == 600
```

### Code Mode (Monaco Editor)

```
CONDITION BUILDER (Code Mode - Power Users)
═══════════════════════════════════════════════════════════════════

┌─ Python Expression ──────────────────────────────────────────────┐
│                                                                   │
│  1 │ # Condition for VFD requirement                             │
│  2 │ def evaluate(asset, context):                               │
│  3 │     return (                                                │
│  4 │         asset.type == "MOTOR" and                           │
│  5 │         asset.rated_power > 75 and                          │
│  6 │         asset.voltage == 600 and                            │
│  7 │         context.project.country in ["CA", "US"]             │
│  8 │     )                                                       │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘

Syntax: ✅ Valid    [Format] [Validate] [Test with Sample Asset]
```

### Rule Testing & Simulation

```
RULE TESTER
═══════════════════════════════════════════════════════════════════

Test Asset: [210-M-001 ▼] or [Create Test Asset]

┌─ Test Asset Properties ──────────────────────────────────────────┐
│ tag: 210-M-001                                                    │
│ type: MOTOR                                                       │
│ rated_power: 100 HP                                               │
│ voltage: 600 V                                                    │
│ location: Area 210                                                │
└───────────────────────────────────────────────────────────────────┘

[▶ Run Test]

┌─ RESULTS ────────────────────────────────────────────────────────┐
│                                                                   │
│  ✅ Condition: MATCHED                                            │
│     - type == "MOTOR" ✓                                           │
│     - rated_power > 75 ✓ (100 > 75)                               │
│     - voltage == 600 ✓                                            │
│                                                                   │
│  📦 Actions to Execute:                                           │
│     1. CREATE_CHILD: VFD (210-M-001-VFD-001)                      │
│        - rated_power: 100 HP                                      │
│        - voltage: 600 V                                           │
│     2. CREATE_CABLE: Power cable (triggered)                      │
│     3. ADD_TO_PACKAGE: EL-M040                                    │
│                                                                   │
│  ⚠️ Conflicts: None                                               │
│  💰 Cost Impact: +$3,500 (VFD) + $450 (cable)                     │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘

[Execute for Real] [Test Another] [Close]
```

---

## Part 3: Rule Templates Library (v0.2.11)

### Predefined Templates

#### Equipment Rules (5 templates)

**1. Pump → Motor**
```yaml
name: "Pumps require Motor"
priority: FIRM (10)
condition:
  type: asset.type == "PUMP"
action:
  type: CREATE_CHILD
  child_type: MOTOR
  properties:
    tag_pattern: "{{parent.tag}}-M-001"
    rated_power: "{{parent.required_hp}}"
    voltage: "{{project.standard_voltage}}"
    rpm: 1800
    enclosure: "TEFC"
```

**2. Motor → Power Cable**
```yaml
name: "Motors require Power Cable"
priority: FIRM (10)
condition:
  type: asset.type == "MOTOR"
action:
  type: CREATE_CABLE
  cable_type: POWER
  properties:
    cable_number: "{{parent.tag}}-PWR"
    from: "{{parent.mcc_panel}}"
    to: "{{parent.tag}}"
    size: "{{calculate_cable_size(parent.rated_power, parent.voltage)}}"
    route: "{{parent.cable_tray}}"
```

**3. Motor >75HP → VFD**
```yaml
name: "Motors >75HP require VFD"
priority: FIRM (10)
condition:
  - asset.type == "MOTOR"
  - asset.rated_power > 75
action:
  type: CREATE_CHILD
  child_type: VFD
  properties:
    tag_pattern: "{{parent.tag}}-VFD-001"
    rated_power: "{{parent.rated_power}}"
    voltage: "{{parent.voltage}}"
    manufacturer: "ABB"
    enclosure: "NEMA 12"
```

**4. VFD → Control Cable**
```yaml
name: "VFDs require Control Cable"
priority: FIRM (10)
condition:
  type: asset.type == "VFD"
action:
  type: CREATE_CABLE
  cable_type: CONTROL
  properties:
    cable_number: "{{parent.tag}}-CTRL"
    from: "PLC-MAIN"
    to: "{{parent.tag}}"
    size: "6x18 AWG"
    type: "SHIELDED"
```

**5. Instrument → Signal Cable**
```yaml
name: "Instruments require Signal Cable"
priority: FIRM (10)
condition:
  - asset.type in ["FT", "PT", "LT", "TT"]
  - asset.output == "4-20mA"
action:
  type: CREATE_CABLE
  cable_type: SIGNAL
  properties:
    cable_number: "{{parent.tag}}-S"
    from: "PLC-{{parent.io_card}}"
    to: "{{parent.tag}}"
    size: "2x18 AWG"
    type: "SHIELDED_TWISTED"
```

#### Property Rules (4 templates)

**6. Set Voltage by Country**
```yaml
name: "Set Motor Voltage by Country"
priority: FIRM (10)
condition:
  type: asset.type == "MOTOR"
action:
  type: SET_PROPERTY
  property: voltage
  value_map:
    CA: 600
    US: 480
    EU: 400
  source: "{{project.country}}"
```

**7. Set Enclosure by Location**
```yaml
name: "Set Enclosure by Location"
priority: PROJECT (20)
condition:
  type: asset.type in ["MOTOR", "VFD", "INSTRUMENT"]
action:
  type: SET_PROPERTY
  property: enclosure
  value_map:
    INDOOR: "NEMA 1"
    OUTDOOR: "NEMA 4X"
    HAZARDOUS: "NEMA 7"
  source: "{{parent.location.area_classification}}"
```

**8. Set Insulation by Temperature**
```yaml
name: "Set Motor Insulation by Temperature"
priority: FIRM (10)
condition:
  - asset.type == "MOTOR"
action:
  type: SET_PROPERTY
  property: insulation_class
  value_map:
    NORMAL: "F"  # <40°C
    ELEVATED: "H"  # 40-80°C
    HIGH: "H+"  # >80°C
  evaluate: |
    lambda asset: (
      "NORMAL" if asset.temperature < 40
      else "ELEVATED" if asset.temperature < 80
      else "HIGH"
    )
```

**9. Set Cable Tray by Area**
```yaml
name: "Assign Cable Tray by Area"
priority: PROJECT (20)
condition:
  type: entity_type == "CABLE"
action:
  type: SET_PROPERTY
  property: cable_tray
  value_map:
    "Area 210": "T-210-POWER"
    "Area 220": "T-220-CONTROL"
    "Area 300": "T-300-SIGNAL"
  source: "{{cable.from_location.area}}"
```

#### Validation Rules (3 templates)

** 10. Motor HP ≥ Pump Requirement**
```yaml
name: "Validate Motor HP matches Pump"
priority: FIRM (10)
condition:
  - asset.type == "PUMP"
  - asset.has_child("MOTOR")
action:
  type: VALIDATE
  validation: |
    lambda asset: (
      asset.child_motor.rated_power >= asset.required_hp
    )
  error_message: "Motor HP ({motor_hp}) < Pump requirement ({required_hp})"
```

**11. Cable Size for Load (CEC)**
```yaml
name: "Validate Cable Sizing (CEC Table 2)"
priority: FIRM (10)
condition:
  type: cable.type == "POWER"
action:
  type: VALIDATE
  validation: |
    lambda cable: (
      cable.ampacity >= cable.load_current * 1.25
    )
  error_message: "Cable undersized: {cable.size} for {cable.load_current}A"
```

**12. VFD Rating ≥ Motor HP**
```yaml
name: "Validate VFD Rating"
priority: FIRM (10)
condition:
  - asset.type == "VFD"
action:
  type: VALIDATE
  validation: |
    lambda asset: (
      asset.rated_power >= asset.parent_motor.rated_power
    )
  error_message: "VFD undersized: {vfd_hp}HP for {motor_hp}HP motor"
```

#### Package Rules (3 templates)

**13. Instruments → IN-P040**
```yaml
name: "Add Instruments to Package IN-P040"
priority: PROJECT (20)
condition:
  type: asset.type in ["FT", "PT", "LT", "TT", "AT"]
action:
  type: ADD_TO_PACKAGE
  package: "IN-P040"
```

**14. Motors → EL-M040**
```yaml
name: "Add Motors to Package EL-M040"
priority: PROJECT (20)
condition:
  type: asset.type == "MOTOR"
action:
  type: ADD_TO_PACKAGE
  package: "EL-M040"
```

**15. Cables → CA-P040**
```yaml
name: "Add Cables to Package CA-P040"
priority: PROJECT (20)
condition:
  type: entity_type == "CABLE"
action:
  type: ADD_TO_PACKAGE
  package: "CA-P040"
```

### Template UI

```
RULE TEMPLATES
═══════════════════════════════════════════════════════════════════

Search: [motor cable_]              Filter: [All ▼] [Equipment ▼]

⭐ Equipment Rules (5)
├── 🔧 Pump → Motor                                    [Use Template]
├── 🔧 Motor → Cable                                   [Use Template]
├── 🔧 Motor >75HP → VFD                               [Use Template]
├── 🔧 VFD → Control Cable                             [Use Template]
└── 🔧 Instrument → Signal Cable                       [Use Template]

⭐ Property Rules (4)
├── 📝 Set Voltage by Country (CA=600V, US=480V)       [Use Template]
├── 📝 Set Enclosure by Location                       [Use Template]
├── 📝 Set Insulation by Temp                          [Use Template]
└── 📝 Set Cable Tray by Area                          [Use Template]

⭐ Validation Rules (3)
├── ✅ Motor HP ≥ Pump requirement                     [Use Template]
├── ✅ Cable size for load (CEC/NEC)                   [Use Template]
└── ✅ VFD rating ≥ Motor HP                           [Use Template]

⭐ Package Rules (3)
├── 📦 Instruments → IN-P040                           [Use Template]
├── 📦 Motors → EL-M040                                [Use Template]
└── 📦 Cables → CA-P040                                [Use Template]

[+ Create Custom Template] [Import Template] [Export All]
```

### Using a Template

```
1. User clicks "Use Template" on "Motor >75HP → VFD"
2. System loads template into editor
3. User can customize:
   - Threshold (75 HP → 100 HP)
   - VFD manufacturer (ABB → Siemens)
   - Tag pattern
4. User saves as new rule or overwrites existing
```

---

## Database Schema

```sql
-- Rule Templates
CREATE TABLE rule_templates (
    id UUID PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- EQUIPMENT, PROPERTY, VALIDATION, PACKAGE
    
    -- Template definition (YAML)
    template_yaml TEXT NOT NULL,
    
    -- Metadata
    is_builtin BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Usage stats
    usage_count INT DEFAULT 0,
    last_used_at TIMESTAMP
);

-- User Custom Templates
CREATE TABLE user_rule_templates (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    template_id UUID REFERENCES rule_templates(id),
    
    -- Customizations
    customized_yaml TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Tech Stack

| Component | Library | License |
|-----------|---------|---------|
| 2D Graph | ReactFlow | MIT |
| Node Editor | ReactFlow + Custom Nodes | MIT |
| Code Editor | Monaco Editor (VS Code) | MIT |
| Form Builder | React Hook Form | MIT |
| Drag & Drop | dnd-kit | MIT |
| YAML Parser | js-yaml | MIT |

---

## API Endpoints

```
# Rule Visualization
GET    /api/v1/rules/graph                Get rule graph data
GET    /api/v1/rules/{id}/execution-trace Get execution history

# Rule Editor
POST   /api/v1/rules/validate-condition   Validate condition syntax
POST   /api/v1/rules/test                 Test rule on sample asset
POST   /api/v1/rules                      Create rule
PUT    /api/v1/rules/{id}                 Update rule
DELETE /api/v1/rules/{id}                 Delete rule

# Templates
GET    /api/v1/rule-templates              List all templates
GET    /api/v1/rule-templates/{code}       Get template
POST   /api/v1/rule-templates              Create custom template
PUT    /api/v1/rule-templates/{code}       Update template
DELETE /api/v1/rule-templates/{code}       Delete custom template
POST   /api/v1/rule-templates/{code}/use   Instantiate template
```

---

## Verification Plan

### Frontend Tests
```bash
cd apps/synapse/frontend
npm run test -- RuleGraph.test.tsx
npm run test -- RuleEditor.test.tsx
npm run test -- RuleTester.test.tsx
npm run test -- RuleTemplates.test.tsx
```

### Manual Testing
1. Open Rule Graph
   - Verify all rules displayed as nodes
   - Verify edges show dependencies
   - Click node → detail panel opens
2. Create new rule
   - Test Natural Language mode
   - Test Form Builder mode
   - Test Node-Based mode
   - Test Code mode
   - Verify all modes generate same condition
3. Test rule
   - Create test asset
   - Run rule simulation
   - Verify predicted actions
4. Use template
   - Select "Motor >75HP → VFD" template
   - Customize threshold
   - Save as new rule
   - Verify rule works

---

**Updated:** 2025-11-24
