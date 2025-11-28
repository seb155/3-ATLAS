# Dev Hub - Plan d'Implémentation Détaillé

**Vision:** Portail de Développement Unifié (Notes + Wiki + Tasks + AI + Graph 3D)

**Status:** ✅ Validé - Full Vision avec 3D InfraNodus
**Timeline:** 6 mois (2 devs parallèle) | 12 mois (solo)
**Start Date:** Nov 2025 (parallèle avec Synapse MVP)
**Target:** Juillet 2026

---

## 🎯 Scope Validé

### Features Incluses (Full Vision)

**Priority 1 (Crit

iques):**
- ✅ Notes/Wiki hiérarchiques (TipTap editor)
- ✅ Kanban board (drag-drop tasks)
- ✅ Gantt chart (timeline roadmap)
- ✅ **Graph 2D/3D avec InfraNodus features**
  - Force-directed 2D view
  - WebGL 3D visualization
  - Advanced filtering (betweenness, PageRank, degree)
  - Community detection (Louvain algorithm)
  - Gap analysis + path finder
  - Time-series animation
- ✅ Recherche universelle (Cmd+K command palette)

**Priority 2 (Importantes):**
- ✅ AI Chatbot global (Claude API)
- ✅ Collaboration real-time (TipTap + Yjs CRDT)

**Priority 3 (Nice-to-have - Phase 7):**
- 🔜 Notifications + Activity feed
- 🔜 Email integration (Outlook/Gmail)
- 🔜 MS Teams integration

---

## 📊 Timeline & Phases

### Phase 1: Fondations UI & Infrastructure (2-3 semaines)

**Objectif:** Setup technique de base pour toutes les features

**Backend Tasks:**
1. **Database Schema** (3-4 jours)
   ```sql
   -- Tables principales
   CREATE TABLE notes (
     id UUID PRIMARY KEY,
     project_id UUID NOT NULL,
     parent_id UUID REFERENCES notes(id),
     title VARCHAR(255) NOT NULL,
     content JSONB NOT NULL,  -- TipTap format
     content_text TEXT,       -- Plain text for search
     content_search TSVECTOR, -- Full-text index
     created_by UUID NOT NULL,
     created_at TIMESTAMP DEFAULT NOW(),
     updated_at TIMESTAMP DEFAULT NOW()
   );

   CREATE TABLE note_links (
     id UUID PRIMARY KEY,
     from_note_id UUID NOT NULL REFERENCES notes(id),
     to_note_id UUID NOT NULL REFERENCES notes(id),
     link_type VARCHAR(50) DEFAULT 'wiki-link'
   );

   CREATE TABLE tasks (
     id UUID PRIMARY KEY,
     project_id UUID NOT NULL,
     title VARCHAR(500) NOT NULL,
     description JSONB,
     status VARCHAR(50) DEFAULT 'backlog',
     priority VARCHAR(20),
     assignee_id UUID,
     due_date DATE,
     linked_note_id UUID REFERENCES notes(id)
   );
   ```

2. **Alembic Migration** (1 jour)
   ```bash
   cd apps/synapse/backend
   alembic revision -m "add dev hub tables (notes, tasks, roadmap)"
   ```

3. **WebSocket Setup** (2-3 jours)
   - Socket.io server
   - JWT auth middleware
   - File: `app/websocket/manager.py`

**Frontend Tasks:**
1. **shadcn/ui Setup** (1 jour)
   ```bash
   cd apps/dev-hub  # ou apps/portal
   npx shadcn@latest init
   ```
   - Add components: Button, Input, Dialog, Card, Tabs, Dropdown

2. **Zustand Stores** (2 jours)
   ```typescript
   // src/stores/useAppStore.ts
   export const useAppStore = create<AppState>()((set) => ({
     sidebarOpen: true,
     theme: 'dark',
     currentView: 'notes',
     toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen }))
   }));

   // src/stores/useEditorStore.ts
   export const useEditorStore = create<EditorState>()((set) => ({
     currentNoteId: null,
     editor: null,
     isEditing: false,
     setEditor: (editor) => set({ editor })
   }));
   ```

