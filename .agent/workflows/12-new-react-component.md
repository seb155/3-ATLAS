---
description: Generate React component following project patterns
---

# Prompt Template: New React Component

**Purpose:** Generate React component following project patterns
**Version:** 1.0
**Pattern Reference:** Existing components in `apps/synapse/frontend/src/components/`

---

## Template

```
Create a React component with the following characteristics:

**Component:** [ComponentName]
**Location:** src/components/[category]/[ComponentName].tsx
**Description:** [Functional description]

**Requirements:**
1. **TypeScript:** Strict mode, no 'any' types
2. **Props Interface:** With JSDoc comments
3. **UI Library:** Shadcn/ui components (Button, Input, Card, etc.)
4. **Styling:** TailwindCSS with VSCode dark theme palette
5. **State Management:** Zustand store (if needed)
6. **Error Handling:** Error boundaries, loading states
7. **Accessibility:** ARIA labels, keyboard navigation
8. **Tests:** Vitest + Testing Library (>70% coverage)
9. **No Modals:** Use pages, panels, or inline forms instead

**UI Guidelines:**
- Dark theme: VSCode color palette (slate-900 background)
- Consistent spacing (p-4, gap-4, etc.)
- Loading states with skeleton or spinner
- Error states with toast notifications (Sonner)
- Responsive design (mobile-first)

**Component Categories:**
- `components/ui/` - Shadcn base components (Button, Input, etc.)
- `components/layout/` - Layout containers (AppLayout, Sidebar, etc.)
- `components/domain/` - Business components (reusable across features)
- `components/features/` - Feature-specific components

**Example Structure:**
```tsx
import React from 'react';
import { Button } from '@/components/ui/button';
import { useFeatureStore } from '@/stores/useFeatureStore';

interface ComponentNameProps {
  /** Description of prop */
  propName: string;
  /** Optional callback */
  onAction?: () => void;
}

/**
 * ComponentName - Brief description
 *
 * @example
 * <ComponentName propName="value" />
 */
export const ComponentName: React.FC<ComponentNameProps> = ({
  propName,
  onAction
}) => {
  const { data, loading, error, fetchData } = useFeatureStore();

  React.useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="p-4 bg-slate-900 text-slate-100">
      <h2 className="text-xl font-semibold mb-4">{propName}</h2>
      <Button onClick={onAction}>Action</Button>
    </div>
  );
};
```

**Follow patterns from:** Existing components in project
**Code Guidelines:** See `docs/contributing/code-guidelines.md`
```

---

## Example Usage

### User Fills Template:
```
Create a React component with the following characteristics:

**Component:** AssetListPanel
**Location:** src/components/features/assets/AssetListPanel.tsx
**Description:** Display list of assets with filters, search, and export

**Requirements:**
[...as above...]

**Additional Details:**
- Display assets in a table (use Shadcn Table component)
- Support search by tag, type, location
- Export to CSV/Excel
- Inline editing (no modals)
- Multi-tenancy filter (automatic via X-Project-ID header)
```

### AI Generates:

