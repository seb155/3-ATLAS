/**
 * Central export point for all theme definitions
 * Import from here to get access to all pre-built themes
 */

// Dark themes
export { nordDark } from './prebuilt/dark/nord';
export { draculaDark } from './prebuilt/dark/dracula';
export { tokyoNightDark } from './prebuilt/dark/tokyo-night';
export { oneDark } from './prebuilt/dark/one-dark';
export { gruvboxDark } from './prebuilt/dark/gruvbox-dark';
export { catppuccinMocha } from './prebuilt/dark/catppuccin-mocha';

// Light themes
export { githubLight } from './prebuilt/light/github-light';
export { solarizedLight } from './prebuilt/light/solarized-light';
export { gruvboxLight } from './prebuilt/light/gruvbox-light';
export { catppuccinLatte } from './prebuilt/light/catppuccin-latte';
export { oneLight } from './prebuilt/light/one-light';
export { tokyoDay } from './prebuilt/light/tokyo-day';

// Custom/Corporate themes
export { gminingCorporate } from './prebuilt/custom/gmining';

// Utilities
export { applyTheme, getActiveThemeId, resetTheme } from './utils/applyTheme';
export { hexToHsl, isValidHex, rgbToHex } from './utils/hexToHsl';
export { validateTheme, validateThemeJSON, isLightColor } from './utils/validateTheme';

// Pre-built themes array for iteration/gallery
import type { ThemeDefinition } from '@/types/theme.types';
import { nordDark } from './prebuilt/dark/nord';
import { draculaDark } from './prebuilt/dark/dracula';
import { tokyoNightDark } from './prebuilt/dark/tokyo-night';
import { oneDark } from './prebuilt/dark/one-dark';
import { gruvboxDark } from './prebuilt/dark/gruvbox-dark';
import { catppuccinMocha } from './prebuilt/dark/catppuccin-mocha';
import { githubLight } from './prebuilt/light/github-light';
import { solarizedLight } from './prebuilt/light/solarized-light';
import { gruvboxLight } from './prebuilt/light/gruvbox-light';
import { catppuccinLatte } from './prebuilt/light/catppuccin-latte';
import { oneLight } from './prebuilt/light/one-light';
import { tokyoDay } from './prebuilt/light/tokyo-day';
import { gminingCorporate } from './prebuilt/custom/gmining';

export const PREBUILT_THEMES: ThemeDefinition[] = [
  // Dark themes first
  nordDark,
  draculaDark,
  tokyoNightDark,
  oneDark,
  gruvboxDark,
  catppuccinMocha,
  // Light themes
  githubLight,
  solarizedLight,
  gruvboxLight,
  catppuccinLatte,
  oneLight,
  tokyoDay,
  // Custom/Corporate
  gminingCorporate,
];

/**
 * Find a theme by ID
 */
export function findThemeById(id: string): ThemeDefinition | undefined {
  return PREBUILT_THEMES.find((theme) => theme.id === id);
}

/**
 * Get all dark themes
 */
export function getDarkThemes(): ThemeDefinition[] {
  return PREBUILT_THEMES.filter((theme) => theme.type === 'dark');
}

/**
 * Get all light themes
 */
export function getLightThemes(): ThemeDefinition[] {
  return PREBUILT_THEMES.filter((theme) => theme.type === 'light');
}

/**
 * Get themes grouped by type
 */
export function getThemesByType(): { dark: ThemeDefinition[]; light: ThemeDefinition[] } {
  return {
    dark: getDarkThemes(),
    light: getLightThemes(),
  };
}
