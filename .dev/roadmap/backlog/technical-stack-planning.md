# SYNAPSE v0.2.0 - Technical Stack Planning

**Version:** v0.2.0  
**Date:** 2025-11-22  
**Purpose:** Map vision features to technology choices and validate architecture

---

## 🎯 Validation Criteria

Stack is successful if:
- [ ] All v0.2.0 features are technically feasible
- [ ] 100% opensource (no paid licenses)
- [ ] Scalable to 10,000+ assets
- [ ] Developer-friendly (good DX)
- [ ] Production-ready components

---

## 📊 Feature-to-Technology Mapping

### 1. Data Layer

#### **3-Tier Asset Model**

| Feature | Technology | Status | Notes |
|---------|------------|--------|-------|
| Engineering Assets | PostgreSQL + SQLAlchemy | ✅ Exists | `assets` table |
| Catalog Assets | PostgreSQL + SQLAlchemy | ➕ Add | `catalog_assets` table (Phase 5) |
| Physical Assets | PostgreSQL + SQLAlchemy | ➕ Add | `physical_assets` table (Phase 6) |
| Versioning | PostgreSQL JSON + Alembic | ➕ Add | `version_history` JSON column |
| Status Workflow | PostgreSQL ENUM | ➕ Add | Custom ENUM type |

**Decision:** Continue with PostgreSQL + SQLAlchemy (proven, flexible, opensource).

---

#### **6 Breakdown Structures**

| Structure | Implementation | Status | Technology |
|-----------|----------------|--------|------------|
| FBS (Functional) | Self-join table `fbs_nodes` | ➕ Add | PostgreSQL + Materialized Path |
| LBS (Location) | Self-join table `lbs_nodes` | ✅ Exists | PostgreSQL + Nested Set |
| WBS (Packages) | Simple table `packages` | ➕ Add | PostgreSQL |
| CBS (Cost) | Aggregation table `cost_items` | ➕ Add | PostgreSQL + Views |
| PBS (Product) | Self-join table `product_hierarchy` | ➕ Add | PostgreSQL + Closure Table |
| OBS (Organizational) | Simple table `disciplines` | ➕ Add | PostgreSQL |

**Decision:** Use different tree patterns for each structure based on query needs:
- **Materialized Path** (FBS) - Fast read of subtrees
- **Nested Set** (LBS) - Fast hierarchy queries
- **Closure Table** (PBS) - Fast ancestor/descendant queries

**Library:** None needed, implement in SQL + SQLAlchemy

---

#### **Rule Engine**

| Feature | Technology | Status | Notes |
|---------|------------|--------|-------|
| Rule Storage | PostgreSQL JSONB | ✅ Exists | Flexible schema |
| Rule Execution | Python (custom) | ✅ Exists | `rule_executor.py` |
| Condition Matching | Python dict queries | ✅ Exists | Simple but works |
| Action Dispatch | Python functions | ✅ Exists | 6 action types |
| Audit Trail | PostgreSQL | ✅ Exists | `rule_executions` table |
| Priority System | Python sorting | ✅ Exists | Sort by priority DESC |

**Decision:** Keep current Python implementation, performant enough for use case.

**Future Optimization (if needed):** Consider Drools (Java) or Rete algorithm for >10K rules.

---

### 2. Backend APIs

#### **REST API**

| Feature | Technology | Status | Notes |
|---------|------------|--------|-------|
| API Framework | FastAPI | ✅ Exists | Python async |
| Auth | JWT + FastAPI security | ✅ Exists | Token-based |
| Validation | Pydantic v2 | ✅ Exists | Type-safe |
| Serialization | Pydantic + SQLAlchemy | ✅ Exists | `serialize_by_alias` |
| CORS | FastAPI middleware | ✅ Exists | Config needed |
| Rate Limiting | Slowapi | ➕ Add | Opensource |

**Decision:** Continue with FastAPI (modern, fast, great DX).

---

#### **Background Jobs**

| Feature | Technology | Status | Notes |
|---------|------------|--------|-------|
| Async Tasks | Celery | ➕ Add | Long-running imports/exports |
| Message Queue | Redis | ➕ Add | Celery backend |
| Scheduling | Celery Beat | ➕ Add | Periodic tasks (backups, etc.) |

**Use Cases:**
- Large CSV imports (3000+ rows)
- Package deliverable generation (complex Excel)
- Batch rule execution (apply to 100+ assets)
- Database backups

