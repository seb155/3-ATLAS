# Hook: Context Update

**Type:** PostToolUse
**Déclencheur:** Après modification de fichiers

## But

Maintenir les fichiers de contexte à jour automatiquement:
- Mettre à jour `hot-files.json` avec les fichiers modifiés
- Tracker les changements pour la session

## Actions

1. Détecter les fichiers modifiés
2. Mettre à jour `.dev/ai/hot-files.json`
3. Optionnel: Mettre à jour session-state.json

## Configuration

Dans `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [".claude/hooks/context-update.sh"]
      }
    ]
  }
}
```

## Fichiers Mis à Jour

### hot-files.json
```json
{
  "last_updated": "2025-11-30T15:30:00Z",
  "files": [
    {
      "path": "apps/synapse/backend/app/services/rule_engine.py",
      "last_modified": "2025-11-30T15:30:00Z",
      "modification_count": 5
    },
    {
      "path": "apps/synapse/frontend/src/components/DevConsole.tsx",
      "last_modified": "2025-11-30T15:25:00Z",
      "modification_count": 3
    }
  ]
}
```

## Script Example

```bash
#!/bin/bash
# .claude/hooks/context-update.sh

# Get recently modified files
modified_files=$(git diff --name-only HEAD 2>/dev/null)

if [ -n "$modified_files" ]; then
    # Update hot-files.json
    # (In practice, this would be a more sophisticated script)
    echo "📝 Updated hot-files.json with:"
    echo "$modified_files"
fi
```

## Comportement

```
📝 Context Update
─────────────────────────────────────────
Fichiers modifiés cette session:
  • app/services/rule_engine.py (5 edits)
  • app/api/endpoints/assets.py (2 edits)

hot-files.json mis à jour ✓
─────────────────────────────────────────
```

## Optimisation Tokens

Ce hook aide à économiser des tokens en:
- Identifiant les fichiers "chauds" (souvent modifiés)
- Permettant de charger seulement les fichiers pertinents
- Évitant de relire des fichiers non modifiés

## Notes

- Ce hook est silencieux (pas d'output visible)
- S'exécute en arrière-plan
- Ne bloque jamais l'opération
- Utile pour `/0-resume` après interruption
