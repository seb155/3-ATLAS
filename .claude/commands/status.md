# /status

Affiche l'etat complet du projet.

## Actions

1. **Etat du projet**
   - Sprint actuel
   - Progression features
   - Deadline

2. **Etat des tests**
   - Coverage backend/frontend
   - Tests failed
   - Last run

3. **Docker**
   - Services running
   - Health status

4. **Issues**
   - Issues ouvertes
   - Blockers

## Exemple

```text
User: /status

ATLAS: "Voici l'etat du projet:

## SYNAPSE - MVP Week 3

**Progress**: 65%
- [x] CSV Import
- [x] Rule Engine
- [ ] Package Export (in progress)
- [ ] Final polish

**Deadline**: Dec 20, 2025 (22 days)

## Tests

| App | Backend | Frontend |
|-----|---------|----------|
| SYNAPSE | 78% | 72% |
| NEXUS | - | 68% |

Last run: 2h ago - All passed

## Docker

| Service | Status |
|---------|--------|
| forge-postgres | healthy |
| forge-redis | healthy |
| synapse-backend | running |

## Issues

| ID | Title | Severity |
|----|-------|----------|
| #004 | Slow export on large datasets | Minor |

No blockers."
```

## Agents invoques

- ATLAS
- DEV-TRACKER
- QA-TESTER (si tests demandes)
