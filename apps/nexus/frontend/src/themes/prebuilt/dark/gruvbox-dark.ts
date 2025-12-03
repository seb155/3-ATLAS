import type { ThemeDefinition } from '@/types/theme.types';

/**
 * Gruvbox Dark Theme - Retro groove color scheme
 * https://github.com/morhetz/gruvbox
 */
export const gruvboxDark: ThemeDefinition = {
  id: 'gruvbox-dark',
  name: 'Gruvbox Dark',
  type: 'dark',
  author: 'Morhetz',
  description: 'Retro groove color scheme with warm earthy tones',
  version: '1.0.0',
  colors: {
    background: '#282828',
    foreground: '#ebdbb2',
    card: '#3c3836',
    cardForeground: '#ebdbb2',
    border: '#504945',
    muted: '#504945',
    mutedForeground: '#a89984',
    primary: '#83a598',
    primaryForeground: '#282828',
    secondary: '#d3869b',
    secondaryForeground: '#282828',
    accent: '#83a598',
    accentForeground: '#282828',
    success: '#b8bb26',
    successForeground: '#282828',
    warning: '#fabd2f',
    warningForeground: '#282828',
    error: '#fb4934',
    errorForeground: '#ebdbb2',
    info: '#83a598',
    infoForeground: '#282828',
    destructive: '#fb4934',
    destructiveForeground: '#ebdbb2',
    input: '#3c3836',
    ring: '#83a598',
    chart1: '#83a598',
    chart2: '#d3869b',
    chart3: '#b8bb26',
    chart4: '#fabd2f',
    chart5: '#fb4934',
  },
  typography: {
    fontFamily: {
      sans: 'system-ui, -apple-system, sans-serif',
      mono: 'ui-monospace, monospace',
      heading: 'system-ui, -apple-system, sans-serif',
    },
  },
};
