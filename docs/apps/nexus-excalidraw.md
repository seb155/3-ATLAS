# Excalidraw Integration in NEXUS

> Drawing and diagramming capabilities powered by Excalidraw, integrated directly into notes

## Overview

The Excalidraw integration provides a rich drawing and diagramming solution for NEXUS. Users can:

- Create and manage drawings in a dedicated Drawing page
- Organize drawings in hierarchical folders
- Embed drawings directly into notes using TipTap blocks
- Edit drawings in modal or inline modes
- Search drawings by title and description
- Track backlinks (which notes embed each drawing)

This feature is available in **Phase 2.5** of NEXUS development.

## Architecture

### Three-Layer Design

```
┌─────────────────────────────────────┐
│  Frontend (React + TipTap)          │
│  - Drawing.tsx page                 │
│  - ExcalidrawBlock extension        │
│  - useDrawingsStore (Zustand)       │
└─────────────────────────────────────┘
                  │
          HTTP REST API
                  │
┌─────────────────────────────────────┐
│  Backend (FastAPI + SQLAlchemy)     │
│  - /api/v1/drawings/* endpoints     │
│  - DrawingsService business logic   │
│  - Optimistic locking (version)     │
└─────────────────────────────────────┘
                  │
            PostgreSQL
                  │
┌─────────────────────────────────────┐
│  Database Tables                    │
│  - drawings (JSONB storage)         │
│  - note_drawing_embeds (links)      │
└─────────────────────────────────────┘
```

### Key Features

| Feature | Implementation | Status |
|---------|---|---|
| Drawing CRUD | REST API + service layer | Phase 2.5 |
| Hierarchical organization | Parent-child relationships + tree queries | Phase 2.5 |
| Full-text search | PostgreSQL TSVECTOR on title + description | Phase 2.5 |
| Optimistic locking | Version field with conflict detection | Phase 2.5 |
| Note embedding | TipTap block extension + embed tracking | Phase 2.5 |
| Thumbnails | Base64 PNG preview images | Phase 2.5 |
| Backlinks | Note-drawing relationship tracking | Phase 2.5 |
| AI generation | Placeholder (Phase 6) | Planned |

## Database Schema

### drawings Table

Stores Excalidraw drawing data with hierarchical organization.

```sql
CREATE TABLE drawings (
  id UUID PRIMARY KEY,
  title VARCHAR(500) NOT NULL,
  description TEXT DEFAULT '',
  elements JSONB NOT NULL DEFAULT '[]',        -- Excalidraw elements array
  app_state JSONB DEFAULT '{}',                 -- Canvas state (zoom, background)
  files JSONB DEFAULT '{}',                     -- Embedded images (base64)
  thumbnail TEXT,                               -- Preview PNG (base64)
  version INTEGER NOT NULL DEFAULT 1,           -- Optimistic locking
  user_id UUID NOT NULL REFERENCES users(id),   -- Owner
  parent_id UUID REFERENCES drawings(id) ON DELETE CASCADE,  -- Folder hierarchy
  is_folder BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  deleted_at TIMESTAMP WITH TIME ZONE,          -- Soft delete
  content_tsvector COMPUTED AS to_tsvector(...) -- Full-text search
);

-- Indexes for performance
CREATE INDEX idx_drawings_user_id ON drawings(user_id);
CREATE INDEX idx_drawings_parent_id ON drawings(parent_id);
CREATE INDEX idx_drawings_title ON drawings(title);
CREATE INDEX idx_drawings_content_tsvector ON drawings USING gin(content_tsvector);
CREATE INDEX idx_drawings_deleted_at ON drawings(deleted_at) WHERE deleted_at IS NULL;
```

### note_drawing_embeds Table

Tracks drawings embedded in notes with display settings.

