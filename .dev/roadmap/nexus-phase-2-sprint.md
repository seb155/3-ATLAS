# NEXUS Phase 2 - TriliumNext Sync + Graph "FRED"

**Sprint Duration:** 3-4 semaines
**Start Date:** TBD (après SYNAPSE MVP)
**Objective:** Synchroniser TriliumNext et visualiser en 3D

---

## Sprint Overview

```
Semaine 1: Backend Setup + TriliumNext Sync
Semaine 2: Graph API + NetworkX Analytics
Semaine 3: Frontend Graph 3D + Note Viewer
Semaine 4: Polish + Testing + Documentation
```

---

## Week 1: Backend Setup + TriliumNext Sync

### Day 1-2: Database Schema

**Tasks:**
- [ ] Create Alembic migration for notes schema
- [ ] Add `trilium_id` column for sync tracking
- [ ] Create `note_links` table for graph edges
- [ ] Create `sync_log` table for sync history
- [ ] Add full-text search indexes

**Files:**
```
backend/alembic/versions/xxxx_add_trilium_sync_tables.py
```

**SQL Preview:**
```sql
CREATE TABLE notes (
    id UUID PRIMARY KEY,
    trilium_id VARCHAR(20) UNIQUE NOT NULL,
    parent_id UUID REFERENCES notes(id),
    title VARCHAR(500) NOT NULL,
    content_html TEXT,
    content_md TEXT,
    content_text TEXT,
    content_search TSVECTOR,
    note_type VARCHAR(50) DEFAULT 'text',
    attributes JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    synced_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE note_links (
    id UUID PRIMARY KEY,
    from_note_id UUID REFERENCES notes(id) ON DELETE CASCADE,
    to_note_id UUID REFERENCES notes(id) ON DELETE CASCADE,
    link_type VARCHAR(50) DEFAULT 'internal',
    link_text VARCHAR(500),
    UNIQUE(from_note_id, to_note_id)
);

CREATE TABLE sync_log (
    id UUID PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    notes_synced INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

### Day 3-4: TriliumNext Sync Service

**Tasks:**
- [ ] Install `trilium-py` and `html2text`
- [ ] Create `TriliumSyncService` class
- [ ] Implement note fetching from ETAPI
- [ ] Implement HTML to Markdown conversion
- [ ] Implement internal link extraction
- [ ] Add error handling and retry logic

**File:** `backend/app/services/trilium_sync_service.py`

```python
from trilium_py.client import ETAPI
import html2text
import re
from typing import List, Dict, Optional
from datetime import datetime

class TriliumSyncService:
    def __init__(self, server_url: str, token: str):
        self.client = ETAPI(server_url)
        self.client.set_token(token)
        self.html_converter = html2text.HTML2Text()
        self.html_converter.body_width = 0

    async def sync_all_notes(self, db: Session) -> Dict:
        """Sync all notes from TriliumNext."""
        started_at = datetime.utcnow()
        stats = {"created": 0, "updated": 0, "errors": 0}

        try:
            # Get all notes from Trilium
            notes = self.client.search_notes("")

            for note in notes:
                try:
                    await self.sync_single_note(note["noteId"], db)
                    stats["created"] += 1
                except Exception as e:
                    stats["errors"] += 1

            # Log sync result
            await self._log_sync(db, "success", stats, started_at)

        except Exception as e:
            await self._log_sync(db, "error", stats, started_at, str(e))
            raise

        return stats

    async def sync_single_note(self, trilium_id: str, db: Session) -> Note:
        """Sync a single note."""
        # Fetch from Trilium
        note_data = self.client.get_note(trilium_id)
        content_html = self.client.get_note_content(trilium_id)

        # Convert to Markdown
        content_md = self.html_to_markdown(content_html)

        # Extract plain text for search
        content_text = self.extract_plain_text(content_html)

        # Extract internal links
        links = self.extract_links(content_html)

        # Upsert note
        note = await self._upsert_note(db, {
            "trilium_id": trilium_id,
            "title": note_data["title"],
            "content_html": content_html,
            "content_md": content_md,
            "content_text": content_text,
            "note_type": note_data.get("type", "text"),
            "attributes": note_data.get("attributes", {}),
        })

        # Update links
        await self._update_links(db, note.id, links)

        return note

    def html_to_markdown(self, html: str) -> str:
        """Convert HTML to Markdown."""
        if not html:
            return ""
        return self.html_converter.handle(html)

    def extract_plain_text(self, html: str) -> str:
        """Extract plain text from HTML."""
        if not html:
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_links(self, html: str) -> List[Dict]:
        """Extract internal Trilium links."""
        if not html:
            return []

        links = []
        # Trilium internal links pattern
        pattern = r'href="#root/([^"]+)"[^>]*>([^<]*)</a>'
        matches = re.findall(pattern, html)

        for note_path, link_text in matches:
            trilium_id = note_path.split("/")[-1]
            links.append({
                "trilium_id": trilium_id,
                "link_text": link_text
            })

        return links
