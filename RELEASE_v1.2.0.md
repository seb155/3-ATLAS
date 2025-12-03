# 🏛️ ATLAS Framework v1.2.0

**AI Agent Orchestration Framework for Claude Code**

---

## ✨ What's New

### 🏛️ Visual Branding System

A beautiful temple-style ASCII banner now greets you at session start:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🏛️  ATLAS FRAMEWORK v1.2  •  AI Agent Orchestration  🤖            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### 📊 StatusLine v2.1 with Emojis

Modern, compact status line showing everything at a glance:

```
🏛️ ATLAS │ 🧠 Opus │ 🏗️ AXIOM/backend │ 🌿 main*3 │ 🔧 BACKEND │ 💰 $1.2 │ 📝 75.6K │ ⏱️ 0:12
```

**Features:**
- 🧠 Model detection (Opus/Sonnet/Haiku)
- 📁 Monorepo support (project + subdirectory)
- 🌿 Git branch + changed files count
- 🤖 Active agent tracking
- 💰 Compact cost ($1.2 instead of $1.25)
- 📝 Token count (75.6K format)
- ⏱️ Duration (H:MM format)

### 🤖 Agent Tracking System

Real-time tracking of which agent is active using a **stack pattern**:

- `PreToolUse` hook captures agent launches
- `SubagentStop` hook handles returns
- Supports nested agents (ATLAS → BACKEND → DEBUGGER → BACKEND → ATLAS)
- State persisted in `~/.claude/session-state.json`

---

## 📦 Supported Projects & Agents

### Projects (11)

| Project | Emoji | Project | Emoji |
|---------|-------|---------|-------|
| AXIOM | 🏗️ | CORTEX | 🔮 |
| NEXUS | 🧠 | FORGE | 🔥 |
| SYNAPSE | ⚡ | PRISM | 💎 |
| ATLAS | 🏛️ | PERSO | 👤 |
| FINDASH | 💰 | HOMELAB | 🖥️ |
| HA | 🏠 | (other) | 📁 |

### Agents (16)

| Agent | Emoji | Agent | Emoji |
|-------|-------|-------|-------|
| ATLAS | 🥇 | DEBUGGER | 🐛 |
| GENESIS | 🧬 | PLANNER | 📋 |
| BRAINSTORM | 💡 | DOC-WRITER | 📝 |
| BACKEND | 🔧 | UX-DESIGNER | 🎯 |
| FRONTEND | 🎨 | OPUS-DIRECT | ⭐ |
| DEVOPS | 🐳 | SONNET-DIRECT | 🔵 |
| EXPLORE | 🔍 | PLAN | 📐 |

---

## 🔧 Technical Details

- **Platform:** Linux/WSL (Bash scripts)
- **Dependencies:** `jq` for JSON parsing
- **Hooks:** PreToolUse, SubagentStop, SessionStart, SessionEnd
- **State:** `~/.claude/session-state.json`

---

## 📥 Installation

```bash
# Clone to your projects directory
git clone https://github.com/seb155/atlas-framework.git

# Create symlink in your project
ln -s /path/to/atlas-framework/.claude /your/project/.claude

# Install jq (required)
sudo apt install -y jq
```

---

## 📚 Documentation

- [CLI Customization Guide](docs/cli-customization.md)
- [Session Management](docs/session-management.md)
- [Agent Standards](docs/agent-standards.md)
- [Commands Reference](docs/commands-reference.md)

---

## 🙏 Credits

Built with Claude Code by [seb155](https://github.com/seb155)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