```sql
CREATE TABLE note_drawing_embeds (
  id UUID PRIMARY KEY,
  note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  drawing_id UUID NOT NULL REFERENCES drawings(id) ON DELETE CASCADE,
  edit_mode VARCHAR(10) NOT NULL DEFAULT 'modal',  -- 'modal' or 'inline'
  width INTEGER DEFAULT 800,                       -- Display width in pixels
  height INTEGER DEFAULT 400,                      -- Display height in pixels
  position INTEGER DEFAULT 0,                      -- Order in note
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_note_drawing_embeds_note ON note_drawing_embeds(note_id);
CREATE INDEX idx_note_drawing_embeds_drawing ON note_drawing_embeds(drawing_id);
```

## API Reference

### Drawing CRUD Operations

#### Create Drawing

```http
POST /api/v1/drawings
Content-Type: application/json
Authorization: Bearer {token}

{
  "title": "System Architecture",
  "description": "High-level system design",
  "elements": [],                    -- Optional: Excalidraw elements
  "app_state": {},                   -- Optional: Canvas state
  "files": {},                       -- Optional: Embedded images
  "is_folder": false,                -- Optional: Create as folder
  "parent_id": null                  -- Optional: Parent folder UUID
}
```

**Response:** `201 Created`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "System Architecture",
  "description": "High-level system design",
  "elements": [],
  "app_state": {},
  "files": {},
  "thumbnail": null,
  "version": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "parent_id": null,
  "is_folder": false,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "deleted_at": null
}
```

#### Get Drawing

```http
GET /api/v1/drawings/{drawing_id}
Authorization: Bearer {token}
```

**Response:** `200 OK` with full Drawing object

#### Get All Drawings

```http
GET /api/v1/drawings?skip=0&limit=100&parent_id={parent_uuid}
Authorization: Bearer {token}
```

**Query Parameters:**
- `skip` (int, default=0): Pagination offset
- `limit` (int, default=100, max=500): Page size
- `parent_id` (UUID, optional): Filter by parent folder

**Response:** Array of Drawing objects

#### Get Drawing Tree

Returns hierarchical structure for sidebar/navigation.

```http
GET /api/v1/drawings/tree
Authorization: Bearer {token}
```

**Response:** `200 OK`

```json
{
  "drawings": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Architecture",
      "parent_id": null,
      "is_folder": true,
      "children_count": 3,
      "thumbnail": null
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "title": "Database Schema",
      "parent_id": "550e8400-e29b-41d4-a716-446655440000",
      "is_folder": false,
      "children_count": 0,
      "thumbnail": "data:image/png;base64,..."
    }
  ],
  "total": 5
}
```

#### Update Drawing

Requires `version` field for optimistic locking conflict detection.

```http
PUT /api/v1/drawings/{drawing_id}
Content-Type: application/json
Authorization: Bearer {token}

{
  "title": "Updated Title",          -- Optional
  "description": "New description",  -- Optional
  "elements": [...],                 -- Optional: Modified elements
  "app_state": {...},                -- Optional
  "files": {...},                    -- Optional
  "version": 2                       -- Required: Current version
}
```

**Response:** `200 OK` with updated Drawing

**Error Cases:**
- `409 Conflict`: Drawing modified by another session (version mismatch)
- `404 Not Found`: Drawing does not exist

#### Move Drawing

Move a drawing to a different parent (for folder organization).

```http
PUT /api/v1/drawings/{drawing_id}/move
Content-Type: application/json
Authorization: Bearer {token}

{
  "new_parent_id": "550e8400-e29b-41d4-a716-446655440005"
}
```

**Error Cases:**
- `400 Bad Request`: Parent not found or would create a cycle

#### Update Thumbnail

```http
PUT /api/v1/drawings/{drawing_id}/thumbnail
Content-Type: application/json
Authorization: Bearer {token}

