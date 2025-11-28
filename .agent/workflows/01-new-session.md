# Workflow: New Session Start

**Purpose:** Boot sequence for AI agents at session start (Full version)
**Time:** 30 seconds (automated) or 2 minutes (manual)
**Note:** For faster startup, use `/00-start` workflow instead

---

## Quick Start (Automated - Recommended)

```powershell
# Run smart-resume script (30 seconds)
.\.dev\scripts\smart-resume-enhanced.ps1
```

**What it loads:**
- Project state (MVP plan + current status)
- Today's journal (current work)
- Test status (auto vs manual validation)
- Git status (uncommitted changes)
- Sprint context (weekly deliverables)

**After script runs:** Jump to [Step 3: Propose Actions](#step-3-propose-actions)

---

## Manual Start (If Script Not Available)

### Step 1: Health Check (30 seconds)

**Check Docker services:**
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

**Expected output:**
- 24+ containers running (workspace services + synapse)
- All status: "Up X minutes/hours"

**If NOT running:**
```powershell
.\dev.ps1    # Windows - starts everything
```

---

### Step 2: Load Context (90 seconds)

**Read these files in order:**

#### 2.1 Project State (ALWAYS FIRST)
```
File: .dev/context/project-state.md
What: Current MVP status, 4-week plan, version info
Focus: Read "🎯 MVP Action Plan" section
```

#### 2.2 Today's Journal (IF EXISTS)
```
File: .dev/journal/YYYY-MM/YYYY-MM-DD.md
What: Today's work log, completed tasks, blockers
Focus: "In Progress" and "Next Session" sections
```

#### 2.3 Test Status
```
File: .dev/testing/test-status.md
What: Feature validation status (auto vs manual)
Focus: ⚠️ Pending and ❌ Failed items
```

#### 2.4 Current Sprint
```
File: .dev/roadmap/current-sprint.md
What: Active sprint goals and deliverables
Focus: Current week tasks
```

#### 2.5 Git Branch Check (CRITICAL)

**AVANT tout développement, vérifier la branche:**
```bash
git branch --show-current
```

**Si sur `main` ou `master`:**
```
⚠️ ATTENTION: Vous êtes sur la branche 'main'.
Le développement direct sur main est INTERDIT.

Actions requises:
1. Créer une branche: git checkout -b feat/<description>
2. Ou basculer sur existante: git checkout <branch-name>

Quelle branche voulez-vous utiliser?
```

**NE PAS commencer à coder tant que sur main!**

#### 2.6 Git Status
```bash
git status --short
git log --oneline -5
```

---

### Step 3: Propose Actions

**Based on context loaded, propose 2-3 options:**

**Example 1 - MVP Week 1 in progress:**
```
I see we're in MVP Week 1 (UI Foundation + Import CSV).

Options:
1. Continue UI Foundation (Days 1-2)
   - Install Shadcn/ui dependencies
   - Create AppLayout.tsx component
   - Setup dark theme

2. Work on CSV Import (Days 3-5)
   - Create backend endpoint POST /api/v1/import/csv
   - Implement CSV parser
   - Create upload UI component

3. Review and fix pending tests
   - 3 features marked ⚠️ in test-status.md need manual validation

Which would you like to focus on?
```

**Example 2 - Blocked or unclear:**
```
I see there are 2 blocked items in test-status.md.

Options:
1. Debug blocked features
   - Review error logs
   - Fix failing tests

2. Continue with unblocked work
   - Move to next MVP week task

3. Update documentation
   - Document blockers in journal
   - Create issue tickets

What should we tackle first?
```

**Example 3 - No active work:**
```
All tasks for MVP Week 1 are complete! ✅

Options:
1. Start MVP Week 2 (Rule Engine + Workflow Logs)
   - Review Week 2 checklist
   - Setup event sourcing infrastructure

2. Polish Week 1 work
   - Code review
   - Performance optimization
   - Documentation

3. Plan ahead
   - Review Week 3 requirements
   - Prepare architecture decisions

What would you like to do?
```

---

## Step 4: Wait for User Decision

**DO NOT:**
- ❌ Start implementing without approval
- ❌ Make architecture decisions alone
- ❌ Push code without asking
- ❌ Guess when requirements are ambiguous

**DO:**
- ✅ Present options with context
- ✅ Ask clarifying questions
- ✅ Wait for explicit user instruction
- ✅ Confirm understanding before proceeding

---

## Step 5: Begin Work

**Once user confirms direction:**

1. **Update todo list** (if using TodoWrite)
2. **Follow appropriate workflow:**
   - New feature → `/10-new-feature-mvp`
   - API endpoint → `/11-new-api-endpoint`
   - React component → `/12-new-react-component`
   - Test validation → `/13-test-validation`
   - Docker rebuild → `/14-docker-rebuild`
3. **Track progress** in `.dev/testing/test-status.md`
4. **Log work** in `.dev/journal/YYYY-MM/YYYY-MM-DD.md`

---

## Session End Checklist

Before ending session:

- [ ] Update test-status.md (mark ✅ completed, ⚠️ pending, ❌ failed)
- [ ] Update today's journal with progress
- [ ] Commit changes with conventional commits (feat:, fix:, docs:)
- [ ] Note blockers or "Next Session" tasks in journal
- [ ] Propose what to work on next time

**Conventional Commit Format:**
```bash
git commit -m "feat: implement [feature]

- [Brief description of changes]
- [Tests status]

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Troubleshooting

### Docker not running
**Symptom:** `docker ps` shows no containers or error
**Fix:** Run `.\dev.ps1` or manually start workspace then synapse

### Files not found
**Symptom:** `.dev/context/project-state.md` not found
**Fix:** You're in wrong directory. Run `cd d:\Projects\EPCB-Tools`

### Git issues
**Symptom:** `git status` fails
**Fix:** Check if you're in a git repository. Run `git status` to verify.

### Smart resume script fails
**Symptom:** PowerShell script errors
**Fix:** Run script with: `powershell -ExecutionPolicy Bypass -File .\.dev\scripts\smart-resume-enhanced.ps1`

---

## Quick Reference

| Need | Command/File |
|------|--------------|
| Load context (auto) | `.\.dev\scripts\smart-resume-enhanced.ps1` |
| Project state | `.dev/context/project-state.md` |
| Today's work | `.dev/journal/YYYY-MM/YYYY-MM-DD.md` |
| Test tracking | `.dev/testing/test-status.md` |
| Start Docker | `.\dev.ps1` |
| Stop Docker | `.\stop.ps1` |
| Git status | `git status --short` |
| Recent commits | `git log --oneline -5` |

---

## Example Session Flow

```
1. User starts session
   └─> AI runs smart-resume script (or reads files manually)

2. AI loads context
   └─> Project state: MVP Week 1 in progress
   └─> Today's journal: 3 tasks completed, 2 pending
   └─> Test status: 1 feature ⚠️ needs validation
   └─> Git: 5 uncommitted files

3. AI proposes actions
   └─> "I see 3 options: continue UI, start CSV, or validate tests"

4. User chooses
   └─> "Let's validate the pending test"

5. AI follows workflow
   └─> Uses /13-test-validation
   └─> Updates test-status.md
   └─> Logs in journal

6. Session ends
   └─> AI updates journal
   └─> Creates commit
   └─> Proposes next session tasks
```

---

**Version:** 1.1 (Merged from 01-smart-resume + 10-new-session)
**Last Updated:** 2025-11-25
**Related Workflows:** `/10-new-feature-mvp`, `/13-test-validation`, `/14-docker-rebuild`
