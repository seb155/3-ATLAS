import type { ThemeDefinition } from '@/types/theme.types';

/**
 * Nord Theme - Arctic, north-bluish color palette
 * https://www.nordtheme.com/
 */
export const nordDark: ThemeDefinition = {
  id: 'nord-dark',
  name: 'Nord',
  type: 'dark',
  author: 'Arctic Ice Studio',
  description: 'Arctic, north-bluish color palette for a professional aesthetic',
  version: '0.2.1',
  colors: {
    background: '#2e3440',
    foreground: '#eceff4',
    card: '#3b4252',
    cardForeground: '#eceff4',
    border: '#4c566a',
    muted: '#4c566a',
    mutedForeground: '#d8dee9',
    primary: '#88c0d0',
    primaryForeground: '#2e3440',
    secondary: '#81a1c1',
    secondaryForeground: '#2e3440',
    accent: '#88c0d0',
    accentForeground: '#2e3440',
    success: '#a3be8c',
    successForeground: '#2e3440',
    warning: '#ebcb8b',
    warningForeground: '#2e3440',
    error: '#bf616a',
    errorForeground: '#eceff4',
    info: '#81a1c1',
    infoForeground: '#2e3440',
    destructive: '#bf616a',
    destructiveForeground: '#eceff4',
    input: '#3b4252',
    ring: '#88c0d0',
    chart1: '#88c0d0',
    chart2: '#81a1c1',
    chart3: '#a3be8c',
    chart4: '#ebcb8b',
    chart5: '#bf616a',
  },
  typography: {
    fontFamily: {
      sans: 'system-ui, -apple-system, sans-serif',
      mono: 'ui-monospace, monospace',
      heading: 'system-ui, -apple-system, sans-serif',
    },
  },
};
