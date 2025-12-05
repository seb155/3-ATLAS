# ATLAS 3.0 Hook System

Based on PAI (Personal AI Infrastructure) hook system.

## Hook Types

| Hook | Trigger | Purpose |
|------|---------|---------|
| `initialize-session` | Session start | Load context, setup environment |
| `capture-session-summary` | Session end | Archive work, generate summary |
| `capture-tool-output` | After tool use | Log tool results |
| `stop-hook` | Before stop | Cleanup, validation |
| `validate-protected` | Before file write | Protect critical files |
| `context-compression` | Context threshold | Auto-checkpoint |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Allow (continue) |
| 1 | Warning (continue with message) |
| 2 | Block (stop operation) |
| 3 | Transform (modify input) |

## Configuration

Hooks are configured in `.atlas/atlas.config.json`:

```json
{
  "core": {
    "hooks": {
      "enabled": true,
      "types": ["PreToolUse", "PostToolUse", "SessionStart", "SessionEnd"]
    }
  }
}
```

## Runtime

Hooks use Bun runtime (NOT Node.js) for performance.

```bash
bun run hooks/initialize-session.ts
```
