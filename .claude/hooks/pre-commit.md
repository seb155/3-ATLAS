# Hook: Pre-Commit

**Type:** PreToolUse
**Déclencheur:** Avant exécution de `git commit`

## But

Valider les changements avant de commiter:
- Vérifier qu'on ne commit pas de secrets
- Vérifier le format du message
- Optionnel: lancer les tests

## Actions

1. Scanner les fichiers pour secrets (.env, credentials)
2. Valider le message de commit (conventional commits)
3. Optionnel: Run tests si configuré

## Configuration

Dans `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "pattern": "git commit",
        "hooks": [".claude/hooks/pre-commit.sh"]
      }
    ]
  }
}
```

## Validations

### 1. Fichiers Sensibles
```
⚠️ ATTENTION: Fichiers sensibles détectés
─────────────────────────────────────────
• .env
• credentials.json
• secrets/

Ces fichiers ne devraient pas être commités.
Voulez-vous continuer? (y/n)
```

### 2. Message de Commit
```
Format attendu: type(scope): description

Types valides:
• feat     - Nouvelle fonctionnalité
• fix      - Correction de bug
• docs     - Documentation
• refactor - Refactoring
• test     - Tests
• chore    - Maintenance
```

### 3. Tests (Optionnel)
```
🧪 Running tests before commit...
─────────────────────────────────────────
pytest: 42 passed, 0 failed
npm test: All tests passed

✅ Ready to commit
```

## Script Example

```bash
#!/bin/bash
# .claude/hooks/pre-commit.sh

# Check for sensitive files
sensitive_files=$(git diff --cached --name-only | grep -E '\.env|credentials|secrets')
if [ -n "$sensitive_files" ]; then
    echo "⚠️ WARNING: Sensitive files detected:"
    echo "$sensitive_files"
    exit 1  # Block commit
fi

# Validate commit message format (if provided)
# ...

exit 0  # Allow commit
```

## Comportement

| Situation | Action |
|-----------|--------|
| Fichiers sensibles | ⛔ Bloquer + avertir |
| Message mal formaté | ⚠️ Avertir (non bloquant) |
| Tests échouent | ⚠️ Avertir (configurable) |

## Notes

- Ne pas être trop strict (frustrant)
- Les avertissements sont préférables aux blocages
- L'utilisateur peut override avec `--no-verify`
