---
description: Optimized session start workflow (Low Token Usage)
---

# Workflow: Fast Session Start

**Purpose:** Quick context load (< 2k tokens)
**Trigger:** Start of every session

## Step 1: Load Context (Automated)

```powershell
# Run context aggregator
.\.dev\scripts\smart-resume-lite.ps1
```

**Action:**
1. Read the JSON output from the script above.
2. **Present the "Manager Dashboard" (Status Report Style):**

```markdown
# 📊 Overview [Project] - [Phase]

**🎯 Version:** [Version]
**📅 Timeline:** [CurrentSprint]

**Progress:** [||||||....] [SprintProgress]%
**Status:** ⚠️ [Pending] Pending Tests | ❌ [Failed] Failed Tests

## 🏃 Current Sprint
- [ ] **Focus:** [ActiveGoal 1]
- [ ] **Focus:** [ActiveGoal 2]

## 📍 Where we are
- **Done:** [Summary of recent achievements from Journal]
- **Next:** [NextSessionTask 1]

## 💡 Manager's Note
- [Suggestion based on context]
```

## Step 2: Wait for User Direction

Present the dashboard and wait for user to indicate next action.

---

**Note:** This is the FAST startup workflow for Gemini/Antigravity.
For detailed context loading, use `/01-new-session` instead.
