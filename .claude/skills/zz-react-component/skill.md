# Skill: React Component

Cree un composant React complet avec TypeScript, store Zustand, et tests.

## Usage

```text
/skill react-component [ComponentName]
```

## Templates Generes

1. `Component.tsx` - Composant React
2. `store.ts` - Store Zustand (si stateful)
3. `Component.test.tsx` - Tests Vitest

## Exemple

```text
/skill react-component NotificationList

Genere:
- src/components/notifications/NotificationList.tsx
- src/stores/notificationStore.ts
- src/components/notifications/NotificationList.test.tsx
```

## Structure Component

```tsx
import { useEffect } from 'react';
import { use{Component}Store } from '@/stores/{component}Store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

interface {Component}Props {
  className?: string;
}

export function {Component}({ className }: {Component}Props) {
  const { items, isLoading, error, fetchItems } = use{Component}Store();

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive">
        <CardContent className="pt-6">
          <p className="text-destructive">{error}</p>
          <Button onClick={fetchItems} variant="outline" className="mt-4">
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{Component}</CardTitle>
      </CardHeader>
      <CardContent>
        {items.map((item) => (
          <div key={item.id} className="py-2 border-b last:border-0">
            {item.name}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
```

## Structure Store

```ts
import { create } from 'zustand';
import { api } from '@/lib/api';

interface {Item} {
  id: number;
  name: string;
}

interface {Component}State {
  items: {Item}[];
  isLoading: boolean;
  error: string | null;
  fetchItems: () => Promise<void>;
  addItem: (item: {Item}) => void;
  removeItem: (id: number) => void;
}

export const use{Component}Store = create<{Component}State>((set) => ({
  items: [],
  isLoading: false,
  error: null,

  fetchItems: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.get('/{items}/');
      set({ items: response.data, isLoading: false });
    } catch (error) {
      set({ error: 'Failed to fetch items', isLoading: false });
    }
  },

  addItem: (item) =>
    set((state) => ({ items: [...state.items, item] })),

  removeItem: (id) =>
    set((state) => ({ items: state.items.filter((i) => i.id !== id) })),
}));
```

## Structure Test

```tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { {Component} } from './{Component}';

vi.mock('@/stores/{component}Store', () => ({
  use{Component}Store: () => ({
    items: [{ id: 1, name: 'Test Item' }],
    isLoading: false,
    error: null,
    fetchItems: vi.fn(),
  }),
}));

describe('{Component}', () => {
  it('renders items', async () => {
    render(<{Component} />);
    await waitFor(() => {
      expect(screen.getByText('Test Item')).toBeInTheDocument();
    });
  });

  it('shows loading state', () => {
    vi.mocked(use{Component}Store).mockReturnValue({
      items: [],
      isLoading: true,
      error: null,
      fetchItems: vi.fn(),
    });
    render(<{Component} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
});
```
