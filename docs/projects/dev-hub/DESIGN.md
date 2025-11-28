# Dev Hub - Design Document

**Design Decisions & Technical Rationale**

---

## 🎯 Problem Statement

### Current Pain Points

**Scattered Information:**
- Notes dans Obsidian local (pas collaboratif)
- Tasks dans GitHub Issues/Projects (pas lié aux notes)
- Documentation dans Markdown files (pas de recherche efficace)
- Knowledge connections invisibles (pas de graph view)

**Tool Fragmentation:**
- Notion pour docs → pas de graph 3D, pas self-hosted
- Linear pour tasks → pas de wiki intégré
- Obsidian pour graph → desktop-only, pas collaboratif
- ChatGPT pour AI → pas de context projet

**Result:**
- Context switching constant
- Information silos
- Duplicate work
- Slow onboarding

---

## 💡 Solution: Dev Hub

**One Portal to Rule Them All**

### Core Concept

Unifier **4 dimensions** du développement:

1. **Knowledge (Wiki)**
   - Hiérarchie de notes (tree structure)
   - Rich text editing (TipTap)
   - Wiki links `[[note]]` pour connexions
   - Backlinks panel

2. **Tasks (Kanban + Gantt)**
   - Visual task management (drag-drop)
   - Timeline planning (Gantt)
   - Link tasks → notes (context)
   - Comments threads

3. **Connections (Graph 2D/3D)**
   - Visualize knowledge network
   - Identify knowledge gaps
   - Find bridge concepts
   - Community detection

4. **Intelligence (AI)**
   - Context-aware assistant
   - Smart suggestions
   - Semantic search
   - Summarization

---

## 🏗️ Architecture Decisions

### Decision 1: Monorepo vs Separate Repo

**Chosen:** Monorepo dans EPCB-Tools (`apps/dev-hub/`)

**Rationale:**
- ✅ Shared infrastructure (PostgreSQL, Redis, Traefik)
- ✅ Shared backend patterns (FastAPI, multi-tenancy)
- ✅ Easier development (single Docker Compose)
- ⚠️ Risk: Coupling (but acceptable, both owned by us)

**Alternative Rejected:** Separate repo
- ❌ Duplicate infrastructure
- ❌ Harder to share code
- ❌ More complex deployment

---

### Decision 2: Editor Choice - TipTap

**Chosen:** TipTap

**Rationale:**
- ✅ Based on ProseMirror (battle-tested)
- ✅ Extensible (custom nodes pour wiki links)
- ✅ Collaborative editing support (Yjs integration)
- ✅ Markdown shortcuts natifs
- ✅ Headless (full UI control)

**Alternatives Rejected:**
- Slate: Plus complexe API, moins d'extensions
- Draft.js: Deprecated par Meta
- Quill: Moins flexible pour custom nodes
- Monaco: Trop "code editor", pas assez "rich text"

---

### Decision 3: Graph Visualization - react-force-graph

**Chosen:** react-force-graph-2d + react-force-graph-3d

**Rationale:**
- ✅ 2D et 3D du même auteur (API cohérente)
- ✅ Three.js under the hood (performant)
- ✅ Force-directed layout (comme InfraNodus)
- ✅ Interactive (click, drag, zoom)
- ✅ Customizable (node colors, sizes, labels)

**Alternatives Rejected:**
- Cytoscape.js: Excellent mais lourd, overkill pour notre use case
- Sigma.js: Bon pour 2D, pas de 3D natif
- D3.js direct: Trop low-level, long à implémenter
- Vis.js: Pas maintenu activement

---

### Decision 4: Collaboration - Yjs CRDT

**Chosen:** Yjs + y-websocket

**Rationale:**
- ✅ CRDT = conflict-free (vs OT qui peut avoir des conflits)
- ✅ TipTap integration native
- ✅ Offline-first (sync quand reconnecté)
- ✅ Provider flexibility (WebSocket, WebRTC, IndexedDB)
- ✅ Battle-tested (utilisé par Figma, CodeSandbox)

**Alternatives Rejected:**
- ShareDB (OT): Plus complexe, conflits possibles
- Automerge: Encore expérimental, moins d'intégrations
- Firebase Realtime: Vendor lock-in, coûteux à scale

---

### Decision 5: AI Provider - Claude (Anthropic)

**Chosen:** Claude 3.5 Sonnet via Anthropic API

