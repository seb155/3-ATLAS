# Token Usage Analysis

Analyse détaillée des patterns d'utilisation pour optimiser la consommation de tokens.

## Exécuter l'Analyse

```bash
# Analyser la session actuelle
bash /home/seb/projects/.claude/scripts/analyze-tools.sh

# Analyser toutes les sessions du projet
bash /home/seb/projects/.claude/scripts/analyze-tools.sh all
```

## Rapport Détaillé

```bash
TOOL_DATA=$(bash /home/seb/projects/.claude/scripts/analyze-tools.sh)

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🔬 TOOL USAGE ANALYSIS                                      ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo ""
echo "$TOOL_DATA" | jq -r '
"  📊 Summary:
  ├─ Total tool calls: \(.summary.total_tool_calls)
  ├─ Unique tools used: \(.summary.unique_tools)
  ├─ Top consumer: \(.summary.top_consumer)
  └─ Need optimization: \(.summary.tools_to_optimize | join(", ") | if . == "" then "None!" else . end)

  📋 Detailed Breakdown:
  ─────────────────────────────────────────────────"'

echo "$TOOL_DATA" | jq -r '.tools[] |
  "  \(.tool):
    ├─ Calls: \(.count)
    ├─ Avg input size: \(.avg_input_size) chars (~\(.est_tokens_per_call) tokens/call)
    ├─ Total impact: ~\(.est_total_tokens) tokens
    ├─ Range: \(.min_input_size) - \(.max_input_size) chars
    └─ Status: \(.status | ascii_upcase)
  "'

echo ""
echo "╚══════════════════════════════════════════════════════════════╝"
```

## Patterns Coûteux Identifiés

### 🔴 Task (Agent Spawning)
**Coût:** ~2,000-5,000 tokens par appel

Le `Task` tool lance un sous-agent avec son propre contexte. Chaque appel inclut:
- Le prompt système complet (~500-1000 tokens)
- Le contexte du projet (~1000-3000 tokens)
- Les instructions de la tâche

**Alternatives:**
| Au lieu de... | Utiliser... |
|---------------|-------------|
| Task pour chercher un fichier | `Glob` pattern matching |
| Task pour chercher du code | `Grep` avec regex |
| Task pour lire plusieurs fichiers | `Read` en parallèle |

### 🟠 WebFetch
**Coût:** ~5,000-20,000 tokens par page

Les pages web longues consomment beaucoup de tokens.

**Optimisations:**
- Demander un résumé spécifique dans le prompt
- Utiliser des URLs de documentation directe (pas de pages index)
- Préférer les API JSON quand disponibles

### 🟡 Read (Fichiers Entiers)
**Coût:** Variable (~1-10K selon taille)

Lire un fichier entier quand seule une partie est nécessaire.

**Optimisations:**
- Utiliser `limit` et `offset` pour les gros fichiers
- Utiliser `Grep` pour trouver d'abord les lignes pertinentes
- Diviser les gros fichiers en modules

### 🟢 Grep/Glob (Efficaces)
**Coût:** ~50-200 tokens

Ces outils sont très efficaces car ils retournent seulement les résultats pertinents.

**Best practices:**
- Utiliser des patterns spécifiques
- Combiner avec `Read` seulement après avoir trouvé le bon fichier

## Règles d'Optimisation

### 1. Pyramide de Recherche
```
         Task (dernier recours)
           ↑
       WebFetch (si externe)
           ↑
     Read (fichier spécifique)
           ↑
    Grep (recherche contenu)
           ↑
   Glob (recherche fichiers)
```

### 2. Règle des 3 Appels
Si une recherche nécessite plus de 3 appels Glob/Grep, considérer Task.
Sinon, les appels individuels sont plus économiques.

### 3. Cache First
Les tokens lus du cache coûtent 10× moins cher.
Garder le contexte système stable maximise le cache hit rate.

## Métriques Cibles

| Métrique | Bon | Acceptable | À Optimiser |
|----------|-----|------------|-------------|
| Cache efficiency | >70% | 50-70% | <50% |
| Task calls/session | <10 | 10-20 | >20 |
| Avg tool input size | <500 chars | 500-1000 | >1000 |
| Context at end | <50% | 50-70% | >70% |

## Commandes Liées

| Commande | Description |
|----------|-------------|
| `/0-tokens` | Dashboard principal |
| `/0-analyze` | Cette analyse |
| `/compact` | Réduire le contexte |
| `/cost` | Coût de la session |