3. **Form Components** (2 jours)
   - react-hook-form + Zod setup
   - Reusable FormField component

4. **Command Palette** (2 jours)
   ```typescript
   // src/features/search/CommandPalette.tsx
   import { Command } from 'cmdk';

   export function CommandPalette() {
     // Cmd+K trigger
     // Search notes, tasks, commands
   }
   ```

**Testing:**
- DB migration tests
- Store unit tests
- Component smoke tests

**Deliverable:** Infrastructure ready for features

---

### Phase 2: Notes / Wiki System (3-4 semaines)

**Objectif:** Notes hiérarchiques avec éditeur riche

**Backend Tasks:**
1. **Notes API** (4-5 jours)
   ```python
   # app/api/endpoints/notes.py

   @router.get("/", response_model=List[NoteResponse])
   async def list_notes(
       project_id: UUID = Depends(get_current_project),
       parent_id: Optional[UUID] = None
   ):
       """List notes in tree structure"""
       pass

   @router.post("/", response_model=NoteResponse)
   async def create_note(note: NoteCreate):
       """Create new note"""
       pass

   @router.patch("/{note_id}", response_model=NoteResponse)
   async def update_note(note_id: UUID, note: NoteUpdate):
       """Update note content (auto-save)"""
       pass

   @router.get("/{note_id}/backlinks")
   async def get_backlinks(note_id: UUID):
       """Get notes linking to this note"""
       pass
   ```

2. **Link Parsing Service** (2-3 jours)
   ```python
   # app/services/note_service.py
   import re

   def extract_wiki_links(content: dict) -> List[str]:
       """Extract [[wiki-links]] from TipTap JSON"""
       # Parse JSON blocks recursively
       # Find [[link]] patterns
       # Return list of linked note titles
       pass

   async def update_note_links(note_id: UUID, content: dict):
       """Update note_links table based on content"""
       links = extract_wiki_links(content)
       # Delete old links
       # Create new links
       pass
   ```

3. **Full-Text Search** (2 jours)
   ```sql
   -- Trigger for auto-updating tsvector
   CREATE TRIGGER notes_search_update
   BEFORE INSERT OR UPDATE ON notes
   FOR EACH ROW EXECUTE FUNCTION
   tsvector_update_trigger(content_search, 'pg_catalog.english', content_text);

   -- Search query
   SELECT * FROM notes
   WHERE content_search @@ plainto_tsquery('english', 'search term')
   ORDER BY ts_rank(content_search, plainto_tsquery('english', 'search term')) DESC;
   ```

**Frontend Tasks:**
1. **TipTap Editor** (5-7 jours)
   ```typescript
   // src/features/notes/NoteEditor.tsx
   import { useEditor, EditorContent } from '@tiptap/react';
   import StarterKit from '@tiptap/starter-kit';
   import Link from '@tiptap/extension-link';
   import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';

   export function NoteEditor({ noteId }: { noteId: string }) {
     const editor = useEditor({
       extensions: [
         StarterKit,
         Link,
         CodeBlockLowlight,
         // Custom [[wiki-link]] extension
       ],
       content: initialContent,
       onUpdate: ({ editor }) => {
         // Debounced auto-save
         debouncedSave(editor.getJSON());
       }
     });

     return <EditorContent editor={editor} />;
   }
   ```

2. **Note Tree Sidebar** (4-5 jours)
   ```typescript
   // src/features/notes/NoteTree.tsx
   import { Tree } from '@dnd-kit/sortable';

   export function NoteTree() {
     const { data: notes } = useNotes();

     // Recursive tree rendering
     // Drag-drop to reorder
     // Create/delete/rename inline
   }
   ```

