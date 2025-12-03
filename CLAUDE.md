# CLAUDE.md

🏛️ **ATLAS Framework** - AI Agent Orchestration for Claude Code

## Quick Start

```bash
# Link to your project
ln -s ~/atlas-framework/.claude .claude

# Start session
claude
/0-session-start
```

## Structure

| Directory | Description |
|-----------|-------------|
| `.claude/agents/` | Agent definitions (15+) |
| `.claude/commands/` | Slash commands |
| `.claude/hooks/` | Event hooks (statusline, tracking) |
| `.claude/scripts/` | Banner, statusline |
| `.claude/skills/` | Reusable skills |
| `forge/` | Docker infrastructure (optional) |

## Key Commands

| Command | Purpose |
|---------|---------|
| `/0-session-start [project]` | Start new session |
| `/0-session-continue [project]` | Continue existing session |
| `/0-session-recover [project]` | Resume after /compact |
| `/9-git-ship [project]` | Git commit + push |
| `/1-start-dev [project]` | Dev session with tracking |

**All commands support `[project-id]` to target a specific project.**

## StatusLine

```
🏛️ ATLAS │ 🧠 Opus │ 🏗️ PROJECT │ 🌿 branch │ 🔧 AGENT │ 💰 $1.2 │ 📝 75K │ ⏱️ 0:12
```

## Documentation

- [CLI Customization](.claude/docs/cli-customization.md)
- [Session Management](.claude/docs/session-management.md)
- [Full CLAUDE.md](.claude/CLAUDE.md)
