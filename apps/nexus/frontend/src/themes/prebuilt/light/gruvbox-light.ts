import type { ThemeDefinition } from '@/types/theme.types';

/**
 * Gruvbox Light Theme - Retro groove light variant
 * https://github.com/morhetz/gruvbox
 */
export const gruvboxLight: ThemeDefinition = {
  id: 'gruvbox-light',
  name: 'Gruvbox Light',
  type: 'light',
  author: 'Morhetz',
  description: 'Retro groove light variant with warm earthy tones',
  version: '1.0.0',
  colors: {
    background: '#fbf1c7',
    foreground: '#3c3836',
    card: '#f2e5bc',
    cardForeground: '#3c3836',
    border: '#ebdbb2',
    muted: '#ebdbb2',
    mutedForeground: '#928374',
    primary: '#458588',
    primaryForeground: '#fbf1c7',
    secondary: '#8f3f71',
    secondaryForeground: '#fbf1c7',
    accent: '#458588',
    accentForeground: '#fbf1c7',
    success: '#79740e',
    successForeground: '#fbf1c7',
    warning: '#b57614',
    warningForeground: '#fbf1c7',
    error: '#cc241d',
    errorForeground: '#fbf1c7',
    info: '#458588',
    infoForeground: '#fbf1c7',
    destructive: '#cc241d',
    destructiveForeground: '#fbf1c7',
    input: '#f2e5bc',
    ring: '#458588',
    chart1: '#458588',
    chart2: '#8f3f71',
    chart3: '#79740e',
    chart4: '#b57614',
    chart5: '#cc241d',
  },
  typography: {
    fontFamily: {
      sans: 'system-ui, -apple-system, sans-serif',
      mono: 'ui-monospace, monospace',
      heading: 'system-ui, -apple-system, sans-serif',
    },
  },
};
