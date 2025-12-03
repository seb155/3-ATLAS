# Arbre de Décision du Routage Intelligent

## Vue d'Ensemble

Ce document décrit l'algorithme de décision utilisé par CORTEX pour router les requêtes vers le modèle optimal.

## Arbre de Décision

```
                              ┌─────────────────────┐
                              │   NOUVELLE REQUÊTE  │
                              └──────────┬──────────┘
                                         │
                                         ▼
                    ┌────────────────────────────────────────┐
                    │  1. CHECK CONFIDENTIALITÉ              │
                    │     Analyser les données de la requête │
                    └──────────────────┬─────────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
              ▼                        ▼                        ▼
      ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
      │   TIER 2      │       │   TIER 1      │       │   TIER 0      │
      │ CONFIDENTIAL  │       │  INTERNAL     │       │   PUBLIC      │
      │               │       │               │       │               │
      │ • Finances    │       │ • Code projet │       │ • Docs publics│
      │ • Mots passe  │       │ • Données     │       │ • Questions   │
      │ • Données     │       │   client      │       │   générales   │
      │   personnelles│       │ • Configs     │       │ • Recherche   │
      └───────┬───────┘       └───────┬───────┘       └───────┬───────┘
              │                       │                       │
              │                       │                       │
              ▼                       ▼                       ▼
      ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
      │ LOCAL         │       │ LOCAL         │       │ CONTINUER     │
      │ OBLIGATOIRE   │       │ PRÉFÉRÉ       │       │ ANALYSE       │
      │               │       │               │       │               │
      │ → Fin         │       │ (sauf override│       │               │
      └───────────────┘       │  explicite)   │       └───────┬───────┘
                              └───────┬───────┘               │
                                      │                       │
                                      └───────────┬───────────┘
                                                  │
                                                  ▼
                              ┌────────────────────────────────────────┐
                              │  2. CHECK BUDGET RESTANT               │
                              │     Vérifier % budget mensuel          │
                              └──────────────────┬─────────────────────┘
                                                 │
              ┌──────────────────────────────────┼──────────────────────────────────┐
              │                                  │                                  │
              ▼                                  ▼                                  ▼
      ┌───────────────┐               ┌───────────────┐               ┌───────────────┐
      │   < 20%       │               │  20% - 80%    │               │   > 80%       │
      │   CRITIQUE    │               │   NORMAL      │               │  CONFORTABLE  │
      │               │               │               │               │               │
      │ Cloud interdit│               │ Cloud si      │               │ Cloud OK      │
      │ → LOCAL ONLY  │               │ nécessaire    │               │               │
      └───────┬───────┘               └───────┬───────┘               └───────┬───────┘
              │                               │                               │
              ▼                               │                               │
      ┌───────────────┐                       │                               │
      │ LOCAL/QUALITY │                       │                               │
      │               │                       │                               │
      │ → Fin         │                       │                               │
      └───────────────┘                       │                               │
                                              └───────────────┬───────────────┘
                                                              │
                                                              ▼
                              ┌────────────────────────────────────────┐
                              │  3. ANALYSER COMPLEXITÉ                │
                              │     (via LLM local rapide)             │
                              └──────────────────┬─────────────────────┘
                                                 │
              ┌──────────────────────────────────┼──────────────────────────────────┐
              │                                  │                                  │
              ▼                                  ▼                                  ▼
      ┌───────────────┐               ┌───────────────┐               ┌───────────────┐
      │   SIMPLE      │               │    MEDIUM     │               │   COMPLEX     │
      │   (1-2 steps) │               │   (3-5 steps) │               │  (6+ steps)   │
      │               │               │               │               │               │
      │ Q&A direct    │               │ Raisonnement  │               │ Multi-step    │
      │ Lookup        │               │ modéré        │               │ Synthesis     │
      │ Format        │               │ Analyse       │               │ Planning      │
      └───────┬───────┘               └───────┬───────┘               └───────┬───────┘
              │                               │                               │
              ▼                               ▼                               ▼
      ┌───────────────┐               ┌───────────────┐               ┌───────────────┐
      │ LOCAL/FAST    │               │ LOCAL/QUALITY │               │ CLOUD/OPUS    │
      │               │               │    ou         │               │    ou         │
      │ Mistral 7B    │               │ CLOUD/SONNET  │               │ LOCAL/QUALITY │
      │               │               │ (selon budget)│               │ (si budget    │
      │ → Fin         │               │               │               │  critique)    │
      └───────────────┘               └───────┬───────┘               └───────────────┘
                                              │
                                              ▼
                              ┌────────────────────────────────────────┐
                              │  4. CHECK TYPE DE TÂCHE                │
                              │     Affiner le choix du modèle         │
                              └──────────────────┬─────────────────────┘
                                                 │
       ┌─────────────────┬───────────────────────┼───────────────────────┬─────────────────┐
       │                 │                       │                       │                 │
       ▼                 ▼                       ▼                       ▼                 ▼
┌─────────────┐  ┌─────────────┐        ┌─────────────┐        ┌─────────────┐  ┌─────────────┐
│    CODE     │  │  CREATIVE   │        │   ANALYSIS  │        │   SEARCH    │  │    CHAT     │
│             │  │             │        │             │        │             │  │             │
│ Generation  │  │ Writing     │        │ Reasoning   │        │ Web/Docs    │  │ Conversation│
│ Review      │  │ Ideas       │        │ Math        │        │ Facts       │  │ Assistance  │
│ Debug       │  │ Content     │        │ Logic       │        │ Lookup      │  │ Support     │
└──────┬──────┘  └──────┬──────┘        └──────┬──────┘        └──────┬──────┘  └──────┬──────┘
       │                │                      │                      │                │
       ▼                ▼                      ▼                      ▼                ▼
┌─────────────┐  ┌─────────────┐        ┌─────────────┐        ┌─────────────┐  ┌─────────────┐
│CLOUD/SONNET │  │ CLOUD/OPUS  │        │ LOCAL/QUALITY│       │ LOCAL/FAST  │  │ LOCAL/FAST  │
│    ou       │  │    ou       │        │    ou        │       │   + TOOLS   │  │             │
│LOCAL/CODE   │  │ CLOUD/GPT4  │        │ CLOUD/OPUS   │       │             │  │             │
└─────────────┘  └─────────────┘        └─────────────┘        └─────────────┘  └─────────────┘
```

