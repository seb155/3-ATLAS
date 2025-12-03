# zz-init-cli

Skill pour initialiser la customisation CLI Claude Code avec status line Powerline.

## Usage

Ce skill est utilise par la commande `/1-init-cli` pour creer les fichiers necessaires.

---

## File Templates

### ~/.claude/settings.json

Merge avec la config existante:

```json
{
  "model": "opus",
  "alwaysThinkingEnabled": true,
  "theme": "dark",
  "statusLine": {
    "type": "command",
    "command": "npx ccstatusline@latest",
    "padding": 0
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -ExecutionPolicy Bypass -File \"$env:USERPROFILE\\.claude\\hooks\\track-agent.ps1\""
          }
        ]
      }
    ]
  }
}
```

---

### ~/.claude/atlas-agent.ps1

```powershell
# Atlas Agent Detector for ccstatusline
# Detecte l'agent Atlas actif via fichier session ou variable d'environnement

$sessionFile = "$env:USERPROFILE\.claude\session-state.json"

if (Test-Path $sessionFile) {
    try {
        $session = Get-Content $sessionFile -Raw | ConvertFrom-Json
        $agent = if ($session.active_agent) { $session.active_agent } else { "ATLAS" }
    } catch {
        $agent = "ATLAS"
    }
} else {
    $agent = if ($env:ATLAS_AGENT) { $env:ATLAS_AGENT } else { "ATLAS" }
}

Write-Host $agent
```

---

### ~/.claude/detect-project.ps1

```powershell
# Project Detector for Atlas Monorepo
# Detecte le projet actif dans le monorepo D:\Projects

param(
    [Parameter(ValueFromPipeline=$true)]
    [string]$InputJson
)

# Lire le JSON depuis stdin si fourni
if (-not $InputJson) {
    $InputJson = [Console]::In.ReadToEnd()
}

try {
    $data = $InputJson | ConvertFrom-Json
    $cwd = $data.workspace.current_dir
} catch {
    $cwd = Get-Location
}

# Mapping des projets avec emojis
# AXIOM sub-apps (check first for more specific matches)
$axiomApps = @{
    "synapse"       = "🧬 SYNAPSE"
    "nexus"         = "🔗 NEXUS"
    "prism"         = "📊 PRISM"
    "atlas"         = "🗺️ ATLAS"
    "forge"         = "🔨 FORGE"
}

# Main projects
$projects = @{
    "AXIOM"         = "⚙️ AXIOM"
    "FinDash"       = "💹 FinDash"
    "Homelab_MSH"   = "🏠 Homelab"
    "HomeAssistant" = "🏡 HA-MCP"
    "Note_synch"    = "📔 NoteSync"
    "atlas-agent"   = "⚡ Atlas"
}

$detected = "📁 ROOT"

# Check AXIOM sub-apps first (more specific)
if ($cwd -match "AXIOM[/\\]apps[/\\]") {
    foreach ($key in $axiomApps.Keys) {
        if ($cwd -match [regex]::Escape($key)) {
            $detected = $axiomApps[$key]
            break
        }
    }
} else {
    # Check main projects
    foreach ($key in $projects.Keys) {
        if ($cwd -match [regex]::Escape($key)) {
            $detected = $projects[$key]
            break
        }
    }
}

Write-Host $detected
```

---

### ~/.claude/hooks/track-agent.ps1

```powershell
# Hook: Track Active Atlas Agent
# Triggered by PreToolUse on Task tool to track which agent is active

# Lire le JSON depuis stdin
$inputJson = [Console]::In.ReadToEnd()

try {
    $data = $inputJson | ConvertFrom-Json
    $agent = $data.tool_input.subagent_type

    if ($agent) {
        # Sauvegarder l'agent actif dans le fichier session
        $sessionState = @{
            active_agent = $agent
            timestamp = (Get-Date).ToString("o")
            tool_name = $data.tool_name
        }

        $sessionFile = "$env:USERPROFILE\.claude\session-state.json"
        $sessionState | ConvertTo-Json | Set-Content $sessionFile -Encoding UTF8
    }
} catch {
    # Silently ignore errors to not block Claude Code
    exit 0
}
```