**Decision:** Add Celery + Redis in Phase 3 when package generation becomes complex.

---

#### **File Storage**

| Feature | Technology | Status | Notes |
|---------|------------|--------|-------|
| Uploads (CSV) | Local filesystem | ✅ Exists | `/uploads` directory |
| Generated Files | Local filesystem | ➕ Add | `/exports` directory |
| Datasheets (PDF) | Local filesystem or S3 | ➕ Add | Phase 5 (catalogs) |
| Drawings (P&ID) | Local filesystem or S3 | ➕ Add | Future |

**Decision Phase 2-4:** Local filesystem (simple, no dependencies).  
**Decision Phase 5+:** MinIO (S3-compatible, opensource) if file volume grows.

---

### 3. Frontend UI

#### **Core Framework**

| Feature | Technology | Status | Notes |
|---------|------------|--------|-------|
| Framework | React 19 | ✅ Exists | Latest stable |
| Language | TypeScript | ✅ Exists | Type safety |
| Build Tool | Vite | ✅ Exists | Fast HMR |
| Routing | React Router v6 | ✅ Exists | SPA routing |
| State Management | Zustand | ✅ Exists | Lightweight |

**Decision:** Continue with current stack (modern, performant).

---

#### **UI Components**

| Feature | Technology | License | Status | Notes |
|---------|------------|---------|--------|-------|
| Data Grid | AG Grid Community | MIT | ✅ Exists | Avoid Enterprise ($999) |
| Tree View | `react-complex-tree` | MIT | ➕ Add | Performant, accessible |
| Flow Diagram | ReactFlow | MIT | ➕ Add | Node-based graphs |
| Resizable Panels | `react-grid-layout` | MIT | ➕ Add | Drag-resize layout |
| Date Picker | `react-datepicker` | MIT | ➕ Add | Simple, accessible |
| Command Palette | `cmdk` | MIT | ➕ Add | Global search UI |
| Tooltips | `@floating-ui/react` | MIT | ➕ Add | Professional tooltips |

**Decision:** All MIT licensed, well-maintained libraries.

**Avoid:**
- ❌ Kendo UI ($999/dev)
- ❌ DevExtreme ($699/dev)
- ❌ Syncfusion ($995/dev)

---

#### **Styling**

| Feature | Technology | Status | Notes |
|---------|------------|--------|-------|
| CSS Framework | TailwindCSS | ✅ Exists | Utility-first |
| Component Lib | shadcn/ui (optional) | ➕ Consider | Tailwind components |
| Icons | Lucide React | ✅ Exists | Clean, consistent |
| Theme | CSS Variables | ➕ Add | Custom theming |

**Decision:** Continue with Tailwind, add CSS variables for theming.

**Alternative:** Consider shadcn/ui for pre-built components (saves dev time).

---

#### **Advanced Features**

##### **Clickable Navigation**

| Feature | Implementation | Library | Status |
|---------|----------------|---------|--------|
| Entity Links | React Router Link + onClick | Built-in | ➕ Add |
| Context Menu | `@radix-ui/react-context-menu` | MIT | ➕ Add |
| Sidebar | Custom component + Zustand | Built-in | ➕ Add |

**Implementation:**
```tsx
// EntityLink component
<EntityLink type="asset" id="210-M-001" />
→ Renders as clickable link
→ onClick: Opens sidebar or navigates
```

---

##### **Developer Console**

| Feature | Implementation | Library | Status |
|---------|----------------|---------|--------|
| Console UI | Custom tabs component | Built-in | ➕ Add |
| Log Streaming | WebSocket or SSE | FastAPI | ➕ Add |
| Network Monitor | Axios interceptors | Axios | ➕ Add |
| Rules Trace | API endpoint + UI | Custom | ➕ Add |
| Error Boundary | React Error Boundary | Built-in | ➕ Add |

**Implementation:**
```tsx
// Backend: WebSocket for logs
@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    while True:
        log = await log_queue.get()
        await websocket.send_json(log)

// Frontend: Display in console
const ws = new WebSocket('ws://localhost:8000/ws/logs');
ws.onmessage = (event) => {
  addLog(JSON.parse(event.data));
};
```

**Decision:** Use Server-Sent Events (SSE) instead of WebSocket (simpler, HTTP-friendly).

---

##### **Raw Database Viewer**

| Feature | Technology | License | Status |
|---------|------------|---------|--------|
| DB Admin | Adminer | Apache 2.0 | ➕ Add |
| Integration | iframe or Docker sidecar | N/A | ➕ Add |

