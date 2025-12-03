# CLI Customization Guide

Guide complet pour la personnalisation du CLI Claude Code avec status line et banner ATLAS.

## Quick Fix - Restaurer la StatusLine

**Si la statusline ne s'affiche pas**, c'est probablement que `settings.json` pointe vers `ccstatusline` au lieu du script bash.

### Fichier à modifier

`/home/seb/atlas-framework/.claude/settings.json`

### Configuration correcte

```json
"statusLine": {
  "type": "command",
  "command": "bash /home/seb/atlas-framework/.claude/scripts/statusline.sh"
}
```

### Attention: Projet vs Global

- **Projet** (`/home/seb/atlas-framework/.claude/settings.json`) - Override le global
- **Global** (`~/.claude/settings.json`) - Config utilisateur

Le settings.json du projet (ATLAS) a priorité. C'est lui qu'il faut modifier.

### Test rapide

```bash
# Vérifier la config actuelle
grep -A2 statusLine /home/seb/atlas-framework/.claude/settings.json

# Tester le script
echo '{"model":{"display_name":"Opus"}}' | bash /home/seb/atlas-framework/.claude/scripts/statusline.sh
```

---

## Overview

### Banner (au démarrage)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🏛️  ATLAS FRAMEWORK v1.1  •  AI Agent Orchestration  🤖            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### StatusLine (en bas du CLI)

```
🏛️ ATLAS │ 🧠 Opus │ 🏗️ AXIOM/backend │ 🌿 main*3 │ 🔧 BACKEND │ 💰 $0.50 │ ⏱️ 12m
```

| Segment | Emoji | Description |
|---------|-------|-------------|
| Framework | 🏛️ | Identifiant ATLAS Framework |
| Model | 🧠/🎵/🍃 | Modèle AI actif (Opus, Sonnet, Haiku) |
| Project | Variable | Projet + sous-dossier (monorepo) |
| Git | 🌿 | Branche + fichiers modifiés |
| Agent | Variable | Agent Atlas actif |
| Cost | 💰 | Coût de la session en USD |
| Time | ⏱️ | Durée de la session |

---

## Architecture (v1.2.0)

### Fichiers Scripts

| Fichier | Description |
|---------|-------------|
| `scripts/banner.sh` | Affiche le banner temple grec |
| `scripts/statusline.sh` | Génère la statusline avec emojis |

### Fichiers Hooks

| Fichier | Trigger | Description |
|---------|---------|-------------|
| `hooks/SessionStart.sh` | Démarrage session | Banner + init state |
| `hooks/SessionEnd.sh` | Fin session | Log fermeture |
| `hooks/PreToolUse-Task.sh` | Avant Task tool | Push agent sur stack |
| `hooks/SubagentStop.sh` | Fin subagent | Pop agent du stack |
| `hooks/PostToolUse-Edit.sh` | Après Edit/Write | (extensible) |
| `hooks/Stop.sh` | Stop agent | (extensible) |

### State File

**Emplacement:** `~/.claude/session-state.json`

```json
{
  "agent_stack": ["ATLAS", "BACKEND-BUILDER"],
  "current_agent": "BACKEND-BUILDER",
  "last_updated": "2025-11-30T15:00:00Z"
}
```

---

## Projets Détectés

Le script détecte le projet via le chemin courant (case-insensitive).

### Projets avec Emojis

| Projet | Emoji | Pattern |
|--------|-------|---------|
| AXIOM | 🏗️ | `*axiom*` |
| NEXUS | 🧠 | `*nexus*` |
| SYNAPSE | ⚡ | `*synapse*` |
| CORTEX | 🔮 | `*cortex*` |
| ATLAS | 🏛️ | `*atlas*` |
| FORGE | 🔥 | `*forge*` |
| PRISM | 💎 | `*prism*` |
| PERSO | 👤 | `*perso*` |
| FINDASH | 💰 | `*findash*` |
| HOMELAB | 🖥️ | `*homelab*` |
| HA | 🏠 | `*homeassistant*` |
| (autre) | 📁 | Nom du dossier |

### Support Monorepo

Le script détecte le projet parent ET le sous-dossier :

```
~/projects/AXIOM/backend  → 🏗️ AXIOM/backend
~/projects/AXIOM/frontend → 🏗️ AXIOM/frontend
~/projects/perso/findash  → 👤 PERSO/findash
~/projects/unknown-proj   → 📁 UNKNOWN-PROJ
```

---

## Agents Trackés

Le système utilise un **stack pattern** pour les agents imbriqués.

### Agents avec Emojis

| Agent | Emoji | Model |
|-------|-------|-------|
| ATLAS | 🥇 | Opus |
| GENESIS | 🧬 | Opus |
| BRAINSTORM | 💡 | Opus |
| SYSTEM-ARCHITECT | 🏛️ | Opus |
| BACKEND-BUILDER | 🔧 | Sonnet |
| FRONTEND-BUILDER | 🎨 | Sonnet |
| DEVOPS-BUILDER | 🐳 | Haiku |
| DEVOPS-MANAGER | 🚀 | Opus |
| DEBUGGER | 🐛 | Sonnet |
| PLANNER | 📋 | Sonnet |
| DOC-WRITER | 📝 | Haiku |
| UX-DESIGNER | 🎯 | Sonnet |
| OPUS-DIRECT | ⭐ | Opus |
| SONNET-DIRECT | 🔵 | Sonnet |
| EXPLORE | 🔍 | - |
| PLAN | 📐 | - |

