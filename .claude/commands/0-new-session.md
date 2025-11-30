# New Session - Mode FULL

Démarre une nouvelle session de travail AXIOM.

## Instructions

1. **Charger le contexte global:**
   - Lire `.dev/ai/session-state.json` pour voir la dernière session
   - Lire `.dev/ai/active-apps.json` pour l'état de toutes les apps

2. **Afficher la revue des applications:**

```
📊 AXIOM - Revue des Applications
═══════════════════════════════════════════════════════

App         Progress  Phase           Focus
─────────────────────────────────────────────────────
SYNAPSE     ████████░░ 85%   MVP          Demo Dec 20
NEXUS       ████░░░░░░ 40%   Phase 1.5    Backend
CORTEX      █░░░░░░░░░ 10%   Design       Architecture
APEX        ░░░░░░░░░░  5%   Planning     Requirements
ATLAS       ██░░░░░░░░ 21%   Phase 1      Slash commands
FORGE       █████████░ 95%   Production   Stable

═══════════════════════════════════════════════════════
```

3. **Demander à l'utilisateur:**
   > "Sur quelle(s) application(s) veux-tu travailler aujourd'hui?"

4. **Après sélection, charger le contexte de l'app:**
   - Lire `apps/{app}/.dev/ai/app-state.json`
   - Lire les fichiers de contexte pertinents

5. **Proposer les prochaines tâches:**
   - Basé sur le `current_focus` de l'app
   - Basé sur les `next_tasks` de la dernière session

6. **Mettre à jour session-state.json:**
   - Définir `current_session.id`
   - Définir `current_session.mode` = "FULL"
   - Définir `active_apps` avec les apps sélectionnées

## Notes

- Ce mode charge le contexte COMPLET
- Utiliser `/0-next` pour des sessions rapides sans revue complète
- Utiliser `/0-resume` après un /compact
