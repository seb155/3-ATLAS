---
description: Git workflow - test, commit, version bump, push with full GitFlow support
---

# /9-git-ship

Complete Git workflow with tests validation, versioning, and GitFlow branching.

## Usage

```bash
/9-git-ship              # Full workflow (test → commit → push)
/9-git-ship echo         # Ship ECHO project specifically
/9-git-ship --skip-tests # Skip tests (use with caution)
/9-git-ship --dry-run    # Show what would happen
```

## Arguments

- `[project-id]` (optional): Identifiant du projet cible
  - Case-insensitive
  - Résolution via Rule 31 (project-resolution.md)
- `--skip-tests`: Skip test execution
- `--dry-run`: Preview without executing

---

## Workflow Steps

### 0. Resolve Project (if argument)

```
IF project-id provided:
    Resolve via Rule 31
    Change to target project directory
    Display: "📂 Shipping: [project name]"
```

### 1. Pre-flight Checks

```
[HH:MM] ▶ Running pre-flight checks...
[HH:MM] ✓ Backend tests: 142 passed (84% coverage)
[HH:MM] ✓ Frontend tests: 89 passed
[HH:MM] ✓ Linting: No errors
[HH:MM] ✓ Build: Success
```

### 2. Git Status Analysis

```
[HH:MM] ▶ Analyzing Git status...

Branch: feature/user-auth
Files:  6 modified, 2 new
Commits: 3 local (not pushed)
```

### 3. Version Bump (if applicable)

Based on Conventional Commits:
| Commit Type | Version Bump | Example |
|-------------|--------------|---------|
| `feat:` | MINOR (0.X.0) | 0.2.0 → 0.3.0 |
| `fix:` | PATCH (0.0.X) | 0.2.0 → 0.2.1 |
| `BREAKING CHANGE:` | MAJOR (X.0.0) | 0.2.0 → 1.0.0 |
| `docs:`, `chore:` | No bump | - |

### 4. Ship It

```
[HH:MM] ✓ Committed: abc1234
[HH:MM] ✓ Tagged: v0.3.0
[HH:MM] ✓ Pushed to origin/feature/user-auth
[HH:MM] ✓ CHANGELOG.md updated

🚀 Shipped!
```

---

## Git Workflow (GitFlow)

### Branch Naming Convention

```
main              # Production-ready code
develop           # Integration branch
feature/xxx       # New features
fix/xxx           # Bug fixes
release/x.x.x     # Release preparation
hotfix/x.x.x      # Urgent production fixes
```

### Feature Development

```bash
# 1. Create feature branch from develop
git checkout develop
git checkout -b feature/user-auth

# 2. Work on feature with conventional commits
git commit -m "feat(auth): add login endpoint"
git commit -m "feat(auth): add JWT validation"

# 3. Push and create PR
git push -u origin feature/user-auth
gh pr create --base develop --title "feat: User authentication"

# 4. After merge, delete branch
git branch -d feature/user-auth
```

---

## Commit Message Format

```
<type>(<scope>): <short description>

[optional body - what and why]

[optional footer - breaking changes, issues]

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Types

| Type | Description | Version Impact |
|------|-------------|----------------|
| `feat` | New feature | MINOR |
| `fix` | Bug fix | PATCH |
| `docs` | Documentation only | None |
| `style` | Formatting, no code change | None |
| `refactor` | Code restructure | None |
| `test` | Adding tests | None |
| `chore` | Maintenance tasks | None |
| `perf` | Performance improvement | PATCH |
| `ci` | CI/CD changes | None |

---

## Safety Checks

Before push, `/9-git-ship` verifies:

| Check | Required | Skip with |
|-------|----------|-----------|
| Tests pass | ✅ Yes | `--skip-tests` |
| Lint clean | ✅ Yes | - |
| Build success | ✅ Yes | - |
| Branch valid | ✅ Yes | - |
| No secrets | ✅ Yes | - |

**If any check fails** → Abort with detailed error message

---

## Output Format

```
╔══════════════════════════════════════════════════════════════╗
║  /9-git-ship | 2025-11-29 14:30 | Project: ECHO              ║
╚══════════════════════════════════════════════════════════════╝

[14:30] ▶ Running tests...
[14:31] ✓ Backend: 142 passed (2.3s)
[14:31] ✓ Frontend: 89 passed (1.8s)
[14:31] ✓ Lint: Clean

[14:31] ▶ Analyzing commits...
        - feat(auth): add login endpoint
        - feat(auth): add JWT validation

[14:31] ▶ Version bump: 0.2.0 → 0.3.0 (MINOR)

[14:32] ✓ Committed: abc1234
[14:32] ✓ Tagged: v0.3.0
[14:32] ✓ Pushed to origin

── Summary ───────────────────────────────────────────────────
Tests:   231 passed
Version: v0.3.0
Commits: 2
Time:    2m 14s

🚀 Successfully shipped!
```

---

## See Also

- `/9-session-archive` - Archive current session
- `/0-view-status` - Check status before shipping
- Rule 31 - Project ID resolution

**Tip:** Use `/9-git-ship` when your work is ready. It handles everything!
