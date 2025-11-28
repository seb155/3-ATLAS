import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { ThemeDefinition } from '@/types/theme.types';
import {
  PREBUILT_THEMES,
  applyTheme,
  validateThemeJSON,
} from '@/themes';

interface ThemeStore {
  // State
  themes: ThemeDefinition[];
  activeThemeId: string;
  customThemes: ThemeDefinition[];
  lastError?: string;

  // Actions
  setTheme: (themeId: string) => void;
  addCustomTheme: (theme: ThemeDefinition) => void;
  updateCustomTheme: (themeId: string, theme: ThemeDefinition) => void;
  deleteCustomTheme: (themeId: string) => void;
  exportTheme: (themeId: string) => string | null;
  importTheme: (json: string) => boolean;
  getTheme: (themeId: string) => ThemeDefinition | undefined;
  getAllThemes: () => ThemeDefinition[];
}

/**
 * Get initial active theme from localStorage or system preference
 */
const getInitialTheme = (): string => {
  if (typeof window === 'undefined') return 'catppuccin-mocha';

  // Check localStorage
  const stored = localStorage.getItem('nexus-active-theme');
  if (stored && PREBUILT_THEMES.some((t) => t.id === stored)) {
    return stored;
  }

  // Default to Catppuccin Mocha dark theme
  return 'catppuccin-mocha';
};

/**
 * Load custom themes from localStorage
 */
const loadCustomThemes = (): ThemeDefinition[] => {
  if (typeof window === 'undefined') return [];

  try {
    const stored = localStorage.getItem('nexus-custom-themes');
    if (stored) {
      const themes = JSON.parse(stored) as ThemeDefinition[];
      return Array.isArray(themes) ? themes : [];
    }
  } catch (error) {
    console.error('Failed to load custom themes:', error);
  }

  return [];
};

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set, get) => ({
      // Initial state
      themes: PREBUILT_THEMES,
      activeThemeId: getInitialTheme(),
      customThemes: loadCustomThemes(),
      lastError: undefined,

      // Set active theme
      setTheme: (themeId: string) => {
        const allThemes = get().getAllThemes();
        const theme = allThemes.find((t) => t.id === themeId);

        if (!theme) {
          set({ lastError: `Theme not found: ${themeId}` });
          return;
        }

        try {
          applyTheme(theme);
          set({ activeThemeId: themeId, lastError: undefined });
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Unknown error';
          set({ lastError: `Failed to apply theme: ${message}` });
        }
      },

      // Add custom theme
      addCustomTheme: (theme: ThemeDefinition) => {
        // Check if ID already exists
        if (get().getAllThemes().some((t) => t.id === theme.id)) {
          set({ lastError: `Theme with ID "${theme.id}" already exists` });
          return;
        }

        const updated = [...get().customThemes, theme];
        set({ customThemes: updated, lastError: undefined });
      },

      // Update custom theme
      updateCustomTheme: (themeId: string, theme: ThemeDefinition) => {
        const customThemes = get().customThemes;
        const index = customThemes.findIndex((t) => t.id === themeId);

        if (index === -1) {
          set({ lastError: `Custom theme not found: ${themeId}` });
          return;
        }

        const updated = [...customThemes];
        updated[index] = theme;
        set({ customThemes: updated, lastError: undefined });

        // If this theme is active, re-apply it
        if (get().activeThemeId === themeId) {
          applyTheme(theme);
        }
      },

      // Delete custom theme
      deleteCustomTheme: (themeId: string) => {
        const customThemes = get().customThemes;
        const filtered = customThemes.filter((t) => t.id !== themeId);

        if (filtered.length === customThemes.length) {
          set({ lastError: `Custom theme not found: ${themeId}` });
          return;
        }

        set({ customThemes: filtered, lastError: undefined });

        // If deleted theme was active, switch to default
        if (get().activeThemeId === themeId) {
          const defaultTheme = 'catppuccin-mocha';
          const theme = get().getTheme(defaultTheme);
          if (theme) {
            get().setTheme(defaultTheme);
          }
        }
      },

      // Export theme as JSON
      exportTheme: (themeId: string): string | null => {
        const theme = get().getTheme(themeId);

        if (!theme) {
          set({ lastError: `Theme not found: ${themeId}` });
          return null;
        }

        try {
          return JSON.stringify(theme, null, 2);
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Unknown error';
          set({ lastError: `Failed to export theme: ${message}` });
          return null;
        }
      },

      // Import theme from JSON
      importTheme: (json: string): boolean => {
        try {
          const theme = validateThemeJSON(json);

          // Check if theme ID already exists
          if (get().getAllThemes().some((t) => t.id === theme.id)) {
            set({ lastError: `Theme with ID "${theme.id}" already exists` });
            return false;
          }

          get().addCustomTheme(theme);
          return true;
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Invalid JSON';
          set({ lastError: message });
          return false;
        }
      },

      // Get specific theme
      getTheme: (themeId: string): ThemeDefinition | undefined => {
        return get().getAllThemes().find((t) => t.id === themeId);
      },

      // Get all themes (prebuilt + custom)
      getAllThemes: (): ThemeDefinition[] => {
        return [...get().themes, ...get().customThemes];
      },
    }),
    {
      name: 'nexus-theme-storage',
      partialize: (state) => ({
        activeThemeId: state.activeThemeId,
        customThemes: state.customThemes,
      }),
    },
  ),
);

/**
 * Apply initial theme on store initialization
 */
if (typeof window !== 'undefined') {
  const initialThemeId = getInitialTheme();
  const theme = PREBUILT_THEMES.find((t) => t.id === initialThemeId);
  if (theme) {
    applyTheme(theme);
  }
}
