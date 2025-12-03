# Claude Code Observability Stack

Documentation pour le stack d'observabilité Claude Code dans FORGE.

## Vue d'ensemble

Le stack permet de monitorer l'utilisation de Claude Code sans consommer de tokens API:
- **Prometheus**: Stockage time-series des métriques
- **ccusage-exporter**: Parse les fichiers JSONL locaux (~/.claude/projects/)
- **Grafana**: Dashboard professionnel de visualisation

## URLs

| Service | URL | Description |
|---------|-----|-------------|
| Grafana | https://grafana.axoiq.com | Dashboard principal |
| Prometheus | https://prometheus.axoiq.com | Métriques brutes |
| Exporter | http://localhost:3202/metrics | Endpoint Prometheus |

## Métriques Disponibles

### Tokens & Coûts

| Métrique | Labels | Description |
|----------|--------|-------------|
| `claude_code_tokens_total` | model, type, project | Tokens par modèle/type |
| `claude_code_cost_usd` | model, project | Coût total (all-time) |
| `claude_code_cost_monthly_usd` | model, project | Coût du mois en cours |

### Sessions & Messages

| Métrique | Labels | Description |
|----------|--------|-------------|
| `claude_code_sessions_total` | project | Sessions par projet |
| `claude_code_messages_total` | role, project | Messages par rôle |
| `claude_code_tools_total` | tool, project | Appels d'outils |

### Réponses & Santé

| Métrique | Labels | Description |
|----------|--------|-------------|
| `claude_code_responses_total` | status, project | success/truncated/error |
| `claude_code_last_activity_timestamp` | project | Dernier activité |

### Budget (Max Plan $300/mois)

| Métrique | Description |
|----------|-------------|
| `claude_code_budget_monthly_usd` | Budget mensuel ($300) |
| `claude_code_budget_used_usd` | Montant utilisé ce mois |
| `claude_code_budget_remaining_usd` | Budget restant |
| `claude_code_budget_used_percent` | % du budget utilisé |

## Pricing (Décembre 2025)

| Modèle | Input | Output | Cache Read | Cache Write |
|--------|-------|--------|------------|-------------|
| **Opus 4.5** | $5/M | $25/M | $0.50/M | $6.25/M |
| **Sonnet 4.5** | $3/M | $15/M | $0.30/M | $3.75/M |
| **Haiku 4.5** | $1/M | $5/M | $0.10/M | $1.25/M |

> Note: Opus 4.5 a baissé de 67% (était $15/$75)

## Dashboard Grafana

Le dashboard "Claude Code Statistics" contient:

1. **Overview**: Total tokens, sessions, coûts jour/semaine, cache efficiency, burn rate
2. **Budget & Health**: Budget gauge, remaining, success rate, erreurs
3. **Token & Cost Trends**: Usage over time, cost by model
4. **Daily Cost**: Bar chart par jour/modèle
5. **Model & Tool Analytics**: Distribution tokens, outils utilisés, message types
6. **Sessions & Activity**: Sessions over time, messages over time
7. **Projects Breakdown**: Table avec coût/tokens/sessions par projet

## Configuration

### Variables d'environnement (docker-compose.observability.yml)

```yaml
ccusage-exporter:
  environment:
    - CLAUDE_PROJECTS_DIR=/data/claude-projects
    - SCRAPE_INTERVAL=60
    - METRICS_PORT=9091
    - CLAUDE_MONTHLY_BUDGET=300
```

### Fichiers

| Fichier | Description |
|---------|-------------|
| `docker-compose.observability.yml` | Stack Docker |
| `services/ccusage-exporter/exporter.py` | Parseur JSONL |
| `config/prometheus/prometheus.yml` | Config Prometheus |
| `config/grafana/provisioning/dashboards/claude-code/` | Dashboard JSON |

## Démarrage

```bash
cd /home/seb/projects/AXIOM/forge

# Démarrer le stack complet
docker compose -f docker-compose.yml -f docker-compose.observability.yml up -d

# Rebuild l'exporter après modifications
docker compose -f docker-compose.yml -f docker-compose.observability.yml up -d --build ccusage-exporter

# Voir les logs
docker logs forge-ccusage-exporter -f
```

## Troubleshooting

### Vérifier les métriques

```bash
curl http://localhost:3202/metrics | head -50
curl http://localhost:3202/health
```

### Vérifier Prometheus

```bash
curl http://localhost:3090/api/v1/targets
```

### Recharger Grafana

```bash
docker restart forge-grafana
```

## Structure JSONL

Les fichiers Claude Code sont dans `~/.claude/projects/<project-hash>/*.jsonl`:

```json
{
  "cwd": "/home/seb/projects/AXIOM",
  "sessionId": "uuid",
  "timestamp": "2025-12-01T22:04:18.748Z",
  "message": {
    "model": "claude-opus-4-5-20251101",
    "role": "assistant",
    "usage": {
      "input_tokens": 10,
      "output_tokens": 231,
      "cache_read_input_tokens": 0,
      "cache_creation_input_tokens": 30545
    },
    "stop_reason": "end_turn"
  }
}
```

## Historique

- **2025-12-01**: Création initiale avec Prometheus + OTEL + ccusage-exporter
- **2025-12-02**: Ajout extraction noms projets, success rate, budget tracking, prix Opus 4.5 mis à jour