**Implementation Options:**

**Option A: Docker Sidecar (Recommended)**
```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16
  
  adminer:
    image: adminer:latest
    ports:
      - "8080:8080"
    environment:
      ADMINER_DEFAULT_SERVER: db
```
Access: `http://localhost:8080`

**Option B: Embedded PHP**
- Deploy Adminer PHP file to server
- Serve via FastAPI static files
- Access: `http://localhost:3000/admin/db`

**Decision:** Docker sidecar (cleaner separation, easier updates).

---

##### **AI Chatbot**

| Feature | Technology | License | Cost | Status |
|---------|------------|---------|------|--------|
| Local LLM | Ollama + LLaMA 3 | Apache 2.0 | Free | ➕ Add Phase 5 |
| Cloud LLM | OpenAI GPT-4 | Proprietary | Paid | ➕ Add Phase 5 |
| Embeddings | Ollama (nomic-embed) | Apache 2.0 | Free | ➕ Add Phase 5 |
| Vector DB | ChromaDB | Apache 2.0 | Free | ➕ Add Phase 5 |
| Chat UI | `react-chatbot-kit` | MIT | Free | ➕ Add Phase 5 |

**Architecture:**
```
User Question
    ↓
Frontend (Chat UI)
    ↓
FastAPI (/api/v1/ai/query)
    ↓
├─ Simple Query → Ollama (free, fast)
└─ Complex Query → GPT-4 (paid, accurate)
    ↓
Query DB (get context)
    ↓
Generate Response
    ↓
Return + Actions
```

**Context Storage:**
- Embed documentation in ChromaDB
- Embed rule definitions
- Embed asset descriptions
- Query similar items for context

**Decision:** 
- Phase 5: Ollama only (MVP)
- Phase 6: Add GPT-4 option (configurable)

---

### 4. Search & Performance

#### **Full-Text Search**

| Feature | Technology | License | Status | Notes |
|---------|------------|---------|--------|-------|
| Asset Search | PostgreSQL FTS | PostgreSQL | ➕ Add | Built-in, good for <100K |
| Fast Search | MeiliSearch | MIT | ➕ Consider | For >100K assets |
| Autocomplete | PostgreSQL LIKE | PostgreSQL | ➕ Add | Simple, works |

**Decision Phase 2-4:** PostgreSQL full-text search (no extra dependency).  
**Decision Phase 5+:** Evaluate MeiliSearch if search performance degrades.

**Implementation (PostgreSQL FTS):**
```sql
-- Add search vectors
ALTER TABLE assets 
ADD COLUMN search_vector tsvector 
GENERATED ALWAYS AS (
  to_tsvector('english', 
    coalesce(tag, '') || ' ' || 
    coalesce(description, '')
  )
) STORED;

CREATE INDEX idx_assets_search ON assets USING GIN(search_vector);

-- Query
SELECT * FROM assets 
WHERE search_vector @@ plainto_tsquery('motor 400V');
```

---

#### **Caching**

| Feature | Technology | Status | Use Case |
|---------|------------|--------|----------|
| API Results | Redis | ➕ Add Phase 4 | Frequently-queried assets |
| Session Data | Redis | ➕ Add Phase 4 | User preferences, filters |
| Rule Cache | Python LRU cache | ✅ Exists | In-memory rule storage |

**Decision:** Add Redis in Phase 4 when performance becomes issue.

---

### 5. Deliverable Generation

#### **Excel Export**

| Feature | Technology | License | Status |
|---------|------------|---------|--------|
| Excel Files | `openpyxl` | MIT | ➕ Add |
| Complex Formatting | `xlsxwriter` | BSD | ➕ Alternative |
| Templates | Jinja2 + Excel | MIT | ➕ Add |

**Use Cases:**
- BID LST (formatted tables)
- MTO (material lists)
- Cable Schedule (with sizing)
- IO List (sorted by PLC)

**Decision:** Start with `openpyxl`, switch to `xlsxwriter` if more formatting needed.

---

#### **PDF Generation**

| Feature | Technology | License | Status | Use Case |
|---------|------------|---------|--------|----------|
| PDF from HTML | WeasyPrint | BSD | ➕ Add Phase 4 | Specs, reports |
| PDF from template | ReportLab | BSD | ➕ Alternative | P&IDs, drawings |

**Decision:** WeasyPrint (HTML → PDF, easier templating with Jinja2).

---

### 6. Deployment & DevOps

