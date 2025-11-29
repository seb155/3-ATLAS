# Rule 10: Context Awareness

**Priority:** IMPORTANT
**Applies to:** All AI agents during sessions

---

## Rule

Monitor context usage and trigger documentation/progress saves before context becomes full.

### Seuils

| Free Space | Status | Action |
|------------|--------|--------|
| >50% | OK | Continuer normalement |
| 30-50% | WARNING | Afficher alerte, suggerer documentation |
| <30% | CRITICAL | Declencher sauvegarde automatique |

---

## Verification

Verifier le context free space:
- Apres chaque tache majeure completee
- Avant de lancer un agent Task complexe
- Quand l'utilisateur demande `/context`

---

## Actions a 30% Free Space

Quand le context atteint 30% ou moins de free space:

### 1. Afficher Alerte

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ CONTEXT AWARENESS - XX% Free Space
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Avant /compact, sauvegarder le travail:

Documentation (./docs/)
- [ ] Documenter nouvelles features
- [ ] MAJ API docs si endpoints ajoutes

Suivi Dev (./.dev/)
- [ ] project-state.md - Status actuel
- [ ] task-queue.md - Taches completees
- [ ] roadmap/ - Milestones atteints

(1) Sauvegarder maintenant  (2) Ignorer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 2. Sauvegarder Documentation (./docs/)

- Creer/MAJ docs pour nouvelles features implementees
- Documenter APIs/endpoints ajoutes
- MAJ README si applicable

### 3. Sauvegarder Suivi Dev (./.dev/)

- MAJ `.dev/context/project-state.md` (version, features)
- MAJ `.dev/context/task-queue.md` (taches completees)
- MAJ `.dev/roadmap/` si milestones atteints

### 4. Suggerer /compact

Apres sauvegarde, suggerer a l'utilisateur de faire `/compact` pour liberer le context.

---

## Configuration

Voir `.claude/context/context-thresholds.json` pour les seuils configurables.

---

## Exemples

### Cas 1: Context OK (55% free)

```
Agent: Continue normalement, pas d'alerte.
```

### Cas 2: Context Warning (35% free)

```
Agent: "Note: Context a 35% free space.
        Penser a documenter le travail bientot."
```

### Cas 3: Context Critical (25% free)

```
Agent: [Affiche alerte complete]
       "Context critique! Sauvegardons le travail avant /compact."
       [Propose actions de sauvegarde]
```

---

## Integration ATLAS

ATLAS doit verifier le context avant de dispatcher vers des agents specialises. Si context < 30%, prioriser la sauvegarde avant de continuer.
