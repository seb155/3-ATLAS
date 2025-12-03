/**
 * TypeScript types for Excalidraw integration.
 */

// Re-export Excalidraw types for convenience
export type {
  ExcalidrawElement,
  AppState,
  BinaryFiles,
} from '@excalidraw/excalidraw/types/types';

// Drawing entity types
export interface Drawing {
  id: string;
  title: string;
  description: string;
  elements: unknown[];
  app_state: Record<string, unknown>;
  files: Record<string, unknown>;
  thumbnail: string | null;
  version: number;
  parent_id: string | null;
  user_id: string;
  is_folder: boolean;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface DrawingCreate {
  title: string;
  description?: string;
  elements?: unknown[];
  app_state?: Record<string, unknown>;
  files?: Record<string, unknown>;
  parent_id?: string | null;
  is_folder?: boolean;
}

export interface DrawingUpdate {
  title?: string;
  description?: string;
  elements?: unknown[];
  app_state?: Record<string, unknown>;
  files?: Record<string, unknown>;
  parent_id?: string | null;
  version: number; // Required for optimistic locking
}

export interface DrawingTreeItem {
  id: string;
  title: string;
  parent_id: string | null;
  is_folder: boolean;
  children_count: number;
  thumbnail: string | null;
}

export interface DrawingTreeResponse {
  drawings: DrawingTreeItem[];
  total: number;
}

export interface DrawingSearchResult {
  id: string;
  title: string;
  description: string;
  thumbnail: string | null;
  score: number;
  is_folder: boolean;
}

export interface DrawingSearchResponse {
  query: string;
  total: number;
  results: DrawingSearchResult[];
}

export interface BacklinkInfo {
  id: string;
  title: string;
  type: 'note' | 'drawing';
  link_text: string | null;
  created_at: string;
}

export interface DrawingWithBacklinks extends Drawing {
  backlinks: BacklinkInfo[];
}

// Embed types
export interface NoteDrawingEmbed {
  id: string;
  note_id: string;
  drawing_id: string;
  edit_mode: 'modal' | 'inline';
  width: number;
  height: number;
  position: number;
  created_at: string;
}

export interface NoteDrawingEmbedCreate {
  note_id: string;
  drawing_id: string;
  edit_mode?: 'modal' | 'inline';
  width?: number;
  height?: number;
  position?: number;
}

// AI Generation types (Phase 6)
export type DiagramType = 'architecture' | 'flowchart' | 'mindmap' | 'wireframe' | 'sequence' | 'erd';

export interface DiagramGenerateRequest {
  description: string;
  diagram_type: DiagramType;
  style?: string;
}

export interface DiagramGenerateResponse {
  status: 'success' | 'pending' | 'error';
  drawing_id: string | null;
  message: string;
}
