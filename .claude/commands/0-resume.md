---
description: Recover session after /compact during active development
---

# /0-resume

Reconstruit le contexte après un /compact en pleine session de développement.

**Mode:** RECOVERY (Context reconstruction)

## Actions

1. **Lit le compact summary**
   - Dernier message avant /compact
   - Récupère: tâche active, todo list, fichiers modifiés

2. **Reconstruit todo list**
   - Parse dernière TodoWrite avant compact
   - Identifie tâche "in_progress"
   - Retrouve tâches pending

3. **Valide progression**
   - Check git diff depuis compact
   - Derniers fichiers modifiés
   - Tests passent?

4. **Reprend exactement où c'était**
   - Affiche: tâche en cours, progression, prochaine étape
   - Choix numérotés

## Agent invoqué

- ATLAS (Mode RECOVERY)

## Exemple

```text
User: /0-resume

ATLAS: "Reconstruction session après compact...

**Compact timestamp:** 2025-11-28 15:45
**Tâche en cours:** Créer AssetHistory.tsx component

**Todo list retrouvée:**
- ✅ Create component structure
- 🔄 Add version timeline UI (IN PROGRESS)
- ⚠️ Add diff viewer
- ⚠️ Add rollback button

**Fichiers modifiés depuis compact:**
- frontend/src/components/AssetHistory.tsx (+150 lignes)

**Git status:**
- 1 fichier modifié, non-commité

**Que veux-tu faire?**
1. Continuer version timeline UI (recommandé)
2. Voir le diff depuis compact
3. Commiter travail actuel
4. Autre chose"
```

## When to use

✅ **Use /0-resume when:**
- Chat was compacted during active development
- You were in the middle of a task
- Todo list was active
- Need to reconstruct exact context

❌ **Don't use /0-resume when:**
- Starting new session (use `/0-new-session`)
- Continuing after break (use `/0-next`)
- No compact happened
- Starting fresh task

## How it works

1. **Finds last state:**
   - Parses conversation before /compact
   - Extracts active todo list
   - Identifies files being modified

2. **Reconstructs context:**
   - Loads modified files
   - Checks git status
   - Verifies what changed

3. **Continues work:**
   - Picks up exactly where you left off
   - No context loss
   - Seamless continuation

---

**Tip:** After /compact during work, type `/0-resume` to continue seamlessly!
