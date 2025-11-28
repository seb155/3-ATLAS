# Git Workflow

How to contribute code using Git.

---

## Branching Strategy

**Main branches:**
- `main` - Production-ready code
- `develop` - Integration branch

**Feature branches:**
- `feature/short-description`
- `fix/bug-description`

---

## Workflow

### 1. Create Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/my-feature
```

### 2. Make Changes

```bash
# Edit files
git add .
git commit -m "descriptive message"
```

### 3. Push

```bash
git push origin feature/my-feature
```

### 4. Create PR

- Open Pull Request on GitHub
- Target: `develop` branch
- Fill in description
- Request review

---

## Commit Messages

**Format:**
```
<type>: <subject>

<body (optional)>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Tests
- `chore:` Maintenance

**Examples:**
```
feat: add cable sizing calculator
fix: rule executor handles null properties
docs: update installation guide
```

---

## Pull Requests

**Before submitting:**
- [ ] Code follows [Code Guidelines](code-guidelines.md)
- [ ] Tests pass
- [ ] No lint errors
- [ ] Documentation updated

**PR description should include:**
- What changed
- Why it changed
- How to test

---

## Questions?

See existing PRs for examples.