3. **Wiki Link Component** (3-4 jours)
   ```typescript
   // TipTap extension for [[links]]
   import { Node } from '@tiptap/core';

   export const WikiLink = Node.create({
     name: 'wikiLink',
     group: 'inline',
     inline: true,
     atom: true,

     addAttributes() {
       return {
         target: { default: null },
         label: { default: null }
       };
     },

     parseHTML() {
       return [{ tag: 'span[data-wiki-link]' }];
     },

     renderHTML({ HTMLAttributes }) {
       return ['span', { ...HTMLAttributes, 'data-wiki-link': '' }];
     },

     addInputRules() {
       return [{
         find: /\[\[([^\]]+)\]\]/,
         handler: ({ state, range, match }) => {
           // Create wiki link node
         }
       }];
     }
   });
   ```

**Testing:**
- Editor component tests
- CRUD API tests
- Link parsing tests
- Search accuracy tests

**Deliverable:** Wiki fonctionnel avec hiérarchie + backlinks

---

### Phase 3: Task Management + Kanban (3-4 semaines)

**Objectif:** Gestion tâches avec Kanban board

**Backend Tasks:**
1. **Tasks API** (5-6 jours)
   ```python
   # app/api/endpoints/tasks.py

   @router.get("/", response_model=List[TaskResponse])
   async def list_tasks(
       project_id: UUID = Depends(get_current_project),
       status: Optional[str] = None,
       assignee_id: Optional[UUID] = None
   ):
       """List tasks with filters"""
       pass

   @router.post("/{task_id}/move")
   async def move_task(task_id: UUID, new_status: str):
       """Change task status (kanban column)"""
       pass

   @router.post("/{task_id}/comments")
   async def add_comment(task_id: UUID, comment: CommentCreate):
       """Add comment to task"""
       pass
   ```

**Frontend Tasks:**
1. **Kanban Board** (5-7 jours)
   ```typescript
   // src/features/tasks/KanbanBoard.tsx
   import { DndContext, DragOverlay } from '@dnd-kit/core';
   import { SortableContext } from '@dnd-kit/sortable';

   export function KanbanBoard() {
     const [activeId, setActiveId] = useState(null);
     const { data: tasks } = useTasks();

     const columns = ['backlog', 'todo', 'in_progress', 'done'];

     function handleDragEnd(event) {
       const { active, over } = event;
       // Update task status via API
       moveTaskMutation.mutate({
         taskId: active.id,
         newStatus: over.id
       });
     }

     return (
       <DndContext onDragEnd={handleDragEnd}>
         {columns.map((column) => (
           <KanbanColumn key={column} status={column}>
             {tasks.filter(t => t.status === column).map(task => (
               <TaskCard key={task.id} task={task} />
             ))}
           </KanbanColumn>
         ))}
       </DndContext>
     );
   }
   ```

2. **Task Detail Panel** (4-5 jours)
   - Slide-out from right
   - Edit title, description (rich text)
   - Assign users, labels, due date
   - Comments thread
   - Link to notes

**Deliverable:** Kanban board fonctionnel

---

### Phase 4: Roadmap + Gantt Chart (2-3 semaines)

**Objectif:** Vue timeline pour planification

**Frontend Tasks:**
1. **Gantt Chart** (6-8 jours)
   ```typescript
   // src/features/roadmap/GanttChart.tsx
   import { Gantt, Task } from 'gantt-task-react';
   import 'gantt-task-react/dist/index.css';

   export function GanttChart() {
     const { data: tasks } = useTasks();
     const { data: milestones } = useMilestones();

     const ganttTasks: Task[] = [
       ...milestones.map(m => ({
         id: m.id,
         name: m.name,
         start: new Date(m.start_date),
         end: new Date(m.end_date),
         type: 'project'
       })),
       ...tasks.map(t => ({
         id: t.id,
         name: t.title,
         start: new Date(t.start_date || Date.now()),
         end: new Date(t.due_date),
         type: 'task',
         project: t.milestone_id
       }))
     ];

     return <Gantt tasks={ganttTasks} />;
   }
   ```

