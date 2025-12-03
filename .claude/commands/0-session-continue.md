---
description: Continue existing session - quick resume (skip env checks)
---

# /0-session-continue

Continue rapidement une session existante sans vérifications complètes.

**Mode:** QUICK (Fast task continuation)

## Usage

```bash
/0-session-continue              # Continue dans le projet courant
/0-session-continue echo         # Continue le projet ECHO
/0-session-continue synapse      # Continue le projet SYNAPSE
/0-session-continue mechvision   # Continue le projet MechVision
```

## Arguments

- `[project-id]` (optional): Identifiant du projet cible
  - Case-insensitive ("ECHO" = "echo")
  - Résolution via Rule 31 (project-resolution.md)
  - Si non fourni: utilise le projet du répertoire courant

## Actions

1. **Résolution du projet** (si argument fourni)
   - Scan les `.dev/.dev-manifest.json` du workspace
   - Match le project-id avec les manifests
   - Si trouvé: charge le contexte de ce projet
   - Si non trouvé: affiche les projets disponibles

2. **Lit le dernier journal**
   - Parse `{project}/.dev/journal/YYYY-MM/latest.md`
   - Section "Next Session"

3. **Identifie la tâche**
   - Prochaine tâche non-completed
   - Ou suggestion du journal

4. **Charge contexte minimal**
   - Fichiers liés à la tâche uniquement
   - Hot files récemment modifiés
   - Skip: Docker check, env variables, full roadmap

5. **Propose de démarrer**
   - Affiche tâche + contexte chargé
   - Choix numérotés

## Agent invoqué

- ATLAS (Mode QUICK)

## Exemple

```text
User: /0-session-continue echo

ATLAS: "📂 Projet ciblé: ECHO (Voice Assistant)
Path: /home/seb/projects/AXIOM/apps/echo

Reprenant session précédente...

**Dernière session:** 2025-11-28 14:30 (45min)
**Sprint:** MVP Week 2
**Tâche en cours:** Tests backend template_service

**Prochaine tâche proposée:**
- Créer tests pytest pour IN-P040 export
- Vérifier coverage > 80%

**Contexte chargé:**
- apps/echo/backend/app/services/template_service.py
- apps/echo/backend/tests/ (structure)

**Que veux-tu faire?**
1. Démarrer tests IN-P040 (recommandé)
2. Voir le plan complet des tests
3. Changer de tâche
4. Autre chose"
```

## When to use

✅ **Use /0-session-continue when:**
- Continuing work from last session
- You know what task comes next
- Environment is already set up
- Want to skip full context loading
- Targeting a specific project by name

❌ **Don't use /0-session-continue when:**
- First session of the day (use `/0-session-start`)
- After /compact during work (use `/0-session-recover`)
- Docker services might be down
- Need full environment check

---

**Tip:** Type `/0-session-continue [project]` to jump right into your next task!

## See Also

- `/0-session-start` - Start new session
- `/0-session-recover` - Recover after /compact
- Rule 31 - Project ID resolution
