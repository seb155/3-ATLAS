# Development Session - YYYY-MM-DD HH:MM

**Focus:** [Brief description of main goal]
**Sprint:** MVP Week [1-4]
**Start Time:** HH:MM
**Date Format:** YYYY-MM-DD HH:MM (Example: 2025-11-28 14:30)

---

## Session 1: [HH:MM]-[HH:MM]

### Context
- **Previous session status:** [Summary from last session]
- **Today's goal:** [What needs to be done]
- **Blockers:** [Any issues from last session]

### AI Generated
- ⚠️ [Feature/Component name] (AUTO-TESTED - result pending)
- ⚠️ [Feature/Component name] (AUTO-TESTED - result pending)
- ⚠️ [Feature/Component name] (NEEDS MANUAL TEST)

### Manual Validation Required
- [ ] [Test description - what to verify]
- [ ] [Test description - edge cases]
- [ ] [Test description - performance]

### Completed
- ✅ [Task name] - AUTO-TESTED, MANUAL VALIDATED
- ✅ [Task name] - AUTO-TESTED, MANUAL VALIDATED

### Blockers
- [Blocker description] OR "None"

### Next Session
- [Task to continue]
- [Task to start]
- [Issue to fix]

---

## Session 2: [HH:MM]-[HH:MM]

### Context
- **Continued from:** Session 1 - [brief status]
- **Focus:** [Specific goal for this session]

### AI Generated
- ⚠️ [Feature/Component name] (AUTO-TESTED - result pending)
- ⚠️ [Feature/Component name] (NEEDS MANUAL TEST)

### Manual Validation Required
- [ ] [Test description]

### Completed
- ✅ [Task name] - VALIDATED

### Blockers
- [Blocker description] OR "None"

### Next Session
- [Task to continue]

---

## Session 3: [HH:MM]-[HH:MM]

### Context
- **Continued from:** Session 2 - [brief status]
- **Focus:** [Specific goal for this session]

### AI Generated
- ⚠️ [Feature/Component name]

### Manual Validation Required
- [ ] [Test description]

### Completed
- ✅ [Task name]

### Blockers
- [Blocker description] OR "None"

### Next Session
- [Task to continue]

---

## Daily Summary

### Total Time
- Session 1: [duration]
- Session 2: [duration]
- Session 3: [duration]
- **Total:** [X hours]

### Key Achievements
1. [Major accomplishment]
2. [Major accomplishment]
3. [Major accomplishment]

### Test Status Updates
Updated `.dev/testing/test-status.md`:
- [Feature name]: TODO → IN PROGRESS
- [Feature name]: IN PROGRESS → DONE
- [Feature name]: AUTO-TESTED (✅ passed)

### Git Activity
```bash
# Commits made today
git log --oneline --since="today" --author="[Your Name]"

# Example output:
# abc1234 feat: implement AppLayout component with VSCode-like shell
# def5678 test: add vitest tests for AppLayout component
# ghi9012 docs: update test-status.md with AppLayout validation
```

### Files Created/Modified
- ✅ `apps/synapse/frontend/src/components/layout/AppLayout.tsx` (NEW)
- ✅ `apps/synapse/frontend/src/components/layout/AppLayout.test.tsx` (NEW)
- ✅ `.dev/testing/test-status.md` (UPDATED)

### Issues Encountered
1. [Issue description] - RESOLVED: [Solution]
2. [Issue description] - BLOCKED: [Waiting for...]

### Tomorrow's Plan
1. [Priority 1 task]
2. [Priority 2 task]
3. [Priority 3 task]

---

## Notes & Learnings

### Technical Notes
- [Note about pattern used, library discovered, etc.]
- [Note about decision made]

### AI Collaboration Notes
- [What worked well with AI]
- [What needed more clarification]
- [Prompt that worked particularly well]

### Reminders
- [ ] [Action item for tomorrow]
- [ ] [Follow-up needed]

---

**End Time:** HH:MM
**Duration:** [Calculate: End - Start]
**Status:** [ON TRACK / BEHIND / AHEAD]
**Next Focus:** [Brief description for next session]

---

## Timestamp Format (IMPORTANT)

**Always use:** `YYYY-MM-DD HH:MM`
- Example: `2025-11-28 14:30`
- Never just date without time
- Never just time without date

---

## Emoji Legend

**Status:**
- ✅ Completed and validated
- ⚠️ Pending validation
- ❌ Failed or blocked
- 🔄 In progress
- 🚫 Blocked by external factor

**Test Results:**
- AUTO-TESTED: AI-generated tests ran (check results)
- MANUAL VALIDATED: User confirmed working
- NEEDS MANUAL TEST: Awaiting user validation
