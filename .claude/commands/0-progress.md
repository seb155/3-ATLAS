# Progress - Vue Roadmap

Affiche la progression de toutes les applications.

## Instructions

1. **Charger les données:**
   - Lire `.dev/ai/active-apps.json`
   - Lire chaque `apps/{app}/.dev/ai/app-state.json`

2. **Afficher la vue d'ensemble:**

```
📈 AXIOM - Progression Globale
═══════════════════════════════════════════════════════

                    0%    25%    50%    75%   100%
                    │      │      │      │      │
SYNAPSE  (MVP)      ████████████████████░░░░░░  85%
  → Demo prep for Dec 20

NEXUS    (Phase 1)  ████████░░░░░░░░░░░░░░░░░░  40%
  → Backend integration

CORTEX   (Design)   ██░░░░░░░░░░░░░░░░░░░░░░░░  10%
  → Architecture design

APEX     (Planning) █░░░░░░░░░░░░░░░░░░░░░░░░░   5%
  → Requirements gathering

ATLAS    (Phase 1)  █████░░░░░░░░░░░░░░░░░░░░░  21%
  → Creating slash commands

FORGE    (Prod)     ███████████████████████░░░  95%
  → Stable - maintenance only

═══════════════════════════════════════════════════════

Priorité actuelle: SYNAPSE (MVP Dec 20) + ATLAS (Dev)
═══════════════════════════════════════════════════════
```

3. **Afficher les jalons à venir:**

```
📅 Jalons
─────────────────────────────────────────────────────
Dec 20   SYNAPSE MVP Demo (boss)
Q1 2026  NEXUS Phase 2
Q2 2026  CORTEX + APEX launch
─────────────────────────────────────────────────────
```

## Notes

- Vue read-only, ne change pas de contexte
- Utiliser `/0-new-session` pour changer d'app
- Les pourcentages viennent de `progress_percent` dans active-apps.json
