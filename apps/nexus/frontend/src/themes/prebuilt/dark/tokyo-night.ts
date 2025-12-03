import type { ThemeDefinition } from '@/types/theme.types';

/**
 * Tokyo Night Theme - Modern neon dark theme
 */
export const tokyoNightDark: ThemeDefinition = {
  id: 'tokyo-night-dark',
  name: 'Tokyo Night',
  type: 'dark',
  author: 'Enkia',
  description: 'Modern neon dark theme inspired by Tokyo night lights',
  version: '1.0.0',
  colors: {
    background: '#1a1b26',
    foreground: '#c0caf5',
    card: '#16161e',
    cardForeground: '#c0caf5',
    border: '#27282f',
    muted: '#27282f',
    mutedForeground: '#565f89',
    primary: '#7aa2f7',
    primaryForeground: '#1a1b26',
    secondary: '#bb9af7',
    secondaryForeground: '#1a1b26',
    accent: '#7aa2f7',
    accentForeground: '#1a1b26',
    success: '#9ece6a',
    successForeground: '#1a1b26',
    warning: '#e0af68',
    warningForeground: '#1a1b26',
    error: '#f7768e',
    errorForeground: '#c0caf5',
    info: '#7aa2f7',
    infoForeground: '#1a1b26',
    destructive: '#f7768e',
    destructiveForeground: '#c0caf5',
    input: '#16161e',
    ring: '#7aa2f7',
    chart1: '#7aa2f7',
    chart2: '#bb9af7',
    chart3: '#9ece6a',
    chart4: '#e0af68',
    chart5: '#f7768e',
  },
  typography: {
    fontFamily: {
      sans: 'system-ui, -apple-system, sans-serif',
      mono: 'ui-monospace, monospace',
      heading: 'system-ui, -apple-system, sans-serif',
    },
  },
};