{
  "thumbnail": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA..."
}
```

**Response:** `204 No Content`

#### Delete Drawing

Soft delete by default (can be recovered). Use `hard=true` to permanently delete.

```http
DELETE /api/v1/drawings/{drawing_id}?hard=false
Authorization: Bearer {token}
```

**Query Parameters:**
- `hard` (boolean, default=false): If true, permanently delete

**Response:** `204 No Content`

### Search Operations

#### Search Drawings

Full-text search using PostgreSQL TSVECTOR on title and description.

```http
GET /api/v1/drawings/search?q=architecture&limit=20
Authorization: Bearer {token}
```

**Query Parameters:**
- `q` (string, min_length=2): Search query
- `limit` (int, default=20, max=100): Maximum results

**Response:** `200 OK`

```json
{
  "query": "architecture",
  "total": 3,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "System Architecture",
      "description": "High-level design...",
      "thumbnail": "data:image/png;base64,...",
      "score": 0.95,
      "is_folder": false
    }
  ]
}
```

#### Find Drawing by Title

Exact title match for wiki-link resolution.

```http
GET /api/v1/drawings/find?title=System%20Architecture
Authorization: Bearer {token}
```

**Query Parameters:**
- `title` (string): Exact drawing title

**Response:** Drawing object or `null` if not found

### Backlinks

#### Get Drawing with Backlinks

Retrieve a drawing and all notes that embed it.

```http
GET /api/v1/drawings/{drawing_id}/backlinks
Authorization: Bearer {token}
```

**Response:** `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Database Schema",
  "description": "...",
  "elements": [...],
  "backlinks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "title": "System Design Notes",
      "type": "note",
      "link_text": null,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### Embedding Operations

#### Create Embed

Link a drawing to a note (usually done automatically when inserting block).

```http
POST /api/v1/drawings/embeds
Content-Type: application/json
Authorization: Bearer {token}

{
  "note_id": "550e8400-e29b-41d4-a716-446655440010",
  "drawing_id": "550e8400-e29b-41d4-a716-446655440000",
  "edit_mode": "modal",        -- Optional: 'modal' or 'inline'
  "width": 800,                -- Optional: Display width
  "height": 400,               -- Optional: Display height
  "position": 0                -- Optional: Order in note
}
```

**Response:** `201 Created` with NoteDrawingEmbed object

#### Get Embeds for Note

Retrieve all drawings embedded in a note.

```http
GET /api/v1/drawings/embeds/note/{note_id}
Authorization: Bearer {token}
```

**Response:** Array of NoteDrawingEmbed objects

#### Delete Embed

```http
DELETE /api/v1/drawings/embeds/{embed_id}
Authorization: Bearer {token}
```

**Response:** `204 No Content`

### AI Generation (Phase 6 - Placeholder)

#### Generate Diagram

```http
POST /api/v1/drawings/generate
Content-Type: application/json
Authorization: Bearer {token}

{
  "description": "Three tier architecture with web, api, and database layers",
  "diagram_type": "architecture",  -- Options: architecture, flowchart, mindmap, wireframe, sequence, erd
  "style": "default"               -- Optional: default, minimal, colorful
}
```

**Current Status:** Returns `501 Not Implemented`

**Available diagram types:**
- `architecture` - System architecture diagrams
- `flowchart` - Process and decision flows
- `mindmap` - Mind mapping
- `wireframe` - UI/UX wireframes
- `sequence` - Sequence diagrams
- `erd` - Entity relationship diagrams

## Frontend Usage

### Drawing Page Component

The dedicated Drawing page at `/drawing` provides a full-featured Excalidraw editor.

**Features:**
- Sidebar with tree navigation (folders + drawings)
- Search functionality
- Create/delete drawings
- Rename drawings with live editing
- Save with optimistic locking
- Unsaved changes indicator

**Component:** `frontend/src/pages/Drawing.tsx`

```typescript
import { Drawing } from '@/pages/Drawing';

// Rendered at: /drawing
```

**State Management:**

The page uses `useDrawingsStore` for state:

```typescript
import { useDrawingsStore } from '@/stores/useDrawingsStore';

function MyComponent() {
  const {
    tree,                    // DrawingTreeItem[]
    currentDrawing,          // Drawing | null
    isLoading,              // boolean
    isSaving,               // boolean
    error,                  // string | null
    fetchTree,              // (token: string) => Promise<void>
    fetchDrawing,           // (token: string, id: string) => Promise<void>
    createDrawing,          // (token: string, data: DrawingCreate) => Promise<Drawing | null>
    updateDrawing,          // (token: string, id: string, data: DrawingUpdate) => Promise<Drawing | null>
    deleteDrawing,          // (token: string, id: string) => Promise<boolean>
    updateThumbnail,        // (token: string, id: string, thumbnail: string) => Promise<boolean>
    search,                 // (token: string, query: string) => Promise<void>
  } = useDrawingsStore();
}
```