#### **Containerization**

| Feature | Technology | Status | Notes |
|---------|------------|--------|-------|
| Backend | Docker | ✅ Exists | `backend/Dockerfile` |
| Frontend | Docker | ✅ Exists | `Dockerfile` |
| Database | Docker (PostgreSQL) | ✅ Exists | `docker-compose.yml` |
| Adminer | Docker | ➕ Add | DB viewer |
| Redis | Docker | ➕ Add Phase 4 | Cache + queue |
| Ollama | Docker | ➕ Add Phase 5 | AI local |

**Current:**
```yaml
services:
  db:
    image: postgres:16
  backend:
    build: ./backend
  frontend:
    build: .
```

**Phase 5 (Complete):**
```yaml
services:
  db:
    image: postgres:16
  redis:
    image: redis:7-alpine
  backend:
    build: ./backend
    depends_on: [db, redis]
  frontend:
    build: .
  adminer:
    image: adminer
  ollama:
    image: ollama/ollama
    volumes:
      - ollama-data:/root/.ollama
```

---

#### **CI/CD**

| Feature | Technology | Status | Notes |
|---------|------------|--------|-------|
| Version Control | Git + GitHub | ✅ Exists | Opensource hosting |
| CI Pipeline | GitHub Actions | ➕ Add | Free for public repos |
| Testing | pytest + Jest | ✅ Partial | Expand coverage |
| Linting | Ruff (Python) + ESLint | ✅ Exists | Fast linters |

**GitHub Actions Workflow:**
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          docker-compose up -d db
          pytest backend/tests
          npm test
```

---

### 7. Monitoring & Logging

#### **Logging**

| Feature | Technology | License | Status |
|---------|------------|---------|--------|
| Backend Logs | Python logging | Built-in | ✅ Exists |
| Frontend Logs | Console + API | Built-in | ➕ Add |
| Log Aggregation | Loki (optional) | AGPL | ➕ Phase 6 |

**Decision:** Simple file logging for now, Loki if centralized logging needed.

---

#### **Monitoring**

| Feature | Technology | License | Status | Use Case |
|---------|------------|---------|--------|----------|
| Metrics | Prometheus | Apache 2.0 | ➕ Phase 6 | API performance |
| Dashboards | Grafana | AGPL | ➕ Phase 6 | Visual monitoring |
| Alerts | Grafana Alerts | AGPL | ➕ Phase 6 | Error notifications |

**Decision:** Add monitoring in Phase 6 (production readiness).

---

## 🏗️ Architecture Diagram (Updated)

```
┌─────────────────────────────────────────────────────────┐
│                    USER BROWSER                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ React 19 + TypeScript + Vite                       │ │
│  │ ├─ AG Grid (data tables)                           │ │
│  │ ├─ ReactFlow (diagrams)                            │ │
│  │ ├─ react-grid-layout (panels)                      │ │
│  │ ├─ cmdk (search)                                   │ │
│  │ └─ Chat UI (AI)                                    │ │
│  └────────────────────────────────────────────────────┘ │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP/WebSocket
┌───────────────────────▼─────────────────────────────────┐
│                   BACKEND (FastAPI)                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │ REST API Endpoints                                 │ │
│  │ ├─ /api/v1/assets/                                 │ │
│  │ ├─ /api/v1/rules/                                  │ │
│  │ ├─ /api/v1/cables/                                 │ │
│  │ ├─ /api/v1/packages/                               │ │
│  │ ├─ /api/v1/ai/query                                │ │
│  │ └─ /ws/logs (SSE)                                  │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Services                                           │ │
│  │ ├─ RuleExecutor (Python)                           │ │
│  │ ├─ CableSizing (CEC calcs)                         │ │
│  │ ├─ PackageGenerator (Excel)                        │ │
│  │ └─ AIService (Ollama/GPT-4)                        │ │
│  └────────────────────────────────────────────────────┘ │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                  DATABASES & STORAGE                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ PostgreSQL   │  │ Redis        │  │ ChromaDB     │  │
│  │ ├─ assets    │  │ ├─ cache     │  │ ├─ AI embed  │  │
│  │ ├─ cables    │  │ └─ sessions  │  │ └─ docs      │  │
│  │ ├─ rules     │  └──────────────┘  └──────────────┘  │
│  │ ├─ packages  │                                       │
│  │ └─ ...       │                                       │
│  └──────────────┘                                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   BACKGROUND JOBS                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Celery Workers (Python)                            │ │
│  │ ├─ Large CSV imports                               │ │
│  │ ├─ Excel generation (complex)                      │ │
│  │ ├─ Batch rule execution                            │ │
│  │ └─ Database backups                                │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   ADMIN TOOLS                            │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │ Adminer      │  │ Ollama       │                     │
│  │ (DB viewer)  │  │ (Local AI)   │                     │
│  │ Port: 8080   │  │ Port: 11434  │                     │
│  └──────────────┘  └──────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Phase-by-Phase Technology Adoption

