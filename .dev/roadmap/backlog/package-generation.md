# Package Generation

**Version:** v0.2.6  
**Goal:** Automated generation of engineering deliverables (Excel/PDF)

---

## Overview

SYNAPSE generates professional engineering deliverables automatically:

**Standard Packages:**
- **IN-P040** - Instrument Index
- **EL-M040** - Motor Schedule  
- **EL-V040** - VFD Schedule
- **CA-P040** - Cable Schedule
- **IO-P040** - IO List (by PLC)
- **BID-LST** - Bill of Materials
- **MTO** - Material Take-Off

**Formats:**
- Excel (`.xlsx`) - Editable, detailed
- PDF (`.pdf`) - Print-ready, client submittals

---

## Package Types

### IN-P040 - Instrument Index

**Content:**
- Complete list of all instruments
- Tag, Type, Service Description
- Range, Output, Location
- Cable number, IO allocation
- Vendor, Model, Notes

**Template Structure:**
```
IN-P040_GoldMine_Rev0.xlsx
├── Cover Sheet
│   └── Project Name, Rev, Date, Engineer
├── Table of Contents
│   └── Clickable links to sheets
├── Instrument Index (Main)
│   └── Tag | Type | Service | Range | Output | Cable | IO | Notes
├── Loop Diagrams (Optional)
│   └── One sheet per loop
└── Data Sheets
    └── One sheet per instrument type
```

**Example Row:**
```
Tag          | Type | Service           | Range    | Output  | Cable         | IO Addr    | Vendor
210-FT-001   | FT   | Slurry Flow       | 0-500GPM | 4-20mA  | 210-FT-001-S  | PLC1:AI.0  | E+H
210-PT-001   | PT   | Slurry Pressure   | 0-100PSI | 4-20mA  | 210-PT-001-S  | PLC1:AI.1  | Rosemount
```

---

### EL-M040 - Motor Schedule

**Content:**
- All motors in project
- Tag, Service, Location
- HP, Voltage, RPM, Frame
- VFD required, Starter type
- MCC/Panel, Breaker size
- Cable number

**Example:**
```
Tag          | Service       | Location    | HP  | Voltage | RPM  | Frame | VFD | MCC       | Cable
210-M-001    | Slurry Pump   | Area 210    | 100 | 600V    | 1800 | 404T  | Yes | MCC-210   | 210-M-001-PWR
210-M-002    | Water Pump    | Area 210    | 75  | 600V    | 1800 | 365T  | No  | MCC-210   | 210-M-002-PWR
```

---

### CA-P040 - Cable Schedule

**Content:**
- All power and control cables
- Cable number, From/To tags
- Cable type, Size, Length
- Route, Tray
- Termination details

**Example:**
```
Cable#         | From        | To         | Type         | Size      | Length | Route      | Notes
210-M-001-PWR  | MCC-210     | 210-M-001  | POWER        | 3x#2 AWG  | 150ft  | Tray T-210 | VFD output
210-FT-001-S   | PLC1        | 210-FT-001 | SIGNAL       | 2x18 AWG  | 75ft   | Tray T-220 | 4-20mA
```

---

### IO-P040 - IO List

**Content:**
- IO allocation by PLC
- Tag, IO Type, Address
- Signal type, Range
- Cable number

**Example:**
```
PLC: PLC1-CPU01
────────────────────────────────────────────────────
Tag          | IO Type | Address | Type     | Range    | Cable
210-FT-001   | AI      | 0       | 4-20mA   | 0-500GPM | 210-FT-001-S
210-PT-001   | AI      | 1       | 4-20mA   | 0-100PSI | 210-PT-001-S
210-PV-001   | DO      | 0       | 24VDC    | OPEN/CLO | 210-PV-001-C
```

---

## Tech Stack

| Component | Library | License |
|-----------|---------|---------|
| Excel Generation | `openpyxl` (Python) | MIT |
| PDF Generation | `WeasyPrint` (Python) | BSD |
| Excel Formatting | `xlsxwriter` (optional) | BSD |
| Charts/Graphs | `matplotlib` | PSF |

---

## Generation Workflow

### User Interaction

```
┌─ Generate Package ──────────────────────────────────┐
│                                                      │
│ Select Package Type:                                 │
│ ● IN-P040 - Instrument Index                        │
│ ○ EL-M040 - Motor Schedule                          │
│ ○ CA-P040 - Cable Schedule                          │
│ ○ IO-P040 - IO List                                 │
│                                                      │
│ Output Format:                                       │
│ ☑️ Excel (.xlsx)                                     │
│ ☑️ PDF (.pdf)                                        │
│                                                      │
│ Options:                                             │
│ ☑️ Include cover page                                │
│ ☑️ Include data sheets                               │
│ ☐ Include loop diagrams                             │
│                                                      │
│ Filename: IN-P040_GoldMine_RevB                     │
│                                                      │
│ [Cancel] [Generate]                                  │
└──────────────────────────────────────────────────────┘

User clicks [Generate]
↓
Progress bar appears
↓
Download starts automatically
```