### Comment ça marche

1. **SessionStart** → Initialise stack à `["ATLAS"]`
2. **PreToolUse (Task)** → Push nouvel agent sur stack
3. **SubagentStop** → Pop dernier agent du stack
4. **StatusLine** → Lit `current_agent` du state file

Exemple de stack pendant l'exécution :
```
ATLAS lance BACKEND-BUILDER    → ["ATLAS", "BACKEND-BUILDER"]
BACKEND-BUILDER lance DEBUGGER → ["ATLAS", "BACKEND-BUILDER", "DEBUGGER"]
DEBUGGER termine               → ["ATLAS", "BACKEND-BUILDER"]
BACKEND-BUILDER termine        → ["ATLAS"]
```

---

## Configuration

### settings.json

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash .claude/scripts/statusline.sh"
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task",
        "hooks": [{
          "type": "command",
          "command": "bash .claude/hooks/PreToolUse-Task.sh"
        }]
      }
    ],
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [{
          "type": "command",
          "command": "bash .claude/hooks/SessionStart.sh"
        }]
      }
    ],
    "SubagentStop": [
      {
        "matcher": "*",
        "hooks": [{
          "type": "command",
          "command": "bash .claude/hooks/SubagentStop.sh"
        }]
      }
    ]
  }
}
```

---

## Prérequis

### Linux/WSL

```bash
# jq pour parsing JSON (requis)
sudo apt install -y jq

# Vérifier
jq --version
```

### Terminal

- Terminal supportant UTF-8 et emojis
- Windows Terminal recommandé pour WSL
- Police: JetBrainsMono Nerd Font (optionnel, pour powerline)

---

## Personnalisation

### Ajouter un Projet

Éditer `scripts/statusline.sh`, section "Project Detection":

```bash
# Ajouter après les projets existants
elif [[ "$CWD_LOWER" == *"monprojet"* ]]; then
    PROJECT_EMOJI="🚀"; PROJECT_NAME="MONPROJET"
```

### Ajouter un Agent

Éditer `scripts/statusline.sh`, section "Agent Display":

```bash
# Ajouter dans le case
"MON-AGENT") AGENT_DISPLAY="🎯 MON-AGENT" ;;
```

### Modifier le Banner

Éditer `scripts/banner.sh`:

```bash
cat << 'EOF'
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🚀  MON FRAMEWORK  •  Custom  🎯  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
EOF
```

---

## Tests

### Test Banner

```bash
bash ~/.claude/scripts/banner.sh
# ou depuis le projet
bash .claude/scripts/banner.sh
```

### Test StatusLine

```bash
# Sans JSON (valeurs par défaut)
bash .claude/scripts/statusline.sh < /dev/null

# Avec JSON (simule Claude Code)
echo '{"model":{"display_name":"Opus"},"cost":{"total_cost_usd":0.50,"total_duration_ms":720000}}' | bash .claude/scripts/statusline.sh
```

### Test Agent Tracking

```bash
# Init state
bash .claude/hooks/SessionStart.sh

# Push agent
echo '{"tool_input":{"subagent_type":"backend-builder"}}' | bash .claude/hooks/PreToolUse-Task.sh
cat ~/.claude/session-state.json

# Pop agent
bash .claude/hooks/SubagentStop.sh
cat ~/.claude/session-state.json
```

---

## Troubleshooting

### StatusLine ne s'affiche pas

1. Vérifier que le script existe et est exécutable:
   ```bash
   ls -la .claude/scripts/statusline.sh
   chmod +x .claude/scripts/statusline.sh
   ```

2. Vérifier jq:
   ```bash
   which jq
   ```

3. Tester manuellement:
   ```bash
   bash .claude/scripts/statusline.sh < /dev/null
   ```

### Erreur CRLF (Windows → WSL)

Si vous voyez `$'\r': command not found`:

```bash
# Convertir tous les scripts
cd .claude
for f in hooks/*.sh scripts/*.sh; do
    sed -i 's/\r$//' "$f"
done
```

### Agent non détecté

1. Vérifier que le hook PreToolUse existe dans settings.json
2. Vérifier le state file:
   ```bash
   cat ~/.claude/session-state.json
   ```
3. L'agent apparaît après le premier usage du Task tool

### Emojis corrompus

- Vérifier l'encodage UTF-8 du terminal
- Windows Terminal supporte les emojis nativement
- Tester: `echo "🏛️ 🔧 🐛"`

---

## Fichiers Référence

| Fichier | Description |
|---------|-------------|
| `.claude/scripts/banner.sh` | Banner ASCII art |
| `.claude/scripts/statusline.sh` | StatusLine v2.0 |
| `.claude/hooks/SessionStart.sh` | Init session + banner |
| `.claude/hooks/PreToolUse-Task.sh` | Track agent start |
| `.claude/hooks/SubagentStop.sh` | Track agent end |
| `.claude/settings.json` | Configuration hooks |
| `~/.claude/session-state.json` | State file (auto-généré) |
| `~/.claude/logs/sessions.log` | Log des sessions |

---

## Related

- `CHANGELOG.md` - Historique des versions
- `agents/rules/response-protocol.md` - Format de réponse
- `docs/session-management.md` - Gestion des sessions
