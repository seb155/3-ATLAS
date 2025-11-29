# NEXUS Development Plan

**Version:** v0.1.0-alpha → v1.0.0
**Status:** Phase 1.5 Complete → Phase 2 Next
**Timeline:** 6 mois (Q1-Q2 2026)
**Last Updated:** 2025-11-29

---

## Vision

**NEXUS** = Second Brain with 3D visualization ("FRED")

Combining:
- **TriliumNext** sync (source of truth for notes)
- **3D Knowledge Graph** (InfraNodus-style)
- **Markdown viewer** (click node → see note)
- **AI-powered insights** (Claude integration)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEXUS + TriliumNext                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TriliumNext ──(ETAPI)──▶ Sync Service ──▶ PostgreSQL          │
│       │                        │                │               │
│       │                        │                │               │
│       │                        ▼                ▼               │
│       │                  ┌─────────────────────────┐            │
│       │                  │    NEXUS Frontend       │            │
│       │                  │                         │            │
│       │                  │  ┌─────────────────┐   │            │
│       │                  │  │  3D GRAPH       │   │            │
│       │                  │  │  "FRED"         │   │            │
│       │                  │  │   ●───●───●     │   │            │
│       │                  │  └────────┬────────┘   │            │
│       │                  │           │ click      │            │
│       │                  │           ▼            │            │
│       │                  │  ┌─────────────────┐   │            │
│       │                  │  │ Markdown Viewer │   │            │
│       │                  │  │ # Note Title    │   │            │
│       │                  │  │ Content...      │   │            │
│       │                  │  └─────────────────┘   │            │
│       │                  └─────────────────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase Summary

| Phase | Name | Duration | Status |
|:---:|:---|:---:|:---:|
| 1 | Foundation | 1 day | ✅ Complete |
| 1.5 | Visual Polish | 1 day | ✅ Complete |
| 2 | TriliumNext Sync + Notes | 3-4 weeks | 🔜 Next |
| 3 | 3D Graph "FRED" | 3-4 weeks | Planned |
| 4 | Task Management | 2-3 weeks | Planned |
| 5 | AI Integration | 2-3 weeks | Planned |
| 6 | Collaboration | 3-4 weeks | Future |

---

## Phase 2: TriliumNext Sync + Notes System

### Objective

Sync notes from TriliumNext to NEXUS and display them with a graph visualization.

### TriliumNext Integration

**API:** ETAPI (REST API)
**Library:** `trilium-py` (Python)
**Auth:** ETAPI Token

**Configuration:**
```env
# .env
TRILIUM_SERVER_URL=http://localhost:8080
TRILIUM_ETAPI_TOKEN=your_token_here
TRILIUM_SYNC_INTERVAL=300  # seconds (5 min)
```

### Database Schema

```sql
-- Notes synced from TriliumNext
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trilium_id VARCHAR(20) UNIQUE NOT NULL,  -- TriliumNext note ID
    parent_id UUID REFERENCES notes(id),
    title VARCHAR(500) NOT NULL,
    content_html TEXT,                        -- Original HTML from Trilium
    content_md TEXT,                          -- Converted Markdown
    content_text TEXT,                        -- Plain text for search
    content_search TSVECTOR,                  -- Full-text search
    note_type VARCHAR(50) DEFAULT 'text',     -- text, code, file, etc.
    attributes JSONB DEFAULT '{}',            -- Trilium attributes
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    synced_at TIMESTAMP DEFAULT NOW()
);

-- Links between notes (extracted from content)
CREATE TABLE note_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    to_note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    link_type VARCHAR(50) DEFAULT 'internal',  -- internal, reference, tag
    link_text VARCHAR(500),                    -- Display text of link
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(from_note_id, to_note_id)
);

-- Sync status tracking
CREATE TABLE sync_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(50) NOT NULL,              -- 'trilium', 'manual', etc.
    status VARCHAR(20) NOT NULL,              -- 'success', 'error', 'partial'
    notes_synced INTEGER DEFAULT 0,
    notes_created INTEGER DEFAULT 0,
    notes_updated INTEGER DEFAULT 0,
    notes_deleted INTEGER DEFAULT 0,
    links_synced INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_ms INTEGER
);

-- Create indexes
CREATE INDEX idx_notes_trilium_id ON notes(trilium_id);
CREATE INDEX idx_notes_parent_id ON notes(parent_id);
CREATE INDEX idx_notes_search ON notes USING gin(content_search);
CREATE INDEX idx_note_links_from ON note_links(from_note_id);
CREATE INDEX idx_note_links_to ON note_links(to_note_id);
```

### Backend Tasks

#### 2.1 TriliumNext Sync Service