**Rationale:**
- ✅ Meilleure compréhension de code (vs GPT-4)
- ✅ Longer context window (200k tokens)
- ✅ Streaming support (meilleure UX)
- ✅ Moins de refusals que GPT-4
- ✅ System prompts puissants

**Alternatives:**
- GPT-4 (OpenAI): Backup option si budget contraint
- Gemini Pro: Expérimental, APIs moins stables
- Local LLM (Ollama): Trop lent pour real-time chat

**Fallback Strategy:**
Support multi-provider via abstraction:
```python
class AIService(ABC):
    @abstractmethod
    async def chat(self, message: str, context: dict):
        pass

class ClaudeAIService(AIService):
    # Implementation

class GPTAIService(AIService):
    # Implementation
```

---

### Decision 6: State Management - Zustand

**Chosen:** Zustand pour UI state

**Rationale:**
- ✅ Lightweight (3kb)
- ✅ Simple API (vs Redux boilerplate)
- ✅ TypeScript natif
- ✅ No Provider hell (vs Context API)
- ✅ DevTools support

**Alternatives Rejected:**
- Redux Toolkit: Trop de boilerplate pour nos besoins
- MobX: Moins TypeScript-friendly
- Jotai/Recoil: Atom-based, plus complexe pour notre use case

**Server State:** TanStack React Query (déjà utilisé)
- Séparation claire: Zustand = UI state, React Query = server state

---

### Decision 7: Component Library - shadcn/ui

**Chosen:** shadcn/ui (Radix UI + Tailwind)

**Rationale:**
- ✅ Copy-paste components (vs NPM dependency hell)
- ✅ Full customization (nous possédons le code)
- ✅ Accessible (Radix UI base)
- ✅ Tailwind native (cohérent avec design system)
- ✅ Dark mode natif

**Alternatives Rejected:**
- Material UI: Trop opinionated, lourd
- Ant Design: Style chinois, pas notre esthétique
- Chakra UI: Moins performant que Tailwind
- Headless UI: Moins de components out-of-box

---

### Decision 8: Database Schema - PostgreSQL + JSONB

**Chosen:** PostgreSQL avec JSONB pour note content

**Rationale:**
- ✅ JSONB = flexible schema pour TipTap content
- ✅ JSONB indexable (GIN index pour search)
- ✅ tsvector pour full-text search (natif)
- ✅ Transactions ACID (vs MongoDB)
- ✅ Relations (notes ↔ tasks)

**Schema Design:**
```sql
-- Flexible: content JSONB (TipTap format)
-- Searchable: content_text + content_search tsvector
-- Relational: note_links table (many-to-many)

CREATE TABLE notes (
    id UUID PRIMARY KEY,
    content JSONB NOT NULL,           -- Rich content
    content_text TEXT,                 -- Plain text extract
    content_search TSVECTOR,           -- Search index
    INDEX idx_search USING gin(content_search)
);
```

**Alternatives Rejected:**
- MongoDB: Pas de relations fortes, pas de full-text natif
- MySQL: JSON support moins mature
- SQLite: Pas de production-ready pour multi-user

---

### Decision 9: Graph Backend - NetworkX

**Chosen:** NetworkX (Python) pour graph algorithms

**Rationale:**
- ✅ Industry standard (utilisé par InfraNodus)
- ✅ Tous les algorithmes dont on a besoin:
  - Centrality: degree, betweenness, closeness, PageRank
  - Community detection: Louvain (via python-louvain)
  - Path finding: shortest path, all paths
- ✅ Pure Python (intègre bien avec FastAPI)
- ✅ Documentation exhaustive

**Alternatives Rejected:**
- Graph databases (Neo4j): Overkill, overhead maintenance
- In-database (PostgreSQL pgRouting): Limité pour analytics
- JavaScript (Graphology): Servir du JS depuis Python = complexe

**Performance Strategy:**
- Cache graph en Redis (evict on note/task change)
- Compute async (Celery background job)
- Incremental updates (recalculate only changed subgraph)

---

### Decision 10: Real-time Architecture - Socket.io

**Chosen:** Socket.io (pas native WebSocket)

**Rationale:**
- ✅ Fallback automatique (WebSocket → long-polling)
- ✅ Rooms support (project_id based)
- ✅ Python integration (python-socketio)
- ✅ Reconnection automatique
- ✅ Broadcast helpers

