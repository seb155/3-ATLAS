# /commit

Cree un commit avec message conventionnel.

## Usage

```text
/commit              # Commit avec message auto-genere
/commit [message]    # Commit avec message specifie
```

## Actions

1. GIT-MANAGER analyse les changements
2. Genere un message Conventional Commits
3. Propose le commit
4. Execute apres approbation

## Agent Invoque

- GIT-MANAGER (haiku) - Gestion Git

## Format Conventional Commits

```text
<type>(<scope>): <description>

[body optionnel]

[footer optionnel]
```

### Types

| Type | Usage |
|------|-------|
| `feat` | Nouvelle fonctionnalite |
| `fix` | Correction de bug |
| `docs` | Documentation |
| `style` | Formatage (pas de changement de code) |
| `refactor` | Refactoring |
| `test` | Ajout/modification de tests |
| `chore` | Maintenance |

## Exemple

```text
User: /commit

GIT-MANAGER:
"Analyse des changements...

Fichiers modifies:
- apps/synapse/frontend/src/components/ProjectList.tsx
- apps/synapse/frontend/src/stores/projectStore.ts

Type detecte: feat (nouvelle fonctionnalite)
Scope detecte: synapse

Message propose:
feat(synapse): add refresh button to project list

- Add handleRefresh function with cache invalidation
- Add RefreshCw icon button in toolbar
- Update projectStore with invalidateProjects action

Tu veux que je commit avec ce message?"

User: "oui"

GIT-MANAGER:
"Commit cree: abc1234
feat(synapse): add refresh button to project list"
```