### Phase 2 (Current - Cables + Versioning)
**Add:**
- PostgreSQL version_history column (JSON)
- PostgreSQL status ENUM
- Alembic migrations

**Frontend:**
- Version history component
- Status badges

---

### Phase 3 (FBS + Packages)
**Add Backend:**
- `fbs_nodes` table (materialized path)
- `packages` table
- `openpyxl` for Excel
- Celery + Redis (background jobs)

**Add Frontend:**
- `react-complex-tree` for FBS
- Package management UI
- Excel download buttons

---

### Phase 4 (LBS + Locations)
**Add Backend:**
- Redis caching layer
- WeasyPrint for PDFs

**Add Frontend:**
- ReactFlow for diagrams
- Context menus (`@radix-ui`)

---

### Phase 5 (Catalog + AI)
**Add Backend:**
- `catalog_assets` table
- Ollama integration
- ChromaDB for embeddings
- MeiliSearch (if needed)

**Add Frontend:**
- AI chat UI
- Advanced search with cmdk
- Clickable navigation

---

### Phase 6 (Construction + Polish)
**Add Backend:**
- `physical_assets` table
- Prometheus metrics
- Loki logs

**Add Frontend:**
- 3D view (Three.js)
- Complete dev console
- Grafana dashboards

---

## ✅ Technology Checklist

### Must Have (Core)
- [x] PostgreSQL 16
- [x] FastAPI
- [x] React 19
- [x] TypeScript
- [x] AG Grid Community
- [ ] Redis
- [ ] Celery
- [ ] openpyxl

### Should Have (Enhanced UX)
- [ ] ReactFlow
- [ ] react-grid-layout
- [ ] react-complex-tree
- [ ] cmdk
- [ ] WeasyPrint

### Nice to Have (Advanced)
- [ ] Ollama + LLaMA 3
- [ ] ChromaDB
- [ ] MeiliSearch
- [ ] Three.js
- [ ] Prometheus + Grafana

### Admin/Dev Tools
- [ ] Adminer
- [ ] Grafana

---

## 🚨 Technology Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| AG Grid Community limitations | Acceptable for v0.2.0 scope |
| Ollama GPU requirements | Fallback to GPT-4 API |
| PostgreSQL FTS performance | Add MeiliSearch if needed |
| Complex Excel formatting | Use xlsxwriter if openpyxl insufficient |
| Tree query performance | Use appropriate pattern per structure |

---

## 💰 Cost Analysis (Opensource Only)

**All technologies: $0 licensing**

**Optional paid services:**
- OpenAI API: ~$20-100/month (pay-per-use)
- Cloud hosting: ~$50-200/month (DigitalOcean, AWS, etc.)

**Total cost for fully-featured system: $0-100/month**

**Compare to:**
- Aras Innovator: $30K+ setup
- Siemens Teamcenter: $100K+ setup
- AG Grid Enterprise: $999/dev/year

---

## ✅ Validation Result

**Stack is VALIDATED for v0.2.0**

- ✅ All features technically feasible
- ✅ 100% opensource technologies
- ✅ Scalable architecture
- ✅ Modern, maintainable stack
- ✅ Developer-friendly tools

**Ready to proceed with implementation!**

---

## 🎨 P&ID & Electrical Drawings (Advanced Feature)

### Feature Overview

**Bidirectional Integration:**
1. **Ingestion (Import):** PDF/DWG → Database
2. **Generation (Export):** Database → PDF/DWG

**Phase:** 7-8 (Future, complex)

---

### 1. P&ID Ingestion (PDF → Database)

#### **Challenge**
Extract equipment, connections, and metadata from P&ID PDFs.

**What to Extract:**
- Equipment symbols (pumps, motors, valves, instruments)
- Tag numbers (210-PP-001, FT-210-05, etc.)
- Connections (pipes, signals)
- Specifications (100HP, 4-20mA, etc.)
- Area assignments
- Elevations, locations

