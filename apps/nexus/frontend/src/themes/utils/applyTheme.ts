import type { ThemeDefinition, ThemeColors } from '@/types/theme.types';
import { hexToHsl, isValidHex } from './hexToHsl';

/**
 * Apply a theme to the document by setting CSS variables
 * This enables instant theme switching without page reload
 */
export function applyTheme(theme: ThemeDefinition): void {
  if (typeof window === 'undefined') return;

  const root = document.documentElement;

  // Set data-theme attribute for CSS selectors
  root.setAttribute('data-theme', theme.id);

  // Set color-scheme for native UI elements
  root.style.colorScheme = theme.type;

  // Apply colors as CSS variables
  applyColors(theme.colors);

  // Apply typography if provided
  if (theme.typography) {
    applyTypography(theme.typography);
  }

  // Apply spacing if provided
  if (theme.spacing) {
    applySpacing(theme.spacing);
  }

  // Apply effects if provided
  if (theme.effects) {
    applyEffects(theme.effects);
  }
}

/**
 * Apply color tokens as CSS custom properties
 * Converts hex colors to HSL format expected by Tailwind
 */
function applyColors(colors: ThemeColors): void {
  const root = document.documentElement;
  const style = root.style;

  const colorMap: Record<string, string> = {
    '--background': colors.background,
    '--foreground': colors.foreground,
    '--card': colors.card,
    '--card-foreground': colors.cardForeground,
    '--border': colors.border,
    '--muted': colors.muted,
    '--muted-foreground': colors.mutedForeground,
    '--primary': colors.primary,
    '--primary-foreground': colors.primaryForeground,
    '--secondary': colors.secondary,
    '--secondary-foreground': colors.secondaryForeground,
    '--accent': colors.accent,
    '--accent-foreground': colors.accentForeground,
    '--success': colors.success,
    '--success-foreground': colors.successForeground,
    '--warning': colors.warning,
    '--warning-foreground': colors.warningForeground,
    '--error': colors.error,
    '--error-foreground': colors.errorForeground,
    '--info': colors.info,
    '--info-foreground': colors.infoForeground,
    '--destructive': colors.destructive,
    '--destructive-foreground': colors.destructiveForeground,
    '--input': colors.input,
    '--ring': colors.ring,
    '--chart-1': colors.chart1,
    '--chart-2': colors.chart2,
    '--chart-3': colors.chart3,
    '--chart-4': colors.chart4,
    '--chart-5': colors.chart5,
  };

  // Apply each color, converting hex to HSL
  Object.entries(colorMap).forEach(([cssVar, hexColor]) => {
    try {
      if (isValidHex(hexColor)) {
        const hslValue = hexToHsl(hexColor);
        style.setProperty(cssVar, hslValue);
      } else {
        console.warn(`Invalid hex color for ${cssVar}: ${hexColor}`);
      }
    } catch (error) {
      console.error(`Error applying color ${cssVar}:`, error);
    }
  });
}

/**
 * Apply typography settings as CSS custom properties
 */
function applyTypography(typography: any): void {
  const root = document.documentElement;
  const style = root.style;

  // Apply font families
  if (typography.fontFamily) {
    if (typography.fontFamily.sans) {
      style.setProperty('--font-sans', typography.fontFamily.sans);
    }
    if (typography.fontFamily.mono) {
      style.setProperty('--font-mono', typography.fontFamily.mono);
    }
    if (typography.fontFamily.heading) {
      style.setProperty('--font-heading', typography.fontFamily.heading);
    }
  }

  // Apply font sizes (in rem or similar)
  if (typography.fontSize) {
    Object.entries(typography.fontSize).forEach(([size, value]) => {
      style.setProperty(`--text-${size}`, value as string);
    });
  }

  // Apply font weights
  if (typography.fontWeight) {
    Object.entries(typography.fontWeight).forEach(([weight, value]) => {
      style.setProperty(`--font-weight-${weight}`, String(value));
    });
  }
}

/**
 * Apply spacing settings as CSS custom properties
 */
function applySpacing(spacing: any): void {
  const root = document.documentElement;
  const style = root.style;

  if (spacing.radius) {
    style.setProperty('--radius', spacing.radius);
  }
}

/**
 * Apply effects (shadows, etc.) as CSS custom properties
 */
function applyEffects(effects: any): void {
  const root = document.documentElement;
  const style = root.style;

  if (effects.shadows) {
    Object.entries(effects.shadows).forEach(([name, value]) => {
      style.setProperty(`--shadow-${name}`, value as string);
    });
  }
}

/**
 * Get the currently active theme ID
 */
export function getActiveThemeId(): string {
  if (typeof window === 'undefined') return 'github-light';
  return document.documentElement.getAttribute('data-theme') || 'github-light';
}

/**
 * Reset to default theme
 */
export function resetTheme(): void {
  const root = document.documentElement;
  root.removeAttribute('data-theme');
  root.style.colorScheme = 'light';
  // CSS will use :root defaults
}
