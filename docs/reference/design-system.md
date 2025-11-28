# SYNAPSE Design System

Dark theme design system for consistent UI.

---

## Color Palette

### Backgrounds
| Usage | Class | Hex |
|-------|-------|-----|
| Main page | `bg-slate-950` | #0f172a |
| Cards, panels | `bg-slate-900` | #1e293b |
| Hover states | `bg-slate-800` | #334155 |

### Text
| Usage | Class | Hex |
|-------|-------|-----|
| Primary | `text-white` / `text-slate-100` | #f1f5f9 |
| Secondary | `text-slate-400` | #94a3b8 |
| Muted | `text-slate-500` | #64748b |

### Borders
| Usage | Class | Hex |
|-------|-------|-----|
| Default | `border-slate-700` | #334155 |
| Hover | `border-slate-600` | #475569 |

### Brand (Mining Teal)
| Usage | Class | Hex |
|-------|-------|-----|
| Primary | `teal-500` | #14b8a6 |
| Hover | `teal-600` | #0d9488 |
| Light | `teal-400` | #2dd4bf |

### Status Colors
| Status | Class | Hex |
|--------|-------|-----|
| Success | `green-500` | #10b981 |
| Warning | `amber-500` | #f59e0b |
| Error | `red-500` | #ef4444 |
| Info | `blue-500` | #3b82f6 |

---

## Component Patterns

### AG Grid (Tables)

Always use alpine-dark theme:

```tsx
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

<div className="ag-theme-alpine-dark h-full">
  <AgGridReact {...props} />
</div>
```

### Panels / Cards

```tsx
<div className="bg-slate-900 border border-slate-700 rounded-lg shadow-xl">
  {/* Content */}
</div>
```

### Inputs

```tsx
<input
  className="bg-slate-900 border border-slate-700 text-white
             focus:ring-2 focus:ring-teal-500 rounded px-3 py-2"
/>
```

### Buttons

```tsx
// Primary
<button className="bg-teal-500 hover:bg-teal-600 text-white px-4 py-2 rounded">
  Action
</button>

// Secondary
<button className="bg-slate-800 hover:bg-slate-700 text-white border border-slate-600 px-4 py-2 rounded">
  Cancel
</button>

// Danger
<button className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded">
  Delete
</button>
```

### Select / Dropdown

```tsx
<select className="bg-slate-900 border border-slate-700 text-white rounded px-3 py-2">
  <option>Option 1</option>
</select>
```

---

## Accessibility (WCAG)

### Contrast Ratios

| Text | Background | Ratio | Status |
|------|------------|-------|--------|
| slate-100 | slate-950 | 15.8:1 | AAA |
| slate-400 | slate-950 | 8.3:1 | AAA |
| teal-500 | slate-950 | 5.2:1 | AA |

All combinations meet WCAG AA minimum (4.5:1 for normal text).

---

## Validation Checklist

Before creating any UI component:

- [ ] Uses `slate-950` or `slate-900` backgrounds
- [ ] Text is `white`, `slate-100`, or `slate-400`
- [ ] AG Grid uses `ag-theme-alpine-dark`
- [ ] Borders use `slate-700`
- [ ] Accent/brand uses `teal-500`
- [ ] Status colors follow the palette
- [ ] Meets WCAG AA contrast requirements

---

## Common Patterns

### Page Layout
```tsx
<div className="min-h-screen bg-slate-950">
  <header className="bg-slate-900 border-b border-slate-700">
    {/* Navigation */}
  </header>
  <main className="p-6">
    {/* Content */}
  </main>
</div>
```

### Sidebar
```tsx
<aside className="w-64 bg-slate-900 border-r border-slate-700 h-screen">
  {/* Navigation items */}
</aside>
```

### Data Table Container
```tsx
<div className="bg-slate-900 rounded-lg border border-slate-700 p-4">
  <div className="ag-theme-alpine-dark h-[600px]">
    <AgGridReact {...props} />
  </div>
</div>
```
