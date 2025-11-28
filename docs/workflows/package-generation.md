# Package Generation Workflow

**Generating engineering deliverables (Excel/PDF)**

> **Detailed specs:** See [package-generation.md](../../.dev/roadmap/backlog/package-generation.md)

---

## Quick Start (One Package)

### Step 1: Navigate to Packages

1. Open project
2. Click **Packages** in sidebar
3. See available packages

### Step 2: Generate

```
┌─ Generate Package ────────────────────────┐
│                                            │
│ Package Type: [IN-P040 - Instrument Index ▼]│
│                                            │
│ Output Format:                             │
│ ☑️ Excel (.xlsx)                           │
│ ☑️ PDF (.pdf)                              │
│                                            │
│ Options:                                   │
│ ☑️ Include cover page                      │
│ ☑️ Include data sheets                     │
│ ☐ Include loop diagrams                   │
│                                            │
│ Filename: [IN-P040_GoldMine_RevB]         │
│                                            │
│ [Cancel] [Generate]                        │
└────────────────────────────────────────────┘
```

### Step 3: Download

- Small packages (<100 assets): Immediate download
- Large packages (>1000 assets): Background job
  - Progress bar appears
  - Download when complete

---

## Batch Generation (Multiple Packages)

### Generate All Packages

```
┌─ Batch Generate ──────────────────────────┐
│                                            │
│ Select Packages:                           │
│ ☑️ IN-P040 - Instrument Index             │
│ ☑️ EL-M040 - Motor Schedule               │
│ ☑️ CA-P040 - Cable Schedule               │
│ ☑️ IO-P040 - IO List                      │
│ ☐ BID-LST - Bill of Materials             │
│                                            │
│ Format: [Excel + PDF ▼]                   │
│                                            │
│ [Cancel] [Generate All]                    │
└────────────────────────────────────────────┘
```

**Result:** ZIP file with all packages

---

## Available Packages

### Instrument Packages

**IN-P040 - Instrument Index**
- All instruments (FT, PT, LT, TT, etc.)
- Columns: Tag, Type, Service, Range, Output, Cable, IO
- Template: Standard EPCB format

### Electrical Packages

**EL-M040 - Motor Schedule**
- All motors with specifications
- Columns: Tag, Service, HP, Voltage, RPM, Frame, VFD, MCC
- Template: Standard EPCB format

**EL-V040 - VFD Schedule**
- All VFDs
- Columns: Tag, HP, Voltage, Manufacturer, Enclosure

### Cable Packages

**CA-P040 - Power Cable Schedule**
- All power cables
- Columns: Cable#, From, To, Type, Size, Length, Route

**CA-C040 - Control Cable Schedule**
- All control/signal cables
- Similar format to power cables

### IO Packages

**IO-P040 - IO List**
- Grouped by PLC
- Columns: Tag, IO Type, Address, Signal Type, Cable

### BOM Packages

**BID-LST - Bill of Materials**
- Complete equipment list
- Quantities, vendors, pricing

---

## Custom Templates

### Using Custom Template

1. Click **[Templates]**
2. Click **[Upload Template]**
3. Select your Excel file
4. Map data fields:
   ```
   {{PROJECT_NAME}} → Cell A1
   {{REVISION}} → Cell B1
   {{TABLE_START}} → Row 5
   ```
5. Save template
6. Use when generating

---

## Best Practices

### Before Generation

✅ **Run rules** - Ensure all assets complete  
✅ **Validate data** - Check for errors  
✅ **Create baseline** - Snapshot before generation  
✅ **Test with small subset** - Generate 10 assets first

### File Naming

✅ **Include revision:** `IN-P040_GoldMine_RevB`  
✅ **Include date:** `IN-P040_GoldMine_2025-11-24`  
❌ **Avoid:** `package1.xlsx`, `final.xlsx`

### Version Control

✅ **Track in baseline** - Link package to baseline  
✅ **Store in SharePoint** - Central repository  
✅ **Track revisions** - Rev A, B, C, etc.

---

## Troubleshooting

**Q: Generation takes too long**  
A: Large packages (1000+ rows) run in background. Check progress or wait for email notification.

**Q: Missing data in package**  
A: Run rules first. Check package filters (may exclude some assets).

**Q: Excel formatting broken**  
A: Update template. Ensure Excel version compatibility.

**Q: PDF looks wrong**  
A: Check page size (Letter vs A4) and orientation (Landscape vs Portrait).

---

## Advanced Features

### Incremental Updates

Only regenerate if data changed:
- System tracks last generation date
- Compares with last asset modification
- Skips if no changes

### Scheduled Generation

Set up auto-generation:
- Weekly reports (every Monday 8 AM)
- After baseline creation
- On change request approval

---

## Related Documentation

- [Package Deliverables Reference](../reference/package-deliverables.md)
- [Package Generation (Technical)](../../.dev/roadmap/backlog/package-generation.md)

---

**Updated:** 2025-11-24
