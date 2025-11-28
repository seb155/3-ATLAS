# Rule Templates Reference

**15 Predefined Rule Templates for Common Engineering Tasks**

---

## Overview

SYNAPSE includes **15 built-in rule templates** to accelerate project setup. These templates cover:

- ⚙️ **Equipment Rules** (5) - Auto-create child assets
- 📝 **Property Rules** (4) - Set properties automatically
- ✅ **Validation Rules** (3) - Enforce engineering standards
- 📦 **Package Rules** (3) - Auto-assign to deliverables

**How to Use:** Select template → Customize if needed → Save as project rule

---

## Equipment Rules

### Template 1: Pump → Motor

**Purpose:** Automatically create motor for every pump

**Condition:**
```
asset.type == "PUMP"
```

**Action:**
```
CREATE_CHILD: MOTOR
- Tag: {{parent.tag}}-M-001
- HP: {{parent.required_hp}}
- Voltage: {{project.standard_voltage}}
- RPM: 1800
- Enclosure: TEFC
```

**Example:**
```
Create: 210-PP-001 (Pump, 100HP required)
→ Auto-creates: 210-M-001 (Motor, 100HP, 600V, 1800RPM)
```

**Customization Options:**
- Change tag pattern
- Add/remove default properties
- Set different enclosure type

---

### Template 2: Motor → Power Cable

**Purpose:** Create power cable for every motor

**Condition:**
```
asset.type == "MOTOR"
```

**Action:**
```
CREATE_CABLE: POWER
- Cable#: {{parent.tag}}-PWR
- From: {{parent.mcc_panel}}
- To: {{parent.tag}}
- Size: {{calculate_cable_size(parent.rated_power, parent.voltage)}}
- Route: {{parent.cable_tray}}
```

**Example:**
```
Create: 210-M-001 (Motor, 100HP, 600V)
→ Auto-creates: 210-M-001-PWR (Power cable, 3x#2 AWG)
```

**Customization Options:**
- Change cable numbering
- Modify sizing calculation
- Add default route/tray

---

### Template 3: Motor >75HP → VFD

**Purpose:** Create VFD for motors above threshold

**Condition:**
```
asset.type == "MOTOR" AND asset.rated_power > 75
```

**Action:**
```
CREATE_CHILD: VFD
- Tag: {{parent.tag}}-VFD-001
- HP: {{parent.rated_power}}
- Voltage: {{parent.voltage}}
- Manufacturer: ABB
- Enclosure: NEMA 12
```

**Example:**
```
Create: 210-M-001 (Motor, 100HP)
→ Auto-creates: 210-VFD-001 (VFD, 100HP, 600V)

Create: 210-M-002 (Motor, 50HP)
→ No VFD created (below threshold)
```

**Customization Options:**
- Change HP threshold (75 → 100)
- Change manufacturer
- Add communication protocol

---

### Template 4: VFD → Control Cable

**Purpose:** Create control cable for VFDs

**Condition:**
```
asset.type == "VFD"
```

**Action:**
```
CREATE_CABLE: CONTROL
- Cable#: {{parent.tag}}-CTRL
- From: PLC-MAIN
- To: {{parent.tag}}
- Size: 6x18 AWG
- Type: SHIELDED
```

**Example:**
```
Create: 210-VFD-001 (VFD)
→ Auto-creates: 210-VFD-001-CTRL (Control cable to PLC)
```

---

### Template 5: Instrument → Signal Cable

**Purpose:** Create signal cable for instruments

**Condition:**
```
asset.type IN ["FT", "PT", "LT", "TT"] AND asset.output == "4-20mA"
```

**Action:**
```
CREATE_CABLE: SIGNAL
- Cable#: {{parent.tag}}-S
- From: PLC-{{parent.io_card}}
- To: {{parent.tag}}
- Size: 2x18 AWG
- Type: SHIELDED_TWISTED
```

**Example:**
```
Create: 210-FT-001 (Flow Transmitter, 4-20mA)
→ Auto-creates: 210-FT-001-S (Signal cable to PLC)
```

---

## Property Rules

### Template 6: Set Voltage by Country

**Purpose:** Set motor voltage based on project country

**Condition:**
```
asset.type == "MOTOR"
```

**Action:**
```
SET_PROPERTY: voltage
CA → 600V
US → 480V
EU → 400V

Source: {{project.country}}
```

**Example:**
```
Project Country: CA
Create Motor → Voltage automatically set to 600V

Project Country: US
Create Motor → Voltage automatically set to 480V
```

**Customization Options:**
- Add more countries
- Change voltage standards
- Apply to other equipment types

---

### Template 7: Set Enclosure by Location

**Purpose:** Set enclosure type based on area classification

**Condition:**
```
asset.type IN ["MOTOR", "VFD", "INSTRUMENT"]
```

**Action:**
```
SET_PROPERTY: enclosure
INDOOR → NEMA 1
OUTDOOR → NEMA 4X
HAZARDOUS → NEMA 7

Source: {{parent.location.area_classification}}
```

**Example:**
```
Asset in OUTDOOR area → Enclosure = NEMA 4X
Asset in INDOOR area → Enclosure = NEMA 1
```

---

### Template 8: Set Insulation by Temperature

**Purpose:** Set motor insulation class by operating temperature

**Condition:**
```
asset.type == "MOTOR"
```

