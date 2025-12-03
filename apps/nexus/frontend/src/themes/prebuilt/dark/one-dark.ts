import type { ThemeDefinition } from '@/types/theme.types';

/**
 * One Dark Theme - VSCode inspired dark theme
 */
export const oneDark: ThemeDefinition = {
  id: 'one-dark',
  name: 'One Dark',
  type: 'dark',
  author: 'Atom',
  description: 'Atom One Dark theme, popular VSCode theme',
  version: '1.0.0',
  colors: {
    background: '#282c34',
    foreground: '#abb2bf',
    card: '#21252b',
    cardForeground: '#abb2bf',
    border: '#3e4451',
    muted: '#3e4451',
    mutedForeground: '#7d8590',
    primary: '#61afef',
    primaryForeground: '#282c34',
    secondary: '#c678dd',
    secondaryForeground: '#282c34',
    accent: '#61afef',
    accentForeground: '#282c34',
    success: '#98c379',
    successForeground: '#282c34',
    warning: '#e5c07b',
    warningForeground: '#282c34',
    error: '#e06c75',
    errorForeground: '#abb2bf',
    info: '#61afef',
    infoForeground: '#282c34',
    destructive: '#e06c75',
    destructiveForeground: '#abb2bf',
    input: '#21252b',
    ring: '#61afef',
    chart1: '#61afef',
    chart2: '#c678dd',
    chart3: '#98c379',
    chart4: '#e5c07b',
    chart5: '#e06c75',
  },
  typography: {
    fontFamily: {
      sans: 'system-ui, -apple-system, sans-serif',
      mono: 'ui-monospace, monospace',
      heading: 'system-ui, -apple-system, sans-serif',
    },
  },
};
