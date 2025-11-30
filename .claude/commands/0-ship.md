# Ship - Git Workflow

Exécute le workflow git complet: test → commit → push.

## Instructions

1. **Vérifier l'état git:**
   ```bash
   git status --short
   git diff --stat
   ```

2. **Afficher résumé des changements:**

```
🚀 Ship - Préparation au commit
═══════════════════════════════════════════════════════

Fichiers modifiés: {count}
Fichiers ajoutés:  {count}
Fichiers supprimés: {count}

Changements:
  M  app/services/rule_engine.py
  A  app/api/endpoints/new_endpoint.py
  ...

═══════════════════════════════════════════════════════
```

3. **Lancer les tests (si configurés):**
   - Backend: `pytest` (si apps/synapse actif)
   - Frontend: `npm run test` (si frontend modifié)
   - Afficher résultat

4. **Si tests passent, proposer commit:**
   - Analyser les changements
   - Suggérer un message de commit (conventional commits)
   - Demander validation

5. **Après validation:**
   ```bash
   git add -A
   git commit -m "message"
   git push -u origin {branch}
   ```

6. **Afficher résultat:**

```
✅ Ship Complete!
═══════════════════════════════════════════════════════

Commit: {hash}
Branch: {branch}
Push:   Success

═══════════════════════════════════════════════════════
```

## Options

- `--no-test` : Skip les tests
- `--amend` : Amender le dernier commit (avec précautions)

## Notes

- TOUJOURS vérifier les tests avant commit
- JAMAIS push --force sans demander
- Suivre conventional commits (feat, fix, docs, refactor, etc.)
