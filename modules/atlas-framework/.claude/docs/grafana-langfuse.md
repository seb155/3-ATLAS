# Grafana Dashboard pour Langfuse

Dashboard de visualisation des métriques LLM ATLAS dans Grafana.

## Accès

- **Grafana**: http://localhost:3000
- **Login**: admin / admin
- **Dashboard**: Dashboards → Langfuse → ATLAS - Langfuse LLM Observability

**Lien direct**: http://localhost:3000/d/atlas-langfuse

## Panels

### Row 1: Métriques clés (4 stats)

| Panel | Description |
|-------|-------------|
| **Traces (24h)** | Nombre de traces dans les dernières 24h |
| **Tokens (24h)** | Total tokens consommés |
| **Cost (24h)** | Coût total en USD |
| **Total Traces** | Nombre total de traces all-time |

### Row 2: Timelines (2 graphiques)

| Panel | Description |
|-------|-------------|
| **Traces Timeline** | Nombre de traces par heure (7 jours) |
| **Cost Timeline** | Coût par heure (7 jours) |

### Row 3: Répartition (3 pie charts)

| Panel | Description |
|-------|-------------|
| **Traces by Agent** | Distribution par agent ATLAS |
| **Traces by Event** | Distribution par type (start, stop, checkpoint) |
| **Traces by Project** | Distribution par projet |

### Row 4: Table détaillée

| Colonne | Description |
|---------|-------------|
| timestamp | Heure du trace |
| name | Nom du trace (atlas-start, atlas-stop) |
| agent | Agent ATLAS utilisé |
| project | Projet concerné |
| tokens | Tokens totaux |
| cost | Coût en USD |
| tags | Tags associés |

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Grafana                           │
│                  localhost:3000                      │
│  ┌───────────────────────────────────────────────┐  │
│  │         ATLAS - Langfuse Dashboard            │  │
│  └───────────────────────┬───────────────────────┘  │
└──────────────────────────│──────────────────────────┘
                           │ SQL Queries
                           ▼
┌─────────────────────────────────────────────────────┐
│              PostgreSQL (forge-postgres)            │
│                    Database: langfuse               │
│  ┌─────────────┐  ┌─────────────┐                  │
│  │   traces    │  │ observations│                  │
│  └─────────────┘  └─────────────┘                  │
└─────────────────────────────────────────────────────┘
```

## Datasource

```yaml
# config/grafana/provisioning/datasources/datasources.yaml
- name: Langfuse
  type: postgres
  uid: langfuse-postgres
  url: forge-postgres:5432
  database: langfuse
  user: postgres
```

## Requêtes SQL clés

### Traces par agent
```sql
SELECT
  COALESCE(metadata->>'agent', 'unknown') as agent,
  COUNT(*) as count
FROM traces
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY 1
ORDER BY 2 DESC
```

### Coût par heure
```sql
SELECT
  date_trunc('hour', start_time) as time,
  SUM(COALESCE(calculated_total_cost, total_cost, 0))::float as cost
FROM observations
WHERE start_time >= NOW() - INTERVAL '7 days'
GROUP BY 1
ORDER BY 1
```

### Traces récents avec coût
```sql
SELECT
  t.timestamp,
  t.name,
  t.metadata->>'agent' as agent,
  COALESCE(SUM(o.total_tokens), 0) as tokens,
  COALESCE(SUM(o.calculated_total_cost), 0)::float as cost
FROM traces t
LEFT JOIN observations o ON o.trace_id = t.id
GROUP BY t.id
ORDER BY t.timestamp DESC
LIMIT 50
```

## Alertes (optionnel)

Pour ajouter des alertes Grafana:

1. Ouvrir le dashboard
2. Éditer un panel (ex: Cost 24h)
3. Tab "Alert" → Create alert rule
4. Condition: `WHEN last() OF query(A) IS ABOVE 10`
5. Notification: Discord/Slack webhook

## Fichiers

```
modules/forge/config/grafana/provisioning/
├── datasources/
│   └── datasources.yaml          # Datasource Langfuse ajoutée
└── dashboards/
    ├── dashboards.yaml           # Provider Langfuse ajouté
    └── langfuse/
        └── atlas-langfuse.json   # Dashboard JSON
```

## Refresh

- Auto-refresh: 30 secondes
- Time range par défaut: 7 jours
- Modifiable dans l'UI Grafana

## Troubleshooting

### Dashboard vide
```bash
# Vérifier que Langfuse a des traces
docker exec forge-postgres psql -U postgres -d langfuse \
  -c "SELECT COUNT(*) FROM traces"
```

### Erreur datasource
```bash
# Vérifier la connexion PostgreSQL
docker exec forge-grafana wget -qO- \
  "http://localhost:3000/api/datasources/proxy/uid/langfuse-postgres/health"
```

### Redémarrer Grafana
```bash
cd modules/forge
docker-compose restart grafana
```
