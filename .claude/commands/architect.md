# /architect

Refactoring majeur ou architecture complexe (utilise Opus).

## Usage

```text
/architect [description]   # Refactoring/architecture complexe
```

## Actions

1. ATLAS detecte la complexite
2. Dispatch a ARCHITECT-BUILDER (opus)
3. Analyse approfondie du code existant
4. Proposition d'architecture
5. Implementation apres approbation

## Agent Invoque

- ARCHITECT-BUILDER (opus) - Pour refactoring majeur

## Cas d'Usage

- Refactoring de modules entiers
- Migration de patterns (ex: class -> hooks)
- Restructuration de dossiers
- Optimisation de performance globale
- Introduction de nouveaux patterns

## Exemple

```text
User: /architect migrer le state management de Context a Zustand

ARCHITECT-BUILDER (opus):
"Migration Context -> Zustand detectee.

Analyse du code existant:
- 5 contexts identifies
- 12 composants impactes
- 3 hooks custom a adapter

Plan de migration:

Phase 1: Creation des stores Zustand
- authStore.ts (remplace AuthContext)
- projectStore.ts (remplace ProjectContext)
- uiStore.ts (remplace UIContext)

Phase 2: Migration progressive
- Commencer par authStore (moins de dependances)
- Adapter les hooks existants
- Migrer composant par composant

Phase 3: Cleanup
- Supprimer les anciens contexts
- Mettre a jour les tests

Estimation: ~200 lignes de code modifiees.

Tu veux que je procede avec cette approche?"
```
