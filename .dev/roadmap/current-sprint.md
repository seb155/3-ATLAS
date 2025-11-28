# Current Sprint: MVP Critical Features Design & Implementation

**Status:** IN PROGRESS
**Target:** 2025-12-20 (MVP Demo)
**Phase:** Design Complete → Implementation Starting

---

## 🎯 Sprint Goal

Design et implémenter les 3 features critiques pour le MVP avec un système de **logs/traçabilité central** qui permet de "montrer ce qui se passe" pendant la démo.

---

## ✅ Completed Previously (v0.2.2)

### Command Palette (Ctrl+K) ✅
- [x] Global search across all entities
- [x] Fuzzy matching with `thefuzz`
- [x] Navigation shortcuts
- [x] Quick actions
- [x] Recent searches (localStorage)
- [x] Keyboard shortcuts (Ctrl+K, Ctrl+P, Escape)

### Global Search Bar ✅
- [x] Search bar in title bar
- [x] Backend `/api/v1/search` endpoint
- [x] Results grouped by type
- [x] Relevance scoring

### AI Provider Abstraction ✅
- [x] Multi-provider support (Ollama, OpenAI, Gemini)
- [x] Backend `/api/v1/ai` endpoints
- [x] Runtime provider switching
- [x] Frontend proxy (no API keys in browser)

### Production Infrastructure ✅
- [x] `docker-compose.prod.yml` with scaling
- [x] Nginx load balancer config
- [x] Gunicorn production server
- [x] Ollama container for local AI
- [x] `DEPLOYMENT.md` documentation

### MeiliSearch Integration ✅
- [x] MeiliSearch v1.11 in Docker (MIT License - 100% Free)
- [x] Multi-index search (assets, rules, cables, locations)
- [x] Typo-tolerant full-text search (~10ms for 10K+ docs)
- [x] Automatic fallback to `thefuzz` when unavailable
- [x] Re-indexing API endpoints (`POST /search/reindex`)
- [x] Index statistics endpoint (`GET /search/status`)
- [x] Project-based filtering
- [x] Backend service: `meilisearch_service.py`

---

## 📅 Timeline

### ✅ 2025-11-28: Whiteboard Session (COMPLETE)
**Objectif:** Design complet AVANT implémentation

- [x] Analyse architecture existante
- [x] Design système de Logs & Traçabilité
- [x] Design Rule Engine (3 actions MVP)
- [x] Design CSV Import pipeline
- [x] Design Package Export
- [x] Décisions architecture
- [ ] Review avec stakeholder

**Document:** `.dev/design/2025-11-28-whiteboard-session.md`

### 📅 2025-12-02 → 2025-12-06: Implementation Week 1
| Jour | Focus | Livrables |
|------|-------|-----------|
| Lun | Database | `workflow_events`, `rules`, `packages` tables + migration |
| Mar | Logging | `WorkflowLogger` service + WebSocket enhanced |
| Mer | Rule Engine | Condition evaluator + CREATE_CHILD action |
| Jeu | Rule Engine | CREATE_CABLE + CREATE_PACKAGE actions |
| Ven | Integration | CSV Import avec logging complet |

### 📅 2025-12-09 → 2025-12-13: Implementation Week 2
| Jour | Focus | Livrables |
|------|-------|-----------|
| Lun | Package | Templates IN-P040, CA-P040 (Excel) |
| Mar | UI | DevConsole enhanced + Timeline view |
| Mer | UI | Asset History (diff view) |
| Jeu | Tests | Backend 70%+ coverage |
| Ven | Tests | Frontend tests + E2E |

### 📅 2025-12-16 → 2025-12-20: Demo Prep
| Jour | Focus | Livrables |
|------|-------|-----------|
| Lun | Polish | Loading states, error handling, toasts |
| Mar | Data | Demo dataset (BBA.csv + rules configurées) |
| Mer | Demo | Script de démo (5 min) |
| Jeu | Rehearsal | 3x demo rehearsal, fix bugs |
| Ven | **DEMO** | Présentation employeur |

---

## 🏗️ Features Critiques MVP

### 1. Système de Logs & Traçabilité (CENTRAL)
**Priorité:** #1 (Base pour tout le reste)
**Status:** 🔄 Design complet, implémentation pending

**Composants:**
- `workflow_events` table (PostgreSQL)
- `WorkflowLogger` service (Python)
- WebSocket broadcast (real-time)
- DevConsole enhanced (UI)
- Timeline view (UI)
- Asset History avec diff (UI)

**Value Démo:**
> "Regardez, chaque action est tracée. Je peux voir exactement
> ce que le Rule Engine a fait, sur quel asset, et pourquoi."

### 2. Rule Engine
**Priorité:** #2 (Coeur de l'automatisation)
**Status:** 🔄 Design complet, implémentation pending