### Embedding in Notes with TipTap

The ExcalidrawBlock TipTap extension allows embedding drawings directly in notes.

**Component:** `frontend/src/components/editor/extensions/ExcalidrawBlock/`

#### Insert a Drawing Block

```typescript
import { useEditor } from '@tiptap/react';
import ExcalidrawBlock from '@/components/editor/extensions/ExcalidrawBlock';

function NoteEditor() {
  const editor = useEditor({
    extensions: [
      // ... other extensions
      ExcalidrawBlock,
    ],
  });

  // Insert a drawing block
  const insertDrawing = (drawingId: string) => {
    editor
      ?.chain()
      .focus()
      .insertExcalidrawBlock({
        drawingId,
        editMode: 'modal',    // or 'inline'
        width: 800,           // Optional
        height: 400,          // Optional
      })
      .run();
  };

  return <div>/* editor UI */</div>;
}
```

#### TipTap Extension: ExcalidrawBlock

The extension handles rendering and interaction of embedded drawings.

**Key features:**
- Lazy-loads Excalidraw to reduce bundle size
- Preview with thumbnail or placeholder
- Hover controls: Edit, Settings, Delete
- Settings panel for edit mode and dimensions
- Modal or inline editing modes

**Edit Modes:**

| Mode | Behavior | Use Case |
|------|----------|----------|
| `modal` | Opens drawing in new tab (separate window) | Large diagrams, dedicated focus |
| `inline` | Expands drawing within note for editing | Quick edits, embedded context |

**Node Attributes:**

```typescript
interface ExcalidrawBlockAttrs {
  drawingId: string;           // UUID of the drawing
  editMode: 'modal' | 'inline'; // How editing opens
  width: number;               // Container width (200-2000px)
  height: number;              // Container height (100-1500px)
}
```

#### Rendering States

The component handles four states:

1. **Loading:** Spinner while fetching drawing
2. **Error:** Red error box with removal option
3. **Editing (Inline):** Full Excalidraw canvas with Done button
4. **Preview (Default):** Thumbnail with hover controls

```typescript
// Example: Rendering in a note
<NodeViewWrapper>
  <div style={{ width: 800, height: 400 }}>
    {/* Thumbnail preview or error/loading state */}
    {isLoading && <Spinner />}
    {error && <ErrorBox onRemove={deleteNode} />}
    {drawing && <ThumbnailPreview drawing={drawing} />}
  </div>
</NodeViewWrapper>
```

## Type Definitions

### Core Types

```typescript
// Drawing entity
interface Drawing {
  id: string;
  title: string;
  description: string;
  elements: unknown[];                    // Excalidraw elements
  app_state: Record<string, unknown>;     // Canvas state
  files: Record<string, unknown>;         // Embedded images
  thumbnail: string | null;               // Base64 PNG
  version: number;                        // For optimistic locking
  parent_id: string | null;               // For hierarchy
  user_id: string;
  is_folder: boolean;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

// Request to create a drawing
interface DrawingCreate {
  title: string;
  description?: string;
  elements?: unknown[];
  app_state?: Record<string, unknown>;
  files?: Record<string, unknown>;
  parent_id?: string | null;
  is_folder?: boolean;
}

// Request to update a drawing
interface DrawingUpdate {
  title?: string;
  description?: string;
  elements?: unknown[];
  app_state?: Record<string, unknown>;
  files?: Record<string, unknown>;
  parent_id?: string | null;
  version: number;  // Required for conflict detection
}

// Tree item for navigation
interface DrawingTreeItem {
  id: string;
  title: string;
  parent_id: string | null;
  is_folder: boolean;
  children_count: number;
  thumbnail: string | null;
}

// Search result
interface DrawingSearchResult {
  id: string;
  title: string;
  description: string;
  thumbnail: string | null;
  score: number;
  is_folder: boolean;
}

// Backlink information
interface BacklinkInfo {
  id: string;
  title: string;
  type: 'note' | 'drawing';
  link_text: string | null;
  created_at: string;
}

// Embed tracking
interface NoteDrawingEmbed {
  id: string;
  note_id: string;
  drawing_id: string;
  edit_mode: 'modal' | 'inline';
  width: number;
  height: number;
  position: number;
  created_at: string;
}
```