---

### ~/.config/ccstatusline/settings.json

```json
{
  "powerlineMode": true,
  "powerlineOptions": {
    "separator": "\ue0b0",
    "leftCap": "\ue0b6",
    "rightCap": "\ue0b4"
  },
  "globalOptions": {
    "padding": true,
    "bold": false,
    "useBackground": true
  },
  "widgets": [
    {
      "type": "customText",
      "text": "⚡ ATLAS",
      "foreground": "#FFFFFF",
      "background": "#2D3436",
      "bold": true
    },
    {
      "type": "separator"
    },
    {
      "type": "model",
      "label": "🧠",
      "foreground": "#FFFFFF",
      "background": "#6C5CE7"
    },
    {
      "type": "separator"
    },
    {
      "type": "customCommand",
      "command": "powershell -NoProfile -ExecutionPolicy Bypass -File C:\\Users\\sgagn\\.claude\\detect-project.ps1",
      "foreground": "#FFFFFF",
      "background": "#00B894"
    },
    {
      "type": "separator"
    },
    {
      "type": "gitBranch",
      "label": "🌿",
      "foreground": "#FFFFFF",
      "background": "#FDCB6E"
    },
    {
      "type": "separator"
    },
    {
      "type": "customCommand",
      "command": "powershell -NoProfile -ExecutionPolicy Bypass -File C:\\Users\\sgagn\\.claude\\atlas-agent.ps1",
      "label": "🤖",
      "foreground": "#FFFFFF",
      "background": "#E17055"
    },
    {
      "type": "flexSeparator"
    },
    {
      "type": "contextPercentage",
      "label": "📊",
      "foreground": "#FFFFFF",
      "background": "#0984E3",
      "showRemaining": true
    },
    {
      "type": "separator"
    },
    {
      "type": "sessionCost",
      "label": "💰",
      "foreground": "#FFFFFF",
      "background": "#00CEC9"
    },
    {
      "type": "separator"
    },
    {
      "type": "tokenTotal",
      "label": "📝",
      "foreground": "#FFFFFF",
      "background": "#636E72"
    }
  ]
}
```

---

## Widgets Reference

| Widget | Emoji | Couleur | Description |
|--------|-------|---------|-------------|
| Branding | ⚡ | #2D3436 | ATLAS Framework identifier |
| Model | 🧠 | #6C5CE7 | AI model (Opus, Sonnet) |
| Project | Variable | #00B894 | Detected project with emoji |
| Git | 🌿 | #FDCB6E | Current branch |
| Agent | 🤖 | #E17055 | Active Atlas agent |
| Context | 📊 | #0984E3 | Remaining context % |
| Cost | 💰 | #00CEC9 | Session cost USD |
| Tokens | 📝 | #636E72 | Total tokens |

---

## Project Emojis

### AXIOM Sub-Apps

| Project | Emoji |
|---------|-------|
| SYNAPSE | 🧬 |
| NEXUS | 🔗 |
| PRISM | 📊 |
| ATLAS | 🗺️ |
| FORGE | 🔨 |

### Other Projects

| Project | Emoji |
|---------|-------|
| AXIOM | ⚙️ |
| FinDash | 💹 |
| Homelab | 🏠 |
| HA-MCP | 🏡 |
| NoteSync | 📔 |
| Atlas | ⚡ |
| ROOT | 📁 |

---

## Validation Checklist

Apres creation, verifier:

- [ ] `~/.claude/settings.json` a la config statusLine
- [ ] `~/.claude/atlas-agent.ps1` est executable
- [ ] `~/.claude/detect-project.ps1` est executable
- [ ] `~/.claude/hooks/track-agent.ps1` existe
- [ ] `~/.config/ccstatusline/settings.json` existe
- [ ] JetBrainsMono Nerd Font installe
- [ ] Windows Terminal configure avec Nerd Font

---

## Related

- `/1-init-cli` - Commande d'initialisation
- `.claude/docs/cli-customization.md` - Documentation complete
