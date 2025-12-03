/**
 * API service for NEXUS backend communication.
 * @module api
 */

import type {
  Drawing,
  DrawingCreate,
  DrawingUpdate,
  DrawingTreeResponse,
  DrawingSearchResponse,
  DrawingWithBacklinks,
  NoteDrawingEmbed,
  NoteDrawingEmbedCreate,
} from '@/types/excalidraw.types';

/**
 * Smart API URL detection based on current origin.
 * Priority: ENV variable > Origin detection > Fallback
 */
const getApiUrl = (): string => {
  // 1. Check environment variable first (highest priority)
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // 2. Detect based on current origin (Traefik vs direct access)
  const origin = window.location.origin;

  // Production: via Traefik (https://nexus.axoiq.com)
  if (origin.includes('nexus.axoiq.com')) {
    return 'https://api-nexus.axoiq.com';
  }

  // Development: via Traefik localhost (https://nexus.localhost)
  if (origin.includes('nexus.localhost')) {
    return 'https://api-nexus.localhost';
  }

  // Fallback: direct port access (http://localhost:5173)
  return 'http://localhost:8000';
};

const API_URL = getApiUrl();

interface RequestOptions extends RequestInit {
  token?: string;
}

class ApiError extends Error {
  constructor(public status: number, message: string, public data?: unknown) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = null;
    }
    throw new ApiError(
      response.status,
      errorData?.detail || `HTTP error ${response.status}`,
      errorData
    );
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// ============================================================================
// Types
// ============================================================================

export interface Note {
  id: string;
  title: string;
  content: string;
  content_plain: string | null;
  parent_id: string | null;
  user_id: string;
  is_folder: boolean;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface NoteCreate {
  title: string;
  content?: string;
  parent_id?: string | null;
  is_folder?: boolean;
}

export interface NoteUpdate {
  title?: string;
  content?: string;
  parent_id?: string | null;
  is_folder?: boolean;
}

export interface NoteTreeItem {
  id: string;
  title: string;
  parent_id: string | null;
  is_folder: boolean;
  children_count: number;
}

export interface NoteTreeResponse {
  notes: NoteTreeItem[];
  total: number;
}

export interface BacklinkInfo {
  id: string;
  title: string;
  link_text: string | null;
  created_at: string;
}

export interface NoteWithBacklinks extends Note {
  backlinks: BacklinkInfo[];
}

export interface SearchResult {
  id: string;
  title: string;
  snippet: string;
  score: number;
  is_folder: boolean;
}

export interface SearchResponse {
  query: string;
  total: number;
  results: SearchResult[];
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
}

// ============================================================================
// Auth API
// ============================================================================

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(response.status, error.detail || 'Login failed', error);
    }

    return response.json();
  },

  register: async (data: {
    email: string;
    password: string;
    full_name?: string;
  }): Promise<User> => {
    return request('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  me: async (token: string): Promise<User> => {
    return request('/api/v1/auth/me', { token });
  },
};

// ============================================================================
// Drawings API
// ============================================================================