**1. Component** (`src/components/features/assets/AssetListPanel.tsx`):
```tsx
import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Download, Search } from 'lucide-react';
import { useAssetStore } from '@/stores/useAssetStore';
import { Asset } from '@/types/asset';

interface AssetListPanelProps {
  /** Optional filter by asset type */
  filterType?: string;
  /** Callback when asset is selected */
  onSelectAsset?: (asset: Asset) => void;
}

/**
 * AssetListPanel - Display and manage assets with search and export
 *
 * Features:
 * - Search by tag, type, location
 * - Export to CSV/Excel
 * - Inline editing
 * - Multi-tenancy filtering (automatic)
 *
 * @example
 * <AssetListPanel filterType="INSTRUMENT" onSelectAsset={handleSelect} />
 */
export const AssetListPanel: React.FC<AssetListPanelProps> = ({
  filterType,
  onSelectAsset
}) => {
  const { assets, loading, error, fetchAssets, exportAssets } = useAssetStore();
  const [searchTerm, setSearchTerm] = React.useState('');

  React.useEffect(() => {
    fetchAssets(filterType);
  }, [fetchAssets, filterType]);

  const filteredAssets = React.useMemo(() => {
    if (!searchTerm) return assets;
    return assets.filter(asset =>
      asset.tag.toLowerCase().includes(searchTerm.toLowerCase()) ||
      asset.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      asset.location?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [assets, searchTerm]);

  const handleExport = async () => {
    await exportAssets(filteredAssets, 'csv');
  };

  if (loading) {
    return (
      <div className="p-4 bg-slate-900 text-slate-100">
        <div className="animate-pulse space-y-4">
          <div className="h-10 bg-slate-800 rounded"></div>
          <div className="h-64 bg-slate-800 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-slate-900 text-red-400">
        Error loading assets: {error}
      </div>
    );
  }

  return (
    <div className="p-4 bg-slate-900 text-slate-100">
      {/* Header with search and export */}
      <div className="flex items-center gap-4 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
          <Input
            type="text"
            placeholder="Search assets (tag, type, location)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 bg-slate-800 border-slate-700 text-slate-100"
          />
        </div>
        <Button
          onClick={handleExport}
          variant="outline"
          className="border-slate-700 hover:bg-slate-800"
        >
          <Download className="w-4 h-4 mr-2" />
          Export CSV
        </Button>
      </div>

      {/* Assets Table */}
      <div className="border border-slate-800 rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-800 border-slate-700">
              <TableHead className="text-slate-300">Tag</TableHead>
              <TableHead className="text-slate-300">Type</TableHead>
              <TableHead className="text-slate-300">Location</TableHead>
              <TableHead className="text-slate-300">Description</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredAssets.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-slate-400 py-8">
                  No assets found
                </TableCell>
              </TableRow>
            ) : (
              filteredAssets.map((asset) => (
                <TableRow
                  key={asset.id}
                  onClick={() => onSelectAsset?.(asset)}
                  className="border-slate-800 hover:bg-slate-800/50 cursor-pointer"
                >
                  <TableCell className="font-mono text-blue-400">{asset.tag}</TableCell>
                  <TableCell className="text-slate-300">{asset.type}</TableCell>
                  <TableCell className="text-slate-300">{asset.location}</TableCell>
                  <TableCell className="text-slate-400 text-sm">{asset.description}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Footer with count */}
      <div className="mt-4 text-sm text-slate-400">
        Showing {filteredAssets.length} of {assets.length} assets
      </div>
    </div>
  );
};
```

**2. Type Definitions** (`src/types/asset.ts`):
```typescript
export interface Asset {
  id: string;
  project_id: string;
  tag: string;
  type: string;
  location?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}
```

**3. Zustand Store** (`src/stores/useAssetStore.ts`):
```typescript
import { create } from 'zustand';
import { Asset } from '@/types/asset';
import { assetService } from '@/services/assetService';

interface AssetStore {
  assets: Asset[];
  loading: boolean;
  error: string | null;
  fetchAssets: (filterType?: string) => Promise<void>;
  exportAssets: (assets: Asset[], format: 'csv' | 'excel') => Promise<void>;
}

export const useAssetStore = create<AssetStore>((set) => ({
  assets: [],
  loading: false,
  error: null,

  fetchAssets: async (filterType) => {
    set({ loading: true, error: null });
    try {
      const assets = await assetService.getAssets(filterType);
      set({ assets, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  exportAssets: async (assets, format) => {
    try {
      await assetService.exportAssets(assets, format);
    } catch (error) {
      set({ error: error.message });
    }
  },
}));
```

**4. Tests** (`src/components/features/assets/AssetListPanel.test.tsx`):
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AssetListPanel } from './AssetListPanel';
import { useAssetStore } from '@/stores/useAssetStore';

vi.mock('@/stores/useAssetStore');

