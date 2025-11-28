# Development Tracking System

**AI-Assisted development tracking for SYNAPSE**

---

## 🎯 Purpose

Track development progress, decisions, and releases in a structured, searchable format.

**Inspired by:** Linear, Anthropic, Vercel, Basecamp SHAPE UP

---

## 📁 Structure

```
.dev/
├── journal/                 # Daily development logs
├── decisions/               # Architecture Decision Records (ADR)
├── roadmap/                 # Sprint planning & tracking
├── releases/                # Release notes & plans
├── context/                 # AI context files
├── scripts/                 # Automation scripts
└── README.md                # This file
```

---

## 📝 Daily Workflow

### 1. Start Session

Open journal: `.dev/journal/YYYY-MM/YYYY-MM-DD.md`

Template (VS

Code):
- Type `devlog` + Tab (if snippet installed)
- Or copy from previous day

### 2. Work

- Log progress in journal
- Create ADR for big decisions
- Update current sprint

### 3. End Session

- Complete journal (✅ done, ⏭️ next)
- Update `context/project-state.md`
- Commit `.dev/` to git

---

## 🏷️ Version Management

### Current Version

See `VERSION` file at project root.

### Bump Version

```powershell
.\dev\scripts\bump-version.ps1 -Type [major|minor|patch]
```

This auto-updates:
- VERSION file
- package.json
- backend __version__
- CHANGELOG.md

### Create Release

```powershell
.\dev\scripts\create-release.ps1 -Version X.Y.Z
```

Creates release notes template in `.dev/releases/`

---

## 📚 File Types

### Journal (`journal/YYYY-MM-DD.md`)

Daily development log:
- Objective
- Accomplished
- Decisions
- Problems
- Metrics
- Next steps

**Why:** Historical record, searchable

### ADR (`decisions/XXX-title.md`)

Architecture Decision Records:
- Context
- Decision
- Consequences
- Alternatives

**Format:** [Standard ADR](https://adr.github.io/)

**Why:** Document important decisions with rationale

### Roadmap (`roadmap/current-sprint.md`)

Sprint tracking:
- Goals
- Scope (bets)
- Progress
- Blockers

**Format:** SHAPE UP inspired

**Why:** Track sprint health, velocity

### Releases (`releases/vX.Y.Z.md`)

Release notes:
- Highlights
- Features
- Fixes
- Migration guide

**Format:** User-friendly + technical

**Why:** Clear communication of changes

### Context (`context/project-state.md`)

Current project state:
- Architecture summary
- What's working
- Known issues
- Recent changes

**Why:** AI agents get instant context

---

## 🛠️ Scripts

### bump-version.ps1

Bump version across project:
```powershell
.\dev\scripts\bump-version.ps1 -Type minor
# Updates: VERSION, package.json, __init__.py, CHANGELOG
# Creates: Git commit + tag
```

### generate-changelog.ps1

Auto-generate CHANGELOG from git:
```powershell
.\dev\scripts\generate-changelog.ps1 -Version 0.3.0
# Parses: Git commits (Conventional Commits format)
# Generates: CHANGELOG section
```

### create-release.ps1

Full release workflow:
```powershell
.\dev\scripts\create-release.ps1 -Version 0.3.0
# Creates: Release notes template
# Builds: Docker images
# Guides: Through release process
```

---

## 🔍 Searching

**Find anything:**
```
Ctrl+Shift+F in VS Code
Search in: .dev/
```

**Examples:**
- "rule engine" → Find all decisions, logs about rules
- "2025-11-23" → Find that day's work
- "bug" → Find all bug fixes logged

---

## 📊 Best Practices

### Journal
- ✅ Write as you go (not at end)
- ✅ Be specific (file names, line numbers)
- ✅ Include metrics (time, files changed)
- ❌ Don't just list tasks

### ADR
- ✅ Write when decision is made (not after)
- ✅ Include alternatives considered
- ✅ Link to related docs/code
- ❌ Don't document trivial choices

### Roadmap
- ✅ Update daily (burn-down)
- ✅ Be honest about reality
- ✅ Document blockers immediately
- ❌ Don't just track tasks (use GitHub for that)

---

## 🤖 For AI Agents

**Read on session start:**
1. `.dev/context/project-state.md` - Current state
2. `.dev/journal/YYYY-MM/YYYY-MM-DD.md` - Today's log
3. `.dev/roadmap/current-sprint.md` - Sprint status

**Update during work:**
- Journal (continuously)
- Project state (when things change)
- Sprint (when progress made)

**Create as needed:**
- ADR (for decisions)
- Release notes (for versions)

---

## 📖 References

- [ADR](https://adr.github.io/) - Architecture Decision Records
- [Keep a Changelog](https://keepachangelog.com/) - Changelog format
- [SemVer](https://semver.org/) - Semantic Versioning
- [SHAPE UP](https://basecamp.com/shapeup) - Sprint methodology
- [Conventional Commits](https://www.conventionalcommits.org/) - Commit format

---

**Questions?** See examples in existing files or ask in discussions.
