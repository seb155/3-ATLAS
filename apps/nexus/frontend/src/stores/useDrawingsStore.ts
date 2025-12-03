import { create } from 'zustand';
import { drawingsApi } from '@/services/api';
import type {
  Drawing,
  DrawingCreate,
  DrawingUpdate,
  DrawingTreeItem,
  DrawingSearchResult,
} from '@/types/excalidraw.types';

interface DrawingsState {
  // Data
  drawings: Drawing[];
  tree: DrawingTreeItem[];
  currentDrawing: Drawing | null;
  searchResults: DrawingSearchResult[];

  // UI State
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  searchQuery: string;

  // Actions
  fetchTree: (token: string) => Promise<void>;
  fetchDrawing: (token: string, id: string) => Promise<void>;
  createDrawing: (token: string, data: DrawingCreate) => Promise<Drawing | null>;
  updateDrawing: (token: string, id: string, data: DrawingUpdate) => Promise<Drawing | null>;
  deleteDrawing: (token: string, id: string) => Promise<boolean>;
  updateThumbnail: (token: string, id: string, thumbnail: string) => Promise<boolean>;
  search: (token: string, query: string) => Promise<void>;
  setCurrentDrawing: (drawing: Drawing | null) => void;
  clearError: () => void;
}

export const useDrawingsStore = create<DrawingsState>()((set, get) => ({
  drawings: [],
  tree: [],
  currentDrawing: null,
  searchResults: [],
  isLoading: false,
  isSaving: false,
  error: null,
  searchQuery: '',

  fetchTree: async (token) => {
    set({ isLoading: true, error: null });
    try {
      const response = await drawingsApi.getTree(token);
      set({ tree: response.drawings, isLoading: false });
    } catch (err) {
      set({
        isLoading: false,
        error: err instanceof Error ? err.message : 'Failed to fetch drawings',
      });
    }
  },

  fetchDrawing: async (token, id) => {
    set({ isLoading: true, error: null });
    try {
      const drawing = await drawingsApi.get(token, id);
      set({ currentDrawing: drawing, isLoading: false });
    } catch (err) {
      set({
        isLoading: false,
        error: err instanceof Error ? err.message : 'Failed to fetch drawing',
        currentDrawing: null,
      });
    }
  },

  createDrawing: async (token, data) => {
    set({ isSaving: true, error: null });
    try {
      const drawing = await drawingsApi.create(token, data);
      // Refresh tree after creating
      await get().fetchTree(token);
      set({ currentDrawing: drawing, isSaving: false });
      return drawing;
    } catch (err) {
      set({
        isSaving: false,
        error: err instanceof Error ? err.message : 'Failed to create drawing',
      });
      return null;
    }
  },

  updateDrawing: async (token, id, data) => {
    set({ isSaving: true, error: null });
    try {
      const drawing = await drawingsApi.update(token, id, data);
      // Refresh tree if title changed
      if (data.title) {
        await get().fetchTree(token);
      }
      set({ currentDrawing: drawing, isSaving: false });
      return drawing;
    } catch (err) {
      // Handle version conflict specifically
      const errorMessage = err instanceof Error ? err.message : 'Failed to update drawing';
      if (errorMessage.includes('modified by another session')) {
        set({
          isSaving: false,
          error: 'Drawing was modified elsewhere. Please refresh and try again.',
        });
      } else {
        set({
          isSaving: false,
          error: errorMessage,
        });
      }
      return null;
    }
  },

  deleteDrawing: async (token, id) => {
    set({ isSaving: true, error: null });
    try {
      await drawingsApi.delete(token, id);
      // Refresh tree and clear current drawing
      await get().fetchTree(token);
      set({
        currentDrawing: null,
        isSaving: false,
      });
      return true;
    } catch (err) {
      set({
        isSaving: false,
        error: err instanceof Error ? err.message : 'Failed to delete drawing',
      });
      return false;
    }
  },

  updateThumbnail: async (token, id, thumbnail) => {
    try {
      await drawingsApi.updateThumbnail(token, id, thumbnail);
      // Update tree to reflect new thumbnail
      const { tree } = get();
      set({
        tree: tree.map((item) =>
          item.id === id ? { ...item, thumbnail } : item
        ),
      });
      return true;
    } catch (err) {
      console.error('Failed to update thumbnail:', err);
      return false;
    }
  },

  search: async (token, query) => {
    if (!query || query.length < 2) {
      set({ searchResults: [], searchQuery: '' });
      return;
    }

    set({ isLoading: true, searchQuery: query });
    try {
      const response = await drawingsApi.search(token, query);
      set({ searchResults: response.results, isLoading: false });
    } catch (err) {
      set({
        isLoading: false,
        error: err instanceof Error ? err.message : 'Search failed',
        searchResults: [],
      });
    }
  },

  setCurrentDrawing: (drawing) => set({ currentDrawing: drawing }),

  clearError: () => set({ error: null }),
}));
