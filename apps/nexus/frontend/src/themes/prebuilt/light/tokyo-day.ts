import type { ThemeDefinition } from '@/types/theme.types';

/**
 * Tokyo Day Theme - Light variant of Tokyo Night
 */
export const tokyoDay: ThemeDefinition = {
  id: 'tokyo-day',
  name: 'Tokyo Day',
  type: 'light',
  author: 'Enkia',
  description: 'Light variant of Tokyo Night with professional colors',
  version: '1.0.0',
  colors: {
    background: '#e1e2e7',
    foreground: '#3760bf',
    card: '#f5f5f8',
    cardForeground: '#3760bf',
    border: '#d5d6db',
    muted: '#d5d6db',
    mutedForeground: '#7e8294',
    primary: '#2e7de9',
    primaryForeground: '#e1e2e7',
    secondary: '#9854f1',
    secondaryForeground: '#e1e2e7',
    accent: '#2e7de9',
    accentForeground: '#e1e2e7',
    success: '#587539',
    successForeground: '#e1e2e7',
    warning: '#c65d0b',
    warningForeground: '#e1e2e7',
    error: '#d20005',
    errorForeground: '#e1e2e7',
    info: '#2e7de9',
    infoForeground: '#e1e2e7',
    destructive: '#d20005',
    destructiveForeground: '#e1e2e7',
    input: '#f5f5f8',
    ring: '#2e7de9',
    chart1: '#2e7de9',
    chart2: '#9854f1',
    chart3: '#587539',
    chart4: '#c65d0b',
    chart5: '#d20005',
  },
  typography: {
    fontFamily: {
      sans: 'system-ui, -apple-system, sans-serif',
      mono: 'ui-monospace, monospace',
      heading: 'system-ui, -apple-system, sans-serif',
    },
  },
};