```

### Day 5: Sync API Endpoints

**Tasks:**
- [ ] Create sync router
- [ ] Implement manual sync trigger endpoint
- [ ] Implement sync status endpoint
- [ ] Add background task support for async sync

**File:** `backend/app/api/endpoints/sync.py`

```python
from fastapi import APIRouter, BackgroundTasks, Depends
from app.services.trilium_sync_service import TriliumSyncService
from app.core.config import settings

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/trilium")
async def trigger_trilium_sync(
    background_tasks: BackgroundTasks,
    full_sync: bool = False,
    db: Session = Depends(get_db)
):
    """Trigger sync from TriliumNext."""
    sync_service = TriliumSyncService(
        settings.TRILIUM_SERVER_URL,
        settings.TRILIUM_ETAPI_TOKEN
    )

    # Run sync in background
    background_tasks.add_task(sync_service.sync_all_notes, db)

    return {"status": "sync_started", "full_sync": full_sync}

@router.get("/status")
async def get_sync_status(db: Session = Depends(get_db)):
    """Get latest sync status."""
    latest = db.query(SyncLog).order_by(SyncLog.started_at.desc()).first()
    return {
        "last_sync": latest.started_at if latest else None,
        "status": latest.status if latest else "never",
        "notes_synced": latest.notes_synced if latest else 0
    }
```

---

## Week 2: Graph API + NetworkX Analytics

### Day 1-2: Graph Service

**Tasks:**
- [ ] Install `networkx` and `python-louvain`
- [ ] Create `GraphService` class
- [ ] Implement graph building from notes/links
- [ ] Implement centrality metrics
- [ ] Implement community detection

**File:** `backend/app/services/graph_service.py`

```python
import networkx as nx
from community import community_louvain
from typing import Dict, List

class GraphService:
    def build_graph(self, notes: List[Note], links: List[NoteLink]) -> nx.Graph:
        """Build NetworkX graph from notes and links."""
        G = nx.Graph()

        # Add nodes
        for note in notes:
            G.add_node(str(note.id),
                title=note.title,
                type=note.note_type,
                trilium_id=note.trilium_id
            )

        # Add edges
        for link in links:
            G.add_edge(str(link.from_note_id), str(link.to_note_id),
                link_type=link.link_type,
                link_text=link.link_text
            )

        return G

    def calculate_metrics(self, G: nx.Graph) -> Dict:
        """Calculate network metrics."""
        if len(G.nodes()) == 0:
            return {}

        return {
            "node_count": G.number_of_nodes(),
            "edge_count": G.number_of_edges(),
            "density": nx.density(G),
            "degree_centrality": nx.degree_centrality(G),
            "betweenness_centrality": nx.betweenness_centrality(G),
            "clustering": nx.clustering(G),
        }

    def detect_communities(self, G: nx.Graph) -> Dict[str, int]:
        """Detect communities using Louvain algorithm."""
        if len(G.nodes()) == 0:
            return {}
        return community_louvain.best_partition(G)

    def get_top_nodes(self, G: nx.Graph, metric: str = "degree", n: int = 10) -> List[Dict]:
        """Get top N nodes by metric."""
        if metric == "degree":
            scores = dict(G.degree())
        elif metric == "betweenness":
            scores = nx.betweenness_centrality(G)
        elif metric == "pagerank":
            scores = nx.pagerank(G)
        else:
            scores = dict(G.degree())

        sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n]

        return [
            {"id": node_id, "score": score, "title": G.nodes[node_id].get("title", "")}
            for node_id, score in sorted_nodes
        ]