#### **Technology Options**

##### **Option A: AI Vision (Claude/GPT-4 Vision) - Recommended**

**How it works:**
1. Upload P&ID PDF to API
2. AI identifies symbols and extracts data
3. Returns structured JSON
4. Parse and populate database

**Technologies:**
- **Anthropic Claude 3.5 Sonnet** (vision API)
- **OpenAI GPT-4 Vision** (alternative)
- **Custom prompts** for P&ID understanding

**Pros:**
- High accuracy with proper prompts
- Handles various P&ID styles
- Understands context (not just OCR)
- No training required

**Cons:**
- Paid API ($0.01-0.05 per page)
- Requires internet
- Rate limits

**Implementation:**
```python
# Backend: P&ID ingestion service
import anthropic

async def ingest_pid_pdf(pdf_path: str) -> List[Asset]:
    # Convert PDF to images
    images = pdf_to_images(pdf_path)
    
    # Call Claude Vision API
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "data": images[0]}
                },
                {
                    "type": "text",
                    "text": """Extract all equipment from this P&ID:
                    For each equipment, return JSON:
                    {
                      "tag": "210-PP-001",
                      "type": "PUMP",
                      "description": "Centrifugal pump",
                      "specifications": {"hp": 100, "flow": "500 GPM"},
                      "x": 150, "y": 300,
                      "connections": [
                        {"to": "210-M-001", "type": "POWER"},
                        {"to": "210-FT-001", "type": "SIGNAL"}
                      ]
                    }
                    """
                }
            ]
        })
    
    # Parse response
    equipment_data = json.loads(response.content[0].text)
    
    # Create assets in database
    assets = []
    for item in equipment_data:
        asset = create_asset_from_pid(item)
        assets.append(asset)
    
    return assets
```

**Cost:** ~$0.01-0.05 per P&ID page

---

##### **Option B: Computer Vision + ML (Opensource)**

**How it works:**
1. Train ML model to recognize symbols
2. Use OpenCV for line/connection tracing
3. OCR for text extraction
4. Combine into structured data

**Technologies:**
- **Symbol Detection:** YOLO v8 (object detection)
- **Line Tracing:** OpenCV (Hough transform)
- **OCR:** Tesseract or EasyOCR
- **Training Data:** Custom P&ID dataset

**Pros:**
- Fully opensource
- No API costs
- Works offline
- Customizable

**Cons:**
- Requires training data (~1000+ P&IDs)
- Lower accuracy initially
- Significant development time
- GPU required

**Implementation Effort:** 3-6 months development

**Decision:** Start with Option A (AI Vision), migrate to Option B if cost becomes issue.

---

### 2. Electrical Drawings Ingestion (DWG/PDF → Database)

#### **DWG Parsing**

**Technologies:**
- **ezdxf** (Python, MIT) - Read/write DXF/DWG
- **Open Design Alliance SDK** (Commercial, expensive)

**Recommendation:** `ezdxf` (opensource)

**What to Extract:**
- Motors, MCCs, VFDs, cables
- Terminal blocks, PLCs, IO
- Wire numbers, cable IDs
- Equipment locations
- Power ratings

**Implementation:**
```python
import ezdxf

def ingest_electrical_dwg(dwg_path: str) -> List[Asset]:
    # Load DWG
    doc = ezdxf.readfile(dwg_path)
    msp = doc.modelspace()
    
    assets = []
    
    # Extract blocks (symbols)
    for entity in msp.query('INSERT'):  # Blocks
        block_name = entity.dxf.name
        
        if 'MOTOR' in block_name:
            # Extract motor tag from attributes
            tag = get_attribute(entity, 'TAG')
            hp = get_attribute(entity, 'HP')
            voltage = get_attribute(entity, 'VOLTAGE')
            
            asset = create_motor(tag, hp, voltage)
            assets.append(asset)
        
        elif 'VFD' in block_name:
            # Similar for VFD
            pass
    
    # Extract lines (cables)
    for line in msp.query('LINE'):
        start_point = line.dxf.start
        end_point = line.dxf.end
        
        # Trace connections
        from_equip = find_equipment_at_point(start_point)
        to_equip = find_equipment_at_point(end_point)
        
        if from_equip and to_equip:
            create_cable(from_equip, to_equip)
    
    return assets
```

---

### 3. P&ID Generation (Database → PDF/DWG)

#### **Challenge**
Generate professional P&IDs from asset database.

#### **Technology Options**

