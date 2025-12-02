# Skill: Infrastructure Status

Affiche rapidement le status de l'infrastructure AXIOM.

## Instructions

Quand ce skill est invoqué, exécuter les actions suivantes:

### 1. Lire le registry
```
Fichier: .dev/infra/registry.yml
```

### 2. Vérifier les services Docker (si possible)
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Docker non accessible"
```

### 3. Afficher le dashboard infrastructure

```
🏗️ AXIOM Infrastructure Status
═══════════════════════════════════════════════════════════════════

📦 Services FORGE
─────────────────────────────────────────────────────────────────
Service          Container           Port      Status
─────────────────────────────────────────────────────────────────
PostgreSQL       forge-postgres      5433      [status]
Redis            forge-redis         6379      [status]
MeiliSearch      forge-meilisearch   7700      [status]
Grafana          forge-grafana       3000      [status]
pgAdmin          forge-pgadmin       5050      [status]
Traefik          forge-traefik       80/443    [status]

═══════════════════════════════════════════════════════════════════

📱 Applications
─────────────────────────────────────────────────────────────────
App              Frontend    Backend     Database    Status
─────────────────────────────────────────────────────────────────
SYNAPSE          4000        4001        synapse     [status]
NEXUS            5000        5001        nexus       [status]

═══════════════════════════════════════════════════════════════════

🌐 URLs (via Traefik)
─────────────────────────────────────────────────────────────────
https://synapse.axoiq.com     → SYNAPSE Frontend
https://api.axoiq.com         → SYNAPSE API
https://nexus.axoiq.com       → NEXUS Frontend
https://grafana.axoiq.com     → Grafana
https://traefik.axoiq.com     → Traefik Dashboard

═══════════════════════════════════════════════════════════════════

📊 Port Ranges
─────────────────────────────────────────────────────────────────
FORGE:    3000-3999  (9 allocated)
SYNAPSE:  4000-4999  (2 allocated)
NEXUS:    5000-5999  (2 allocated)
APEX:     6000-6999  (0 allocated)
CORTEX:   7000-7999  (2 allocated)

═══════════════════════════════════════════════════════════════════
```

### 4. Si problème détecté
- Identifier le service en erreur
- Suggérer commande de diagnostic:
  ```bash
  docker logs {container} --tail 50
  ```

## Notes

- Ce skill est READ-ONLY - pas de modifications
- Pour modifier l'infrastructure, utiliser DevOps Manager agent
- Les fichiers infrastructure sont PROTÉGÉS (règle 20)
