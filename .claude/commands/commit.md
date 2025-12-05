# /commit

Create a commit with Conventional Commits format.

## Usage

```bash
/commit              # Auto-generate commit message
/commit [message]    # Use specified message
/commit --amend      # Amend last commit
```

---

## Conventional Commits Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Commit Types

| Type | Description | Version Impact |
|------|-------------|----------------|
| `feat` | New feature | MINOR bump |
| `fix` | Bug fix | PATCH bump |
| `docs` | Documentation only | No bump |
| `style` | Formatting (no code change) | No bump |
| `refactor` | Code restructure | No bump |
| `test` | Adding/updating tests | No bump |
| `chore` | Maintenance tasks | No bump |
| `perf` | Performance improvement | PATCH bump |
| `ci` | CI/CD configuration | No bump |
| `build` | Build system changes | No bump |
| `revert` | Revert previous commit | Depends |

### Scope (optional)

The scope provides context. Examples:
- `feat(api):` - API-related feature
- `fix(auth):` - Auth module fix
- `docs(readme):` - README update
- `refactor(ui):` - UI refactoring

---

## Breaking Changes

For breaking changes, add `!` after type or include footer:

```bash
# Option 1: Bang notation
feat(api)!: change response format

# Option 2: Footer
feat(api): change response format

BREAKING CHANGE: Response now returns array instead of object
```

---

## Examples

### Feature
```
feat(auth): add JWT token refresh endpoint

- Add /auth/refresh endpoint
- Implement token rotation
- Add refresh token to response

Closes #123
```

### Bug Fix
```
fix(database): resolve connection pool exhaustion

The pool was not releasing connections after timeout.
Added explicit cleanup in finally block.

Fixes #456
```

### Documentation
```
docs(api): update authentication examples

- Add curl examples for all endpoints
- Include error response samples
```

### Refactor
```
refactor(utils): extract date formatting to shared module

No functional changes. Moved formatDate, parseDate, and
getTimestamp functions to shared/dateUtils.ts
```

---

## Workflow

1. **Analyze changes**
   ```
   [HH:MM] ▶ Analyzing staged changes...

   Files: 3 modified, 1 new
   - src/api/auth.ts (modified)
   - src/api/auth.test.ts (modified)
   - src/utils/jwt.ts (new)
   - README.md (modified)
   ```

2. **Detect type and scope**
   ```
   [HH:MM] ▶ Detected: feat(auth)

   Reason: New file jwt.ts + changes to auth module
   ```

3. **Generate message**
   ```
   [HH:MM] ▶ Proposed commit message:

   feat(auth): add JWT token utilities

   - Add generateToken function
   - Add verifyToken function
   - Add token expiration handling
   - Update auth endpoint to use new utilities
   ```

4. **Confirm and commit**
   ```
   [HH:MM] ✓ Committed: abc1234
   ```

---

## Output Format

```
╔══════════════════════════════════════════════════════════════╗
║  /commit | 2025-11-29 14:30                                   ║
╚══════════════════════════════════════════════════════════════╝

[14:30] ▶ Analyzing changes...
        Files: 3 modified, 1 new

[14:30] ▶ Type detected: feat
        Scope detected: auth

[14:30] ▶ Proposed message:
        ─────────────────────────────────────────
        feat(auth): add JWT token utilities

        - Add generateToken function
        - Add verifyToken function
        - Add token expiration handling
        ─────────────────────────────────────────

[14:30] ✓ Committed: abc1234
```

---

## Best Practices

1. **One logical change per commit** - Don't mix unrelated changes
2. **Present tense** - "add feature" not "added feature"
3. **Imperative mood** - "fix bug" not "fixes bug"
4. **Clear and concise** - First line under 72 characters
5. **Reference issues** - Include `Fixes #123` or `Closes #456`

---

**Tip:** Let Atlas analyze your changes for the best commit message!
