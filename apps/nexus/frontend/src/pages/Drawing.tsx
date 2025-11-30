import { useEffect, useState, useCallback, lazy, Suspense, useRef } from 'react';
import '@excalidraw/excalidraw/index.css';
import {
  PenTool,
  Plus,
  Search,
  Folder,
  FolderOpen,
  ChevronRight,
  ChevronDown,
  Trash2,
  Save,
  Loader2,
  Image,
  PanelLeftClose,
  PanelLeftOpen,
  Maximize2,
  Minimize2,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useAuthStore } from '@/stores/useAuthStore';
import { useDrawingsStore } from '@/stores/useDrawingsStore';
import type { DrawingTreeItem } from '@/types/excalidraw.types';
import { cn } from '@/lib/utils';

// Lazy load Excalidraw to reduce initial bundle size (~2MB)
const Excalidraw = lazy(() =>
  import('@excalidraw/excalidraw').then((mod) => ({ default: mod.Excalidraw }))
);

// ============================================================================
// Tree Node Component
// ============================================================================

interface TreeNodeProps {
  item: DrawingTreeItem;
  allItems: DrawingTreeItem[];
  selectedId: string | null;
  expandedIds: Set<string>;
  onSelect: (id: string) => void;
  onToggle: (id: string) => void;
  onRename?: (id: string, newTitle: string) => Promise<void>;
  level?: number;
}

