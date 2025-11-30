# Next Task - Mode QUICK

Continue le travail rapidement sans revue complète.

## Instructions

1. **Charger contexte minimal:**
   - Lire `.dev/ai/session-state.json` uniquement
   - Identifier la dernière app travaillée

2. **Afficher résumé rapide:**

```
⚡ Mode QUICK - Reprise rapide
═══════════════════════════════════════════════════════

Dernière session: {last_session.id}
App active:       {last_session.apps_worked_on[0]}
Focus:            {last_session.focus}

Dernière tâche complétée:
  ✓ {last_session.completed_tasks[-1]}

Prochaine tâche suggérée:
  → {last_session.next_tasks[0]}

═══════════════════════════════════════════════════════
```

3. **Demander confirmation:**
   > "On continue avec cette tâche, ou tu veux faire autre chose?"

4. **Si confirmé:**
   - Charger le contexte de l'app active
   - Commencer la tâche

5. **Mettre à jour session-state.json:**
   - `current_session.mode` = "QUICK"

## Notes

- Mode rapide = pas de revue de toutes les apps
- Utiliser `/0-new-session` pour une revue complète
- Utiliser `/0-progress` pour voir toutes les apps sans changer de mode
