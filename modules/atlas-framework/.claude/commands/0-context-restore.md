# Restore Context Checkpoint

Restore session context from a saved checkpoint.

## Arguments

- `$ARGUMENTS` - Optional checkpoint name (default: latest)

## What Gets Restored

1. **Context Information** - Read and display saved state
2. **Work Summary** - What was being worked on
3. **Git State** - Branch and commit at checkpoint time
4. **Token Usage** - Historical usage data
5. **Todos** - Pending tasks if saved

## Execution

1. **List available checkpoints** (if no name specified):
   ```bash
   node .claude/lib/context/index.js list
   ```

2. **Restore specific checkpoint**:
   ```bash
   node .claude/lib/context/index.js restore $ARGUMENTS
   ```

## Output Format

```
🔄 Restoring Context...
═══════════════════════════════════════════════════════

📋 Context: ctx-1701234567890
📅 Saved: 2025-12-03T10:15:00.000Z
📁 Project: AXIOM
🌿 Git: main (a1b2c3d) - 3 uncommitted changes
🤖 Agent: BACKEND-BUILDER

📊 Session Stats at Checkpoint:
   • Tokens: 50,000 (25 messages)
   • Cost: $1.25

📝 Note: Completed API endpoints for user auth

📂 Recent Files:
   • src/api/auth.py
   • src/api/users.py
   • tests/test_auth.py

───────────────────────────────────────────────────────

## Recommended Actions

1. **Verify git state** - Check if branch/commit matches
2. **Review recent files** - Open files that were being edited
3. **Check todos** - Resume pending tasks
4. **Continue work** - Pick up where you left off
```

## Interactive Mode

If no checkpoint specified, offer choices:

```
📋 Available Checkpoints:

1. latest.json (2 min ago)
   📝 Completed API endpoints for user auth

2. checkpoint-1701234500000.json (1 hour ago)
   📝 Started user authentication feature

3. checkpoint-1701231000000.json (yesterday)
   📝 Database schema complete

> Select checkpoint (1-3) or type name:
```

## Use Cases

1. **After /compact** - Restore context that was lost
2. **New session** - Resume previous work
3. **Recovery** - Restore after crash or disconnect
4. **Context switch** - Return to previous task

## Related Commands

- `/0-context-save` - Create checkpoint
- `/0-session-recover` - Full session recovery
- `/0-session-continue` - Quick continue existing session