**Deliverable:** Roadmap avec Gantt chart

---

### Phase 5: Graph 2D/3D + InfraNodus Features (4-5 semaines)

**Objectif:** Visualisation graph avancée comme InfraNodus

**Backend Tasks:**
1. **Graph Builder Service** (6-8 jours)
   ```python
   # app/services/graph_builder.py
   import networkx as nx
   from community import community_louvain

   class GraphBuilder:
       def build_graph(self, project_id: UUID) -> nx.Graph:
           """Build graph from notes and tasks"""
           G = nx.Graph()

           # Add nodes (notes + tasks)
           notes = await get_notes(project_id)
           for note in notes:
               G.add_node(note.id, type='note', label=note.title)

           # Add edges (links)
           links = await get_note_links(project_id)
           for link in links:
               G.add_edge(link.from_note_id, link.to_note_id)

           return G

       def calculate_metrics(self, G: nx.Graph) -> dict:
           """Calculate network metrics"""
           return {
               'degree_centrality': nx.degree_centrality(G),
               'betweenness_centrality': nx.betweenness_centrality(G),
               'pagerank': nx.pagerank(G),
               'clustering': nx.clustering(G)
           }

       def detect_communities(self, G: nx.Graph) -> dict:
           """Detect communities using Louvain"""
           partition = community_louvain.best_partition(G)
           return partition
   ```

2. **Graph API** (4-5 jours)
   ```python
   # app/api/endpoints/graph.py

   @router.get("/data")
   async def get_graph_data(
       project_id: UUID = Depends(get_current_project),
       node_types: Optional[List[str]] = Query(None),
       min_degree: Optional[int] = None,
       keywords: Optional[str] = None
   ):
       """Get graph data with filters"""
       G = graph_builder.build_graph(project_id)

       # Apply filters
       if node_types:
           G = filter_by_type(G, node_types)
       if min_degree:
           G = filter_by_degree(G, min_degree)

       metrics = graph_builder.calculate_metrics(G)
       communities = graph_builder.detect_communities(G)

       return {
           'nodes': [{'id': n, **data, 'metrics': metrics[n]} for n, data in G.nodes(data=True)],
           'edges': [{'source': u, 'target': v} for u, v in G.edges()],
           'communities': communities
       }
   ```

**Frontend Tasks:**
1. **Graph 2D View** (5-6 jours)
   ```typescript
   // src/features/graph/Graph2DView.tsx
   import ForceGraph2D from 'react-force-graph-2d';

   export function Graph2DView() {
     const { data } = useGraphData();

     return (
       <ForceGraph2D
         graphData={data}
         nodeLabel="label"
         nodeColor={node => getColorByType(node.type)}
         onNodeClick={handleNodeClick}
         linkDirectionalArrowLength={3.5}
       />
     );
   }
   ```

2. **Graph 3D View** (7-10 jours)
   ```typescript
   // src/features/graph/Graph3DView.tsx
   import ForceGraph3D from 'react-force-graph-3d';
   import * as THREE from 'three';

   export function Graph3DView() {
     const { data } = useGraphData();
     const graphRef = useRef();

     useEffect(() => {
       // Camera setup
       graphRef.current.cameraPosition({ z: 1000 });

       // Custom node rendering
       graphRef.current.nodeThreeObject(node => {
         const sprite = new SpriteText(node.label);
         sprite.color = getColorByType(node.type);
         sprite.textHeight = 8;
         return sprite;
       });
     }, []);

     return (
       <ForceGraph3D
         ref={graphRef}
         graphData={data}
         nodeAutoColorBy="type"
         onNodeClick={handleNodeClick}
         linkOpacity={0.5}
       />
     );
   }
   ```

