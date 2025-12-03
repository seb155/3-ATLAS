import type { ThemeDefinition } from '@/types/theme.types';

/**
 * Dracula Theme - Bold, vibrant dark theme
 * https://draculatheme.com/
 */
export const draculaDark: ThemeDefinition = {
  id: 'dracula-dark',
  name: 'Dracula',
  type: 'dark',
  author: 'Dracula Theme',
  description: 'Bold and vibrant dark theme with accent colors',
  version: '2.0.0',
  colors: {
    background: '#282a36',
    foreground: '#f8f8f2',
    card: '#21222c',
    cardForeground: '#f8f8f2',
    border: '#44475a',
    muted: '#44475a',
    mutedForeground: '#f8f8f2',
    primary: '#bd93f9',
    primaryForeground: '#282a36',
    secondary: '#ff79c6',
    secondaryForeground: '#282a36',
    accent: '#bd93f9',
    accentForeground: '#282a36',
    success: '#50fa7b',
    successForeground: '#282a36',
    warning: '#f1fa8c',
    warningForeground: '#282a36',
    error: '#ff5555',
    errorForeground: '#f8f8f2',
    info: '#8be9fd',
    infoForeground: '#282a36',
    destructive: '#ff5555',
    destructiveForeground: '#f8f8f2',
    input: '#21222c',
    ring: '#bd93f9',
    chart1: '#bd93f9',
    chart2: '#ff79c6',
    chart3: '#50fa7b',
    chart4: '#f1fa8c',
    chart5: '#8be9fd',
  },
  typography: {
    fontFamily: {
      sans: 'system-ui, -apple-system, sans-serif',
      mono: 'ui-monospace, monospace',
      heading: 'system-ui, -apple-system, sans-serif',
    },
  },
};
