# /brainstorm

Lance une session de brainstorming creative.

## Usage

```text
/brainstorm [sujet]    # Brainstorm sur un sujet specifique
```

## Actions

1. ATLAS detecte le besoin de creativite
2. Dispatch a BRAINSTORM (opus)
3. Exploration libre des idees
4. Presentation structuree des options
5. Decision collaborative

## Agent Invoque

- BRAINSTORM (opus) - Sessions creatives

## Cas d'Usage

- Explorer des approches architecturales
- Definir de nouvelles features
- Resoudre des problemes complexes
- Imaginer des ameliorations UX
- Planifier des refactorings majeurs

## Style de Session

### Phase Divergente
- Toutes les idees sont les bienvenues
- Pas de jugement immediat
- Explorer les extremes

### Phase Convergente
- Evaluer les options
- Identifier les trade-offs
- Recommander une approche

## Exemple

```text
User: /brainstorm comment gerer les notifications en temps reel

BRAINSTORM (opus):
"Session de brainstorm: Notifications temps reel

Explorons les possibilites...

Option 1: WebSockets
- Connexion persistante bidirectionnelle
- Temps reel pur (<100ms)
- Complexite: Moyenne
- Scaling: Redis pub/sub requis

Option 2: Server-Sent Events (SSE)
- Connexion unidirectionnelle (serveur -> client)
- Temps reel (~100-500ms)
- Complexite: Faible
- Scaling: Plus simple

Option 3: Long Polling
- Requetes HTTP repetees
- Latence: 1-5 secondes
- Complexite: Tres faible
- Scaling: Stress serveur

Option 4: Push Notifications (PWA)
- Notifications systeme
- Fonctionne app fermee
- Complexite: Moyenne
- Limite: Besoin permission user

Combinaison recommandee:
- SSE pour notifications in-app (simple, efficace)
- Push PWA pour notifications critiques (app fermee)

Tu veux explorer une de ces options plus en detail?"
```