### Backend Flow

```python
# FastAPI endpoint
@router.post("/api/v1/packages/generate")
async def generate_package(
    request: PackageGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session
):
    # 1. Validate request
    if request.package_type not in SUPPORTED_PACKAGES:
        raise HTTPException(400, "Invalid package type")
    
    # 2. Queue generation job (if using Celery)
    # OR generate immediately for small projects
    if project_asset_count > 1000:
        # Background job (v0.4.0+)
        job_id = queue_package_generation(request)
        return {"job_id": job_id, "status": "queued"}
    else:
        # Immediate generation
        file_path = await generate_package_sync(request, db)
        return FileResponse(file_path)

async def generate_package_sync(request, db):
    # 1. Fetch data
    assets = fetch_assets_for_package(request.package_type, db)
    
    # 2. Select generator
    if request.package_type == "IN-P040":
        generator = InstrumentIndexGenerator()
    elif request.package_type == "EL-M040":
        generator = MotorScheduleGenerator()
    # ... etc
    
    # 3. Generate files
    files = []
    if "xlsx" in request.formats:
        excel_file = generator.generate_excel(assets, request.options)
        files.append(excel_file)
    
    if "pdf" in request.formats:
        pdf_file = generator.generate_pdf(assets, request.options)
        files.append(pdf_file)
    
    # 4. If multiple files, zip them
    if len(files) > 1:
        return create_zip(files)
    else:
        return files[0]
```

### Excel Generation (Example)

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

class InstrumentIndexGenerator:
    def generate_excel(self, instruments: List[Asset], options: dict) -> str:
        wb = Workbook()
        ws = wb.active
        ws.title = "Instrument Index"
        
        # Cover page (if requested)
        if options.get("include_cover"):
            self._create_cover_page(wb, instruments)
        
        # Table of Contents
        if options.get("include_toc"):
            self._create_toc(wb)
        
        # Main instrument index
        ws = wb.create_sheet("Instrument Index")
        self._create_main_table(ws, instruments)
        
        # Data sheets (if requested)
        if options.get("include_datasheets"):
            self._create_datasheets(wb, instruments)
        
        # Save file
        filename = f"{options['filename']}.xlsx"
        filepath = f"/tmp/packages/{filename}"
        wb.save(filepath)
        return filepath
    
    def _create_main_table(self, ws, instruments):
        # Header row
        headers = [
            "Tag", "Type", "Service Description", 
            "Range", "Output", "Cable#", 
            "IO Address", "Location", "Vendor", "Notes"
        ]
        ws.append(headers)
        
        # Style header
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="366092")
            cell.alignment = Alignment(horizontal="center")
        
        # Data rows
        for inst in instruments:
            ws.append([
                inst.tag,
                inst.type,
                inst.properties.get("service"),
                inst.properties.get("range"),
                inst.properties.get("output"),
                get_cable_number(inst),
                get_io_address(inst),
                get_location(inst),
                inst.properties.get("vendor"),
                inst.properties.get("notes")
            ])
        
        # Auto-size columns
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column_letter].width = max_length + 2
```

### PDF Generation (Example)

```python
from weasyprint import HTML, CSS
from jinja2 import Template