```

### Day 3-4: Graph API Endpoints

**Tasks:**
- [ ] Create graph router
- [ ] Implement graph data endpoint (nodes + edges)
- [ ] Implement metrics endpoint
- [ ] Add filtering parameters

**File:** `backend/app/api/endpoints/graph.py`

```python
@router.get("/data")
async def get_graph_data(
    root_note_id: Optional[UUID] = None,
    depth: int = 3,
    min_connections: int = 0,
    db: Session = Depends(get_db)
):
    """Get graph data for 3D visualization."""
    notes = db.query(Note).all()
    links = db.query(NoteLink).all()

    graph_service = GraphService()
    G = graph_service.build_graph(notes, links)

    # Apply filters
    if min_connections > 0:
        G = G.subgraph([n for n, d in G.degree() if d >= min_connections])

    communities = graph_service.detect_communities(G)

    return {
        "nodes": [
            {
                "id": node_id,
                "title": data.get("title", ""),
                "type": data.get("type", "text"),
                "community": communities.get(node_id, 0),
                "connections": G.degree(node_id)
            }
            for node_id, data in G.nodes(data=True)
        ],
        "links": [
            {"source": u, "target": v}
            for u, v in G.edges()
        ]
    }

@router.get("/metrics")
async def get_graph_metrics(db: Session = Depends(get_db)):
    """Get network analytics."""
    notes = db.query(Note).all()
    links = db.query(NoteLink).all()

    graph_service = GraphService()
    G = graph_service.build_graph(notes, links)
    metrics = graph_service.calculate_metrics(G)

    return {
        "total_nodes": metrics.get("node_count", 0),
        "total_edges": metrics.get("edge_count", 0),
        "density": metrics.get("density", 0),
        "top_by_degree": graph_service.get_top_nodes(G, "degree"),
        "top_by_betweenness": graph_service.get_top_nodes(G, "betweenness"),
        "communities_count": len(set(graph_service.detect_communities(G).values()))
    }
```

### Day 5: Notes API Update

**Tasks:**
- [ ] Update notes router with new fields
- [ ] Add markdown endpoint
- [ ] Add search endpoint
- [ ] Add backlinks endpoint

---

## Week 3: Frontend Graph 3D + Note Viewer

### Day 1-2: Dependencies + Setup

**Tasks:**
- [ ] Install 3D graph dependencies
- [ ] Install markdown renderer
- [ ] Create hooks for API calls
- [ ] Setup React Query for data fetching

**Commands:**
```bash
cd apps/nexus/frontend
npm install react-force-graph-3d three three-spritetext
npm install react-markdown remark-gfm
npm install @tanstack/react-query
```

### Day 3-4: Graph 3D Component "FRED"

**Tasks:**
- [ ] Create Graph3DView component
- [ ] Implement node rendering with labels
- [ ] Implement community coloring
- [ ] Add camera controls
- [ ] Handle node click events

**File:** `frontend/src/features/graph/Graph3DView.tsx`

```typescript
import { useRef, useEffect, useCallback } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import SpriteText from 'three-spritetext';
import { useGraphData } from '@/hooks/useGraphData';

const COMMUNITY_COLORS = [
  '#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#8b5cf6',
  '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1'
];

interface Graph3DViewProps {
  onNodeClick: (nodeId: string) => void;
}

export function Graph3DView({ onNodeClick }: Graph3DViewProps) {
  const graphRef = useRef<any>();
  const { data: graphData, isLoading } = useGraphData();

  useEffect(() => {
    if (graphRef.current && graphData) {
      // Position camera
      graphRef.current.cameraPosition({ z: 400 });

      // Custom node objects with text labels
      graphRef.current.nodeThreeObject((node: any) => {
        const sprite = new SpriteText(node.title);
        sprite.color = COMMUNITY_COLORS[node.community % COMMUNITY_COLORS.length];
        sprite.textHeight = 6;
        sprite.backgroundColor = 'rgba(0,0,0,0.6)';
        sprite.padding = 2;
        return sprite;
      });
    }
  }, [graphData]);

  const handleNodeClick = useCallback((node: any) => {
    onNodeClick(node.id);

    // Zoom to node
    if (graphRef.current) {
      const distance = 100;
      const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
      graphRef.current.cameraPosition(
        { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio },
        node,
        1000
      );
    }
  }, [onNodeClick]);

  if (isLoading) {
    return <div className="flex items-center justify-center h-full">Loading graph...</div>;
  }

  return (
    <ForceGraph3D
      ref={graphRef}
      graphData={graphData || { nodes: [], links: [] }}
      nodeLabel="title"
      nodeVal={(node: any) => node.connections + 1}
      nodeColor={(node: any) => COMMUNITY_COLORS[node.community % COMMUNITY_COLORS.length]}
      linkColor={() => 'rgba(255,255,255,0.15)'}
      linkWidth={0.5}
      onNodeClick={handleNodeClick}
      backgroundColor="#09090b"
      showNavInfo={false}
    />
  );
}
```

### Day 5: Note Viewer Component

**Tasks:**
- [ ] Create NoteViewer component
- [ ] Implement Markdown rendering
- [ ] Add syntax highlighting for code blocks
- [ ] Handle internal links
- [ ] Add slide-in panel animation

**File:** `frontend/src/features/notes/NoteViewer.tsx`

```typescript
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useNote } from '@/hooks/useNote';

