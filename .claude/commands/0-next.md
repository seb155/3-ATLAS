---
description: Continue next task - quick resume (skip env checks)
---

# /0-next

Reprend rapidement la prochaine tâche sans vérifications complètes.

**Mode:** QUICK (Fast task continuation)

## Actions

1. **Lit le dernier journal**
   - Parse `.dev/journal/YYYY-MM/latest.md`
   - Section "Next Session"

2. **Identifie la tâche**
   - Prochaine tâche non-completed
   - Ou suggestion du journal

3. **Charge contexte minimal**
   - Fichiers liés à la tâche uniquement
   - Hot files récemment modifiés
   - Skip: Docker check, env variables, full roadmap

4. **Propose de démarrer**
   - Affiche tâche + contexte chargé
   - Choix numérotés

## Agent invoqué

- ATLAS (Mode QUICK)

## Exemple

```text
User: /0-next

ATLAS: "Reprenant session précédente...

**Dernière session:** 2025-11-28 14:30 (45min)
**Sprint:** MVP Week 2
**Tâche en cours:** Tests backend template_service

**Prochaine tâche proposée:**
- Créer tests pytest pour IN-P040 export
- Vérifier coverage > 80%

**Contexte chargé:**
- apps/synapse/backend/app/services/template_service.py
- apps/synapse/backend/tests/ (structure)

**Que veux-tu faire?**
1. Démarrer tests IN-P040 (recommandé)
2. Voir le plan complet des tests
3. Changer de tâche
4. Autre chose"
```

## When to use

✅ **Use /0-next when:**
- Continuing work from last session
- You know what task comes next
- Environment is already set up
- Want to skip full context loading

❌ **Don't use /0-next when:**
- First session of the day (use `/0-new-session`)
- After /compact during work (use `/0-resume`)
- Docker services might be down
- Need full environment check

---

**Tip:** Type `/0-next` to jump right into your next task!
