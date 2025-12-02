# ATLAS Hooks

Ce dossier contient les hooks pour automatiser certaines actions dans Claude Code.

## Types de Hooks

| Hook | Type | Déclencheur |
|------|------|-------------|
| session-start | PreToolUse | Début de session |
| pre-commit | PreToolUse | Avant git commit |
| context-update | PostToolUse | Après modification fichiers |

## Configuration

Les hooks sont configurés dans `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": ["~/.claude/hooks/session-start.sh"]
      }
    ]
  }
}
```

## Fichiers

| Fichier | Description |
|---------|-------------|
| `session-start.sh` | Charge le contexte au démarrage |
| `pre-commit.sh` | Valide avant commit |
| `context-update.sh` | Met à jour hot-files après modifs |

## Usage

Les hooks s'exécutent automatiquement selon leur déclencheur.
Pour les désactiver temporairement, modifier settings.local.json.