## Development Patterns

### Optimistic Locking

Drawings use a `version` field to prevent concurrent edit conflicts.

**How it works:**

1. Client fetches drawing with `version: 5`
2. Client modifies and sends update with `version: 5`
3. Server increments to `version: 6` and returns success
4. If another client modified the drawing, server returns `409 Conflict`

**Implementation:**

```typescript
// Backend: app/services/drawings.py
def update_drawing(db, drawing_id, user_id, update: DrawingUpdate):
    drawing = db.query(Drawing).filter_by(id=drawing_id, user_id=user_id).first()
    if drawing.version != update.version:
        raise ValueError("Drawing modified by another session")

    # Apply updates
    drawing.version += 1
    db.commit()

// Frontend: useDrawingsStore
updateDrawing: async (token, id, data) => {
  try {
    const drawing = await drawingsApi.update(token, id, data);
    set({ currentDrawing: drawing });
  } catch (err) {
    if (err.message.includes('modified by another session')) {
      set({ error: 'Drawing was modified elsewhere. Please refresh.' });
    }
  }
}
```

### Full-Text Search

Drawings are searchable using PostgreSQL TSVECTOR for English-language content.

**How it works:**

1. A computed column `content_tsvector` automatically indexes title + description
2. Search API uses `@@ to_tsquery('english', ...)` for matching
3. Results include relevance scores

**SQL:**

```sql
-- Computed index (automatic)
ALTER TABLE drawings
ADD COLUMN content_tsvector tsvector
GENERATED ALWAYS AS (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))) STORED;

-- Search query
SELECT id, title, description, thumbnail, is_folder,
  ts_rank(content_tsvector, to_tsquery('english', 'architecture')) as score
FROM drawings
WHERE user_id = $1
  AND deleted_at IS NULL
  AND content_tsvector @@ to_tsquery('english', 'architecture')
ORDER BY score DESC
LIMIT 20;
```

### Thumbnail Generation

Thumbnails are base64-encoded PNG images generated client-side.

**Generation (Client):**

```typescript
import { Excalidraw } from '@excalidraw/excalidraw';

// In ExcalidrawCanvas component
const handleSave = async (elements, appState, files) => {
  // Excalidraw provides exportToBlob
  const blob = await (Excalidraw as any).exportToBlob({
    elements,
    appState,
    files,
    pixelRatio: 1,
  });

  const reader = new FileReader();
  reader.onload = (e) => {
    const base64 = e.target?.result as string;
    updateThumbnail(token, drawingId, base64);
  };
  reader.readAsDataURL(blob);
};
```

**Storage (Backend):**

Thumbnails are stored as base64 strings in the `thumbnail` TEXT column.

```python
# app/models/drawing.py
thumbnail = Column(Text, nullable=True)  # Base64 PNG string

# Storage example:
drawing.thumbnail = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA..."
db.commit()
```

## Common Tasks

### Create a Drawing Programmatically

```typescript
const drawingsApi = useDrawingsStore();

const drawing = await drawingsApi.createDrawing(token, {
  title: "New Architecture Diagram",
  description: "System components and relationships",
  is_folder: false,
  parent_id: null,
});

if (drawing) {
  console.log(`Created drawing: ${drawing.id}`);
}
```

### Fetch a Drawing for Editing