```python
# app/services/trilium_sync_service.py
from trilium_py.client import ETAPI
from typing import List, Dict
import html2text
import re

class TriliumSyncService:
    """Service to sync notes from TriliumNext to NEXUS database."""

    def __init__(self, server_url: str, token: str):
        self.client = ETAPI(server_url)
        self.client.set_token(token)
        self.html_converter = html2text.HTML2Text()
        self.html_converter.body_width = 0  # No line wrapping

    async def sync_all_notes(self) -> Dict:
        """Full sync of all notes from TriliumNext."""
        pass

    async def sync_note(self, trilium_id: str) -> Dict:
        """Sync a single note by Trilium ID."""
        # 1. Fetch note from Trilium
        note = self.client.get_note(trilium_id)
        content = self.client.get_note_content(trilium_id)

        # 2. Convert HTML to Markdown
        markdown = self.html_to_markdown(content)

        # 3. Extract internal links
        links = self.extract_links(content)

        # 4. Save to database
        return await self.save_note(note, content, markdown, links)

    def html_to_markdown(self, html: str) -> str:
        """Convert HTML content to Markdown."""
        return self.html_converter.handle(html)

    def extract_links(self, html: str) -> List[Dict]:
        """Extract internal Trilium links from HTML content."""
        # Trilium uses data-note-path attribute for internal links
        pattern = r'data-note-path="([^"]+)"'
        matches = re.findall(pattern, html)
        return [{'trilium_id': m.split('/')[-1]} for m in matches]
```

#### 2.2 API Endpoints

```python
# app/api/endpoints/notes.py

@router.get("/", response_model=List[NoteResponse])
async def list_notes(
    parent_id: Optional[UUID] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """List notes with optional filtering."""
    pass

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: UUID):
    """Get a single note."""
    pass

@router.get("/{note_id}/markdown", response_model=str)
async def get_note_markdown(note_id: UUID):
    """Get note content as Markdown."""
    pass

@router.get("/{note_id}/links", response_model=List[NoteLinkResponse])
async def get_note_links(note_id: UUID):
    """Get all links from/to this note."""
    pass


# app/api/endpoints/sync.py

@router.post("/trilium", response_model=SyncResultResponse)
async def sync_from_trilium(
    full_sync: bool = False,
    background_tasks: BackgroundTasks
):
    """Trigger sync from TriliumNext."""
    pass

@router.get("/status", response_model=SyncStatusResponse)
async def get_sync_status():
    """Get current sync status."""
    pass


# app/api/endpoints/graph.py

@router.get("/data", response_model=GraphDataResponse)
async def get_graph_data(
    root_note_id: Optional[UUID] = None,
    depth: int = 3,
    min_connections: int = 0
):
    """Get graph data for visualization."""
    pass

@router.get("/metrics", response_model=GraphMetricsResponse)
async def get_graph_metrics():
    """Get network metrics (centrality, clustering, etc.)."""
    pass
```

### Frontend Tasks

#### 2.3 Note Viewer Component

```typescript
// src/features/notes/NoteViewer.tsx
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';

interface NoteViewerProps {
  noteId: string;
}

export function NoteViewer({ noteId }: NoteViewerProps) {
  const { data: note, isLoading } = useNote(noteId);

  if (isLoading) return <Skeleton />;

  return (
    <div className="note-viewer prose dark:prose-invert max-w-none">
      <h1>{note.title}</h1>
      <div className="note-meta">
        <span>Synced: {formatDate(note.synced_at)}</span>
      </div>
      <ReactMarkdown
        components={{
          code: ({ inline, className, children }) => {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <SyntaxHighlighter language={match[1]}>
                {String(children)}
              </SyntaxHighlighter>
            ) : (
              <code className={className}>{children}</code>
            );
          },
          a: ({ href, children }) => {
            // Handle internal links
            if (href?.startsWith('/note/')) {
              return <InternalLink noteId={href.slice(6)}>{children}</InternalLink>;
            }
            return <a href={href} target="_blank" rel="noopener">{children}</a>;
          }
        }}
      >
        {note.content_md}
      </ReactMarkdown>
    </div>
  );
}
```

#### 2.4 Graph 3D "FRED" Component

```typescript
// src/features/graph/Graph3DView.tsx
import ForceGraph3D from 'react-force-graph-3d';
import SpriteText from 'three-spritetext';

interface Graph3DViewProps {
  onNodeClick: (nodeId: string) => void;
}

export function Graph3DView({ onNodeClick }: Graph3DViewProps) {
  const { data: graphData } = useGraphData();
  const graphRef = useRef<any>();

  useEffect(() => {
    if (graphRef.current) {
      // Camera setup
      graphRef.current.cameraPosition({ z: 500 });

      // Custom node rendering with labels
      graphRef.current.nodeThreeObject((node: any) => {
        const sprite = new SpriteText(node.title);
        sprite.color = getNodeColor(node.type);
        sprite.textHeight = 6;
        return sprite;
      });
    }
  }, []);

  return (
    <div className="graph-container w-full h-full">
      <ForceGraph3D
        ref={graphRef}
        graphData={graphData}
        nodeLabel="title"
        nodeColor={node => getNodeColor(node.type)}
        linkColor={() => 'rgba(255,255,255,0.2)'}
        linkWidth={1}
        onNodeClick={(node) => onNodeClick(node.id)}
        backgroundColor="#09090b"
      />
    </div>
  );
}
```

