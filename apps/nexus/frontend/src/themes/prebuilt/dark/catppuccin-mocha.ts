import type { ThemeDefinition } from '@/types/theme.types';

/**
 * Catppuccin Mocha Theme - Soft pastel dark theme
 * https://github.com/catppuccin/catppuccin
 */
export const catppuccinMocha: ThemeDefinition = {
  id: 'catppuccin-mocha',
  name: 'Catppuccin Mocha',
  type: 'dark',
  author: 'Catppuccin',
  description: 'Soft pastel dark theme with soothing colors',
  version: '1.0.0',
  colors: {
    background: '#1e1e2e',
    foreground: '#cdd6f4',
    card: '#313244',
    cardForeground: '#cdd6f4',
    border: '#45475a',
    muted: '#45475a',
    mutedForeground: '#a6adc8',
    primary: '#89b4fa',
    primaryForeground: '#1e1e2e',
    secondary: '#f5c2e7',
    secondaryForeground: '#1e1e2e',
    accent: '#89b4fa',
    accentForeground: '#1e1e2e',
    success: '#a6e3a1',
    successForeground: '#1e1e2e',
    warning: '#f9e2af',
    warningForeground: '#1e1e2e',
    error: '#f38ba8',
    errorForeground: '#cdd6f4',
    info: '#89b4fa',
    infoForeground: '#1e1e2e',
    destructive: '#f38ba8',
    destructiveForeground: '#cdd6f4',
    input: '#313244',
    ring: '#89b4fa',
    chart1: '#89b4fa',
    chart2: '#f5c2e7',
    chart3: '#a6e3a1',
    chart4: '#f9e2af',
    chart5: '#f38ba8',
  },
  typography: {
    fontFamily: {
      sans: 'system-ui, -apple-system, sans-serif',
      mono: 'ui-monospace, monospace',
      heading: 'system-ui, -apple-system, sans-serif',
    },
  },
};
