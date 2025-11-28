/**
 * Complete theme system type definitions
 * Used for type safety across all theme-related code
 */

export interface ThemeColors {
  // Base colors
  background: string;
  foreground: string;
  card: string;
  cardForeground: string;
  border: string;
  muted: string;
  mutedForeground: string;

  // Primary accent
  primary: string;
  primaryForeground: string;

  // Secondary
  secondary: string;
  secondaryForeground: string;

  // Accent/hover
  accent: string;
  accentForeground: string;

  // Semantic colors
  success: string;
  successForeground: string;
  warning: string;
  warningForeground: string;
  error: string;
  errorForeground: string;
  info: string;
  infoForeground: string;
  destructive: string;
  destructiveForeground: string;

  // Input & Ring
  input: string;
  ring: string;

  // Chart colors for data visualization
  chart1: string;
  chart2: string;
  chart3: string;
  chart4: string;
  chart5: string;
}

export interface ThemeTypography {
  fontFamily?: {
    sans?: string;
    mono?: string;
    heading?: string;
  };
  fontSize?: {
    xs?: string;
    sm?: string;
    base?: string;
    lg?: string;
    xl?: string;
    '2xl'?: string;
    '3xl'?: string;
    '4xl'?: string;
    '5xl'?: string;
  };
  fontWeight?: {
    light?: number;
    normal?: number;
    medium?: number;
    semibold?: number;
    bold?: number;
  };
}

export interface ThemeSpacing {
  radius?: string;
}

export interface ThemeEffects {
  shadows?: {
    sm?: string;
    md?: string;
    lg?: string;
    xl?: string;
  };
}

export interface ThemeDefinition {
  // Metadata
  id: string; // Unique identifier: "nord-dark", "github-light"
  name: string; // Display name: "Nord Dark"
  type: 'light' | 'dark'; // Theme category
  author?: string; // Creator/source
  description?: string; // Description for UI
  version?: string; // Semantic versioning

  // Core content
  colors: ThemeColors;
  typography?: ThemeTypography;
  spacing?: ThemeSpacing;
  effects?: ThemeEffects;
}

export interface ThemeState {
  themes: ThemeDefinition[];
  activeThemeId: string;
  customThemes: ThemeDefinition[];
  lastError?: string;
}

export type ThemeType = 'light' | 'dark';
