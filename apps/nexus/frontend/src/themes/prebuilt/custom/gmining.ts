import type { ThemeDefinition } from '@/types/theme.types';

/**
 * Gmining Corporate Theme - Professional mining industry theme
 * Primary blue for trust & professionalism
 * Gold accents for mining industry association
 * Dark background for readability
 */
export const gminingCorporate: ThemeDefinition = {
  id: 'gmining-corporate',
  name: 'Gmining Corporate',
  type: 'dark',
  author: 'Gmining',
  description: 'Professional Gmining corporate theme with mining industry colors',
  version: '1.0.0',
  colors: {
    // Deep professional blue background
    background: '#0f1f2e',
    foreground: '#e8eef5',
    card: '#1a2a3a',
    cardForeground: '#e8eef5',
    border: '#2a3a4a',
    muted: '#2a3a4a',
    mutedForeground: '#9aa7b3',

    // Primary: Deep trust blue
    primary: '#003d5c',
    primaryForeground: '#e8eef5',

    // Secondary: Professional slate
    secondary: '#1e5a7a',
    secondaryForeground: '#e8eef5',

    // Accent: Gold (mining association)
    accent: '#d4a017',
    accentForeground: '#0f1f2e',

    // Success: Professional green
    success: '#3db870',
    successForeground: '#0f1f2e',

    // Warning: Professional amber
    warning: '#f59e0b',
    warningForeground: '#0f1f2e',

    // Error: Professional red
    error: '#e74c3c',
    errorForeground: '#e8eef5',

    // Info: Light blue
    info: '#5a9fd4',
    infoForeground: '#0f1f2e',

    // Destructive: Same as error
    destructive: '#e74c3c',
    destructiveForeground: '#e8eef5',

    // Input/Ring
    input: '#1a2a3a',
    ring: '#d4a017',

    // Chart colors (brand palette)
    chart1: '#003d5c',    // Primary blue
    chart2: '#d4a017',    // Gold
    chart3: '#3db870',    // Green
    chart4: '#f59e0b',    // Amber
    chart5: '#5a9fd4',    // Light blue
  },
  typography: {
    fontFamily: {
      sans: 'system-ui, -apple-system, sans-serif',
      mono: 'ui-monospace, monospace',
      heading: 'system-ui, -apple-system, sans-serif',
    },
  },
};