```typescript
const { currentDrawing, fetchDrawing, isLoading } = useDrawingsStore();

// Fetch
await fetchDrawing(token, "550e8400-e29b-41d4-a716-446655440000");

// Use
if (currentDrawing) {
  console.log(currentDrawing.elements);  // Excalidraw elements
  console.log(currentDrawing.app_state); // Canvas state
}
```

### Save Changes with Optimistic Locking

```typescript
import { useDrawingsStore } from '@/stores/useDrawingsStore';

function DrawingEditor() {
  const { currentDrawing, updateDrawing, error } = useDrawingsStore();
  const [elements, setElements] = useState(currentDrawing?.elements || []);

  const handleSave = async () => {
    const result = await updateDrawing(token, currentDrawing.id, {
      title: currentDrawing.title,
      elements,
      version: currentDrawing.version, // Required!
    });

    if (!result && error?.includes('modified')) {
      // Conflict: reload and retry
      await fetchDrawing(token, currentDrawing.id);
    }
  };

  return <button onClick={handleSave}>Save</button>;
}
```

### Embed a Drawing in a Note

```typescript
import { useEditor } from '@tiptap/react';

function InsertDrawingButton({ drawingId }: { drawingId: string }) {
  const editor = useEditor();

  return (
    <button
      onClick={() => {
        editor
          ?.chain()
          .focus()
          .insertExcalidrawBlock({
            drawingId,
            editMode: 'inline',
            width: 600,
            height: 400,
          })
          .run();
      }}
    >
      Insert Drawing
    </button>
  );
}
```

### Search Drawings

```typescript
const { search, searchResults } = useDrawingsStore();

// Trigger search
await search(token, "architecture");

// Use results
console.log(searchResults);  // DrawingSearchResult[]
searchResults.forEach((result) => {
  console.log(`${result.title} (score: ${result.score})`);
});
```

### Organize with Folders

```typescript
// Create a folder
const folder = await createDrawing(token, {
  title: "Diagrams",
  is_folder: true,
});

// Move drawing into folder
await moveDrawing(token, drawingId, {
  new_parent_id: folder.id,
});

// Get folder structure
const tree = await fetchTree(token);  // Returns hierarchical structure
```

## Performance Considerations

### Bundle Size

Excalidraw (~2MB) is lazy-loaded using React.lazy():

```typescript
// Lazy load (~/2MB reduction in main bundle)
const Excalidraw = lazy(() =>
  import('@excalidraw/excalidraw').then((mod) => ({ default: mod.Excalidraw }))
);

// Use with Suspense
<Suspense fallback={<Spinner />}>
  <Excalidraw {...props} />
</Suspense>
```

**Impact:**
- Initial page load: ~2MB saved
- Drawing page: Loaded on demand
- Search/navigation: Instant

### Database Indexing

JSONB columns are efficiently stored; full-text search is indexed:

```sql
-- FTS index (fast search)
CREATE INDEX idx_drawings_content_tsvector ON drawings USING gin(content_tsvector);

-- Lookup indexes
CREATE INDEX idx_drawings_user_id ON drawings(user_id);
CREATE INDEX idx_drawings_parent_id ON drawings(parent_id);
CREATE INDEX idx_drawings_title ON drawings(title);
```

**Query optimization:**
- Tree queries: O(1) with parent_id index
- Search: O(log n) with TSVECTOR GIN index
- User filtering: O(1) with user_id index

### Caching Strategy

Frontend state is managed via Zustand with automatic refetching:

```typescript
// Tree is cached in memory
fetchTree(token);  // Sets to state

// Selective refresh on write
createDrawing() -> fetchTree()  // Refresh tree after creation
updateDrawing() -> Direct state update (no refetch unless title changed)
deleteDrawing() -> fetchTree()  // Refresh after deletion
```

## Extending the Feature

### Add Custom Metadata

Extend the Drawing model to store custom fields:

```python
# backend/app/models/drawing.py
class Drawing(Base):
    __tablename__ = "drawings"
    # ... existing fields
    tags = Column(JSONB, default=list)        # Add custom tags
    color_category = Column(String(20))        # Add category
    is_shared = Column(Boolean, default=False) # Add sharing flag
```

