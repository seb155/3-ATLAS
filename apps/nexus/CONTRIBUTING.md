# Contributing to Nexus

Thank you for considering contributing to Nexus! We welcome contributions from the community.

## 🎯 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/Nexus.git
cd Nexus
```

### 2. Set Up Development Environment

```bash
# Install dependencies
cd frontend
npm install

# Start dev server
npm run dev
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## 📝 Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) for clear git history:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style (formatting, missing semicolons, etc.)
- `refactor:` Code refactoring
- `perf:` Performance improvement
- `test:` Adding or updating tests
- `chore:` Maintenance tasks
- `ci:` CI/CD changes

### Examples

```bash
feat(notes): add TipTap rich text editor
fix(sidebar): resolve navigation highlighting bug
docs(readme): update installation instructions
refactor(store): simplify state management logic
```

## 🎨 Code Style

### TypeScript

- Use TypeScript strict mode
- Prefer `interface` over `type` for object shapes
- Use type-only imports when possible: `import type { Foo } from 'bar'`
- No `any` types (use `unknown` if necessary)

### React

- Use functional components with hooks
- Prefer named exports over default exports
- Keep components small and focused
- Use composition over prop drilling

### File Structure

```
src/
├── components/
│   ├── layout/          # Layout components
│   ├── ui/              # Reusable UI components
│   └── features/        # Feature-specific components
├── pages/               # Route pages
├── stores/              # Zustand stores
├── lib/                 # Utilities and helpers
└── types/               # TypeScript type definitions
```

### Naming Conventions

- **Components:** PascalCase (`MyComponent.tsx`)
- **Hooks:** camelCase with `use` prefix (`useMyHook.ts`)
- **Stores:** camelCase with `use` prefix (`useAppStore.ts`)
- **Utils:** camelCase (`myUtil.ts`)
- **Types:** PascalCase (`MyType.ts` or in `types/index.ts`)

## ✅ Before Submitting

1. **Run linter**
   ```bash
   npm run lint
   ```

2. **Build successfully**
   ```bash
   npm run build
   ```

3. **Test your changes**
   - Manual testing in browser
   - Check responsive design
   - Test dark/light theme switching

4. **Update documentation**
   - Update README if adding features
   - Add JSDoc comments for complex functions
   - Update `.dev/` docs if relevant

## 🔄 Pull Request Process

1. **Update your branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Use a clear, descriptive title
   - Reference related issues
   - Describe what changed and why
   - Add screenshots for UI changes

### PR Template

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

## 🐛 Reporting Bugs

Use GitHub Issues with:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment (OS, browser, Node version)

## 💡 Suggesting Features

Use GitHub Issues with:
- Clear use case
- Proposed solution
- Alternative solutions considered
- Mockups/wireframes if applicable

## 📚 Documentation

- Keep documentation up to date
- Use clear, concise language
- Include code examples
- Add screenshots for UI features

## 🙏 Questions?

Feel free to open a discussion on GitHub or reach out to the maintainers.

---

**Thank you for contributing to Nexus!** 🌐
