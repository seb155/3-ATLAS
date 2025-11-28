import type { ThemeDefinition } from '@/types/theme.types';

/**
 * Catppuccin Latte Theme - Soft pastel light theme
 * https://github.com/catppuccin/catppuccin
 */
export const catppuccinLatte: ThemeDefinition = {
  id: 'catppuccin-latte',
  name: 'Catppuccin Latte',
  type: 'light',
  author: 'Catppuccin',
  description: 'Soft pastel light theme with modern colors',
  version: '1.0.0',
  colors: {
    background: '#eff1f5',
    foreground: '#4c4f69',
    card: '#e6e9f5',
    cardForeground: '#4c4f69',
    border: '#dce0e8',
    muted: '#dce0e8',
    mutedForeground: '#8c8fa1',
    primary: '#1e66f5',
    primaryForeground: '#eff1f5',
    secondary: '#ea76cb',
    secondaryForeground: '#eff1f5',
    accent: '#1e66f5',
    accentForeground: '#eff1f5',
    success: '#40a02b',
    successForeground: '#eff1f5',
    warning: '#df8e1d',
    warningForeground: '#eff1f5',
    error: '#d20f39',
    errorForeground: '#eff1f5',
    info: '#1e66f5',
    infoForeground: '#eff1f5',
    destructive: '#d20f39',
    destructiveForeground: '#eff1f5',
    input: '#e6e9f5',
    ring: '#1e66f5',
    chart1: '#1e66f5',
    chart2: '#ea76cb',
    chart3: '#40a02b',
    chart4: '#df8e1d',
    chart5: '#d20f39',
  },
  typography: {
    fontFamily: {
      sans: 'system-ui, -apple-system, sans-serif',
      mono: 'ui-monospace, monospace',
      heading: 'system-ui, -apple-system, sans-serif',
    },
  },
};