**Actions MVP:**
1. `CREATE_CHILD` - Crée un asset enfant (ex: Motor pour Pump)
2. `CREATE_CABLE` - Crée un câble entre assets
3. `CREATE_PACKAGE` - Groupe assets dans un package

**Value Démo:**
> "J'importe 100 instruments, le Rule Engine crée automatiquement
> les moteurs, les câbles, et les packages. 500+ assets en 5 secondes."

### 3. CSV Import
**Priorité:** #3 (Point d'entrée des données)
**Status:** 🔄 40% (Backend pending)

**Pipeline:**
1. Upload → Parse → Preview
2. Column mapping (auto-detect + manuel)
3. Validation (required fields, types)
4. Import avec logging complet
5. Trigger rules (optionnel)

### 4. Package Export
**Priorité:** #4 (Livrable final)
**Status:** ⚠️ Not started

**Templates MVP:**
- IN-P040 (Instrument Index)
- CA-P040 (Cable Schedule)

**Format:** Excel (openpyxl + Jinja2)

---

## 📊 Database Schema (Nouvelles Tables)

```sql
-- À créer cette semaine
workflow_events     -- Tous les événements (logs structurés)
asset_changes       -- Changements par asset (audit trail)
rules               -- Définitions des règles
rule_executions     -- Historique d'exécution
packages            -- Packages livrables
```

**Migration:** `alembic revision -m "add_mvp_tables"`

---

## 🔧 Stack Technique

| Composant | Technologie | Status |
|-----------|-------------|--------|
| Logs DB | PostgreSQL (`workflow_events`) | 📋 À créer |
| Logs Stream | WebSocket (existant) | ✅ Ready |
| Logs UI | DevConsole (existant) | 🔄 À améliorer |
| Rule Engine | Python service | 📋 À créer |
| Templates | Jinja2 + openpyxl | 📋 À créer |
| Timeline | React component | 📋 À créer |
| Diff View | React component | 📋 À créer |
| Search | MeiliSearch | ✅ Ready |

---

## ✅ Acceptance Criteria (Démo)

### Import CSV
- [ ] Upload BBA.csv (100 instruments)
- [ ] Voir preview des données
- [ ] Mapper colonnes automatiquement
- [ ] Voir progress en temps réel dans DevConsole
- [ ] Import complété en <5s

### Rule Engine
- [ ] Exécuter "Create Motor for Pump"
- [ ] Voir chaque asset créé dans DevConsole
- [ ] 49 motors créés automatiquement
- [ ] Exécuter "Generate Power Cables"
- [ ] 95 cables créés avec sizing automatique
- [ ] Voir warnings pour cables >100m

### Traçabilité
- [ ] Ouvrir Timeline view
- [ ] Voir chronologie des événements
- [ ] Cliquer sur un asset → voir son historique
- [ ] Voir diff entre versions
- [ ] Pouvoir identifier: "qui a changé quoi et pourquoi"

### Export
- [ ] Sélectionner Area 210
- [ ] Générer package IN-P040
- [ ] Download Excel formaté
- [ ] 47 instruments dans le fichier

---

## 📝 Notes de Design

### Pourquoi le système de logs est central?

1. **Démo Impact:** Montre la valeur de l'automatisation
2. **Debug:** Permet de comprendre les erreurs
3. **Audit:** Répond à "qui a fait quoi"
4. **Rollback:** Base pour undo/redo futur
5. **Compliance:** Traçabilité pour audits externes

### Décisions Architecture

| Décision | Choix | Raison |
|----------|-------|--------|
| Logs storage | PostgreSQL | Query flexibility + joins avec assets |
| Real-time | WebSocket | Déjà implémenté, performant |
| Rule config | Database | Modifiable sans redeploy |
| Templates | Jinja2 | Standard Python, flexible |
| Excel | openpyxl | Template support, formatting |
| Search | MeiliSearch | Fast (~10ms), typo-tolerant |
| AI fallback | thefuzz | Graceful degradation |

---

## 🚨 Risques

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Rule Engine complexe | HIGH | 3 actions simples, JSON config |
| Logs volume | MEDIUM | Pagination, retention policy |
| Timeline perf | MEDIUM | Lazy loading, virtualization |
| Excel formatting | LOW | Tests manuels exhaustifs |

---

## 📚 Documentation

- **Whiteboard Session:** `.dev/design/2025-11-28-whiteboard-session.md`
- **Architecture Review:** `.dev/analysis/2025-11-28-architecture-review.md`
- **Search Implementation:** `backlog/search-navigation.md`
- **Deployment:** `apps/synapse/DEPLOYMENT.md`
- **API Docs:** `http://localhost:8001/docs`

---

**Updated:** 2025-11-28 (Merged v0.2.2 completion + MVP planning)
