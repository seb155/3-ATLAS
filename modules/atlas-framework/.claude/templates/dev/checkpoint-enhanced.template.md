# Checkpoint: {timestamp}

**Type:** {checkpoint_type}
**Created:** {created_date}
**Project:** {project_name}
**Session:** {session_description}
**Branch:** {git_branch}

---

## Active Todos (Complete State)

### In Progress
{todos_in_progress}

### Pending
{todos_pending}

### Completed This Session
{todos_completed}

---

## Git State

### Branch
{git_branch}

### Status Summary
```
{git_status}
```

### Staged Changes
```
{git_staged_diff}
```

### Unstaged Changes
```
{git_unstaged_diff}
```

### Full Diff (if needed)
<details>
<summary>Click to expand full diff</summary>

```diff
{git_full_diff}
```

</details>

---

## Files Modified This Session

| File | Action | Purpose |
|------|--------|---------|
{modified_files_table}

---

## Key Decisions Made

| Decision | Rationale | Files Affected |
|----------|-----------|----------------|
{decisions_table}

---

## Current Focus

**Task:** {current_task}
**Progress:** {task_progress}
**Next Step:** {next_step}
**Blockers:** {blockers}

---

## Context Summary

{context_summary}

---

## Open Questions

{open_questions}

---

## Recovery Instructions

Pour reprendre exactement ou j'etais:

1. Executer `/0-resume`
2. Ce fichier sera detecte comme dernier checkpoint
3. Charger aussi: `.dev/context/hot-context.md`
4. Ouvrir les fichiers: {hot_files_list}
5. Reprendre la tache: {current_task}

### Quick Recovery Command
```
/0-resume
```

---

## Recommended Compact Instructions

Si tu dois faire `/compact`, utilise ces instructions:

```
{recommended_compact_instructions}
```

---

## Session Files Reference

- Hot context: `.dev/context/hot-context.md`
- Session: `.dev/1-sessions/active/current-session.md`
- Decisions: `.dev/context/decisions.md`
- Journal: `.dev/journal/{journal_date}.md`

---

*Checkpoint created by: {created_by}*
*Reason: {checkpoint_reason}*