3. **Filter Panel** (4-5 jours)
   ```typescript
   // src/features/graph/FilterPanel.tsx

   export function FilterPanel() {
     const [filters, setFilters] = useState({
       nodeTypes: ['notes', 'tasks'],
       minDegree: 0,
       minBetweenness: 0,
       keywords: ''
     });

     return (
       <div className="filter-panel">
         <h3>Filters</h3>

         <div className="filter-group">
           <label>Node Types</label>
           <Checkbox checked={filters.nodeTypes.includes('notes')}
                     onChange={() => toggleNodeType('notes')}>
             Notes
           </Checkbox>
           <Checkbox checked={filters.nodeTypes.includes('tasks')}
                     onChange={() => toggleNodeType('tasks')}>
             Tasks
           </Checkbox>
         </div>

         <div className="filter-group">
           <label>Min Connections: {filters.minDegree}</label>
           <Slider value={filters.minDegree}
                   onChange={setMinDegree}
                   min={0} max={20} />
         </div>

         <div className="filter-group">
           <label>Min Betweenness (Bridge Nodes)</label>
           <Slider value={filters.minBetweenness}
                   onChange={setMinBetweenness}
                   min={0} max={1} step={0.01} />
         </div>
       </div>
     );
   }
   ```

4. **Analytics Panel** (5-7 jours)
   ```typescript
   // src/features/graph/AnalyticsPanel.tsx

   export function AnalyticsPanel() {
     const { data: analytics } = useGraphAnalytics();

     return (
       <div className="analytics-panel">
         <h3>Network Metrics</h3>
         <div className="metric">
           <span>Total Nodes:</span>
           <strong>{analytics.nodeCount}</strong>
         </div>
         <div className="metric">
           <span>Total Edges:</span>
           <strong>{analytics.edgeCount}</strong>
         </div>
         <div className="metric">
           <span>Network Density:</span>
           <strong>{analytics.density.toFixed(3)}</strong>
         </div>

         <h4>Top Hubs (Most Connected)</h4>
         <ul>
           {analytics.topByDegree.map(node => (
             <li key={node.id}>
               {node.label} ({node.degree} connections)
             </li>
           ))}
         </ul>

         <h4>Bridge Nodes (High Betweenness)</h4>
         <ul>
           {analytics.topByBetweenness.map(node => (
             <li key={node.id}>
               {node.label} (betweenness: {node.betweenness.toFixed(3)})
             </li>
           ))}
         </ul>

         <h4>Communities Detected</h4>
         <div className="communities">
           {analytics.communities.map((community, idx) => (
             <div key={idx} className="community">
               <div className="community-color" style={{ background: getColor(idx) }} />
               <span>{community.nodeCount} nodes</span>
             </div>
           ))}
         </div>
       </div>
     );
   }
   ```

**Deliverable:** Graph 2D/3D avec features InfraNodus

---

### Phase 6: AI Chat + Collaboration (4-6 semaines)

**Objectif:** AI chatbot + real-time collaboration

**Backend Tasks (AI):**
1. **AI Service** (4-5 jours)
   ```python
   # app/services/ai_service.py
   from anthropic import Anthropic

   class AIService:
       def __init__(self):
           self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

       async def chat(
           self,
           message: str,
           context: dict,
           stream: bool = True
       ):
           """Send message to Claude with context"""
           system_prompt = self._build_context_prompt(context)

           if stream:
               async for chunk in self.client.messages.create_stream(
                   model="claude-3-5-sonnet-20241022",
                   max_tokens=2048,
                   system=system_prompt,
                   messages=[{"role": "user", "content": message}]
               ):
                   yield chunk
           else:
               response = await self.client.messages.create(
                   model="claude-3-5-sonnet-20241022",
                   max_tokens=2048,
                   system=system_prompt,
                   messages=[{"role": "user", "content": message}]
               )
               return response

       def _build_context_prompt(self, context: dict) -> str:
           """Build system prompt with project context"""
           return f"""You are an AI assistant helping with project "{context['project_name']}".

Current note: {context.get('current_note_title', 'N/A')}
Note content: {context.get('current_note_content', 'N/A')}
Related tasks: {context.get('related_tasks', [])}

Help the user with their request based on this context."""
   ```

