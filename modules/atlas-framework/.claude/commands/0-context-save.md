# Save Context Checkpoint

Create a checkpoint of the current session context for recovery.

## Arguments

- `$ARGUMENTS` - Optional note describing what was accomplished

## What to Save

1. **Session State**
   - Current agent
   - Agent stack
   - Session ID

2. **Project State**
   - Current working directory
   - Git branch and commit
   - Uncommitted changes count

3. **Token Usage**
   - Input/Output/Cache tokens
   - Total cost
   - Message count

4. **Work Summary**
   - Recent files modified
   - User's note (from arguments)

## Execution

Run the context save utility:

```bash
node .claude/lib/context/index.js save $ARGUMENTS
```

## Output Format

After saving, display:

```
✅ Context Checkpoint Saved!
═══════════════════════════════════════════════════════

📋 ID: ctx-1701234567890
📅 Time: 2025-12-03 10:15:00
📁 Project: AXIOM
🌿 Git: main (a1b2c3d)
🤖 Agent: BACKEND-BUILDER
📊 Tokens: 50,000 (25 messages)
💰 Cost: $1.25

📝 Note: Completed API endpoints for user auth

📍 Saved to: ~/.atlas/context/checkpoint-1701234567890.json

───────────────────────────────────────────────────────
💡 Tip: Use /0-context-restore to load this checkpoint
```

## Use Cases

1. **Before /compact** - Save state before compressing context
2. **End of work session** - Checkpoint progress
3. **Before risky changes** - Create restore point
4. **Handoff** - Document state for future sessions

## Related Commands

- `/0-context-restore` - Restore from checkpoint
- `/0-session-save` - Full session save (more comprehensive)
- `/0-session-checkpoint` - Quick checkpoint during work
