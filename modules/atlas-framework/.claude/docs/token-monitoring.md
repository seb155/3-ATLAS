# Token Monitoring System

Système de monitoring précis des tokens pour ATLAS Framework.

## Vue d'ensemble

Le système parse les fichiers transcript JSONL de Claude Code pour obtenir les **vrais** compteurs de tokens, remplaçant l'ancienne estimation basée sur le coût.

## Composants

### Scripts

| Script | Description |
|--------|-------------|
| `scripts/parse-tokens.sh` | Parse les transcripts JSONL pour les compteurs précis |
| `scripts/analyze-tools.sh` | Analyse les patterns d'utilisation des outils |
| `scripts/statusline.sh` | Status line responsive avec tokens/coût/contexte |

### Commandes

| Commande | Description |
|----------|-------------|
| `/0-tokens` | Dashboard complet avec breakdown et analytics |
| `/0-analyze` | Analyse détaillée des patterns d'utilisation |

## Tarification Opus 4.5

| Type | Prix/Million | Description |
|------|--------------|-------------|
| 📥 Input | $5.00 | Nouveaux tokens envoyés |
| 📤 Output | $25.00 | Tokens générés (5× plus cher) |
| 💾 Cache Write | $6.25 | Tokens mis en cache (1.25×) |
| 💾 Cache Read | $0.50 | Tokens lus du cache (90% économie!) |

## Status Line Responsive

La status line s'adapte automatiquement à la largeur du terminal:

### Modes d'affichage

| Largeur | Mode | Affichage |
|---------|------|-----------|
| < 60 | Ultra Compact | `💰 $0.45 │ 🟢 37%` |
| 60-89 | Compact | `🏛️ ATLAS │ 🧠 Opus │ 💰 $0.45 │ 🟢 37%` |
| 90-119 | Standard | `+ 📝 75K` (total tokens) |
| ≥ 120 | Full | `+ 📥 5K │ 📤 2K │ 💾 68K` (breakdown) |

### Exemple Full Mode

```
🏛️ ATLAS │ 🧠 Opus │ 📁 PROJECT │ 🥇 ATLAS │ 📥 20K │ 📤 26K │ 💾 10.8M │ 💰 $11.3 │ 🔴 100%
```

### Indicateurs Contexte

| Icône | % | Status | Action |
|-------|---|--------|--------|
| 🟢 | 0-50% | OK | Continuer |
| 🟡 | 50-70% | WARNING | Surveiller |
| 🟠 | 70-85% | HIGH | Considérer /compact |
| 🔴 | 85-100% | CRITICAL | /compact requis |

## Configuration

### Forcer un mode d'affichage

Pour les terminaux split, définir la variable d'environnement:

```bash
# Dans ~/.bashrc ou ~/.zshrc
export ATLAS_TERM_WIDTH=70   # Force COMPACT
export ATLAS_TERM_WIDTH=100  # Force STANDARD
export ATLAS_TERM_WIDTH=150  # Force FULL (défaut)
```

### Fichiers de données

Les transcripts sont stockés dans:
```
~/.claude/projects/-{encoded-path}/*.jsonl
```

Chaque message contient:
```json
{
  "message": {
    "usage": {
      "input_tokens": 100,
      "output_tokens": 500,
      "cache_creation_input_tokens": 5000,
      "cache_read_input_tokens": 20000
    }
  }
}
```

## Analytics des Outils

Le script `analyze-tools.sh` identifie les outils coûteux:

```bash
bash .claude/scripts/analyze-tools.sh
```

### Patterns Coûteux

| Pattern | Coût | Alternative |
|---------|------|-------------|
| `Task` agents | ~2-5K tokens/call | `Grep/Glob` pour recherches |
| `WebFetch` | ~5-20K tokens | Demander résumé spécifique |
| `Read` entier | ~1-10K tokens | Utiliser `limit` et `offset` |

### Métriques Cibles

| Métrique | Bon | Acceptable | À Optimiser |
|----------|-----|------------|-------------|
| Cache efficiency | >70% | 50-70% | <50% |
| Task calls/session | <10 | 10-20 | >20 |
| Avg tool input | <500 chars | 500-1000 | >1000 |

## Cache Claude

Le cache permet jusqu'à 90% d'économies:

```
Sans cache:  100K tokens × $5/M = $0.50
Avec cache:  100K tokens × $0.50/M = $0.05
Économie:    $0.45 par 100K tokens!
```

### Maximiser le cache

- TTL de 5 minutes - garder les requêtes rapprochées
- Contexte système stable (CLAUDE.md, agents)
- Éviter de modifier les fichiers de config fréquemment

## Dépannage

### Status line affiche mode compact

Le script détecte mal la largeur en mode pipe. Solutions:
1. Définir `ATLAS_TERM_WIDTH=150` dans l'environnement
2. Vérifier que le script a les bonnes fins de ligne (LF, pas CRLF)

### Pas de données tokens

Vérifier que:
1. `jq` est installé
2. Le transcript existe: `ls ~/.claude/projects/-$(pwd | sed 's|/|-|g')/`
3. Le script est exécutable: `chmod +x .claude/scripts/*.sh`

### Context % toujours à 100%

C'est normal si beaucoup de cache est utilisé. Le % est capé à 100%.
Pour le vrai context window %, utiliser ccstatusline avec `context-percentage`.