**Frontend Tasks (AI):**
1. **AI Chat Panel** (4-5 jours)
   ```typescript
   // src/features/ai/AIChatPanel.tsx
   import { useState } from 'react';
   import { useEventSource } from '@/hooks/useEventSource';

   export function AIChatPanel() {
     const [messages, setMessages] = useState([]);
     const [input, setInput] = useState('');
     const [streaming, setStreaming] = useState(false);

     const sendMessage = async () => {
       const userMessage = { role: 'user', content: input };
       setMessages(prev => [...prev, userMessage]);
       setInput('');
       setStreaming(true);

       // Stream response
       const response = await fetch('/api/v1/chat/stream', {
         method: 'POST',
         body: JSON.stringify({
           message: input,
           context: {
             current_note_id: currentNoteId,
             project_id: projectId
           }
         })
       });

       const reader = response.body.getReader();
       const decoder = new TextDecoder();
       let assistantMessage = '';

       while (true) {
         const { done, value } = await reader.read();
         if (done) break;

         const chunk = decoder.decode(value);
         assistantMessage += chunk;
         setMessages(prev => [...prev.slice(0, -1), {
           role: 'assistant',
           content: assistantMessage
         }]);
       }

       setStreaming(false);
     };

     return (
       <div className="ai-chat-panel">
         <div className="messages">
           {messages.map((msg, idx) => (
             <div key={idx} className={`message ${msg.role}`}>
               {msg.content}
             </div>
           ))}
           {streaming && <div className="typing-indicator">...</div>}
         </div>

         <div className="input-area">
           <input
             value={input}
             onChange={(e) => setInput(e.target.value)}
             onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
             placeholder="Ask AI..."
           />
           <button onClick={sendMessage}>Send</button>
         </div>
       </div>
     );
   }
   ```

**Backend Tasks (Collaboration):**
1. **Yjs WebSocket Provider** (5-7 jours)
   ```python
   # app/websocket/yjs_provider.py
   import y_py as Y
   from socketio import AsyncServer

   class YjsProvider:
       def __init__(self):
           self.docs = {}  # doc_id -> Y.YDoc

       async def handle_update(self, sid, data):
           """Handle Yjs update from client"""
           doc_id = data['doc_id']
           update = data['update']

           # Get or create Y.YDoc
           if doc_id not in self.docs:
               self.docs[doc_id] = Y.YDoc()

           doc = self.docs[doc_id]

           # Apply update
           Y.apply_update(doc, update)

           # Broadcast to other clients
           await self.sio.emit('yjs_update', {
               'doc_id': doc_id,
               'update': update
           }, skip_sid=sid)

           # Persist to database
           await self.save_doc_state(doc_id, Y.encode_state_as_update(doc))
   ```

**Frontend Tasks (Collaboration):**
1. **Collaborative Editor** (7-10 jours)
   ```typescript
   // src/features/notes/CollaborativeEditor.tsx
   import { useEditor } from '@tiptap/react';
   import Collaboration from '@tiptap/extension-collaboration';
   import CollaborationCursor from '@tiptap/extension-collaboration-cursor';
   import * as Y from 'yjs';
   import { WebsocketProvider } from 'y-websocket';

   export function CollaborativeEditor({ noteId }: { noteId: string }) {
     const ydoc = useMemo(() => new Y.Doc(), []);
     const provider = useMemo(() => new WebsocketProvider(
       'ws://localhost:8001/ws/yjs',
       `note-${noteId}`,
       ydoc
     ), [noteId]);

     const editor = useEditor({
       extensions: [
         StarterKit,
         Collaboration.configure({
           document: ydoc
         }),
         CollaborationCursor.configure({
           provider,
           user: {
             name: currentUser.name,
             color: getRandomColor()
           }
         })
       ]
     });

     return <EditorContent editor={editor} />;
   }
   ```

