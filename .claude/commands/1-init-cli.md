# /1-init-cli

Initialize or repair Claude Code CLI customization with Powerline status line.

## Usage

```bash
/1-init-cli              # Full setup
/1-init-cli --repair     # Repair missing files only
/1-init-cli --validate   # Check current setup
```

---

## What It Does

### Step 1: Check Prerequisites

```
Check Nerd Font installation:
  winget list --name "JetBrainsMono"

IF not installed:
    "Installing JetBrainsMono Nerd Font..."
    winget install DEVCOM.JetBrainsMonoNerdFont

Check Windows Terminal font config (manual step)
```

### Step 2: Create Scripts

Create the following in `~/.claude/`:

1. **atlas-agent.ps1** - Agent detection
2. **detect-project.ps1** - Project detection
3. **hooks/track-agent.ps1** - Agent tracking hook

Use skill `zz-init-cli` for file templates.

### Step 3: Configure settings.json

Merge with existing `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "npx ccstatusline@latest",
    "padding": 0
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task",
        "hooks": [{
          "type": "command",
          "command": "powershell -ExecutionPolicy Bypass -File \"$env:USERPROFILE\\.claude\\hooks\\track-agent.ps1\""
        }]
      }
    ]
  }
}
```

### Step 4: Configure ccstatusline

Create `~/.config/ccstatusline/settings.json` with Powerline widgets.

### Step 5: Validate

Check all files exist and are valid.

---

## Output

```
CLI Customization Setup

Prerequisites:
  Nerd Font: [installed/missing]

Scripts:
  ~/.claude/atlas-agent.ps1: [created/exists/error]
  ~/.claude/detect-project.ps1: [created/exists/error]
  ~/.claude/hooks/track-agent.ps1: [created/exists/error]

Configuration:
  ~/.claude/settings.json: [configured]
  ~/.config/ccstatusline/settings.json: [configured]

Status: [Success/Partial/Failed]

Next steps:
1. Restart Claude Code to see the new status line
2. Configure Windows Terminal font to JetBrainsMono Nerd Font
```

---

## Repair Mode (--repair)

Only creates missing files, doesn't overwrite existing ones.

```bash
/1-init-cli --repair
```

---

## Validate Mode (--validate)

Checks current setup without making changes.

```bash
/1-init-cli --validate
```

Output:
```
CLI Customization Validation

[OK] Nerd Font installed
[OK] ~/.claude/atlas-agent.ps1 exists
[OK] ~/.claude/detect-project.ps1 exists
[OK] ~/.claude/hooks/track-agent.ps1 exists
[OK] ~/.claude/settings.json has statusLine config
[OK] ~/.config/ccstatusline/settings.json exists

Status: All checks passed
```

---

## Troubleshooting

### Permission Denied

Run PowerShell as Administrator or:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ccstatusline Not Found

```bash
npm install -g ccstatusline
# or use npx (no install needed)
```

### Status Line Not Showing

1. Restart Claude Code
2. Check settings.json has statusLine config
3. Run `/1-init-cli --validate`

---

## Related

- `.claude/docs/cli-customization.md` - Full documentation
- `.claude/skills/zz-init-cli/skill.md` - File templates