### Deliverables Phase 2

- [ ] TriliumNext sync service (Python + trilium-py)
- [ ] Database schema with notes + links
- [ ] Notes API (CRUD + search)
- [ ] Graph API (data + metrics)
- [ ] Sync API (trigger + status)
- [ ] Note Viewer (Markdown render)
- [ ] Graph 3D "FRED" (basic visualization)
- [ ] Click node → show note panel

---

## Phase 3: 3D Graph "FRED" Advanced

### Objective

Full InfraNodus-style graph analytics.

### Features

- [ ] 2D/3D toggle
- [ ] Community detection (Louvain algorithm)
- [ ] Centrality metrics (degree, betweenness, PageRank)
- [ ] Filtering panel (by type, connections, keywords)
- [ ] Path finder between nodes
- [ ] Cluster highlighting
- [ ] Time-based animation

### Technologies

| Component | Technology |
|:---|:---|
| Graph rendering | react-force-graph-3d, Three.js |
| Network analysis | NetworkX (Python backend) |
| Community detection | python-louvain |
| Metrics | numpy, scipy |

---

## Phase 4: Task Management

### Objective

Kanban board linked to notes.

### Features

- [ ] Kanban columns (Backlog, Todo, In Progress, Done)
- [ ] Task cards with details
- [ ] Link tasks to notes
- [ ] Drag-drop reordering
- [ ] Due dates and priorities

---

## Phase 5: AI Integration

### Objective

Claude-powered insights and assistance.

### Features

- [ ] AI chat with note context
- [ ] Auto-summarization
- [ ] Related notes suggestions
- [ ] Gap analysis ("what's missing in your knowledge?")

---

## Configuration Required

### TriliumNext Setup

1. **Install TriliumNext** (if not done)
   ```bash
   docker run -d -p 8080:8080 triliumnext/notes
   ```

2. **Get ETAPI Token**
   - Open TriliumNext → Options → ETAPI
   - Generate new token
   - Save token securely

3. **Configure NEXUS**
   ```env
   # apps/nexus/backend/.env
   TRILIUM_SERVER_URL=http://localhost:8080
   TRILIUM_ETAPI_TOKEN=your_token_here
   TRILIUM_SYNC_INTERVAL=300
   ```

### Dependencies to Add

**Backend:**
```bash
pip install trilium-py html2text python-louvain networkx
```

**Frontend:**
```bash
npm install react-force-graph-3d three three-spritetext react-markdown
```

---

## Files to Create

| File | Purpose |
|:---|:---|
| `backend/app/services/trilium_sync_service.py` | TriliumNext sync |
| `backend/app/services/graph_service.py` | Graph analytics |
| `backend/app/api/endpoints/sync.py` | Sync API |
| `backend/app/api/endpoints/graph.py` | Graph API |
| `backend/app/models/note.py` | Note model (update) |
| `backend/app/models/sync_log.py` | Sync log model |
| `frontend/src/features/graph/Graph3DView.tsx` | 3D graph |
| `frontend/src/features/notes/NoteViewer.tsx` | Markdown viewer |
| `frontend/src/hooks/useGraphData.ts` | Graph data hook |
| `frontend/src/hooks/useTriliumSync.ts` | Sync hook |

---

## Success Criteria

### Phase 2 Complete When:

1. ✅ Notes sync from TriliumNext on demand
2. ✅ Notes visible in NEXUS database
3. ✅ Graph shows all notes as nodes
4. ✅ Links between notes shown as edges
5. ✅ Click node → Markdown viewer opens
6. ✅ Search notes by title/content
7. ✅ Sync status visible in UI

---

## Next Steps

1. **Finish SYNAPSE MVP** (Priority - Dec 20, 2025)
2. **Setup TriliumNext** (if not done)
3. **Get ETAPI Token** from TriliumNext
4. **Start Phase 2** when ready

---

*Document created: 2025-11-29*
*Sources: [TriliumNext Docs](https://triliumnext.github.io/Docs/) | [ETAPI Wiki](https://github.com/TriliumNext/Trilium/wiki/ETAPI) | [trilium-py](https://pypi.org/project/trilium-py/)*