class InstrumentIndexGenerator:
    def generate_pdf(self, instruments: List[Asset], options: dict str:
        # Render HTML template
        template = Template(INSTRUMENT_INDEX_TEMPLATE)
        html_content = template.render(
            project_name=options["project_name"],
            revision=options["revision"],
            instruments=instruments,
            date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # Custom CSS for professional styling
        css = CSS(string=PACKAGE_STYLES_CSS)
        
        # Generate PDF
        filename = f"{options['filename']}.pdf"
        filepath = f"/tmp/packages/{filename}"
        HTML(string=html_content).write_pdf(filepath, stylesheets=[css])
        return filepath

# HTML Template
INSTRUMENT_INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ project_name }} - Instrument Index</title>
</head>
<body>
    <div class="cover-page">
        <h1>{{ project_name }}</h1>
        <h2>Instrument Index</h2>
        <p>Document: IN-P040</p>
        <p>Revision: {{ revision }}</p>
        <p>Date: {{ date }}</p>
    </div>
    
    <div class="page-break"></div>
    
    <table class="instrument-table">
        <thead>
            <tr>
                <th>Tag</th>
                <th>Type</th>
                <th>Service</th>
                <th>Range</th>
                <th>Output</th>
                <th>Cable#</th>
            </tr>
        </thead>
        <tbody>
            {% for inst in instruments %}
            <tr>
                <td>{{ inst.tag }}</td>
                <td>{{ inst.type }}</td>
                <td>{{ inst.properties.service }}</td>
                <td>{{ inst.properties.range }}</td>
                <td>{{ inst.properties.output }}</td>
                <td>{{ inst.cable_number }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

PACKAGE_STYLES_CSS = """
@page {
    size: Letter landscape;
    margin: 0.5in;
}
.cover-page {
    text-align: center;
    padding-top: 3in;
}
.page-break {
    page-break-after: always;
}
.instrument-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 10pt;
}
.instrument-table th {
    background-color: #366092;
    color: white;
    padding: 8px;
    text-align: left;
    border: 1px solid #ccc;
}
.instrument-table td {
    padding: 6px;
    border: 1px solid #ccc;
}
"""
```

---

## Database Schema

```sql
-- Package Templates
CREATE TABLE package_templates (
    id UUID PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL, -- IN-P040, EL-M040, etc.
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Template files
    excel_template_path TEXT,
    pdf_template_path TEXT,
    
    -- Generation config
    generator_class VARCHAR(100), -- Python class name
    query_config JSONB, -- How to fetch data
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Generated Packages (History)
CREATE TABLE generated_packages (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    template_id UUID REFERENCES package_templates(id),
    
    filename VARCHAR(200),
    file_path TEXT,
    file_size_bytes BIGINT,
    format VARCHAR(10), -- xlsx, pdf
    
    -- Generation metadata
    generated_by UUID REFERENCES users(id),
    generated_at TIMESTAMP DEFAULT NOW(),
    generation_time_ms INT,
    
    -- Snapshot reference
    baseline_id UUID REFERENCES project_baselines(id),
    
    -- Download tracking
    download_count INT DEFAULT 0,
    last_downloaded_at TIMESTAMP
);

-- Package Options Default
CREATE TABLE package_default_options (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    template_code VARCHAR(20),
    
    default_options JSONB, -- User preferences
    
    UNIQUE(user_id, template_code)
);
```

---

## Advanced Features

### Custom Templates

**User can upload custom Excel templates:**
```
1. User uploads template: "Custom_IN-P040.xlsx"
2. System validates template has required placeholders:
   - {{PROJECT_NAME}}
   - {{REVISION}}
   - {{TABLE_START}} ... {{TABLE_END}}
3. System saves template
4. User selects template when generating package
5. System populates template with project data
```

### Batch Generation

**Generate all packages at once:**
```
POST /api/v1/packages/generate-all

Request:
{
  "packages": ["IN-P040", "EL-M040", "CA-P040"],
  "format": "xlsx",
  "zip_output": true
}

Response:
{
  "job_id": "abc-123",
  "status": "queued",
  "estimated_time": "45 seconds"
}
```

### Incremental Updates

**Only regenerate if data changed:**
```python
def should_regenerate_package(package_id: UUID, db: Session) -> bool:
    last_gen = db.query(GeneratedPackage)\
        .filter_by(template_id=package_id)\
        .order_by(GeneratedPackage.generated_at.desc())\
        .first()
    
    if not last_gen:
        return True
    
    # Check if any assets changed since last generation
    last_change = db.query(AuditLog)\
        .filter(AuditLog.changed_at > last_gen.generated_at)\
        .filter(AuditLog.entity_type == "ASSET")\
        .first()
    
    return last_change is not None
```

---

## API Endpoints

```
# Package Generation
POST   /api/v1/packages/generate              Generate single package
POST   /api/v1/packages/generate-all          Generate multiple packages
GET    /api/v1/packages/history               List generated packages
GET    /api/v1/packages/{id}/download         Download package
DELETE /api/v1/packages/{id}                  Delete generated package

# Templates
GET    /api/v1/package-templates              List all templates
GET    /api/v1/package-templates/{code}       Get template details
POST   /api/v1/package-templates              Upload custom template
PUT    /api/v1/package-templates/{code}       Update template
DELETE /api/v1/package-templates/{code}       Delete custom template

# User Preferences
GET    /api/v1/users/me/package-options       Get default options
PUT    /api/v1/users/me/package-options       Save default options
```

---

## Verification Plan

### Backend Tests
```bash
docker exec synapse-backend-1 pytest tests/test_package_generation.py
docker exec synapse-backend-1 pytest tests/test_excel_generator.py
docker exec synapse-backend-1 pytest tests/test_pdf_generator.py
```

### Manual Testing
1. Create project with 50+ instruments
2. Generate IN-P040 (Excel)
   - Verify cover page
   - Verify table format
   - Verify all data present
3. Generate IN-P040 (PDF)
   - Verify professional styling
   - Verify page breaks
   - Verify print quality
4. Generate multiple packages
   - Verify ZIP download
5. Upload custom template
   - Verify template validation
   - Verify data population

---

## Future Enhancements (v0.4.0+)

- **Real-time collaboration:** Multiple users edit same package
- **Version control:** Track package revisions
- **Digital signatures:** Sign packages for submittal
- **Cloud storage integration:** Direct upload to SharePoint/OneDrive
- **Email distribution:** Auto-send packages to stakeholders

---

**Updated:** 2025-11-24