##### **Option A: AutoCAD Automation (Industry Standard)**

**How it works:**
1. Use AutoCAD Plant 3D API (Python .NET)
2. Place symbols from library
3. Connect with lines
4. Add annotations
5. Export to PDF/DWG

**Pros:**
- Industry standard output
- Professional symbols
- Full compliance with standards

**Cons:**
- Requires AutoCAD license ($1,700/year)
- Windows only
- Complex API

**Decision:** Only if client requires AutoCAD format.

---

##### **Option B: QElectroTech (Opensource) - Recommended**

**How it works:**
1. Use QElectroTech Python API
2. Place symbols programmatically
3. Generate DXF output
4. Convert to PDF

**Technologies:**
- **QElectroTech** (GPL, free)
- **Python automation**

**Pros:**
- Fully opensource
- Cross-platform
- Good symbol library
- DXF/PDF export

**Cons:**
- Less polished than AutoCAD
- Limited to electrical diagrams

---

##### **Option C: Custom SVG/Canvas Generation**

**How it works:**
1. Define symbol library (SVG)
2. Layout algorithm (auto-place equipment)
3. Render to SVG/Canvas
4. Export to PDF

**Technologies:**
- **Cairo** (graphics library)
- **ReportLab** (PDF generation)
- **SVG.js** (frontend preview)
- **Custom layout algorithms**

**Pros:**
- Full control
- Customizable styling
- Web-based preview
- Opensource

**Cons:**
- Significant development (6+ months)
- Symbol library creation
- Layout complexity

**Implementation:**
```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_pid_pdf(assets: List[Asset], output_path: str):
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Place equipment symbols
    for asset in assets:
        x, y = calculate_position(asset)
        symbol = get_symbol_for_type(asset.type)
        
        # Draw symbol
        c.drawImage(symbol, x, y, width=50, height=50)
        
        # Add tag
        c.drawString(x, y-10, asset.tag)
        c.drawString(x, y-20, asset.description)
    
    # Draw connections
    for cable in get_cables(assets):
        from_asset = cable.from_asset
        to_asset = cable.to_asset
        
        from_x, from_y = get_position(from_asset)
        to_x, to_y = get_position(to_asset)
        
        c.line(from_x, from_y, to_x, to_y)
    
    c.save()
```

---

### 4. Electrical Diagram Generation (Database → DWG)

#### **Single-Line Diagrams**

**Option A: QElectroTech**
- Generate one-line diagrams
- Motor control, VFD, MCC
- Export DXF

**Option B: Custom SVG**
- Simpler than P&IDs
- Standard symbols
- PDF export

#### **Implementation Priority**

**Phase 7 (Future):**
- P&ID Ingestion (AI Vision)
- Basic P&ID generation (SVG → PDF)

**Phase 8 (Advanced):**
- DWG ingestion (`ezdxf`)
- Electrical diagram generation
- AutoCAD integration (if client requirement)

---

### 5. Symbol Libraries

#### **Opensource P&ID Symbols**

**Sources:**
- ISA standard symbols (public domain)
- OpenSymbol project (CC-BY)
- Custom SVG library

**Create Library:**
```
symbols/
├── instruments/
│   ├── FT.svg (Flow Transmitter)
│   ├── PT.svg (Pressure Transmitter)
│   ├── LT.svg (Level Transmitter)
│   └── TT.svg (Temperature Transmitter)
├── equipment/
│   ├── PUMP.svg
│   ├── TANK.svg
│   ├── VALVE.svg
│   └── MOTOR.svg
└── electrical/
    ├── MCC.svg
    ├── VFD.svg
    ├── PLC.svg
    └── TRANSFORMER.svg
```

Format: SVG (scalable, editable, web-compatible)

---

### 6. Auto-Layout Algorithm

**Challenge:** Automatically position equipment on drawing.

**Algorithms:**
- **Force-directed layout** (physics simulation)
- **Hierarchical layout** (top-down)
- **Grid-based layout** (structured)

**Library:**
- **Graphviz** (opensource) - Auto-layout graphs
- **D3.js force simulation** - Interactive layout

**Implementation:**
```python
import graphviz

def auto_layout_pid(assets: List[Asset]) -> Dict[str, Tuple[int, int]]:
    # Create graph
    graph = graphviz.Digraph()
    
    # Add nodes
    for asset in assets:
        graph.node(asset.tag, label=f"{asset.tag}\n{asset.type}")
    
    # Add edges (connections)
    for cable in get_cables(assets):
        graph.edge(cable.from_asset.tag, cable.to_asset.tag)
    
    # Render to get positions
    graph.render('temp', format='plain')
    
    # Parse positions from output
    positions = parse_graphviz_positions('temp.plain')
    
    return positions  # {asset_tag: (x, y)}
```

