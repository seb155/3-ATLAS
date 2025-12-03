# Nexus Developer Guide

Welcome to the Nexus developer guide! This documentation is for anyone who wants to contribute to Nexus.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Workflow](#development-workflow)
3. [Code Style](#code-style)
4. [Testing](#testing)
5. [Documentation](#documentation)
6. [Pull Requests](#pull-requests)

---

## Getting Started

### Prerequisites

Ensure you have the following installed:
- **Node.js 18+** ([Download](https://nodejs.org/))
- **npm** (comes with Node.js)
- **Git** ([Download](https://git-scm.com/))
- **(Phase 2+) Python 3.11+** for backend
- **(Phase 2+) PostgreSQL 15+** for database
- **(Phase 2+) Redis 7+** for caching

### Quick Setup

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/Nexus.git
cd Nexus

# 3. Install dependencies
cd frontend
npm install

# 4. Start development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

**[→ Detailed Setup Guide](setup.md)**

---

## Development Workflow

### 1. Create a Branch

Always work on a feature branch:

```bash
# For new features
git checkout -b feature/add-amazing-feature

# For bug fixes
git checkout -b fix/fix-critical-bug

# For documentation
git checkout -b docs/improve-readme
```

### 2. Make Your Changes

Edit files, add features, fix bugs, improve docs.

### 3. Test Your Changes

```bash
# Run linter
npm run lint

# Build to check for errors
npm run build

# (Future) Run tests
npm test
```

### 4. Commit Your Changes

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat: add dark mode toggle"
```

**Commit Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code formatting
- `refactor:` Code restructuring
- `perf:` Performance improvement
- `test:` Adding tests
- `chore:` Maintenance

### 5. Push and Create PR

```bash
git push origin feature/add-amazing-feature
```

Then create a Pull Request on GitHub.

---

## Code Style

### TypeScript

```typescript
// ✅ Good - Use interfaces for objects
interface User {
  id: string
  name: string
  email: string
}

// ✅ Good - Use type-only imports
import type { ReactNode } from 'react'

// ✅ Good - Explicit return types for functions
function getUser(id: string): User | null {
  // ...
}

// ❌ Bad - Don't use 'any'
function process(data: any) { // Avoid
  // ...
}

// ✅ Good - Use 'unknown' instead
function process(data: unknown) {
  // Type guard first
  if (typeof data === 'string') {
    // ...
  }
}
```

### React Components

```typescript
// ✅ Good - Functional components with types
interface ButtonProps {
  label: string
  onClick: () => void
  variant?: 'primary' | 'secondary'
}

export function Button({ label, onClick, variant = 'primary' }: ButtonProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'px-4 py-2 rounded',
        variant === 'primary' ? 'bg-primary' : 'bg-secondary'
      )}
    >
      {label}
    </button>
  )
}

// ❌ Bad - Default exports
export default function Button() { ... }
```

### File Naming

- **Components:** PascalCase - `MyComponent.tsx`
- **Hooks:** camelCase with `use` - `useMyHook.ts`
- **Utils:** camelCase - `formatDate.ts`
- **Types:** PascalCase - `User.ts` or in `types/index.ts`
- **Stores:** camelCase with `use` - `useAppStore.ts`

### Directory Structure

```
src/
├── components/
│   ├── layout/          # Layout components
│   ├── ui/              # Reusable UI components
│   └── features/        # Feature-specific components
├── pages/               # Route pages
├── stores/              # Zustand stores
├── lib/                 # Utilities
├── hooks/               # Custom hooks
└── types/               # TypeScript types
```

**[→ Full Code Style Guide](code-style.md)**

---

## Testing

### Current Status

Phase 1 doesn't have automated tests yet. We'll add them in future phases.

### Future Testing Strategy

**Unit Tests:**
- Vitest for unit tests
- React Testing Library for component tests
- >70% code coverage goal

**E2E Tests:**
- Playwright for end-to-end tests
- Critical user flows covered

**Example:**
```typescript
// __tests__/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from '@/components/ui/Button'

describe('Button', () => {
  it('renders and handles clicks', () => {
    const handleClick = vi.fn()
    render(<Button label="Click me" onClick={handleClick} />)

    const button = screen.getByText('Click me')
    fireEvent.click(button)

    expect(handleClick).toHaveBeenCalledOnce()
  })
})
```

**[→ Full Testing Guide](testing.md)**

---

## Documentation

### Documentation Standards

1. **Code Comments**
   - Only for complex logic
   - Explain "why", not "what"
   - Use JSDoc for public APIs

2. **README Files**
   - Every major directory should have a README
   - Explain purpose and usage

3. **Inline Documentation**
   - Type definitions are self-documenting
   - Use descriptive variable names

### Example: JSDoc

```typescript
/**
 * Formats a date string to a human-readable format
 *
 * @param date - ISO 8601 date string
 * @param locale - Locale for formatting (default: 'en-US')
 * @returns Formatted date string
 *
 * @example
 * formatDate('2025-11-27') // "November 27, 2025"
 */
export function formatDate(date: string, locale = 'en-US'): string {
  return new Date(date).toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
```

---

## Pull Requests

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All linters pass (`npm run lint`)
- [ ] Build succeeds (`npm run build`)
- [ ] Tests pass (when we have them)
- [ ] Documentation updated
- [ ] Commit messages follow Conventional Commits

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested locally
- [ ] Tested responsive design
- [ ] Tested dark/light themes

## Screenshots
(if applicable)

## Related Issues
Fixes #123
```

### Review Process

1. **Automated Checks** - Linters, build, tests
2. **Code Review** - At least one maintainer reviews
3. **Discussion** - Address feedback
4. **Approval** - Merge when approved
5. **CI/CD** - Automated deployment (future)

---

## Development Tips

### Hot Reload

Vite provides instant HMR. Save a file and see changes immediately.

### Path Aliases

Use `@/*` instead of relative imports:

```typescript
// ✅ Good
import { Button } from '@/components/ui/Button'

// ❌ Avoid
import { Button } from '../../../components/ui/Button'
```

### Debugging

**React DevTools:**
- Install [React DevTools](https://react.dev/learn/react-developer-tools)
- Inspect component tree
- View props and state

**VSCode Extensions:**
- ESLint
- Tailwind CSS IntelliSense
- TypeScript Vue Plugin (Volar)

### Performance

**Bundle Analysis:**
```bash
npm run build -- --mode analyze
```

**React Profiler:**
- Use React DevTools Profiler
- Identify slow renders
- Optimize with `React.memo`, `useMemo`, `useCallback`

---

## Getting Help

### Resources

- **Documentation:** [docs/](../)
- **GitHub Issues:** [Report bugs](https://github.com/seb155/Nexus/issues)
- **Discussions:** [Ask questions](https://github.com/seb155/Nexus/discussions)

### Common Issues

**Port already in use:**
- Change port in `vite.config.ts`

**Module not found:**
- Run `npm install`
- Check imports use `@/` prefix

**TypeScript errors:**
- Check `tsconfig.json`
- Ensure types are imported with `import type`

---

## Contributing Checklist

Before your first contribution:

- [ ] Read [CONTRIBUTING.md](../../CONTRIBUTING.md)
- [ ] Fork the repository
- [ ] Clone your fork locally
- [ ] Set up development environment
- [ ] Read code style guide
- [ ] Understand project architecture
- [ ] Join GitHub Discussions

For each contribution:

- [ ] Create feature branch
- [ ] Make changes
- [ ] Test locally
- [ ] Commit with conventional commits
- [ ] Push to your fork
- [ ] Create pull request
- [ ] Address review feedback

---

## Advanced Topics

### Backend Development (Phase 2+)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**[→ Backend Setup Guide](setup.md#backend-setup)**

### Database Migrations (Phase 2+)

```bash
# Create migration
alembic revision --autogenerate -m "Add users table"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Docker Development (Future)

```bash
docker-compose up -d
```

**[→ Deployment Guide](deployment.md)**

---

## License

Nexus is MIT licensed. See [LICENSE](../../LICENSE).

---

**Ready to contribute?** Check out [open issues](https://github.com/seb155/Nexus/issues) labeled `good first issue`!

---

**[⬆ Back to Docs Home](../README.md)**

*Last Updated: 2025-11-27*
