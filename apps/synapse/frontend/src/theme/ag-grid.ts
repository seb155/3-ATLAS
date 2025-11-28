import { themeQuartz } from 'ag-grid-community';

/**
 * Official AG Grid Quartz Theme with Synapse branding
 * 
 * This theme uses colorSchemeVariable (default) which automatically
 * switches between light/dark based on the data-ag-theme-mode attribute
 * on any parent element.
 * 
 * Usage: Set data-ag-theme-mode="dark" or "light" on the grid container
 */
export const synapseTheme = themeQuartz.withParams({
    // Synapse brand accent (Teal)
    accentColor: '#14b8a6',

    // Typography
    fontFamily: "'Inter', system-ui, sans-serif",
    fontSize: 13,
    headerFontSize: 11,
    headerFontWeight: 600,

    // Row Hover
    rowHoverColor: 'rgba(255, 255, 255, 0.05)',
});