describe('AssetListPanel', () => {
  const mockAssets = [
    {
      id: '1',
      project_id: 'proj-1',
      tag: 'FT-101',
      type: 'INSTRUMENT',
      location: 'Area A',
      description: 'Flow transmitter',
      created_at: '2025-11-25T10:00:00Z',
      updated_at: '2025-11-25T10:00:00Z',
    },
    {
      id: '2',
      project_id: 'proj-1',
      tag: 'PT-102',
      type: 'INSTRUMENT',
      location: 'Area B',
      description: 'Pressure transmitter',
      created_at: '2025-11-25T10:00:00Z',
      updated_at: '2025-11-25T10:00:00Z',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    useAssetStore.mockReturnValue({
      assets: mockAssets,
      loading: false,
      error: null,
      fetchAssets: vi.fn(),
      exportAssets: vi.fn(),
    });
  });

  it('renders asset list', () => {
    render(<AssetListPanel />);
    expect(screen.getByText('FT-101')).toBeInTheDocument();
    expect(screen.getByText('PT-102')).toBeInTheDocument();
  });

  it('filters assets by search term', async () => {
    render(<AssetListPanel />);
    const searchInput = screen.getByPlaceholderText(/search assets/i);

    fireEvent.change(searchInput, { target: { value: 'FT-101' } });

    await waitFor(() => {
      expect(screen.getByText('FT-101')).toBeInTheDocument();
      expect(screen.queryByText('PT-102')).not.toBeInTheDocument();
    });
  });

  it('calls exportAssets on export button click', async () => {
    const mockExportAssets = vi.fn();
    useAssetStore.mockReturnValue({
      assets: mockAssets,
      loading: false,
      error: null,
      fetchAssets: vi.fn(),
      exportAssets: mockExportAssets,
    });

    render(<AssetListPanel />);
    const exportButton = screen.getByText(/export csv/i);

    fireEvent.click(exportButton);

    await waitFor(() => {
      expect(mockExportAssets).toHaveBeenCalledWith(mockAssets, 'csv');
    });
  });

  it('displays loading state', () => {
    useAssetStore.mockReturnValue({
      assets: [],
      loading: true,
      error: null,
      fetchAssets: vi.fn(),
      exportAssets: vi.fn(),
    });

    render(<AssetListPanel />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('displays error state', () => {
    useAssetStore.mockReturnValue({
      assets: [],
      loading: false,
      error: 'Failed to fetch assets',
      fetchAssets: vi.fn(),
      exportAssets: vi.fn(),
    });

    render(<AssetListPanel />);
    expect(screen.getByText(/error loading assets/i)).toBeInTheDocument();
  });

  it('calls onSelectAsset when row is clicked', () => {
    const onSelectAsset = vi.fn();
    render(<AssetListPanel onSelectAsset={onSelectAsset} />);

    const row = screen.getByText('FT-101').closest('tr');
    fireEvent.click(row);

    expect(onSelectAsset).toHaveBeenCalledWith(mockAssets[0]);
  });
});
```

---

## Checklist for AI

Before presenting code, verify:
- [ ] TypeScript strict mode (no 'any')
- [ ] Props interface with JSDoc comments
- [ ] Shadcn/ui components used
- [ ] TailwindCSS with VSCode dark theme (slate-900, slate-800, slate-700)
- [ ] Loading state implemented
- [ ] Error state implemented
- [ ] Zustand store for state management (if needed)
- [ ] No modals (use inline forms, panels, pages)
- [ ] Tests cover rendering, interactions, edge cases
- [ ] Tests achieve >70% coverage
- [ ] ARIA labels and keyboard navigation
- [ ] Responsive design (mobile-first)
- [ ] Follows patterns from existing components

---

## VSCode Dark Theme Palette

```css
/* Background */
bg-slate-900    /* Main background */
bg-slate-800    /* Secondary background (cards, inputs) */
bg-slate-700    /* Tertiary background (hover states) */

/* Text */
text-slate-100  /* Primary text */
text-slate-300  /* Secondary text (labels) */
text-slate-400  /* Tertiary text (placeholders, hints) */

/* Borders */
border-slate-800  /* Default border */
border-slate-700  /* Hover border */

/* Accents */
text-blue-400   /* Links, tags, primary actions */
text-red-400    /* Errors, warnings */
text-green-400  /* Success states */
text-yellow-400 /* Warnings, pending states */
```

---

## Component Category Guide

### `components/ui/` - Shadcn Base Components
**Examples:** Button, Input, Card, Table, Dialog, Select, Checkbox
**Usage:** Import and use as-is, customize with TailwindCSS classes
**Pattern:** Copy from shadcn/ui CLI, do NOT modify source

### `components/layout/` - Layout Containers
**Examples:** AppLayout, Sidebar, Header, Footer, Panel
**Usage:** Structural components that compose the app shell
**Pattern:** Use Allotment for resizable panes, React Mosaic for split views

### `components/domain/` - Business Components (Reusable)
**Examples:** AssetCard, CableRow, RuleEditor, WorkflowTimeline
**Usage:** Reusable across features, domain-specific logic
**Pattern:** Accept data via props, emit events via callbacks

### `components/features/` - Feature-Specific Components
**Examples:** AssetListPanel, CSVImportPanel, PackageExportPanel
**Usage:** Feature-specific, not reusable elsewhere
**Pattern:** Use Zustand stores, compose domain components

---

**Version:** 1.0
**Last Updated:** 2025-11-25
