---
description: Save context before /compact - comprehensive checkpoint
---

# /0-session-save

Prépare le contexte avant /compact en créant un checkpoint complet et générant des instructions optimales.

Utilise cette commande AVANT de lancer `/compact` pour assurer une préservation complète du contexte.

## Usage

```bash
/0-session-save              # Full pre-compact preparation
/0-session-save [focus]      # With specific focus area
```

---

## When to Use

- Before manual `/compact` when you want maximum context preservation
- When you've done significant work that might not be auto-documented
- Before risky operations where you might need to compact mid-work
- When the hook alone isn't enough (you need custom instructions)

---

## Workflow

### Step 1: Analyze Current State

```
Gather and document:
- All active todos (complete state)
- Git status (staged + unstaged + untracked)
- Git diff summary
- Files modified this session (with purpose)
- Key decisions made (documented or not)
- Current task in progress
- Open questions/blockers
```

### Step 2: Create Enhanced Checkpoint

```
Create .dev/checkpoints/[timestamp]-pre-compact-manual.md

Include:
- Full todo state (not just summary)
- Complete git diff (not just stats)
- Decision log with rationale
- Recovery instructions
- Recommended compact instructions
```

### Step 3: Update Hot Context

```
Update .dev/context/hot-context.md with:
- Current session summary
- Reference to new checkpoint
- Critical context to preserve
```

### Step 4: Generate Compact Instructions

```
Display optimal instructions for /compact:

---
RECOMMENDED COMPACT INSTRUCTIONS:

Preserve session context:
- Project: [current project]
- Checkpoint: [checkpoint path]
- Active task: [task description]

Key context:
- [Decision 1]
- [Decision 2]
- [Current blocker/question]

Files in progress:
- [file1] - [what's being done]
- [file2] - [what's being done]

Recovery: Use /0-session-recover after compact
---
```

### Step 5: Confirm Ready

```
Display:
"Pre-compact preparation complete!"

Checkpoint: [path]
Hot context: Updated
Compact instructions: Generated

Copy the instructions above and run:
/compact [paste instructions]

Or just run /compact - the PreCompact hook will create a basic checkpoint automatically.

---

What do you want to do?
1. Run /compact now (instructions copied)
2. View the checkpoint
3. Add more context manually
4. Cancel (continue working)
```

---

## Comparison with Hook

| Feature | PreCompact Hook | /0-session-save |
|---------|-----------------|-----------------|
| Automatic | Yes | No (manual) |
| Depth | Basic (git status) | Full (todos, decisions, diff) |
| Custom instructions | None | Generated |
| Interactive | No | Yes |
| Use case | Safety net | Planned compact |

**Recommendation:** Use `/0-session-save` when you know you'll compact soon and want maximum preservation. The hook is your safety net for unexpected compacts.

---

## See Also

- `/0-session-checkpoint` - Standard checkpoint (less comprehensive)
- `/0-session-recover` - Resume after compact
- `.claude/hooks/pre-compact.ps1` - Automatic hook
