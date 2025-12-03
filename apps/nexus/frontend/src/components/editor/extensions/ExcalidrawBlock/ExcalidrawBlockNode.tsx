/**
 * TipTap NodeView component for rendering Excalidraw blocks in the editor.
 *
 * Shows a preview thumbnail with edit/delete controls.
 * Opens modal or expands inline for editing based on editMode setting.
 */

import { useState, useEffect, useCallback, lazy, Suspense, useRef } from 'react';
import { NodeViewWrapper } from '@tiptap/react';
import { PenTool, Maximize2, Trash2, Settings, Loader2, ExternalLink } from 'lucide-react';
import { useAuthStore } from '@/stores/useAuthStore';
import { drawingsApi } from '@/services/api';
import type { Drawing } from '@/types/excalidraw.types';
import { cn } from '@/lib/utils';

// Lazy load Excalidraw
const Excalidraw = lazy(() =>
  import('@excalidraw/excalidraw').then((mod) => ({ default: mod.Excalidraw }))
);

interface ExcalidrawBlockNodeProps {
  node: {
    attrs: {
      drawingId: string;
      editMode: 'modal' | 'inline';
      width: number;
      height: number;
    };
  };
  updateAttributes: (attrs: Partial<ExcalidrawBlockNodeProps['node']['attrs']>) => void;
  deleteNode: () => void;
  selected: boolean;
}

