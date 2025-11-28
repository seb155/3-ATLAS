import type { ThemeDefinition } from '@/types/theme.types';

/**
 * One Light Theme - VSCode Atom One Light theme
 */
export const oneLight: ThemeDefinition = {
  id: 'one-light',
  name: 'One Light',
  type: 'light',
  author: 'Atom',
  description: 'Atom One Light theme, popular VSCode light theme',
  version: '1.0.0',
  colors: {
    background: '#fafafa',
    foreground: '#383a42',
    card: '#f6f8fa',
    cardForeground: '#383a42',
    border: '#e1e4e8',
    muted: '#e1e4e8',
    mutedForeground: '#a0a1a7',
    primary: '#4078f2',
    primaryForeground: '#fafafa',
    secondary: '#a626a4',
    secondaryForeground: '#fafafa',
    accent: '#4078f2',
    accentForeground: '#fafafa',
    success: '#50a14f',
    successForeground: '#fafafa',
    warning: '#c18401',
    warningForeground: '#fafafa',
    error: '#e45649',
    errorForeground: '#fafafa',
    info: '#4078f2',
    infoForeground: '#fafafa',
    destructive: '#e45649',
    destructiveForeground: '#fafafa',
    input: '#f6f8fa',
    ring: '#4078f2',
    chart1: '#4078f2',
    chart2: '#a626a4',
    chart3: '#50a14f',
    chart4: '#c18401',
    chart5: '#e45649',
  },
  typography: {
    fontFamily: {
      sans: 'system-ui, -apple-system, sans-serif',
      mono: 'ui-monospace, monospace',
      heading: 'system-ui, -apple-system, sans-serif',
    },
  },
};