**Alternatives Rejected:**
- Native WebSocket: Pas de fallback, manual reconnection
- Server-Sent Events (SSE): Unidirectional, limité
- gRPC streaming: Overkill, complexe pour browser

---

## 🎨 Design Principles

### 1. Local-First (where possible)

**Approach:**
- Notes content stocké localement (IndexedDB)
- Sync to server périodique
- Offline editing possible
- Conflict resolution via Yjs CRDT

**Rationale:** Vitesse + resilience

### 2. Progressive Enhancement

**Layers:**
1. **Core:** Wiki + Tasks (fonctionne sans JS)
2. **Enhanced:** Real-time collab (requires WebSocket)
3. **Advanced:** Graph 3D (requires WebGL)
4. **AI:** Chatbot (requires API key)

**Rationale:** Accessible même si features avancées fail

### 3. Mobile-Friendly (Future)

**Current:** Desktop-first
**Phase 2:** Responsive design
**Phase 3:** Native mobile app (React Native)

**Rationale:** Start where users are (desktop), expand later

---

## 📊 Data Model

### Entity Relationship Diagram

```
┌─────────────┐
│   Project   │
└──────┬──────┘
       │
       ├──────────┬──────────┬──────────┐
       ↓          ↓          ↓          ↓
   ┌───────┐  ┌──────┐  ┌─────────┐  ┌──────┐
   │ Notes │  │Tasks │  │Roadmap  │  │Users │
   └───┬───┘  └──┬───┘  └─────────┘  └───┬──┘
       │         │                        │
       ↓         ↓                        ↓
  ┌──────────┐  │                   ┌─────────┐
  │NoteLinks │  └──────────────────→│Comments │
  └──────────┘                      └─────────┘
```

### Key Relationships

**Notes ↔ Notes (via NoteLinks):**
- Type: Many-to-Many
- Link types: wiki-link, reference, embed
- Directed graph (from → to)

**Tasks → Notes:**
- Type: Many-to-One (optional)
- Relationship: linked_note_id

**Tasks → Users:**
- Type: Many-to-One (optional)
- Relationship: assignee_id

**Notes/Tasks → Comments:**
- Type: One-to-Many
- Polymorphic (commentable_type + commentable_id)

---

## 🔍 Search Strategy

### Multi-Level Search

**Level 1: Full-Text Search (PostgreSQL tsvector)**
- Query: `SELECT * FROM notes WHERE content_search @@ plainto_tsquery('keyword')`
- Ranking: `ts_rank(content_search, query)`
- Speed: ~10ms for 10k notes

**Level 2: Semantic Search (Future)**
- Embeddings: OpenAI text-embedding-3-small
- Vector DB: pgvector extension
- Similarity: cosine distance
- Use case: "Find notes similar to this concept"

**Level 3: Graph-based Search (Future)**
- Algorithm: Personalized PageRank from query node
- Use case: "Find notes related to X via knowledge graph"

### Search UI

**Command Palette (Cmd+K):**
```
┌────────────────────────────────────┐
│ 🔍 Search...                       │
├────────────────────────────────────┤
│ Notes                              │
│ ├─ "Architecture Decision 001"    │
│ └─ "Database Schema"               │
├────────────────────────────────────┤
│ Tasks                              │
│ ├─ "Implement graph 3D"            │
│ └─ "Setup CI/CD"                   │
├────────────────────────────────────┤
│ Commands                           │
│ ├─ Create new note                 │
│ └─ Switch to graph view            │
└────────────────────────────────────┘
```

---

## 🚀 Performance Targets

### Frontend

| Metric | Target | Strategy |
|--------|--------|----------|
| **First Load** | <3s | Code splitting, lazy routes |
| **Editor Open** | <200ms | Virtualized tree, lazy content |
| **Graph Render** | <1s (1000 nodes) | WebGL, throttle updates |
| **Search** | <100ms | Debounce input, index backend |

### Backend

| Metric | Target | Strategy |
|--------|--------|----------|
| **API Latency** | <100ms (p95) | Redis cache, DB indexes |
| **Graph Build** | <5s (10k nodes) | Incremental, background job |
| **WebSocket Latency** | <50ms | Direct connection, no proxy |

### Database

| Metric | Target | Strategy |
|--------|--------|----------|
| **Note Query** | <10ms | Index on project_id, parent_id |
| **Search Query** | <50ms | GIN index on tsvector |
| **Graph Query** | <200ms | Materialized view, cache |

