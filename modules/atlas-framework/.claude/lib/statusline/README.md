# StatusLine (Node.js)

Modern, performant status line for Claude Code, inspired by lemmy-tui's differential rendering.

## Features

- **Real token counts** from JSONL transcripts (not estimates)
- **Responsive modes** - Adapts to terminal width
- **Project detection** - Monorepo-aware
- **Agent tracking** - Shows current ATLAS agent
- **Git integration** - Branch and changes count
- **Cost calculation** - Opus 4.5 pricing

## Quick Start

### Switch to Node.js version

Update `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash /path/to/.claude/scripts/statusline-node.sh"
  }
}
```

### Test it

```bash
# Run directly
node .claude/lib/statusline/index.js

# With specific width
node .claude/lib/statusline/index.js --width 120

# Show help
node .claude/lib/statusline/index.js --help
```

## Responsive Modes

| Width    | Mode         | Example                                                    |
| -------- | ------------ | ---------------------------------------------------------- |
| < 60     | Ultra        | `💰 $0.45 │ 🟢 37%`                                        |
| 60-89    | Compact      | `🏛️ ATLAS │ 🧠 Opus │ 💰 $0.45 │ 🟢 37%`                   |
| 90-119   | Standard     | `+ 📝 75K (total tokens)`                                  |
| >= 120   | Full         | `+ 📥 5K │ 📤 2K │ 💾 68K (breakdown)`                     |

## Output Format

```
🏛️ ATLAS │ 🧠 Opus │ 🏗️ AXIOM/synapse │ 🌿 main*3 │ 🥇 ATLAS │ 📥 5K │ 📤 2K │ 💾 68K │ 💰 $0.45 │ 🟢 37% │ ⏱️ 0:15
```

| Segment    | Description              |
| ---------- | ------------------------ |
| 🏛️ ATLAS   | Framework identifier     |
| 🧠 Opus    | Current model            |
| 🏗️ PROJECT | Project (monorepo aware) |
| 🌿 branch  | Git branch + changes     |
| 🥇 ATLAS   | Current agent            |
| 📥 5K      | Input tokens             |
| 📤 2K      | Output tokens            |
| 💾 68K     | Cache tokens             |
| 💰 $0.45   | Session cost             |
| 🟢 37%     | Context usage            |
| ⏱️ 0:15    | Session duration         |

## Configuration

### Environment Variables

```bash
# Force terminal width
export ATLAS_TERM_WIDTH=150

# Override project detection
export ATLAS_PROJECT_NAME="MYPROJECT"
```

### Project Emojis

Edit the `CONFIG.projects` object in `index.js`:

```javascript
projects: {
  myproject: { emoji: "🚀", name: "MYPROJECT" },
}
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                     StatusLine                       │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ parseClaudeInput │ parseTokens │ getGitDisplay│ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
│         └────────────────┼────────────────┘         │
│                          ▼                          │
│  ┌───────────────────────────────────────────────┐ │
│  │              buildStatusLine()                 │ │
│  │   Responsive output based on terminal width    │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## Comparison: Bash vs Node.js

| Aspect      | Bash             | Node.js          |
| ----------- | ---------------- | ---------------- |
| Performance | ~50ms            | ~20ms            |
| Subshells   | Many (jq, git)   | None (native)    |
| Error handling | Basic         | Full try/catch   |
| Maintainability | Complex       | Modular          |
| Dependencies | jq, bash        | Node.js only     |

## Troubleshooting

### No tokens showing

1. Check transcript exists: `ls ~/.claude/projects/-*/`
2. Verify JSONL has usage data: `tail ~/.claude/projects/-*/latest.jsonl`

### Wrong project detected

Set explicitly:
```bash
export ATLAS_PROJECT_NAME="CORRECT_NAME"
```

### Fallback to Bash

If Node.js not available, the wrapper automatically uses the bash version.
