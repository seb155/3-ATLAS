# Visual Rule Editor Workflow

**Creating rules with drag-and-drop interface**

> **Detailed specs:** See [rule-visualization-editor.md](../../.dev/roadmap/backlog/rule-visualization-editor.md)

---

## When to Use

Use the visual editor when:
- ✅ Creating rules without coding
- ✅ Building complex conditions visually
- ✅ Testing rules before deployment
- ✅ Learning rule structure

Use code mode when:
- ✅ Complex logic (if/else)
- ✅ Mathematical calculations
- ✅ Power user with Python knowledge

---

## Quick Start

### Step 1: Open Rule Editor

1. Navigate to **Rules**
2. Click **[+ Create Rule]**
3. Choose editor mode:
   - **Natural Language** (recommended for beginners)
   - **Form Builder** (structured inputs)
   - **Node-Based** (visual flowchart)
   - **Code Mode** (Python for power users)

---

## Natural Language Mode

**Best for:** Beginners, simple rules

### Example: Create Motor Rule

```
┌─ Natural Language Editor ────────────────┐
│                                           │
│ When [asset type ▼] is [MOTOR ▼]         │
│ AND [property ▼] [rated_power ▼]         │
│     is [greater than ▼] [75] HP          │
│                                           │
│ Then CREATE [VFD ▼]                       │
│   with Tag: [{{parent.tag}}-VFD-001]     │
│   and HP: [{{parent.rated_power}}]       │
│                                           │
│ [+ Add Condition] [+ Add Action]          │
│ [Test] [Save]                             │
└───────────────────────────────────────────┘
```

**Steps:**
1. Fill dropdowns for condition
2. Fill dropdowns for action
3. Click **[Test]** with sample asset
4. Click **[Save]**

---

## Form Builder Mode

**Best for:** Structured data entry

```
┌─ Form Builder ────────────────────────────┐
│                                            │
│ CONDITION:                                 │
│ ┌────────────────────────────────────────┐ │
│ │ Field: [type ▼]                        │ │
│ │ Operator: [equals ▼]                   │ │
│ │ Value: [MOTOR          ]               │ │
│ │                        [× Remove]      │ │
│ └────────────────────────────────────────┘ │
│ [+ Add Condition] [+ Add OR Group]         │
│                                            │
│ ACTION:                                    │
│ ┌────────────────────────────────────────┐ │
│ │ Type: [CREATE_CHILD ▼]                 │ │
│ │ Child Type: [VFD ▼]                    │ │
│ │ Tag Pattern: [{{parent.tag}}-VFD-001] │ │
│ │ Properties:                            │ │
│ │   rated_power: [{{parent.rated_power}}]│ │
│ │                        [× Remove]      │ │
│ └────────────────────────────────────────┘ │
│ [+ Add Action]                             │
│                                            │
│ [Test] [Save]                              │
└────────────────────────────────────────────┘
```

---

## Node-Based Mode

**Best for:** Visual thinkers

```
┌─ Node-Based Editor ───────────────────────┐
│                                            │
│  ┌──────────┐     ┌──────────┐            │
│  │ 📦 Asset │────▶│ 🔗 AND   │            │
│  │ type=    │     │          │            │
│  │ MOTOR    │     │          │            │
│  └──────────┘     │          │            │
│                   │          │            │
│  ┌──────────┐     │          │            │
│  │ 📊 Prop  │────▶│          │            │
│  │ HP > 75  │     └─────┬────┘            │
│  └──────────┘           │                 │
│                         ▼                 │
│                   ┌──────────┐            │
│                   │ ➕ Create│            │
│                   │ VFD      │            │
│                   └──────────┘            │
│                                            │
│ [+ Add Node] [Connect] [Test] [Save]       │
└────────────────────────────────────────────┘
```

**How to:**
1. Drag nodes from palette
2. Connect nodes with arrows
3. Configure each node
4. Test and save

---

## Testing Rules

### Before Saving

**Always test your rule:**

```
┌─ Rule Tester ─────────────────────────────┐
│                                            │
│ Test Asset: [Create Sample ▼]             │
│                                            │
│ Sample Asset:                              │
│ - Tag: TEST-M-001                          │
│ - Type: MOTOR                              │
│ - HP: 100                                  │
│                                            │
│ [▶ Run Test]                               │
│                                            │
│ RESULTS:                                   │
│ ✅ Condition: MATCHED                      │
│ ✅ Action: Would create TEST-M-001-VFD-001 │
│                                            │
│ [Execute for Real] [Test Another]          │
└────────────────────────────────────────────┘
```

---

## Using Templates

**Fastest way to create rules:**

1. Click **[Templates]** tab
2. Browse template library
3. Find "Motor >75HP → VFD"
4. Click **[Use Template]**
5. Customize if needed
6. Save

**Available Templates:** 15 predefined (see [rule-templates.md](../reference/rule-templates.md))

---

## Best Practices

✅ **Start with Natural Language** for simple rules  
✅ **Test before saving** - Always!  
✅ **Use templates** when available  
✅ **Switch to Code Mode** only for complex logic  
✅ **Name rules clearly** ("Motors >75HP require VFD")

---

## Common Mistakes

❌ **Not testing** → Rule breaks production data  
❌ **Complex conditions in Natural Language** → Use Code Mode  
❌ **Forgetting {{brackets}}** → Template variables need {{}}  
❌ **Wrong operator** → "equals" vs "greater than"

---

## Related Documentation

- [Rule Templates Reference](../reference/rule-templates.md)
- [Rule Visualization & Editor (Technical)](../../.dev/roadmap/backlog/rule-visualization-editor.md)
- [Rule Engine Reference](../reference/rule-engine.md)

---

**Updated:** 2025-11-24
