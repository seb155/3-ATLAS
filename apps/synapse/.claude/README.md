# SYNAPSE - Claude Code Configuration

This directory contains SYNAPSE-specific Claude Code configurations
that **override** the root `.claude/` settings.

## Layer System

```
Priority (highest wins):
├── apps/synapse/.claude/  ← App-specific (this directory)
└── .claude/               ← Root (shared)
```

## What Can Be Overridden

| Component | Override? | Example |
|-----------|-----------|---------|
| Commands | ✅ Yes | `/test` runs SYNAPSE-specific tests |
| Agent Rules | ✅ Yes | SYNAPSE-specific routing rules |
| Context | ✅ Yes | App-specific hot files |
| Agents | ❌ No | Use root agents |
| Skills | ❌ No | Use root skills |
| Hooks | ❌ No | Use root hooks |

## Current Overrides

### Commands

| Command | Purpose |
|---------|---------|
| `/test` | Run SYNAPSE test suite (backend + frontend) |

## Adding New Overrides

1. Create file in appropriate subdirectory:
   ```
   apps/synapse/.claude/commands/my-command.md
   ```

2. File will automatically override root version when working in SYNAPSE

## See Also

- Root config: `/.claude/`
- Monorepo config: `/.atlas/config.yml`
- SYNAPSE docs: `/apps/synapse/README.md`
