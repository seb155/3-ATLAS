import type { ThemeDefinition } from '@/types/theme.types';
import { isValidHex } from './hexToHsl';

/**
 * Validate that a theme definition has all required fields and valid colors
 */
export function validateTheme(theme: unknown): theme is ThemeDefinition {
  if (!theme || typeof theme !== 'object') {
    console.error('Theme must be an object');
    return false;
  }

  const t = theme as any;

  // Required string fields
  if (typeof t.id !== 'string' || !t.id.trim()) {
    console.error('Theme must have a non-empty id string');
    return false;
  }

  if (typeof t.name !== 'string' || !t.name.trim()) {
    console.error('Theme must have a non-empty name string');
    return false;
  }

  if (typeof t.type !== 'string' || !['light', 'dark'].includes(t.type)) {
    console.error('Theme type must be "light" or "dark"');
    return false;
  }

  // Colors are required
  if (!t.colors || typeof t.colors !== 'object') {
    console.error('Theme must have a colors object');
    return false;
  }

  // Validate all required color properties
  const requiredColors = [
    'background',
    'foreground',
    'card',
    'cardForeground',
    'border',
    'muted',
    'mutedForeground',
    'primary',
    'primaryForeground',
    'secondary',
    'secondaryForeground',
    'accent',
    'accentForeground',
    'success',
    'successForeground',
    'warning',
    'warningForeground',
    'error',
    'errorForeground',
    'info',
    'infoForeground',
    'destructive',
    'destructiveForeground',
    'input',
    'ring',
    'chart1',
    'chart2',
    'chart3',
    'chart4',
    'chart5',
  ];

  for (const colorKey of requiredColors) {
    if (!(colorKey in t.colors)) {
      console.error(`Theme colors missing required property: ${colorKey}`);
      return false;
    }

    const color = t.colors[colorKey];
    if (typeof color !== 'string' || !isValidHex(color)) {
      console.error(`Theme color ${colorKey} must be a valid hex color, got: ${color}`);
      return false;
    }
  }

  // Optional fields are allowed but must have correct types if present
  if (t.author !== undefined && typeof t.author !== 'string') {
    console.error('Theme author must be a string if provided');
    return false;
  }

  if (t.description !== undefined && typeof t.description !== 'string') {
    console.error('Theme description must be a string if provided');
    return false;
  }

  if (t.version !== undefined && typeof t.version !== 'string') {
    console.error('Theme version must be a string if provided');
    return false;
  }

  return true;
}

/**
 * Validate a JSON string as a theme
 * Throws if invalid
 */
export function validateThemeJSON(json: string): ThemeDefinition {
  let theme: unknown;

  try {
    theme = JSON.parse(json);
  } catch (error) {
    throw new Error(`Invalid JSON: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }

  if (!validateTheme(theme)) {
    throw new Error('Theme validation failed. Check console for details.');
  }

  return theme as ThemeDefinition;
}

/**
 * Check if a color is light or dark
 * Used for accessibility contrast ratios
 */
export function isLightColor(hex: string): boolean {
  hex = hex.replace('#', '');
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);

  // Calculate luminance (WCAG standard)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.5;
}
