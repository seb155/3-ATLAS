# /debug

Analyse et corrige les erreurs.

## Usage

```text
/debug [erreur]           # Analyse une erreur specifique
/debug                    # Analyse la derniere erreur
/debug [fichier:ligne]    # Debug a une position specifique
```

## Actions

1. DEBUGGER analyse l'erreur
2. Identifie la cause racine
3. Propose des solutions
4. Implemente la correction choisie
5. Verifie avec tests

## Agent Invoque

- DEBUGGER (sonnet) - Analyse et correction d'erreurs

## Types d'Erreurs

| Type | Approche |
|------|----------|
| Syntax | Correction immediate |
| Runtime | Analyse de stack trace |
| Logic | Analyse de flux |
| Performance | Profiling |
| Integration | Analyse cross-system |

## Exemple

```text
User: /debug TypeError: Cannot read property 'id' of undefined

DEBUGGER:
"Analyse de l'erreur TypeError...

Stack trace analyse:
- Origine: ProjectList.tsx:45
- Contexte: Acces a project.id dans un map
- Cause probable: Array contient des valeurs undefined

Investigation:
1. Lecture de ProjectList.tsx
2. Verification de l'API response
3. Identification du probleme

Cause identifiee:
L'API retourne parfois des projets null dans la liste
quand ils sont soft-deleted.

Solutions:
1. Filtrer les nulls cote frontend (quick fix)
2. Corriger l'API pour exclure les soft-deleted (proper fix)

Je recommande la solution 2.
Tu veux que j'implemente?"
```
