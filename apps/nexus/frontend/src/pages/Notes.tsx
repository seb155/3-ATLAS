import { useEffect, useState, useCallback } from 'react';
import {
  FileText,
  Plus,
  Search,
  Folder,
  FolderOpen,
  ChevronRight,
  ChevronDown,
  Trash2,
  Save,
  LogIn,
  Loader2,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Editor } from '@/components/editor';
import { useAuthStore } from '@/stores/useAuthStore';
import { useNotesStore } from '@/stores/useNotesStore';
import type { NoteTreeItem } from '@/services/api';
import { cn } from '@/lib/utils';

// ============================================================================
// Tree Node Component
// ============================================================================

interface TreeNodeProps {
  item: NoteTreeItem;
  allItems: NoteTreeItem[];
  selectedId: string | null;
  expandedIds: Set<string>;
  onSelect: (id: string) => void;
  onToggle: (id: string) => void;
  level?: number;
}

function TreeNode({
  item,
  allItems,
  selectedId,
  expandedIds,
  onSelect,
  onToggle,
  level = 0,
}: TreeNodeProps) {
  const children = allItems.filter((n) => n.parent_id === item.id);
  const hasChildren = children.length > 0 || item.is_folder;
  const isExpanded = expandedIds.has(item.id);
  const isSelected = selectedId === item.id;

  return (
    <div>
      <button
        onClick={() => {
          if (hasChildren) {
            onToggle(item.id);
          }
          onSelect(item.id);
        }}
        className={cn(
          'w-full flex items-center gap-1 px-2 py-1.5 text-sm rounded-md',
          'hover:bg-muted transition-colors text-left',
          isSelected && 'bg-primary/10 text-primary'
        )}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
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
        ) : (
          <FileText className="h-4 w-4 text-muted-foreground" />
        )}
        <span className="truncate flex-1">{item.title}</span>
        {item.children_count > 0 && (
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
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Login Form Component
// ============================================================================

function LoginForm() {
  const { login, isLoading, error, clearError } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login({ email, password });
  };

  return (
    <Card className="max-w-md mx-auto mt-12">
      <CardContent className="pt-6">
        <div className="text-center mb-6">
          <LogIn className="h-12 w-12 mx-auto text-primary mb-4" />
          <h2 className="text-xl font-bold">Sign in to Notes</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Enter your credentials to access your notes
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 bg-destructive/10 text-destructive text-sm rounded-md">
              {error}
              <button
                type="button"
                onClick={clearError}
                className="ml-2 underline"
              >
                Dismiss
              </button>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-md bg-background"
              placeholder="admin@localhost"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-md bg-background"
              placeholder="admin"
              required
            />
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Signing in...
              </>
            ) : (
              <>
                <LogIn className="h-4 w-4 mr-2" />
                Sign In
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Main Notes Page
// ============================================================================

export function Notes() {
  const { isAuthenticated, token, logout, user } = useAuthStore();
  const {
    tree,
    currentNote,
    isLoading,
    isSaving,
    error,
    fetchTree,
    fetchNote,
    createNote,
    updateNote,
    deleteNote,
    setCurrentNote,
    clearError,
  } = useNotesStore();

  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
  const [editedContent, setEditedContent] = useState('');
  const [editedTitle, setEditedTitle] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Load tree on mount
  useEffect(() => {
    if (isAuthenticated && token) {
      fetchTree(token);
    }
  }, [isAuthenticated, token, fetchTree]);

  // Sync edited content with current note
  useEffect(() => {
    if (currentNote) {
      setEditedContent(currentNote.content || '');
      setEditedTitle(currentNote.title);
      setHasUnsavedChanges(false);
    }
  }, [currentNote]);

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
        await fetchNote(token, id);
      }
    },
    [token, fetchNote]
  );

  const handleContentChange = useCallback((html: string) => {
    setEditedContent(html);
    setHasUnsavedChanges(true);
  }, []);

  const handleTitleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setEditedTitle(e.target.value);
    setHasUnsavedChanges(true);
  }, []);

  const handleSave = useCallback(async () => {
    if (!token || !currentNote) return;

    await updateNote(token, currentNote.id, {
      title: editedTitle,
      content: editedContent,
    });
    setHasUnsavedChanges(false);
  }, [token, currentNote, editedTitle, editedContent, updateNote]);

  const handleNewNote = useCallback(async () => {
    if (!token) return;

    const note = await createNote(token, {
      title: 'New Note',
      content: '',
      is_folder: false,
    });

    if (note) {
      setEditedTitle(note.title);
      setEditedContent(note.content);
    }
  }, [token, createNote]);

  const handleNewFolder = useCallback(async () => {
    if (!token) return;

    await createNote(token, {
      title: 'New Folder',
      content: '',
      is_folder: true,
    });
  }, [token, createNote]);

  const handleDelete = useCallback(async () => {
    if (!token || !currentNote) return;

    if (window.confirm(`Delete "${currentNote.title}"?`)) {
      await deleteNote(token, currentNote.id);
    }
  }, [token, currentNote, deleteNote]);

  // Filter tree by search
  const filteredTree = searchQuery
    ? tree.filter((item) =>
        item.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : tree;

  const rootItems = filteredTree.filter((item) => !item.parent_id);

  if (!isAuthenticated) {
    return <LoginForm />;
  }

  return (
    <div className="h-[calc(100vh-120px)] flex gap-4">
      {/* Sidebar */}
      <div className="w-64 flex-shrink-0 border-r border-border flex flex-col">
        {/* Header */}
        <div className="p-3 border-b border-border">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-semibold">Notes</h2>
            <div className="flex gap-1">
              <button
                onClick={handleNewNote}
                className="p-1.5 hover:bg-muted rounded"
                title="New Note"
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
            </div>
          </div>
          <div className="relative">
            <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search notes..."
              className="w-full pl-8 pr-3 py-1.5 text-sm border border-border rounded-md bg-background"
            />
          </div>
        </div>

        {/* Tree */}
        <div className="flex-1 overflow-y-auto p-2">
          {isLoading && tree.length === 0 ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : rootItems.length === 0 ? (
            <div className="text-center py-8 text-sm text-muted-foreground">
              <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No notes yet</p>
              <p className="text-xs mt-1">Click + to create one</p>
            </div>
          ) : (
            rootItems.map((item) => (
              <TreeNode
                key={item.id}
                item={item}
                allItems={filteredTree}
                selectedId={currentNote?.id || null}
                expandedIds={expandedIds}
                onSelect={handleSelect}
                onToggle={handleToggle}
              />
            ))
          )}
        </div>

        {/* User info */}
        <div className="p-3 border-t border-border text-xs text-muted-foreground">
          <div className="flex items-center justify-between">
            <span>{user?.email}</span>
            <button onClick={logout} className="hover:text-foreground">
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Editor Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {error && (
          <div className="mb-4 p-3 bg-destructive/10 text-destructive text-sm rounded-md flex justify-between">
            <span>{error}</span>
            <button onClick={clearError} className="underline">
              Dismiss
            </button>
          </div>
        )}

        {currentNote ? (
          <>
            {/* Title & Actions */}
            <div className="flex items-center gap-4 mb-4">
              <input
                type="text"
                value={editedTitle}
                onChange={handleTitleChange}
                className="flex-1 text-2xl font-bold bg-transparent border-none focus:outline-none"
                placeholder="Untitled"
              />
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
              </div>
            </div>

            {/* Editor */}
            <div className="flex-1 min-h-0">
              <Editor
                content={editedContent}
                onChange={handleContentChange}
                placeholder="Start writing your note..."
                className="h-full"
                autoFocus
              />
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Select a note from the sidebar</p>
              <p className="text-sm mt-1">or create a new one</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
