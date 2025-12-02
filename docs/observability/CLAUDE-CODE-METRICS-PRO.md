# Claude Code Metrics PRO

Système d'observabilité avancé pour Claude Code et ATLAS.

## Vue d'ensemble

```
+------------------------+     +-------------------+     +---------------+
|   Claude Code          |     |  ccusage-exporter |     |   Prometheus  |
|   ~/.claude/projects/  | --> |   PRO             | --> |   (3090)      |
|   *.jsonl              |     |   (3202)          |     +-------+-------+
+------------------------+     +-------------------+             |
                                     |                           v
                               +-----+-----+              +---------------+
                               | /insights |              |   Grafana     |
                               | /summary  |              | Claude Code   |
                               +-----------+              | PRO Dashboard |
                                                          +---------------+
```

## Accès rapide

| Endpoint | URL | Description |
|----------|-----|-------------|
| **Dashboard** | https://grafana.axoiq.com | Dashboard "Claude Code PRO" |
| **Métriques** | http://localhost:3202/metrics | Format Prometheus |
| **Insights** | http://localhost:3202/insights | Recommandations d'optimisation |
| **Résumé** | http://localhost:3202/summary | Vue rapide JSON |

## Métriques disponibles

### Token Flow (Flux de tokens)

| Métrique | Description | Importance |
|----------|-------------|------------|
| `claude_code_tokens_sent_total` | Tokens **envoyés** au cloud (input) | Ce que VOUS payez en contexte |
| `claude_code_tokens_received_total` | Tokens **reçus** de Claude (output) | Réponses de l'IA |
| `claude_code_tokens_cached_total` | Tokens depuis le **cache** | GRATUIT! Économies |
| `claude_code_tokens_cache_created_total` | Tokens pour créer le cache | Investissement one-time |

### Comprendre le flux

```
VOUS (Input)                              CLAUDE (Output)
    |                                          ^
    v                                          |
+---+---+     +---------+     +--------+      |
| Prompt| --> | Cache?  | --> | API    | -----+
| Context     | YES: $0 |     | Cloud  |
| Files |     | NO: $$$ |     |        |
+-------+     +---------+     +--------+
```

**Input tokens (envoyés):**
- Votre prompt/question
- Le contexte (fichiers lus, historique)
- Les instructions système

**Output tokens (reçus):**
- La réponse de Claude
- Le code généré
- Les tool calls

**Cached tokens (économies!):**
- Contexte déjà mis en cache
- Économise ~90% du coût input
- Plus le cache hit rate est élevé, mieux c'est

### Coûts

| Métrique | Description |
|----------|-------------|
| `claude_code_cost_usd` | Coût total (all-time) |
| `claude_code_cost_monthly_usd` | Coût du mois en cours |
| `claude_code_cost_saved_cache_usd` | Argent économisé grâce au cache |
| `claude_code_budget_used_usd` | Budget utilisé ce mois |
| `claude_code_budget_remaining_usd` | Budget restant |
| `claude_code_budget_used_percent` | % du budget utilisé |

### ATLAS Commands

| Métrique | Description |
|----------|-------------|
| `claude_code_atlas_commands_total{command}` | Usage des commandes slash |
| `claude_code_workflows_total{workflow}` | Types de workflows détectés |

**Commandes trackées:**
- `/0-new-session`, `/0-next`, `/0-resume`
- `/0-ship`, `/0-progress`, `/0-dashboard`
- `/compact`, `/clear`, `/help`, `/doctor`

**Workflows détectés:**
- `testing` - Tests (pytest, jest)
- `git_operations` - Git (commit, push, merge)
- `debugging` - Debug (fix, error, bug)
- `development` - Dev (create, add, implement)
- `documentation` - Docs (readme, comment)
- `deployment` - Deploy (docker, container)
- `api_development` - API (endpoint, route)

### Optimisation

| Métrique | Description | Bon si |
|----------|-------------|--------|
| `claude_code_cache_hit_rate` | Taux de cache hit | > 50% |
| `claude_code_avg_output_tokens` | Tokens moyens par réponse | < 1000 |
| `claude_code_model_switches_total` | Changements de modèle en session | < 5 |
| `claude_code_optimization_insights_total` | Alertes d'optimisation | 0 |

### Tools