interface NoteViewerProps {
  noteId: string;
  onClose: () => void;
  onNavigate: (noteId: string) => void;
}

export function NoteViewer({ noteId, onClose, onNavigate }: NoteViewerProps) {
  const { data: note, isLoading } = useNote(noteId);

  if (isLoading) {
    return (
      <div className="fixed inset-y-0 right-0 w-[500px] bg-zinc-900 border-l border-zinc-800 p-6">
        <Skeleton className="h-8 w-3/4 mb-4" />
        <Skeleton className="h-4 w-full mb-2" />
        <Skeleton className="h-4 w-full mb-2" />
        <Skeleton className="h-4 w-2/3" />
      </div>
    );
  }

  return (
    <div className="fixed inset-y-0 right-0 w-[500px] bg-zinc-900 border-l border-zinc-800 overflow-auto animate-in slide-in-from-right">
      {/* Header */}
      <div className="sticky top-0 bg-zinc-900/95 backdrop-blur border-b border-zinc-800 p-4 flex justify-between items-center">
        <h2 className="text-lg font-semibold truncate">{note?.title}</h2>
        <button onClick={onClose} className="p-2 hover:bg-zinc-800 rounded">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="p-6 prose prose-invert prose-sm max-w-none">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            a: ({ href, children }) => {
              // Handle internal note links
              if (href?.startsWith('#note/')) {
                return (
                  <button
                    onClick={() => onNavigate(href.slice(6))}
                    className="text-blue-400 hover:underline"
                  >
                    {children}
                  </button>
                );
              }
              return <a href={href} target="_blank" rel="noopener">{children}</a>;
            },
            code: ({ inline, className, children }) => {
              if (inline) {
                return <code className="bg-zinc-800 px-1.5 py-0.5 rounded">{children}</code>;
              }
              return (
                <pre className="bg-zinc-800 p-4 rounded-lg overflow-x-auto">
                  <code>{children}</code>
                </pre>
              );
            }
          }}
        >
          {note?.content_md || ''}
        </ReactMarkdown>
      </div>

      {/* Footer with metadata */}
      <div className="border-t border-zinc-800 p-4 text-xs text-zinc-500">
        <p>Synced: {new Date(note?.synced_at).toLocaleString()}</p>
        <p>Connections: {note?.links_count || 0}</p>
      </div>
    </div>
  );
}
```

---

## Week 4: Integration + Polish

### Day 1-2: Page Integration

**Tasks:**
- [ ] Update Graph page to use Graph3DView
- [ ] Add split view (graph + note viewer)
- [ ] Add sync button to UI
- [ ] Add sync status indicator

### Day 3-4: Testing + Polish

**Tasks:**
- [ ] Test full sync flow
- [ ] Test graph rendering performance
- [ ] Test note viewer with various content
- [ ] Add error handling UI
- [ ] Add loading states

### Day 5: Documentation

**Tasks:**
- [ ] Update NEXUS README
- [ ] Document TriliumNext setup
- [ ] Add configuration guide
- [ ] Create demo screenshots

---

## Configuration Checklist

### TriliumNext Setup

- [ ] TriliumNext installed and running
- [ ] ETAPI enabled in Options
- [ ] Token generated and saved

### NEXUS Backend

- [ ] `.env` file with Trilium credentials
- [ ] Dependencies installed (`trilium-py`, `networkx`, etc.)
- [ ] Database migration run

### NEXUS Frontend

- [ ] Dependencies installed (`react-force-graph-3d`, etc.)
- [ ] API hooks created
- [ ] Environment variables set

---

## Success Criteria

| Criteria | Status |
|:---|:---:|
| Sync notes from TriliumNext | ⬜ |
| Notes stored in PostgreSQL | ⬜ |
| Links extracted and stored | ⬜ |
| Graph 3D renders all nodes | ⬜ |
| Communities colored differently | ⬜ |
| Click node opens note viewer | ⬜ |
| Markdown renders correctly | ⬜ |
| Internal links navigable | ⬜ |
| Sync status visible in UI | ⬜ |
| < 1s load time for 500 notes | ⬜ |

---

*Sprint plan created: 2025-11-29*