**Deliverable:** AI chatbot + collaborative editing

---

## 📁 Structure du Projet

```
apps/dev-hub/  (ou apps/portal étendu)
├── frontend/
│   ├── src/
│   │   ├── features/
│   │   │   ├── notes/
│   │   │   │   ├── NotesPage.tsx
│   │   │   │   ├── NoteEditor.tsx
│   │   │   │   ├── NoteTree.tsx
│   │   │   │   ├── WikiLink.tsx
│   │   │   │   └── CollaborativeEditor.tsx
│   │   │   ├── tasks/
│   │   │   │   ├── TasksPage.tsx
│   │   │   │   ├── KanbanBoard.tsx
│   │   │   │   ├── TaskCard.tsx
│   │   │   │   └── TaskDetailPanel.tsx
│   │   │   ├── roadmap/
│   │   │   │   ├── RoadmapPage.tsx
│   │   │   │   ├── GanttChart.tsx
│   │   │   │   └── MilestoneForm.tsx
│   │   │   ├── graph/
│   │   │   │   ├── GraphPage.tsx
│   │   │   │   ├── Graph2DView.tsx
│   │   │   │   ├── Graph3DView.tsx
│   │   │   │   ├── FilterPanel.tsx
│   │   │   │   ├── AnalyticsPanel.tsx
│   │   │   │   └── PathFinder.tsx
│   │   │   ├── ai/
│   │   │   │   ├── AIChatPanel.tsx
│   │   │   │   └── AICommands.tsx
│   │   │   └── search/
│   │   │       └── CommandPalette.tsx
│   │   ├── stores/
│   │   │   ├── useAppStore.ts
│   │   │   ├── useEditorStore.ts
│   │   │   └── useTaskStore.ts
│   │   ├── components/
│   │   │   └── ui/  (shadcn/ui)
│   │   └── hooks/
│   │       ├── useNotes.ts
│   │       ├── useTasks.ts
│   │       ├── useGraphData.ts
│   │       └── useAutoSave.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.ts
└── backend/ (apps/synapse/backend extended)
    └── app/
        ├── api/endpoints/
        │   ├── notes.py
        │   ├── tasks.py
        │   ├── roadmap.py
        │   ├── graph.py
        │   ├── chat.py
        │   └── search.py
        ├── models/
        │   ├── note.py
        │   ├── task.py
        │   └── chat_message.py
        ├── services/
        │   ├── note_service.py
        │   ├── task_service.py
        │   ├── graph_builder.py
        │   ├── ai_service.py
        │   └── search_engine.py
        └── websocket/
            ├── manager.py
            └── yjs_provider.py
```

---

## 🚀 Next Steps

### Semaine 1 (Nov 26 - Dec 2)

**Setup Initial:**
1. [ ] Créer structure `apps/dev-hub/` (ou étendre `apps/portal/`)
2. [ ] Vite + React 19 + TypeScript init
3. [ ] shadcn/ui CLI init
4. [ ] Backend: Create DB schema draft

**Decision:**
- Monorepo dans EPCB-Tools? ✅ Recommandé
- Ou repo séparé? ⚠️ Complexifie sync

### Semaine 2 (Dec 2-9)

**Phase 1 Start:**
- [ ] Install shadcn/ui components
- [ ] Setup Zustand stores
- [ ] Backend: Alembic migration
- [ ] WebSocket setup skeleton

### Tracking

**GitHub Projects Board:**
- Backlog
- Todo
- In Progress
- In Review
- Done

**Milestones:**
- M1: Fondations (Sem 4)
- M2: Wiki MVP (Sem 8)
- M3: Tasks (Sem 12)
- M4: Roadmap (Sem 14)
- M5: Graph 2D/3D (Sem 20)
- M6: AI + Collab (Sem 26)

---

**Last Updated:** 2025-11-26
**Status:** Planning - Ready to Start
**Owner:** [@sgagn]