| Métrique | Description |
|----------|-------------|
| `claude_code_tools_total{tool, project}` | Usage par outil |

**Top tools typiques:**
- `Read` - Lecture fichiers
- `Edit` - Modifications
- `Bash` - Commandes shell
- `Task` - Agents
- `Grep` - Recherche contenu

## Dashboard Grafana

### Sections

1. **Token Flow Analysis**
   - Sent vs Received vs Cached
   - Cache hit rate gauge
   - Money saved indicator

2. **ATLAS Commands & Workflows**
   - Top commandes utilisées (table)
   - Distribution des workflows (pie)
   - Top 10 tools (bar chart)

3. **Cost Analysis & Budget**
   - Budget gauge ($300 Max)
   - Daily cost by model
   - Burn rate per day

4. **Usage Patterns**
   - Heatmap par heure
   - Cost by model distribution
   - Avg output tokens

5. **Projects & Sessions**
   - Table détaillée par projet

## API Endpoints

### GET /insights

Retourne les recommandations d'optimisation:

```json
{
  "insights": [
    {
      "type": "cache_optimization",
      "severity": "high",
      "project": "AXIOM",
      "message": "Cache hit rate is 25%. Consider structuring prompts...",
      "potential_savings": "up to 90% on repeated context"
    }
  ],
  "generated_at": "2025-12-02T10:00:00",
  "total_insights": 1
}
```

### GET /summary

Vue rapide de l'utilisation:

```json
{
  "token_flow": {
    "sent_to_claude": 1500000,
    "received_from_claude": 450000,
    "from_cache": 800000,
    "cache_efficiency": "34.8%"
  },
  "costs": {
    "this_month": "$45.23",
    "saved_via_cache": "$12.50",
    "budget_remaining": "$254.77"
  },
  "top_commands": {
    "session_start": 45,
    "git_workflow": 32,
    "agent_spawn": 28
  },
  "top_workflows": {
    "development": 120,
    "testing": 85,
    "debugging": 45
  }
}
```

## Optimisations recommandées

### 1. Maximiser le cache

```markdown
Problème: Cache hit rate < 30%
Solution:
- Utiliser /compact avant les longues sessions
- Structurer les prompts de manière cohérente
- Éviter de changer de contexte fréquemment
```

### 2. Utiliser le bon modèle

```markdown
Problème: Opus pour des tâches simples
Solution:
- Haiku pour: lecture fichiers, recherche, questions simples
- Sonnet pour: code generation, refactoring
- Opus pour: architecture, décisions complexes
```

### 3. Réduire le contexte

```markdown
Problème: Input >> Output (ratio < 0.3)
Solution:
- Moins de fichiers en contexte
- Questions plus ciblées
- Utiliser /clear entre les tâches
```

## Déploiement

```bash
# Rebuild l'exporter avec la version PRO
cd /d/Projects/AXIOM/forge
docker compose -f docker-compose.yml -f docker-compose.observability.yml build ccusage-exporter

# Redémarrer
docker compose -f docker-compose.yml -f docker-compose.observability.yml up -d ccusage-exporter

# Vérifier
curl http://localhost:3202/health
curl http://localhost:3202/summary
```

## Pricing (Décembre 2025)

| Modèle | Input/M | Output/M | Cache Read/M |
|--------|---------|----------|--------------|
| Opus 4.5 | $5.00 | $25.00 | $0.50 |
| Sonnet 4.5 | $3.00 | $15.00 | $0.30 |
| Haiku 4.5 | $1.00 | $5.00 | $0.10 |

**Note:** Le cache read coûte 90% moins cher que l'input standard!

## Troubleshooting

### Pas de données dans Grafana

1. Vérifier que l'exporter tourne:
   ```bash
   docker logs forge-ccusage-exporter
   ```

2. Vérifier les métriques:
   ```bash
   curl http://localhost:3202/metrics | head -50
   ```

3. Vérifier les fichiers JSONL:
   ```bash
   ls -la ~/.claude/projects/
   ```

### Cache hit rate = 0

- Normal si nouvelle session
- Le cache se construit au fil du temps
- Utiliser `/compact` ne réinitialise PAS le cache

### Insights severity = high

- Lire les recommandations: `curl http://localhost:3202/insights`
- Appliquer les optimisations suggérées
- Re-vérifier après quelques sessions