export const drawingsApi = {
  list: async (token: string, parentId?: string): Promise<Drawing[]> => {
    const params = parentId ? `?parent_id=${parentId}` : '';
    return request(`/api/v1/drawings${params}`, { token });
  },

  getRoot: async (token: string): Promise<Drawing[]> => {
    return request('/api/v1/drawings/root', { token });
  },

  getTree: async (token: string): Promise<DrawingTreeResponse> => {
    return request('/api/v1/drawings/tree', { token });
  },

  get: async (token: string, id: string): Promise<Drawing> => {
    return request(`/api/v1/drawings/${id}`, { token });
  },

  getWithBacklinks: async (token: string, id: string): Promise<DrawingWithBacklinks> => {
    return request(`/api/v1/drawings/${id}/backlinks`, { token });
  },

  findByTitle: async (token: string, title: string): Promise<Drawing | null> => {
    return request(`/api/v1/drawings/find?title=${encodeURIComponent(title)}`, { token });
  },

  create: async (token: string, data: DrawingCreate): Promise<Drawing> => {
    return request('/api/v1/drawings', {
      method: 'POST',
      token,
      body: JSON.stringify(data),
    });
  },

  update: async (token: string, id: string, data: DrawingUpdate): Promise<Drawing> => {
    return request(`/api/v1/drawings/${id}`, {
      method: 'PUT',
      token,
      body: JSON.stringify(data),
    });
  },

  move: async (token: string, id: string, newParentId: string | null): Promise<Drawing> => {
    return request(`/api/v1/drawings/${id}/move`, {
      method: 'PUT',
      token,
      body: JSON.stringify({ new_parent_id: newParentId }),
    });
  },

  updateThumbnail: async (token: string, id: string, thumbnail: string): Promise<void> => {
    return request(`/api/v1/drawings/${id}/thumbnail`, {
      method: 'PUT',
      token,
      body: JSON.stringify({ thumbnail }),
    });
  },

  delete: async (token: string, id: string, hard = false): Promise<void> => {
    const params = hard ? '?hard=true' : '';
    return request(`/api/v1/drawings/${id}${params}`, {
      method: 'DELETE',
      token,
    });
  },

  search: async (token: string, query: string, limit = 20): Promise<DrawingSearchResponse> => {
    return request(`/api/v1/drawings/search?q=${encodeURIComponent(query)}&limit=${limit}`, {
      token,
    });
  },

  // Embed operations
  createEmbed: async (token: string, data: NoteDrawingEmbedCreate): Promise<NoteDrawingEmbed> => {
    return request('/api/v1/drawings/embeds', {
      method: 'POST',
      token,
      body: JSON.stringify(data),
    });
  },

  getEmbedsForNote: async (token: string, noteId: string): Promise<NoteDrawingEmbed[]> => {
    return request(`/api/v1/drawings/embeds/note/${noteId}`, { token });
  },

  deleteEmbed: async (token: string, embedId: string): Promise<void> => {
    return request(`/api/v1/drawings/embeds/${embedId}`, {
      method: 'DELETE',
      token,
    });
  },
};

// ============================================================================
// Notes API
// ============================================================================

export const notesApi = {
  list: async (token: string, parentId?: string): Promise<Note[]> => {
    const params = parentId ? `?parent_id=${parentId}` : '';
    return request(`/api/v1/notes${params}`, { token });
  },

  getRoot: async (token: string): Promise<Note[]> => {
    return request('/api/v1/notes/root', { token });
  },

  getTree: async (token: string): Promise<NoteTreeResponse> => {
    return request('/api/v1/notes/tree', { token });
  },

  get: async (token: string, id: string): Promise<Note> => {
    return request(`/api/v1/notes/${id}`, { token });
  },

  getWithBacklinks: async (token: string, id: string): Promise<NoteWithBacklinks> => {
    return request(`/api/v1/notes/${id}/backlinks`, { token });
  },

  getChildren: async (token: string, id: string): Promise<Note[]> => {
    return request(`/api/v1/notes/${id}/children`, { token });
  },

  create: async (token: string, data: NoteCreate): Promise<Note> => {
    return request('/api/v1/notes', {
      method: 'POST',
      token,
      body: JSON.stringify(data),
    });
  },

  update: async (token: string, id: string, data: NoteUpdate): Promise<Note> => {
    return request(`/api/v1/notes/${id}`, {
      method: 'PUT',
      token,
      body: JSON.stringify(data),
    });
  },

  move: async (token: string, id: string, newParentId: string | null): Promise<Note> => {
    const params = newParentId ? `?new_parent_id=${newParentId}` : '';
    return request(`/api/v1/notes/${id}/move${params}`, {
      method: 'PUT',
      token,
    });
  },

  delete: async (token: string, id: string, hard = false): Promise<void> => {
    const params = hard ? '?hard=true' : '';
    return request(`/api/v1/notes/${id}${params}`, {
      method: 'DELETE',
      token,
    });
  },

  search: async (token: string, query: string, limit = 20): Promise<SearchResponse> => {
    return request(`/api/v1/notes/search?q=${encodeURIComponent(query)}&limit=${limit}`, {
      token,
    });
  },
};

export { ApiError };
