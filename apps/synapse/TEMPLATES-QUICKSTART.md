# Templates & Export - Quick Start Guide

**2 minutes to your first export!**

---

## 🚀 Quick Export (3 steps)

### Step 1: Create a Package

```bash
curl -X POST http://localhost:8001/api/v1/packages \
  -H "Content-Type: application/json" \
  -H "X-Project-ID: YOUR_PROJECT_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "IN-P210-001",
    "description": "Instrumentation Package - Area 210"
  }'
```

### Step 2: Add Assets

```bash
curl -X POST http://localhost:8001/api/v1/packages/PACKAGE_ID/assets/ASSET_ID \
  -H "X-Project-ID: YOUR_PROJECT_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 3: Export

```bash
curl "http://localhost:8001/api/v1/packages/PACKAGE_ID/export?template_type=IN-P040" \
  -H "X-Project-ID: YOUR_PROJECT_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o my_export.xlsx
```

**Done!** Open `my_export.xlsx` ✅

---

## 📋 Available Templates

| Template | What it exports | Use for |
|----------|----------------|---------|
| **IN-P040** | Instrument Index | Panels, instruments, IO points |
| **CA-P040** | Cable Schedule | Power & signal cables, routing |

---

## 🐍 Python Example

```python
from app.core.database import SessionLocal
from app.services.template_service import TemplateService

db = SessionLocal()
service = TemplateService(db)

# Export package
result = service.export_package(
    package_id="YOUR_PACKAGE_ID",
    template_type="IN-P040",  # or "CA-P040"
    format="xlsx"
)

if result.success:
    with open(result.file_name, 'wb') as f:
        f.write(result.file_data)
    print(f"✅ Exported: {result.file_name}")

db.close()
```

---

## ⚛️ React Example

```typescript
import { usePackages } from '@/hooks/usePackages'

function ExportButton({ packageId, projectId }) {
    const { exportPackage, loading } = usePackages(projectId)

    return (
        <button
            onClick={() => exportPackage(packageId, 'IN-P040')}
            disabled={loading}
        >
            {loading ? 'Exporting...' : 'Export IN-P040'}
        </button>
    )
}
```

---

## 🔍 Preview Before Export

```bash
curl "http://localhost:8001/api/v1/packages/PACKAGE_ID/export/preview?template_type=IN-P040" \
  -H "X-Project-ID: YOUR_PROJECT_ID" \
  | jq
```

**Response:**
```json
{
  "package": { "name": "IN-P210-001", ... },
  "template_type": "IN-P040",
  "asset_count": 5,
  "assets": [ ... ]
}
```

---

## 📊 What's in the Export?

### IN-P040 Columns
- Tag Number
- Service Description
- Type
- Location
- Power Supply
- Signal Type
- IO Points
- Panel
- Remarks

### CA-P040 Columns
- Cable Number
- From/To Equipment
- Cable Type
- Core/Size
- Length (m)
- Routing
- Tray/Duct
- Terminations

---

## ❓ Troubleshooting

**Q: Export returns 404**
→ Check package ID exists

**Q: Export shows "No assets"**
→ Add assets to package first

**Q: Export fails with 401**
→ Add valid Authorization header

**Q: Excel file is corrupted**
→ Use binary mode: `-o file.xlsx` (not `-O`)

---

## 📚 Full Documentation

→ [`backend/docs/templates-export-system.md`](./apps/synapse/backend/docs/templates-export-system.md)

---

**Need help?** Check the API docs: `http://localhost:8001/docs#/packages`
