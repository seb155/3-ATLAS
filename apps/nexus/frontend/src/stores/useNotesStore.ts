import { create } from 'zustand';
import { notesApi, type Note, type NoteTreeItem, type NoteCreate, type NoteUpdate, type SearchResult } from '@/services/api';

interface NotesState {
  // Data
  notes: Note[];
  tree: NoteTreeItem[];
  currentNote: Note | null;
  searchResults: SearchResult[];

  // UI State
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  searchQuery: string;

  // Actions
  fetchTree: (token: string) => Promise<void>;
  fetchNote: (token: string, id: string) => Promise<void>;
  createNote: (token: string, data: NoteCreate) => Promise<Note | null>;
  updateNote: (token: string, id: string, data: NoteUpdate) => Promise<Note | null>;
  deleteNote: (token: string, id: string) => Promise<boolean>;
  search: (token: string, query: string) => Promise<void>;
  setCurrentNote: (note: Note | null) => void;
  clearError: () => void;
}

export const useNotesStore = create<NotesState>()((set, get) => ({
  notes: [],
  tree: [],
  currentNote: null,
  searchResults: [],
  isLoading: false,
  isSaving: false,
  error: null,
  searchQuery: '',

  fetchTree: async (token) => {
    set({ isLoading: true, error: null });
    try {
      const response = await notesApi.getTree(token);
      set({ tree: response.notes, isLoading: false });
    } catch (err) {
      set({
        isLoading: false,
        error: err instanceof Error ? err.message : 'Failed to fetch notes',
      });
    }
  },

  fetchNote: async (token, id) => {
    set({ isLoading: true, error: null });
    try {
      const note = await notesApi.get(token, id);
      set({ currentNote: note, isLoading: false });
    } catch (err) {
      set({
        isLoading: false,
        error: err instanceof Error ? err.message : 'Failed to fetch note',
        currentNote: null,
      });
    }
  },

  createNote: async (token, data) => {
    set({ isSaving: true, error: null });
    try {
      const note = await notesApi.create(token, data);
      // Refresh tree after creating
      await get().fetchTree(token);
      set({ currentNote: note, isSaving: false });
      return note;
    } catch (err) {
      set({
        isSaving: false,
        error: err instanceof Error ? err.message : 'Failed to create note',
      });
      return null;
    }
  },

  updateNote: async (token, id, data) => {
    set({ isSaving: true, error: null });
    try {
      const note = await notesApi.update(token, id, data);
      // Refresh tree if title changed
      if (data.title) {
        await get().fetchTree(token);
      }
      set({ currentNote: note, isSaving: false });
      return note;
    } catch (err) {
      set({
        isSaving: false,
        error: err instanceof Error ? err.message : 'Failed to update note',
      });
      return null;
    }
  },

  deleteNote: async (token, id) => {
    set({ isSaving: true, error: null });
    try {
      await notesApi.delete(token, id);
      // Refresh tree and clear current note
      await get().fetchTree(token);
      set({
        currentNote: null,
        isSaving: false,
      });
      return true;
    } catch (err) {
      set({
        isSaving: false,
        error: err instanceof Error ? err.message : 'Failed to delete note',
      });
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
      const response = await notesApi.search(token, query);
      set({ searchResults: response.results, isLoading: false });
    } catch (err) {
      set({
        isLoading: false,
        error: err instanceof Error ? err.message : 'Search failed',
        searchResults: [],
      });
    }
  },

  setCurrentNote: (note) => set({ currentNote: note }),

  clearError: () => set({ error: null }),
}));
