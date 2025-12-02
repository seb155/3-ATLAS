# Hook: Session Start

**Type:** PreToolUse
**Déclencheur:** Première interaction de la session

## But

Charger automatiquement le contexte AXIOM au début de chaque session.

## Actions

1. Lire `.dev/ai/session-state.json`
2. Identifier la dernière session et son état
3. Préparer le contexte approprié

## Configuration

Dans `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task|Bash|Read",
        "hooks": [".claude/hooks/session-start.sh"]
      }
    ]
  }
}
```

## Script Example

```bash
#!/bin/bash
# .claude/hooks/session-start.sh

# Check if session context exists
if [ -f ".dev/ai/session-state.json" ]; then
    echo "📋 Session context found"
    # Could output context summary
fi
```

## Comportement Attendu

Quand une nouvelle session démarre:

```
🚀 ATLAS Session Hook
═══════════════════════════════════════════════════════

Dernière session: 2025-11-30-phase3
Mode: DEVELOPMENT
Focus: Creating skills

💡 Tip: Use /0-new-session for full app review
        Use /0-next for quick continuation

═══════════════════════════════════════════════════════
```

## Notes

- Ce hook est informatif, pas bloquant
- Ne charge PAS tout le contexte (économie tokens)
- Suggère les commandes appropriées