## Matrice de Décision Résumée

| Confidentialité | Budget | Complexité | Type Tâche | → Modèle |
|-----------------|--------|------------|------------|----------|
| TIER 2 | * | * | * | LOCAL/* |
| TIER 1 | * | Simple | * | LOCAL/FAST |
| TIER 1 | * | Medium | * | LOCAL/QUALITY |
| TIER 1 | * | Complex | * | LOCAL/QUALITY |
| TIER 0 | < 20% | * | * | LOCAL/* |
| TIER 0 | 20-80% | Simple | * | LOCAL/FAST |
| TIER 0 | 20-80% | Medium | Code | CLOUD/SONNET |
| TIER 0 | 20-80% | Medium | Analysis | LOCAL/QUALITY |
| TIER 0 | 20-80% | Complex | * | CLOUD/OPUS |
| TIER 0 | > 80% | Simple | * | LOCAL/FAST |
| TIER 0 | > 80% | Medium | * | CLOUD/SONNET |
| TIER 0 | > 80% | Complex | * | CLOUD/OPUS |

## Exemples Concrets

### Exemple 1: Question Finance Personnelle
```
Input: "Quel est mon budget restant ce mois-ci?"
↓
Confidentialité: TIER 2 (données financières)
↓
Décision: LOCAL OBLIGATOIRE
↓
Modèle: LOCAL/FAST (Mistral 7B)
Coût: $0.00
```

### Exemple 2: Génération de Code
```
Input: "Écris une fonction Python pour parser des CSV"
↓
Confidentialité: TIER 0 (code générique)
Budget: 60% restant
Complexité: MEDIUM
Type: CODE
↓
Décision: CLOUD OK
↓
Modèle: CLOUD/SONNET
Coût estimé: ~$0.05
```

### Exemple 3: Analyse Complexe (Budget Critique)
```
Input: "Analyse cette architecture et propose des améliorations"
↓
Confidentialité: TIER 0 (discussion générale)
Budget: 15% restant (!!)
Complexité: COMPLEX
↓
Décision: LOCAL FORCÉ (budget critique)
↓
Modèle: LOCAL/QUALITY (LLaMA 70B)
Coût: $0.00
Warning: "Qualité potentiellement réduite (budget critique)"
```

### Exemple 4: Recherche Web
```
Input: "Quelles sont les dernières nouvelles sur Kubernetes?"
↓
Confidentialité: TIER 0
Budget: 75% restant
Complexité: SIMPLE
Type: SEARCH
↓
Décision: LOCAL + TOOLS
↓
Modèle: LOCAL/FAST + Web Search Tool
Coût: $0.00
```

## Implémentation

```python
def route_request(request: Request) -> RoutingDecision:
    # 1. Confidentialité (VETO)
    conf = analyze_confidentiality(request)
    if conf == Tier.CONFIDENTIAL:
        return Decision(model="local/quality", reason="confidential_data")

    # 2. Budget
    budget = get_budget_status()
    if budget.remaining_percent < 20:
        return Decision(model="local/quality", reason="budget_critical")

    # 3. Complexité
    complexity = analyze_complexity(request)

    # 4. Type de tâche
    task_type = classify_task(request)

    # 5. Décision finale
    if complexity == Complexity.SIMPLE:
        return Decision(model="local/fast")

    if complexity == Complexity.MEDIUM:
        if task_type == TaskType.CODE and budget.remaining_percent > 20:
            return Decision(model="cloud/sonnet")
        return Decision(model="local/quality")

    if complexity == Complexity.COMPLEX:
        if conf == Tier.PUBLIC and budget.remaining_percent > 20:
            return Decision(model="cloud/opus")
        return Decision(model="local/quality", warning="reduced_quality")
```

## Métriques de Succès

| Métrique | Cible | Mesure |
|----------|-------|--------|
| % requêtes locales | > 80% | Prometheus |
| Coût moyen / requête | < $0.01 | Budget Tracker |
| Latence P95 | < 5s | Grafana |
| Taux de fallback | < 5% | Logs |
| Satisfaction qualité | > 90% | User feedback |
