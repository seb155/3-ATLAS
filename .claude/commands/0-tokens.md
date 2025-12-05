# Token Usage Dashboard

Affiche les tokens REELS (pas d'estimation!) et analyse l'utilisation.

## Exécuter l'Analyse

Lancer le parser de tokens pour obtenir les compteurs précis:

```bash
bash /home/seb/projects/.claude/scripts/parse-tokens.sh
```

Puis afficher le dashboard formaté:

```bash
TOKEN_DATA=$(bash /home/seb/projects/.claude/scripts/parse-tokens.sh)
TOOL_DATA=$(bash /home/seb/projects/.claude/scripts/analyze-tools.sh)

echo "$TOKEN_DATA" | jq -r '
"
╔══════════════════════════════════════════════════════════════╗
║  📊 TOKEN DASHBOARD - COMPTEURS PRECIS (Opus 4.5)            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  TOKEN BREAKDOWN                    COST                     ║
║  ├─ 📥 Input:      \(.input | tostring | . + "        "[0:(12-length)])   @ $5/M    = $\(.cost_input)
║  ├─ 📤 Output:     \(.output | tostring | . + "        "[0:(12-length)])   @ $25/M   = $\(.cost_output)
║  ├─ 💾 Cache W:    \(.cache_write | tostring | . + "        "[0:(12-length)])   @ $6.25/M = $\(.cost_cache_write)
║  └─ 💾 Cache R:    \(.cache_read | tostring | . + "        "[0:(12-length)])   @ $0.50/M = $\(.cost_cache_read)
║                                                              ║
║  ─────────────────────────────────────────────────           ║
║  TOTAL:  \(.total) tokens                                    ║
║  COST:   $\(.cost_total)                                     ║
║  CONTEXT: \(.context_pct)% of 200K window                    ║
║                                                              ║
║  💰 CACHE SAVINGS: $\(.cache_savings) (vs no-cache)          ║
║  📈 CACHE EFFICIENCY: \(.cache_efficiency)%                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"'

echo ""
echo "🔧 TOP TOOLS BY USAGE:"
echo "─────────────────────────────────────────────────"
echo "$TOOL_DATA" | jq -r '.tools[:5][] | "  \(.count | tostring | . + "  "[0:(4-length)]) × \(.tool) (avg \(.avg_input_size) chars) → \(.status | ascii_upcase)"'
echo ""
echo "💡 OPTIMIZATIONS SUGGESTED:"
echo "$TOOL_DATA" | jq -r 'if (.summary.tools_to_optimize | length) > 0 then "  ⚠️  Consider optimizing: \(.summary.tools_to_optimize | join(", "))" else "  ✅ All tools usage looks efficient!" end'
```

## Tarification Opus 4.5

| Type | Prix/Million | Note |
|------|--------------|------|
| 📥 Input | $5.00 | Nouveaux tokens envoyés |
| 📤 Output | $25.00 | Tokens générés (5× plus cher!) |
| 💾 Cache Write | $6.25 | Tokens mis en cache (1.25×) |
| 💾 Cache Read | $0.50 | Tokens lus du cache (90% économie!) |

## Seuils de Contexte

| % | Status | Action |
|---|--------|--------|
| 0-50% | 🟢 OK | Continuer normalement |
| 50-70% | 🟡 WARNING | Surveiller, considérer /compact |
| 70-85% | 🟠 HIGH | Exécuter /compact bientôt |
| 85-100% | 🔴 CRITICAL | /compact MAINTENANT |

## Patterns Coûteux

| Pattern | Coût | Alternative |
|---------|------|-------------|
| `Task` agents | ~2-5K tokens/call | Utiliser `Grep/Glob` pour recherches simples |
| `Read` fichier entier | ~1-10K tokens | Utiliser `limit` et `offset` |
| `WebFetch` pages longues | ~5-20K tokens | Demander résumé spécifique |
| `Bash cat` | Variable | Utiliser `Read` tool |

## Actions Rapides

| Commande | Effet |
|----------|-------|
| `/0-tokens` | Ce dashboard |
| `/0-analyze` | Analyse détaillée des outils |
| `/compact` | Compresser l'historique |
| `/model haiku` | Passer au modèle moins cher |

## Comprendre les Économies de Cache

Le cache Claude permet d'économiser jusqu'à 90% sur les tokens répétés:

```
Sans cache:  100K tokens × $5/M = $0.50
Avec cache:  100K tokens × $0.50/M = $0.05
Économie:    $0.45 par 100K tokens!
```

Le cache a un TTL de 5 minutes. Pour maximiser les économies:
- Garder le contexte système stable
- Éviter de modifier les fichiers CLAUDE.md fréquemment
- Utiliser des prompts cohérents