function TreeNode({
  item,
  allItems,
  selectedId,
  expandedIds,
  onSelect,
  onToggle,
  onRename,
  level = 0,
}: TreeNodeProps) {
  const children = allItems.filter((n) => n.parent_id === item.id);
  const hasChildren = children.length > 0 || item.is_folder;
  const isExpanded = expandedIds.has(item.id);
  const isSelected = selectedId === item.id;

  // Inline editing state
  const [isEditing, setIsEditing] = useState(false);
  const [editingTitle, setEditingTitle] = useState(item.title);

  const handleDoubleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!item.is_folder) {
      setIsEditing(true);
      setEditingTitle(item.title);
    }
  };

  const handleRename = async () => {
    if (editingTitle && editingTitle !== item.title && onRename) {
      await onRename(item.id, editingTitle);
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleRename();
    } else if (e.key === 'Escape') {
      setIsEditing(false);
      setEditingTitle(item.title);
    }
  };

  return (
    <div>
      <button
        onClick={() => {
          if (hasChildren) {
            onToggle(item.id);
          }
          onSelect(item.id);
        }}
        onDoubleClick={handleDoubleClick}
        className={cn(
          'w-full flex items-center gap-1 px-2 py-1.5 text-sm rounded-md',
          'hover:bg-muted transition-colors text-left',
          isSelected && 'bg-primary/10 text-primary'
        )}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        title={!item.is_folder ? 'Double-click to rename' : undefined}
      >
        {hasChildren ? (
          <span className="w-4 h-4 flex items-center justify-center">
            {isExpanded ? (
              <ChevronDown className="h-3 w-3" />
            ) : (
              <ChevronRight className="h-3 w-3" />
            )}
          </span>
        ) : (
          <span className="w-4" />
        )}
        {item.is_folder ? (
          isExpanded ? (
            <FolderOpen className="h-4 w-4 text-primary" />
          ) : (
            <Folder className="h-4 w-4 text-primary" />
          )
        ) : item.thumbnail ? (
          <img
            src={item.thumbnail}
            alt=""
            className="h-4 w-4 rounded object-cover"
          />
        ) : (
          <PenTool className="h-4 w-4 text-muted-foreground" />
        )}
        {isEditing ? (
          <input
            autoFocus
            value={editingTitle}
            onChange={(e) => setEditingTitle(e.target.value)}
            onBlur={handleRename}
            onKeyDown={handleKeyDown}
            onClick={(e) => e.stopPropagation()}
            className="flex-1 px-1 py-0.5 text-sm bg-background border border-primary rounded"
          />
        ) : (
          <span className="truncate flex-1">{item.title}</span>
        )}
        {item.children_count > 0 && !isEditing && (
          <span className="text-xs text-muted-foreground">{item.children_count}</span>
        )}
      </button>
      {isExpanded && children.length > 0 && (
        <div>
          {children.map((child) => (
            <TreeNode
              key={child.id}
              item={child}
              allItems={allItems}
              selectedId={selectedId}
              expandedIds={expandedIds}
              onSelect={onSelect}
              onToggle={onToggle}
              onRename={onRename}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Excalidraw Canvas Wrapper
// ============================================================================

interface ExcalidrawCanvasProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  initialData?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onChange?: (elements: any[], appState: any, files: any) => void;
}

function ExcalidrawCanvas({ initialData, onChange }: ExcalidrawCanvasProps) {
  // Library state management
  const [libraries, setLibraries] = useState<any[]>(() => {
    const saved = localStorage.getItem('excalidraw-libraries');
    return saved ? JSON.parse(saved) : [];
  });

  // Ref to access Excalidraw API methods like updateLibrary()
  // Required for programmatic library installation from libraries.excalidraw.com
  const excalidrawRef = useRef<any>(null);

  const handleLibraryChange = useCallback((items: any) => {
    localStorage.setItem('excalidraw-libraries', JSON.stringify(items));
    setLibraries(items);
  }, []);

  // Handle library installation from libraries.excalidraw.com
  // When user clicks "Add to Excalidraw", the browser redirects back with
  // hash parameters: #addLibrary=<libraryURL>&token=<token>
  // This effect listens for those parameters and installs the library
  useEffect(() => {
    const handleHashChange = async () => {
      // Parse URL hash to extract library URL
      const hash = new URLSearchParams(window.location.hash.slice(1));
      const libraryUrl = hash.get('addLibrary');

      if (libraryUrl && excalidrawRef.current) {
        try {
          // Install library via Excalidraw API
          await excalidrawRef.current.updateLibrary({
            libraryItems: libraryUrl,      // URL to fetch library from
            merge: true,                    // Merge with existing libraries
            prompt: true,                   // Show confirmation dialog
            openLibraryMenu: true,         // Auto-open library menu
          });
          // Clean up hash after successful installation
          window.location.hash = '';
        } catch (error) {
          console.error('Failed to install library:', error);
        }
      }
    };

    // Listen for hash changes (library browser redirect)
    window.addEventListener('hashchange', handleHashChange);

    // Also check on component mount in case hash already present
    handleHashChange();

    return () => {
      window.removeEventListener('hashchange', handleHashChange);
    };
  }, []);

  return (
    <div
      className="h-full w-full excalidraw-container"
      style={{
        isolation: 'isolate',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <Suspense
        fallback={
          <div
            className="flex items-center justify-center"
            style={{ height: '100%', width: '100%' }}
          >
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            <span className="ml-2 text-muted-foreground">Loading Excalidraw...</span>
          </div>
        }
      >
        <Excalidraw
          ref={excalidrawRef}
          initialData={initialData}
          onChange={onChange}
          theme="dark"
          libraryReturnUrl={`${window.location.origin}${window.location.pathname}`}
          onLibraryChange={handleLibraryChange}
        />
      </Suspense>
    </div>
  );
}

// ============================================================================
// Login Required Component
// ============================================================================

function LoginRequired() {
  return (
    <Card className="max-w-md mx-auto mt-12">
      <CardContent className="pt-6">
        <div className="text-center">
          <PenTool className="h-12 w-12 mx-auto text-primary mb-4" />
          <h2 className="text-xl font-bold">Sign in Required</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Please sign in from the Notes page to access drawings
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Main Drawing Page
// ============================================================================

export function Drawing() {
  const { isAuthenticated, token, user, logout } = useAuthStore();
  const {
    tree,
    currentDrawing,
    isLoading,
    isSaving,
    error,
    fetchTree,
    fetchDrawing,
    createDrawing,
    updateDrawing,
    updateThumbnail,
    deleteDrawing,
    setCurrentDrawing,
    clearError,
  } = useDrawingsStore();

  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [editedElements, setEditedElements] = useState<any[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [editedAppState, setEditedAppState] = useState<any>({});
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [editedFiles, setEditedFiles] = useState<any>({});
  const [editedTitle, setEditedTitle] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // UI states for sidebar and fullscreen
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() =>
    localStorage.getItem('drawing-sidebar-collapsed') === 'true'
  );
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Load tree on mount
  useEffect(() => {
    if (isAuthenticated && token) {
      fetchTree(token);
    }
  }, [isAuthenticated, token, fetchTree]);

  // Sync edited content with current drawing
  useEffect(() => {
    if (currentDrawing) {
      setEditedElements(currentDrawing.elements || []);
      setEditedAppState(currentDrawing.app_state || {});
      setEditedFiles(currentDrawing.files || {});
      setEditedTitle(currentDrawing.title);
      setHasUnsavedChanges(false);
    }
  }, [currentDrawing]);

  const handleToggle = useCallback((id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const handleSelect = useCallback(
    async (id: string) => {
      if (token) {
        await fetchDrawing(token, id);
      }
    },
    [token, fetchDrawing]
  );

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const handleCanvasChange = useCallback((elements: any[], appState: any, files: any) => {
    setEditedElements(elements);
    setEditedAppState(appState);
    setEditedFiles(files);
    setHasUnsavedChanges(true);
  }, []);

  const handleTitleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setEditedTitle(e.target.value);
    setHasUnsavedChanges(true);
  }, []);

  const handleSave = useCallback(async () => {
    if (!token || !currentDrawing) return;

    const result = await updateDrawing(token, currentDrawing.id, {
      title: editedTitle,
      elements: editedElements,
      app_state: editedAppState,
      files: editedFiles,
      version: currentDrawing.version,
    });

    if (result) {
      setHasUnsavedChanges(false);

      // Generate and save thumbnail asynchronously
      // Note: In production, you'd use Excalidraw's exportToBlob API
      // For now, we skip thumbnail generation
    }
  }, [token, currentDrawing, editedTitle, editedElements, editedAppState, editedFiles, updateDrawing]);

  const handleNewDrawing = useCallback(async () => {
    if (!token) return;

    const drawing = await createDrawing(token, {
      title: 'New Drawing',
      elements: [],
      app_state: {},
      files: {},
      is_folder: false,
    });

    if (drawing) {
      // Auto-select the newly created drawing
      await fetchDrawing(token, drawing.id);
    }
  }, [token, createDrawing, fetchDrawing]);

  const handleNewFolder = useCallback(async () => {
    if (!token) return;

    await createDrawing(token, {
      title: 'New Folder',
      elements: [],
      is_folder: true,
    });
  }, [token, createDrawing]);

  const handleDelete = useCallback(async () => {
    if (!token || !currentDrawing) return;

    if (window.confirm(`Delete "${currentDrawing.title}"?`)) {
      await deleteDrawing(token, currentDrawing.id);
    }
  }, [token, currentDrawing, deleteDrawing]);

  // Rename drawing from sidebar
  const handleRenameDrawing = useCallback(async (id: string, newTitle: string) => {
    if (!token) return;

    await updateDrawing(token, id, { title: newTitle });
    // Store automatically refreshes tree on title change (ligne 96)
  }, [token, updateDrawing]);

  // Toggle sidebar collapse
  const toggleSidebar = useCallback(() => {
    setIsSidebarCollapsed((prev) => {
      const newValue = !prev;
      localStorage.setItem('drawing-sidebar-collapsed', String(newValue));
      return newValue;
    });
  }, []);

  // Toggle fullscreen mode
  const toggleFullscreen = useCallback(() => {
    setIsFullscreen((prev) => !prev);
  }, []);

  // Keyboard shortcut for fullscreen (F key)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Only trigger if not typing in an input
      if (document.activeElement?.tagName === 'INPUT') return;

      if (e.key === 'f' || e.key === 'F') {
        e.preventDefault();
        toggleFullscreen();
      }
      if (e.key === 'Escape' && isFullscreen) {
        toggleFullscreen();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [toggleFullscreen, isFullscreen]);

  // Filter tree by search
  const filteredTree = searchQuery
    ? tree.filter((item) =>
        item.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : tree;

  const rootItems = filteredTree.filter((item) => !item.parent_id);

  if (!isAuthenticated) {
    return <LoginRequired />;
  }

  // Fullscreen mode - canvas only
  if (isFullscreen && currentDrawing) {
    return (
      <div className="fixed inset-0 z-50 bg-background">
        <div className="h-full flex flex-col">
          {/* Exit fullscreen button */}
          <button
            onClick={toggleFullscreen}
            className="absolute top-2 right-2 z-10 p-2 bg-background/80 backdrop-blur rounded hover:bg-muted transition-colors"
            title="Exit Fullscreen (F or Esc)"
          >
            <Minimize2 className="h-5 w-5" />
          </button>

          {/* Canvas plein écran */}
          <div className="flex-1">
            <ExcalidrawCanvas
              key={currentDrawing.id}
              initialData={{
                elements: editedElements,
                appState: editedAppState,
                files: editedFiles,
              }}
              onChange={handleCanvasChange}
            />
          </div>
        </div>
      </div>
    );
  }

  // Normal mode
  return (
    <div className="h-[calc(100vh-120px)] flex gap-4">
      {/* Sidebar */}
      <div
        className={cn(
          'flex-shrink-0 border-r border-border flex flex-col transition-all duration-300',
          isSidebarCollapsed ? 'w-12' : 'w-64'
        )}
      >
        {/* Header */}
        <div className="p-3 border-b border-border">
          {!isSidebarCollapsed ? (
            <>
              <div className="flex items-center justify-between mb-2">
                <h2 className="font-semibold">Drawings</h2>
                <div className="flex gap-1">
                  <button
                    onClick={handleNewDrawing}
                    className="p-1.5 hover:bg-muted rounded"
                    title="New Drawing"
                  >
                    <Plus className="h-4 w-4" />
                  </button>
                  <button
                    onClick={handleNewFolder}
                    className="p-1.5 hover:bg-muted rounded"
                    title="New Folder"
                  >
                    <Folder className="h-4 w-4" />
                  </button>
                  <button
                    onClick={toggleSidebar}
                    className="p-1.5 hover:bg-muted rounded"
                    title="Collapse sidebar"
                  >
                    <PanelLeftClose className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </>
          ) : (
            <button
              onClick={toggleSidebar}
              className="w-full p-1.5 hover:bg-muted rounded flex justify-center"
              title="Expand sidebar"
            >
              <PanelLeftOpen className="h-4 w-4" />
            </button>
          )}
          {!isSidebarCollapsed && (
            <div className="relative">
              <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search drawings..."
                className="w-full pl-8 pr-3 py-1.5 text-sm border border-border rounded-md bg-background"
              />
            </div>
          )}
        </div>

        {/* Tree */}
        {!isSidebarCollapsed && (
          <div className="flex-1 overflow-y-auto p-2">
          {isLoading && tree.length === 0 ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : rootItems.length === 0 ? (
            <div className="text-center py-8 text-sm text-muted-foreground">
              <PenTool className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No drawings yet</p>
              <p className="text-xs mt-1">Click + to create one</p>
            </div>
          ) : (
            rootItems.map((item) => (
              <TreeNode
                key={item.id}
                item={item}
                allItems={filteredTree}
                selectedId={currentDrawing?.id || null}
                expandedIds={expandedIds}
                onSelect={handleSelect}
                onToggle={handleToggle}
                onRename={handleRenameDrawing}
              />
            ))
          )}
          </div>
        )}

        {/* User info */}
        {!isSidebarCollapsed && (
          <div className="p-3 border-t border-border text-xs text-muted-foreground">
            <div className="flex items-center justify-between">
              <span>{user?.email}</span>
              <button onClick={logout} className="hover:text-foreground">
                Logout
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Canvas Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {error && (
          <div className="mb-4 p-3 bg-destructive/10 text-destructive text-sm rounded-md flex justify-between">
            <span>{error}</span>
            <button onClick={clearError} className="underline">
              Dismiss
            </button>
          </div>
        )}

        {currentDrawing ? (
          <>
            {/* Title & Actions */}
            <div className="flex items-center gap-4 mb-4">
              <div className="flex items-center gap-2 flex-1">
                <PenTool className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                <input
                  type="text"
                  value={editedTitle}
                  onChange={handleTitleChange}
                  className={cn(
                    'flex-1 text-2xl font-bold bg-transparent',
                    'border-b-2 border-transparent',
                    'focus:border-primary focus:outline-none',
                    'hover:border-muted transition-colors',
                    'px-2 py-1'
                  )}
                  placeholder="Untitled Drawing"
                />
              </div>
              <div className="flex items-center gap-2">
                {hasUnsavedChanges && (
                  <span className="text-xs text-muted-foreground">Unsaved</span>
                )}
                <Button
                  size="sm"
                  onClick={handleSave}
                  disabled={isSaving || !hasUnsavedChanges}
                >
                  {isSaving ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Save className="h-4 w-4 mr-2" />
                  )}
                  Save
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleDelete}
                  className="text-destructive hover:text-destructive"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={toggleFullscreen}
                  title="Fullscreen (F)"
                >
                  <Maximize2 className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Excalidraw Canvas */}
            <div
              className="flex-1 min-h-0 border border-border rounded-lg overflow-hidden"
              style={{ display: 'flex', flexDirection: 'column' }}
            >
              <ExcalidrawCanvas
                key={currentDrawing.id} // Force remount on drawing change
                initialData={{
                  elements: editedElements,
                  appState: editedAppState,
                  files: editedFiles,
                }}
                onChange={handleCanvasChange}
              />
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center text-muted-foreground">
              <PenTool className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Select a drawing from the sidebar</p>
              <p className="text-sm mt-1">or create a new one</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
