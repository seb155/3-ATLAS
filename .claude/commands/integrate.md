# /integrate

Integration cross-application (utilise Opus).

## Usage

```text
/integrate [description]   # Integration entre apps AXIOM
```

## Actions

1. ATLAS detecte les apps concernees
2. Dispatch a INTEGRATION-BUILDER (opus)
3. Analyse des interfaces entre apps
4. Proposition d'integration
5. Implementation coordonnee

## Agent Invoque

- INTEGRATION-BUILDER (opus) - Pour integration cross-app

## Cas d'Usage

- Partage de donnees entre SYNAPSE et NEXUS
- Integration de composants PRISM dans d'autres apps
- Unification de l'authentification
- Synchronisation de schemas de base de donnees
- APIs partagees via FORGE

## Exemple

```text
User: /integrate faire que NEXUS puisse afficher les assets de SYNAPSE

INTEGRATION-BUILDER (opus):
"Integration SYNAPSE -> NEXUS detectee.

Analyse des systemes:
- SYNAPSE: Assets stockes en PostgreSQL (forge-postgres)
- NEXUS: Knowledge Graph avec Neo4j
- Point commun: FORGE infrastructure

Approche proposee:

Option 1: API Gateway (recommande)
- SYNAPSE expose /api/v1/assets/public
- NEXUS consomme via client HTTP
- Avantage: Decouplage fort

Option 2: Base de donnees partagee
- Vue PostgreSQL pour NEXUS
- Avantage: Performance
- Risque: Couplage fort

Option 3: Event-driven
- SYNAPSE publie sur Redis pub/sub
- NEXUS s'abonne aux evenements
- Avantage: Temps reel

Je recommande l'Option 1 pour commencer.
Tu veux que j'implemente cette integration?"
```
