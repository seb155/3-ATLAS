# Current App Context

> Auto-detecte par ATLAS basee sur le working directory

## Detection

```text
Working Directory -> App Detection

apps/synapse/*  -> SYNAPSE
apps/nexus/*    -> NEXUS
apps/prism/*    -> PRISM
apps/atlas/*    -> ATLAS
forge/*         -> FORGE
racine          -> Global (monorepo)
```

## App Courante

```yaml
# Auto-rempli par ATLAS
app: [auto]
path: [auto]
backend_running: [auto]
frontend_running: [auto]
last_test_status: [auto]
```

## Details par App

### SYNAPSE
- **Backend**: `apps/synapse/backend/` (FastAPI)
- **Frontend**: `apps/synapse/frontend/` (React)
- **Port Backend**: 8000
- **Port Frontend**: 4000
- **Database**: synapse (forge-postgres)

### NEXUS
- **Frontend**: `apps/nexus/` (React + Neo4j)
- **Port**: 5173
- **Database**: Neo4j (dedicated)

### PRISM
- **Frontend**: `apps/prism/` (React)
- **Port**: 5174
- **Database**: PostgreSQL (shared)

### ATLAS
- **Type**: AI Collaboration
- **Status**: Planning

### FORGE
- **Path**: `forge/`
- **Type**: Infrastructure
- **Services**: PostgreSQL, Redis, Grafana, etc.

## Contexte de Travail

### Fichiers Recents
<!-- Auto-rempli -->
- ...

### Branches Git
<!-- Auto-rempli -->
- ...

### Taches en Cours
<!-- Auto-rempli -->
- ...

---

**Derniere mise a jour**: [auto]