---

### 7. Technology Stack Summary

| Feature | Technology | License | Phase | Cost |
|---------|------------|---------|-------|------|
| **P&ID Ingestion** | Claude Vision API | Proprietary | 7 | $0.01-0.05/page |
| **P&ID Ingestion** | YOLO + OpenCV (alt) | MIT | 8 | Free (GPU required) |
| **DWG Parsing** | ezdxf | MIT | 7 | Free |
| **P&ID Generation** | Custom SVG + Cairo | MIT | 7 | Free |
| **P&ID Generation** | QElectroTech (alt) | GPL | 7 | Free |
| **Electrical Gen** | QElectroTech | GPL | 8 | Free |
| **Symbol Library** | Custom SVG | Public/CC-BY | 7 | Free |
| **Auto-Layout** | Graphviz | EPL | 7 | Free |
| **PDF Export** | ReportLab | BSD | 7 | Free |

---

### 8. Implementation Roadmap

#### **Phase 7: P&ID Ingestion & Basic Generation (3-4 months)**

**Milestones:**
1. **P&ID Ingestion**
   - Integrate Claude Vision API
   - Parse AI response to structured data
   - Create assets from P&ID
   - Handle multi-page PDFs

2. **Symbol Library**
   - Create SVG symbol library (50+ symbols)
   - Categorize (instruments, equipment, electrical)
   - Web preview

3. **Basic P&ID Generation**
   - Auto-layout algorithm (Graphviz)
   - Render symbols to SVG
   - Export to PDF (ReportLab)
   - Preview in browser

**Deliverables:**
- Import P&ID PDF → Create 100+ assets automatically
- Generate P&ID PDF from database
- 80% accuracy on tag extraction

---

#### **Phase 8: Electrical Diagrams (2-3 months)**

**Milestones:**
1. **DWG Parsing**
   - Integrate ezdxf
   - Extract blocks, attributes
   - Create electrical assets

2. **Electrical Generation**
   - Single-line diagrams
   - Motor control circuits
   - Export DXF

**Deliverables:**
- Import electrical DWG → Create assets
- Generate single-line diagrams
- QElectroTech integration

---

### 9. Accuracy & Validation

**P&ID Ingestion Accuracy:**
- **AI Vision:** 85-95% (with good prompts)
- **ML Model:** 70-85% (requires training)

**Human Validation:**
- Always review AI-generated assets
- Flag uncertain extractions
- Manual correction UI

**UI Feature:**
```
Imported from P&ID: Sheet-001.pdf
─────────────────────────────────────
✅ 210-PP-001 (PUMP) - Confidence: 98%
✅ 210-M-001 (MOTOR) - Confidence: 95%
⚠️ 210-FT-??? (FLOW?) - Confidence: 65% [Review]
❌ Could not extract tag - [Manual Entry]

[Approve All] [Review Flagged] [Manual Review]
```

---

### 10. Updated Architecture (with Drawings)

```
USER
  ↓ Upload P&ID PDF
BACKEND
  ↓ PDF → Images
AI VISION API (Claude)
  ↓ Extract equipment + connections
BACKEND
  ↓ Parse JSON → Create assets
DATABASE
  ↓ Store assets, cables, connections
  
---

DATABASE
  ↓ Query assets for area
BACKEND
  ↓ Auto-layout (Graphviz)
  ↓ Render symbols (SVG)
  ↓ Generate PDF (ReportLab)
USER
  ↓ Download P&ID PDF
```

---

### 11. Success Criteria

Drawing features successful if:
- [ ] Import 10-page P&ID → 200+ assets created
- [ ] 85%+ accuracy on tag extraction
- [ ] Generate P&ID from 200 assets in <30 seconds
- [ ] Generated P&IDs readable by engineers
- [ ] Full opensource stack (except AI Vision API)

---

### 12. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| AI Vision API cost | Batch processing, cache results |
| Low extraction accuracy | Human validation required |
| Symbol library incomplete | Incremental addition, user-contributed |
| Layout not perfect | Manual adjustment tools |
| AutoCAD requirement | Support DXF export (compatible) |

---

**Phase 7-8 = Advanced drawing integration (Future priority)**

