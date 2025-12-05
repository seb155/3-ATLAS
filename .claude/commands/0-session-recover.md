---
description: Recover session after /compact during active development
---

# /0-session-recover

Reconstruit le contexte après un /compact en pleine session de développement.

**Mode:** RECOVERY (Context reconstruction)

## Usage

```bash
/0-session-recover              # Recover session du projet courant
/0-session-recover echo         # Recover session du projet ECHO
/0-session-recover synapse      # Recover session du projet SYNAPSE
/0-session-recover mechvision   # Recover session du projet MechVision
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

2. **Cherche session active**
   - Lit `{PROJECT_PATH}/.dev/1-sessions/active/current-session.md`
   - Récupère: topic, progress, next steps

3. **Cherche checkpoint récent**
   - Lit `{PROJECT_PATH}/.dev/checkpoints/` (dernier fichier)
   - Récupère: context summary, active tasks, hot files

4. **Lit hot-context**
   - Lit `{PROJECT_PATH}/.dev/context/hot-context.md`
   - Récupère: current focus, key files, blockers

5. **Reconstruit todo list**
   - Parse dernière TodoWrite avant compact
   - Identifie tâche "in_progress"
   - Retrouve tâches pending

6. **Valide progression**
   - Check git diff depuis compact
   - Derniers fichiers modifiés
   - Tests passent?

7. **Reprend exactement où c'était**
   - Affiche: tâche en cours, progression, prochaine étape
   - Choix numérotés

## Agent invoqué

- ATLAS (Mode RECOVERY)

## Exemple

```text
User: /0-session-recover echo

ATLAS: "🔄 Reconstruction session...

**Projet ciblé:** ECHO (Voice Assistant)
**Path:** /home/seb/projects/AXIOM/apps/echo

**Sources trouvées:**
✅ Session active: .dev/1-sessions/active/current-session.md
✅ Checkpoint: .dev/checkpoints/20251128-1530-checkpoint.md
✅ Hot-context: .dev/context/hot-context.md

**Session:** API Refactoring
**Started:** 2025-11-28 14:30
**Last checkpoint:** 2025-11-28 15:30

**Todo list retrouvée:**
- ✅ Create component structure
- 🔄 Add version timeline UI (IN PROGRESS)
- ⚠️ Add diff viewer
- ⚠️ Add rollback button

**Fichiers modifiés depuis checkpoint:**
- frontend/src/components/AssetHistory.tsx (+150 lignes)

**Git status:**
- 1 fichier modifié, non-commité

**Que veux-tu faire?**
1. Continuer version timeline UI (recommandé)
2. Voir le checkpoint complet
3. Commiter travail actuel
4. Autre chose"
```

## When to use

✅ **Use /0-session-recover when:**
- Chat was compacted during active development
- You were in the middle of a task
- Todo list was active
- Need to reconstruct exact context

❌ **Don't use /0-session-recover when:**
- Starting new session (use `/0-session-start`)
- Continuing after break (use `/0-session-continue`)
- No compact happened
- Starting fresh task

---

**Tip:** After /compact during work, type `/0-session-recover [project]` to continue seamlessly!

## See Also

- `/0-session-start` - Start new session
- `/0-session-continue` - Continue existing session
- `/0-session-save` - Save before /compact
- Rule 31 - Project ID resolution
