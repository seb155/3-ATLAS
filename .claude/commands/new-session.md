# /new-session

Demarre une nouvelle session de developpement.

## Actions

1. **Charge le contexte**
   - Lit `.dev/context/project-state.md`
   - Lit le journal recent
   - Verifie l'etat des tests

2. **Detecte l'environnement**
   - OS: Windows / Linux
   - Mode: dev / prod
   - Docker: services running

3. **Detecte l'application**
   - Basee sur le working directory
   - SYNAPSE, NEXUS, PRISM, ATLAS, FORGE

4. **Propose les priorites**
   - Taches en cours
   - Sprint actuel
   - Blockers connus

## Exemple

```text
User: /new-session

ATLAS: "Bonjour! Je charge le contexte...

**Environnement**
- OS: Windows 11
- Docker: forge-postgres, forge-redis (healthy)
- Mode: Development

**Application**: SYNAPSE (backend detected)

**Sprint**: MVP Week 3 (Dec 20 deadline)

**Etat des tests**
- Backend: 78% coverage
- Frontend: 72% coverage

**En cours**
- Systeme de notifications (90%)

**Priorites suggeres**
1. Finir tests notifications
2. Integration NEXUS
3. UI polish

Par quoi veux-tu commencer?"
```

## Agent invoque

- ATLAS (orchestrateur principal)
- DEV-TRACKER (chargement contexte)
