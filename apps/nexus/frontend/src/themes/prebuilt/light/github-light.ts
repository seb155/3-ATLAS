import type { ThemeDefinition } from '@/types/theme.types';

/**
 * GitHub Light Theme - Clean, professional light theme
 * Based on GitHub's official light theme
 */
export const githubLight: ThemeDefinition = {
  id: 'github-light',
  name: 'GitHub Light',
  type: 'light',
  author: 'GitHub',
  description: 'Clean and professional light theme used by GitHub',
  version: '1.0.0',
  colors: {
    background: '#ffffff',
    foreground: '#24292e',
    card: '#f6f8fa',
    cardForeground: '#24292e',
    border: '#e1e4e8',
    muted: '#f6f8fa',
    mutedForeground: '#6a737d',
    primary: '#0969da',
    primaryForeground: '#ffffff',
    secondary: '#6f42c1',
    secondaryForeground: '#ffffff',
    accent: '#0969da',
    accentForeground: '#ffffff',
    success: '#28a745',
    successForeground: '#ffffff',
    warning: '#ffc107',
    warningForeground: '#24292e',
    error: '#d73a49',
    errorForeground: '#ffffff',
    info: '#0969da',
    infoForeground: '#ffffff',
    destructive: '#d73a49',
    destructiveForeground: '#ffffff',
    input: '#f6f8fa',
    ring: '#0969da',
    chart1: '#0969da',
    chart2: '#6f42c1',
    chart3: '#28a745',
    chart4: '#ffc107',
    chart5: '#d73a49',
  },
  typography: {
    fontFamily: {
      sans: 'system-ui, -apple-system, sans-serif',
      mono: 'ui-monospace, monospace',
      heading: 'system-ui, -apple-system, sans-serif',
    },
  },
};
