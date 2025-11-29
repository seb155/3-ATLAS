/**
 * Search Service - Client for backend global search API
 */

import apiClient from './apiClient';

export interface SearchResult {
  id: string;
  type: 'asset' | 'rule' | 'cable' | 'location' | 'project' | 'action' | 'navigation';
  title: string;
  subtitle: string | null;
  icon: string | null;
  path: string | null;
  score: number;
  metadata?: Record<string, unknown>;
}

export interface SearchResponse {
  query: string;
  total: number;
  results: SearchResult[];
  categories: Record<string, number>;
}

export interface SearchSuggestion {
  text: string;
  type: string;
  path: string;
}

/**
 * Perform global search across all entities
 */
export const globalSearch = async (
  query: string,
  options?: {
    limit?: number;
    types?: string[];
    projectId?: string;
  }
): Promise<SearchResponse> => {
  const params: Record<string, string | number> = {
    q: query,
    limit: options?.limit || 20
  };

  if (options?.types?.length) {
    params.types = options.types.join(',');
  }

  if (options?.projectId) {
    params.project_id = options.projectId;
  }

  const response = await apiClient.get<SearchResponse>('/search/', { params });
  return response.data;
};

/**
 * Get autocomplete suggestions (faster, simpler response)
 */
export const getSuggestions = async (
  query: string,
  limit = 5
): Promise<SearchSuggestion[]> => {
  const response = await apiClient.get<SearchSuggestion[]>('/search/suggestions', {
    params: { q: query, limit }
  });
  return response.data;
};

/**
 * Get recent searches (per user)
 */
export const getRecentSearches = async (): Promise<{ recent: string[] }> => {
  const response = await apiClient.get('/search/recent');
  return response.data;
};

/**
 * Search within a specific entity type
 */
export const searchByType = async (
  type: 'asset' | 'rule' | 'cable' | 'location',
  query: string,
  limit = 10
): Promise<SearchResult[]> => {
  const response = await globalSearch(query, { types: [type], limit });
  return response.results;
};

// Keyboard shortcut utilities
export const SEARCH_SHORTCUTS = {
  OPEN_PALETTE: ['ctrl+k', 'meta+k'],
  SEARCH_ASSETS: ['ctrl+shift+a'],
  SEARCH_RULES: ['ctrl+shift+r'],
  SEARCH_CABLES: ['ctrl+shift+c'],
};

/**
 * Check if a keyboard event matches a shortcut
 */
export const matchesShortcut = (
  event: KeyboardEvent,
  shortcuts: string[]
): boolean => {
  const key = event.key.toLowerCase();
  const hasCtrl = event.ctrlKey;
  const hasMeta = event.metaKey;
  const hasShift = event.shiftKey;

  return shortcuts.some(shortcut => {
    const parts = shortcut.split('+');
    const requiredKey = parts[parts.length - 1];
    const needsCtrl = parts.includes('ctrl');
    const needsMeta = parts.includes('meta');
    const needsShift = parts.includes('shift');

    return (
      key === requiredKey &&
      (needsCtrl ? hasCtrl : !hasCtrl || needsMeta) &&
      (needsMeta ? hasMeta : !hasMeta || needsCtrl) &&
      needsShift === hasShift
    );
  });
};