---

## 🔐 Security Considerations

### Authentication

**Method:** JWT tokens (existing Synapse backend)
- Access token: 15min expiry
- Refresh token: 7 days expiry
- HttpOnly cookies (XSS protection)

### Authorization

**Multi-Tenancy:** project_id filter on ALL queries
```python
@router.get("/notes")
async def list_notes(
    project_id: UUID = Depends(get_current_project)  # Auto-injected
):
    # ALWAYS filter by project_id
    return db.query(Note).filter(Note.project_id == project_id).all()
```

### Data Privacy

**Sensitive Data:**
- Note content: encrypted at rest (PostgreSQL encryption)
- AI chat history: separate table, auto-purge after 30 days
- User emails: hashed before storage

### WebSocket Security

**Authentication:**
```python
@sio.on('connect')
async def handle_connect(sid, environ, auth):
    token = auth.get('token')
    user = verify_jwt(token)
    if not user:
        raise ConnectionRefusedError('Invalid token')

    # Store user context
    sio.save_session(sid, {'user_id': user.id})
```

---

## 🧪 Testing Strategy

### Unit Tests (>70% coverage)

**Backend:**
```python
# pytest
def test_create_note():
    note = create_note(NoteCreate(title="Test", content={}))
    assert note.id is not None
    assert note.title == "Test"

def test_extract_wiki_links():
    content = {"type": "doc", "content": [{"text": "[[link]]"}]}
    links = extract_wiki_links(content)
    assert "link" in links
```

**Frontend:**
```typescript
// vitest + testing-library
describe('NoteEditor', () => {
  it('should render', () => {
    render(<NoteEditor noteId="123" />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('should save on input', async () => {
    const { user } = render(<NoteEditor noteId="123" />);
    await user.type(screen.getByRole('textbox'), 'Hello');
    await waitFor(() => expect(mockSave).toHaveBeenCalled());
  });
});
```

### Integration Tests

**API:**
```python
def test_note_workflow(client):
    # Create
    response = client.post("/notes", json={"title": "Test"})
    note_id = response.json()["id"]

    # Update
    response = client.patch(f"/notes/{note_id}", json={"content": {}})
    assert response.status_code == 200

    # Get
    response = client.get(f"/notes/{note_id}")
    assert response.json()["title"] == "Test"

    # Delete
    response = client.delete(f"/notes/{note_id}")
    assert response.status_code == 200
```

### E2E Tests (Playwright)

```typescript
test('create note and link', async ({ page }) => {
  // Login
  await page.goto('/login');
  await page.fill('[name=email]', 'test@example.com');
  await page.fill('[name=password]', 'password');
  await page.click('button[type=submit]');

  // Create note
  await page.click('text=New Note');
  await page.fill('[role=textbox]', 'This is a [[link]]');
  await page.waitForSelector('text=link', { state: 'visible' });

  // Verify link created
  await page.click('text=link');
  await expect(page).toHaveURL(/\/notes\/.*/);
});
```

---

## 📈 Analytics & Monitoring

### Metrics to Track

**Usage:**
- Notes created/day
- Tasks completed/day
- Graph views/day
- AI queries/day

**Performance:**
- API latency (p50, p95, p99)
- Graph render time
- Search latency
- WebSocket connection time

**Errors:**
- API error rate
- WebSocket disconnections
- AI API failures
- Database query failures

### Tools

**Backend:**
- Prometheus (metrics collection)
- Grafana (visualization)
- Sentry (error tracking)

**Frontend:**
- Web Vitals (Core Web Vitals)
- PostHog (product analytics)
- LogRocket (session replay)

---

## 🔮 Future Enhancements

### Phase 7+ (Post-Launch)

**Integrations:**
- GitHub (PR → task, commit → note)
- Slack (notifications)
- Email (Outlook, Gmail sync)
- MS Teams (chat archive)

**AI Enhancements:**
- Voice input (Whisper API)
- Image generation (DALL-E in notes)
- Code completion (Copilot-like)
- Meeting transcription (Whisper → notes)

**Mobile:**
- React Native app
- Offline-first mobile
- Push notifications

**Enterprise:**
- SAML/SSO auth
- Audit logs
- Admin dashboard
- Usage quotas

---

**Version:** 0.1.0
**Last Updated:** 2025-11-26
**Status:** Design Phase → Moving to Implementation