export function ExcalidrawBlockNode({
  node,
  updateAttributes,
  deleteNode,
  selected,
}: ExcalidrawBlockNodeProps) {
  const { token } = useAuthStore();
  const [drawing, setDrawing] = useState<Drawing | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  // Library state management - shared with Drawing page via localStorage
  const [libraries, setLibraries] = useState<any[]>(() => {
    const saved = localStorage.getItem('excalidraw-libraries');
    return saved ? JSON.parse(saved) : [];
  });

  // Ref to access Excalidraw API methods like updateLibrary()
  // Required for programmatic library installation from libraries.excalidraw.com
  const excalidrawRef = useRef<any>(null);

  const { drawingId, editMode, width, height } = node.attrs;

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

  // Fetch drawing data
  useEffect(() => {
    async function fetchDrawing() {
      if (!token || !drawingId) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        const data = await drawingsApi.get(token, drawingId);
        setDrawing(data);
        setError(null);
      } catch (err) {
        setError('Failed to load drawing');
        console.error('Failed to load drawing:', err);
      } finally {
        setIsLoading(false);
      }
    }

    fetchDrawing();
  }, [token, drawingId]);

  // Handle save from inline editor
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const handleSave = async (elements: any[], appState: any, files: any) => {
    if (!token || !drawing) return;

    try {
      await drawingsApi.update(token, drawing.id, {
        elements,
        app_state: appState,
        files,
        version: drawing.version,
      });
      // Refresh drawing data
      const updated = await drawingsApi.get(token, drawing.id);
      setDrawing(updated);
    } catch (err) {
      console.error('Failed to save drawing:', err);
    }
  };

  if (!drawingId) {
    return (
      <NodeViewWrapper>
        <div className="p-4 border border-dashed border-border rounded-lg text-center text-muted-foreground">
          <PenTool className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p>No drawing selected</p>
        </div>
      </NodeViewWrapper>
    );
  }

  if (isLoading) {
    return (
      <NodeViewWrapper>
        <div
          className="flex items-center justify-center border border-border rounded-lg bg-muted/30"
          style={{ width, height: Math.min(height, 200) }}
        >
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      </NodeViewWrapper>
    );
  }

  if (error || !drawing) {
    return (
      <NodeViewWrapper>
        <div className="p-4 border border-destructive/50 rounded-lg text-center text-destructive bg-destructive/10">
          <PenTool className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p>{error || 'Drawing not found'}</p>
          <button
            onClick={deleteNode}
            className="mt-2 text-sm underline hover:no-underline"
          >
            Remove block
          </button>
        </div>
      </NodeViewWrapper>
    );
  }

  // Inline editing mode
  if (isEditing && editMode === 'inline') {
    return (
      <NodeViewWrapper>
        <div
          className={cn(
            'border rounded-lg overflow-hidden',
            selected ? 'border-primary ring-2 ring-primary/20' : 'border-border'
          )}
          style={{ width, height }}
        >
          <div className="h-8 bg-muted flex items-center justify-between px-2">
            <span className="text-sm font-medium truncate">{drawing.title}</span>
            <button
              onClick={() => setIsEditing(false)}
              className="p-1 hover:bg-background rounded text-xs"
            >
              Done
            </button>
          </div>
          <div className="h-[calc(100%-32px)]">
            <Suspense
              fallback={
                <div className="h-full flex items-center justify-center">
                  <Loader2 className="h-6 w-6 animate-spin" />
                </div>
              }
            >
              <Excalidraw
                ref={excalidrawRef}
                initialData={{
                  elements: drawing.elements,
                  appState: drawing.app_state,
                  files: drawing.files,
                }}
                onChange={(elements, appState, files) => {
                  // Debounce save
                  handleSave(elements, appState, files);
                }}
                theme="dark"
                libraryReturnUrl={`${window.location.origin}${window.location.pathname}`}
                onLibraryChange={handleLibraryChange}
              />
            </Suspense>
          </div>
        </div>
      </NodeViewWrapper>
    );
  }

  // Preview mode (default)
  return (
    <NodeViewWrapper>
      <div
        className={cn(
          'relative group border rounded-lg overflow-hidden bg-muted/30',
          selected ? 'border-primary ring-2 ring-primary/20' : 'border-border'
        )}
        style={{ width, height: Math.min(height, 300) }}
      >
        {/* Preview/Thumbnail */}
        {drawing.thumbnail ? (
          <img
            src={drawing.thumbnail}
            alt={drawing.title}
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-center text-muted-foreground">
              <PenTool className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p className="font-medium">{drawing.title}</p>
              <p className="text-xs">Click to edit</p>
            </div>
          </div>
        )}

        {/* Hover overlay with controls */}
        <div className="absolute inset-0 bg-background/80 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <button
            onClick={() => {
              if (editMode === 'modal') {
                // Open in new tab/modal
                window.open(`/drawing?id=${drawing.id}`, '_blank');
              } else {
                setIsEditing(true);
              }
            }}
            className="p-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
            title="Edit drawing"
          >
            {editMode === 'modal' ? (
              <ExternalLink className="h-5 w-5" />
            ) : (
              <Maximize2 className="h-5 w-5" />
            )}
          </button>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 bg-muted text-foreground rounded-lg hover:bg-muted/80"
            title="Settings"
          >
            <Settings className="h-5 w-5" />
          </button>
          <button
            onClick={deleteNode}
            className="p-2 bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90"
            title="Remove"
          >
            <Trash2 className="h-5 w-5" />
          </button>
        </div>

        {/* Settings dropdown */}
        {showSettings && (
          <div className="absolute top-full left-0 mt-2 p-3 bg-popover border border-border rounded-lg shadow-lg z-10 min-w-[200px]">
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium">Edit Mode</label>
                <select
                  value={editMode}
                  onChange={(e) => updateAttributes({ editMode: e.target.value as 'modal' | 'inline' })}
                  className="mt-1 w-full px-2 py-1 text-sm border border-border rounded bg-background"
                >
                  <option value="modal">Open in new tab</option>
                  <option value="inline">Edit inline</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-medium">Width</label>
                <input
                  type="number"
                  value={width}
                  onChange={(e) => updateAttributes({ width: parseInt(e.target.value, 10) })}
                  className="mt-1 w-full px-2 py-1 text-sm border border-border rounded bg-background"
                  min={200}
                  max={2000}
                />
              </div>
              <div>
                <label className="text-xs font-medium">Height</label>
                <input
                  type="number"
                  value={height}
                  onChange={(e) => updateAttributes({ height: parseInt(e.target.value, 10) })}
                  className="mt-1 w-full px-2 py-1 text-sm border border-border rounded bg-background"
                  min={100}
                  max={1500}
                />
              </div>
              <button
                onClick={() => setShowSettings(false)}
                className="w-full px-2 py-1 text-sm bg-muted rounded hover:bg-muted/80"
              >
                Close
              </button>
            </div>
          </div>
        )}

        {/* Title bar */}
        <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-background/90 to-transparent">
          <p className="text-sm font-medium truncate">{drawing.title}</p>
        </div>
      </div>
    </NodeViewWrapper>
  );
}

export default ExcalidrawBlockNode;
