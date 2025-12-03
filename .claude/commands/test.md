# /test

Lance les tests et analyse les resultats.

## Usage

```text
/test              # Lance tous les tests de l'app courante
/test [scope]      # Lance les tests d'un scope specifique
/test coverage     # Lance avec rapport de couverture
```

## Actions

1. Detecte l'app courante
2. Invoque QA-TESTER
3. Execute les tests
4. Analyse les resultats
5. Rapporte les echecs

## Agent Invoque

- QA-TESTER (haiku) - Execution et analyse des tests

## Scopes Supportes

| Scope | Description |
|-------|-------------|
| `unit` | Tests unitaires uniquement |
| `integration` | Tests d'integration |
| `e2e` | Tests end-to-end |
| `coverage` | Avec rapport de couverture |
| `[fichier]` | Tests d'un fichier specifique |

## Exemple

```text
User: /test coverage

QA-TESTER:
"Execution des tests avec couverture...

App: SYNAPSE (backend detecte)
Commande: pytest --cov=app --cov-report=html

Resultats:
- Tests passes: 142/150
- Tests echoues: 8
- Couverture: 73%

Echecs:
1. test_asset_create - AssertionError ligne 45
2. test_project_delete - Timeout
...

Fichiers sous 70%:
- app/services/workflow.py (45%)
- app/api/v1/assets.py (62%)

Tu veux que j'analyse les echecs en detail?"
```
