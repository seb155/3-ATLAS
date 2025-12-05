# /implement

Implemente une feature ou tache specifique.

## Usage

```text
/implement [description]   # Implemente la feature decrite
```

## Actions

1. ATLAS analyse la demande
2. Si complexe (>3 etapes): dispatch au PLANNER
3. Si simple: dispatch direct au builder appropriate
4. Supervise l'execution
5. Valide avec QA-TESTER

## Agents Invoques

| Complexite | Agent |
|------------|-------|
| Simple backend | BACKEND-BUILDER (sonnet) |
| Simple frontend | FRONTEND-BUILDER (sonnet) |
| Complexe | PLANNER -> Builders |
| Cross-app | INTEGRATION-BUILDER (opus) |

## Exemple

```text
User: /implement ajouter un bouton de refresh sur la liste des projets

ATLAS: "Tache simple frontend detectee.
Je dispatch au FRONTEND-BUILDER..."

FRONTEND-BUILDER:
"J'ajoute le bouton refresh:
- Composant: ProjectList.tsx
- Action: handleRefresh() avec invalidation du cache
- UI: IconButton avec Lucide RefreshCw

[Implementation...]

Termine. Le bouton est ajoute."
```
