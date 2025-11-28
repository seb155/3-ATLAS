import type { ThemeDefinition } from '@/types/theme.types';

/**
 * Solarized Light Theme - Low contrast, eye-friendly
 * https://ethanschoonover.com/solarized/
 */
export const solarizedLight: ThemeDefinition = {
  id: 'solarized-light',
  name: 'Solarized Light',
  type: 'light',
  author: 'Ethan Schoonover',
  description: 'Low contrast light theme, easy on the eyes',
  version: '1.0.0',
  colors: {
    background: '#fdf6e3',
    foreground: '#657b83',
    card: '#eee8d5',
    cardForeground: '#657b83',
    border: '#d6d0c8',
    muted: '#d6d0c8',
    mutedForeground: '#93a1a1',
    primary: '#268bd2',
    primaryForeground: '#fdf6e3',
    secondary: '#6c71c4',
    secondaryForeground: '#fdf6e3',
    accent: '#268bd2',
    accentForeground: '#fdf6e3',
    success: '#859900',
    successForeground: '#fdf6e3',
    warning: '#b58900',
    warningForeground: '#fdf6e3',
    error: '#dc322f',
    errorForeground: '#fdf6e3',
    info: '#268bd2',
    infoForeground: '#fdf6e3',
    destructive: '#dc322f',
    destructiveForeground: '#fdf6e3',
    input: '#eee8d5',
    ring: '#268bd2',
    chart1: '#268bd2',
    chart2: '#6c71c4',
    chart3: '#859900',
    chart4: '#b58900',
    chart5: '#dc322f',
  },
  typography: {
    fontFamily: {
      sans: 'system-ui, -apple-system, sans-serif',
      mono: 'ui-monospace, monospace',
      heading: 'system-ui, -apple-system, sans-serif',
    },
  },
};