### Custom Export Formats

Implement export handlers:

```python
# backend/app/services/drawings.py
class DrawingsService:
    @staticmethod
    def export_as_svg(drawing: Drawing) -> str:
        """Export Excalidraw drawing as SVG."""
        # Use Excalidraw's exportToSvg or similar
        pass

    @staticmethod
    def export_as_png(drawing: Drawing) -> bytes:
        """Export as PNG with custom dimensions."""
        pass
```

### AI-Powered Features (Phase 6)

The `/api/v1/drawings/generate` endpoint is prepared for AI diagram generation:

```python
# Future implementation
@router.post("/generate", response_model=DiagramGenerateResponse)
def generate_diagram(
    request: DiagramGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate diagram from text using AI.

    Args:
        description: Text description of the diagram
        diagram_type: Type (architecture, flowchart, mindmap, wireframe, sequence, erd)
        style: Visual style (default, minimal, colorful)
    """
    # Call LLM to generate Excalidraw JSON
    # Create drawing with generated elements
    # Return drawing ID and status
```

## Troubleshooting

### Drawing Not Loading in Embed

**Symptoms:** Gray box with "Failed to load drawing"

**Causes:**
1. Drawing ID doesn't exist
2. User doesn't own the drawing
3. Network error

**Debug:**
```typescript
// Check API response
const response = await drawingsApi.get(token, drawingId);
console.log(response);  // Should return Drawing object

// Check permissions
// Verify drawing.user_id matches current user
```

### Version Conflict on Save

**Error:** "Drawing was modified elsewhere"

**Causes:** Two sessions editing simultaneously

**Resolution:**
1. Client automatically reloads drawing
2. User can retry after reviewing conflict
3. Implement manual merge UI (Phase 6)

### Thumbnail Not Generating

**Symptoms:** Thumbnail stays null after save

**Causes:**
1. Excalidraw.exportToBlob not available
2. FileReader.readAsDataURL failed
3. Server failed to store base64

**Debug:**
```typescript
// Client-side
const blob = await Excalidraw.exportToBlob({...});
console.log(blob);  // Should be Blob object

// Server-side
# Verify base64 string is valid
import base64
decoded = base64.b64decode(thumbnail_string)
```

### Search Results Empty

**Symptoms:** No search results for known drawing

**Causes:**
1. Drawing title/description doesn't match query
2. Drawing is soft-deleted (deleted_at is set)
3. FTS index not updated

**Debug:**
```sql
-- Check if drawing exists
SELECT id, title, deleted_at FROM drawings
WHERE title ILIKE '%architecture%';

-- Check FTS index
SELECT id, title, content_tsvector FROM drawings
WHERE id = '...';  -- Should have content_tsvector populated
```

## Future Enhancements

| Phase | Feature | Status |
|-------|---------|--------|
| 2.5 (Current) | Drawing CRUD + embedding | Complete |
| 3.0 | Collaborative editing (Yjs) | Planned |
| 4.0 | Drawing comments + annotations | Planned |
| 5.0 | AI diagram generation | Planned |
| 5.0 | SVG/PNG export | Planned |
| 6.0 | Diagram-to-code generation | Planned |

## Related Documentation

- [NEXUS Overview](./nexus.md)
- [Notes API Reference](../reference/api/)
- [TipTap Extensions](../developer-guide/tiptap-extensions.md) (when created)
- [Excalidraw Documentation](https://excalidraw.com/docs)

## Files Reference

| File | Purpose |
|------|---------|
| `backend/app/models/drawing.py` | Database models |
| `backend/app/schemas/drawing.py` | Pydantic schemas |
| `backend/app/routers/drawings.py` | API endpoints |
| `backend/app/services/drawings.py` | Business logic |
| `frontend/src/pages/Drawing.tsx` | Drawing editor page |
| `frontend/src/stores/useDrawingsStore.ts` | Zustand state |
| `frontend/src/components/editor/extensions/ExcalidrawBlock/` | TipTap integration |
| `frontend/src/types/excalidraw.types.ts` | TypeScript types |
