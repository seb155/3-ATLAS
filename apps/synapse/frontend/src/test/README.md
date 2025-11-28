# Frontend Tests

Quick reference for running tests in SYNAPSE frontend.

## Quick Start

```bash
# Run all tests
npm run test

# Run in watch mode (auto-rerun on changes)
npm run test:watch

# Run with coverage
npm run test:coverage

# Run with UI (interactive)
npm run test:ui
```

## Test Files

- `src/test/useLogStore.test.ts` - Example: Testing Zustand store
- More tests to be added as features are developed

## Writing New Tests

See [`docs/developer-guide/08-testing.md`](../../docs/developer-guide/08-testing.md) for comprehensive guide.

**Quick template - Component test**:

```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MyComponent } from './MyComponent'

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent title="Test" />)
    
    expect(screen.getByText('Test')).toBeInTheDocument()
  })
})
```

**Quick template - Hook test**:

```typescript
import { renderHook, act } from '@testing-library/react'
import { useMyHook } from './useMyHook'

describe('useMyHook', () => {
  it('updates state correctly', () => {
    const { result } = renderHook(() => useMyHook())
    
    act(() => {
      result.current.setValue('test')
    })
    
    expect(result.current.value).toBe('test')
  })
})
```

## Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| UI Components | 70%+ | - |
| Hooks/Stores | 80%+ | - |
| Utilities | 95%+ | - |

Run `npm run test:coverage` to check current coverage.

## Troubleshooting

**Tests not running?**
```bash
# Reinstall dependencies
npm install
```

**Import errors?**
- Check that `vitest.config.ts` path aliases match your imports
- Ensure all dependencies are installed

**DOM/React errors?**
- Make sure `@testing-library/react` is installed
- Check that `src/test/setup.ts` is configured in `vitest.config.ts`

---

**Full Documentation**: [`docs/developer-guide/08-testing.md`](../../docs/developer-guide/08-testing.md)