**Action:**
```
SET_PROPERTY: insulation_class
Temperature < 40°C → Class F
Temperature 40-80°C → Class H
Temperature > 80°C → Class H+
```

**Example:**
```
Motor at 25°C → Class F
Motor at 65°C → Class H
Motor at 95°C → Class H+
```

---

### Template 9: Set Cable Tray by Area

**Purpose:** Auto-assign cable tray based on area

**Condition:**
```
entity_type == "CABLE"
```

**Action:**
```
SET_PROPERTY: cable_tray
Area 210 → T-210-POWER
Area 220 → T-220-CONTROL
Area 300 → T-300-SIGNAL
```

---

## Validation Rules

### Template 10: Motor HP ≥ Pump Requirement

**Purpose:** Ensure motor is sized for pump

**Condition:**
```
asset.type == "PUMP" AND asset.has_child("MOTOR")
```

**Action:**
```
VALIDATE: motor.rated_power >= pump.required_hp

Error Message:
"Motor HP ({{motor_hp}}) is less than Pump requirement ({{required_hp}})"
```

**Example:**
```
Pump requires 100HP
Motor is 75HP → ❌ Validation FAILS
Motor is 100HP → ✅ Validation PASSES
Motor is 125HP → ✅ Validation PASSES (oversized is OK)
```

---

### Template 11: Cable Size for Load (CEC)

**Purpose:** Validate cable sizing per CEC Table 2

**Condition:**
```
cable.type == "POWER"
```

**Action:**
```
VALIDATE: cable.ampacity >= cable.load_current * 1.25

Error Message:
"Cable undersized: {{cable.size}} for {{cable.load_current}}A load"
```

**Example:**
```
Load: 100A
Cable: 3x#4 AWG (ampacity 85A) → ❌ FAILS (85 < 125)
Cable: 3x#2 AWG (ampacity 130A) → ✅ PASSES (130 >= 125)
```

---

### Template 12: VFD Rating ≥ Motor HP

**Purpose:** Ensure VFD can drive motor

**Condition:**
```
asset.type == "VFD"
```

**Action:**
```
VALIDATE: vfd.rated_power >= motor.rated_power

Error Message:
"VFD undersized: {{vfd_hp}}HP for {{motor_hp}}HP motor"
```

---

## Package Rules

### Template 13: Instruments → IN-P040

**Purpose:** Auto-add instruments to Instrument Index package

**Condition:**
```
asset.type IN ["FT", "PT", "LT", "TT", "AT"]
```

**Action:**
```
ADD_TO_PACKAGE: IN-P040 (Instrument Index)
```

**Result:** All instruments automatically included when generating IN-P040

---

### Template 14: Motors → EL-M040

**Purpose:** Auto-add motors to Motor Schedule package

**Condition:**
```
asset.type == "MOTOR"
```

**Action:**
```
ADD_TO_PACKAGE: EL-M040 (Motor Schedule)
```

---

### Template 15: Cables → CA-P040

**Purpose:** Auto-add cables to Cable Schedule package

**Condition:**
```
entity_type == "CABLE"
```

**Action:**
```
ADD_TO_PACKAGE: CA-P040 (Cable Schedule)
```

---

## Using Templates

### Quick Start

1. **Navigate to Rules** → Click **[Templates]** tab
2. **Browse templates** → Find relevant template
3. **Click [Use Template]** → Opens in editor
4. **Customize** (optional):
   - Change thresholds
   - Modify properties
   - Adjust tag patterns
5. **Save** → Template becomes active rule

### Example Workflow

**Project Setup for Mining:**

1. Use **Template 1-5** (Equipment rules) → Creates motors, cables, VFDs automatically
2. Use **Template 6** (Voltage) → Set to CA (600V)
3. Use **Template 7** (Enclosure) → Map areas to INDOOR/OUTDOOR
4. Use **Template 10-12** (Validation) → Catch sizing errors
5. Use **Template 13-15** (Packages) → Auto-populate deliverables

**Result:** 15 minutes to set up complete rule set for project!

---

## Customization Guide

### Changing Thresholds

**Example:** Change VFD threshold from 75HP to 100HP

1. Open **Template 3: Motor >75HP → VFD**
2. Edit condition: `asset.rated_power > 75` → `asset.rated_power > 100`
3. Save as: "Motors >100HP require VFD"

### Adding Properties

**Example:** Add efficiency to motor template

1. Open **Template 1: Pump → Motor**
2. Add property: `efficiency: 95.4%`
3. Save

### Combining Templates

**Example:** Motor rule that creates both cable AND VFD

1. Start with **Template 2: Motor → Cable**
2. Add action from **Template 3: VFD**
3. Save as custom rule

---

## Common Questions

**Q: Can I modify built-in templates?**  
A: No, but you can create a copy and modify the copy.

**Q: Can I share templates between projects?**  
A: Yes (future feature). Currently, re-create in each project.

**Q: What if a template doesn't match my standards?**  
A: Customize it! All values are editable.

**Q: Can I create my own templates?**  
A: Yes, create a rule then save as template.

**Q: Do templates update automatically?**  
A: No. Once saved as a rule, it's independent of the template.

---

## Related Documentation

- [Rule Visualization & Editor (Technical)](../../.dev/roadmap/backlog/rule-visualization-editor.md)
- [Rule Engine Reference](rule-engine.md)
- [Visual Rule Editor Guide](../workflows/visual-rule-editor.md)

---

**Updated:** 2025-11-24
