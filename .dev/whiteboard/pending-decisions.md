# Décisions Whiteboard - SYNAPSE MVP

> **Objectif:** Tracker les points de décision architecturale et fonctionnelle nécessitant validation avant développement.
>
> **Dernière mise à jour:** 2025-11-28
> **Statut global:** 2/10 validés

---

## Légende des statuts

| Statut | Signification |
|--------|---------------|
| `[ ]` | En attente de discussion |
| `[~]` | En cours de discussion |
| `[x]` | Validé |
| `[!]` | Bloquant pour le MVP |

---

## 1. Infrastructure & Base de données `[x]` VALIDÉ

### 1.1 Choix de la base de données
**Statut:** `[x]` Validé - Session #1 (2025-11-28)

**Décision finale:**

| Composant | Choix | Justification |
|-----------|-------|---------------|
| **Base principale** | PostgreSQL 15 | ACID, mature, JSON natif |
| **Extension AI** | pgvector | Embeddings pour semantic search |
| **Cache** | Redis 7 | Cache AI, sessions, job queue |
| **Suppression** | Soft delete | `deleted_at` timestamp |

**Architecture validée:**
```
PostgreSQL 15
├── Tables métier (assets, rules, cables, packages...)
├── pgvector (embeddings pour semantic search)
│   └── Recherche sur: FBS, LBS, WBS, priorités, tags
├── JSONB (attributs flexibles par type d'asset)
└── m_files_links (document_id, url, metadata)

Redis 7
├── Cache requêtes AI (coûteuses)
├── Sessions utilisateur
└── Job queue (sync Plant3D, futur M-Files)
```

**Intégrations AI confirmées:**
- **Ollama** (local) - Pour dev et données sensibles
- **OpenAI** (cloud) - Pour production/démo

**Volume cible:** Gros projets (5,000 - 50,000 assets par projet)

---

### 1.2 Structure des tables et relations
**Statut:** `[x]` Validé

**Décisions:**
- [x] Soft delete avec `deleted_at` timestamp
- [x] UUID comme clés primaires
- [x] JSONB pour attributs flexibles
- [x] Indexes sur project_id, tag, deleted_at

---

### 1.3 Backup & Recovery
**Statut:** `[ ]` En attente (post-MVP)

---

### 1.4 Intégration M-Files Cloud
**Statut:** `[x]` Validé (scope MVP)

**Décision MVP:**
- **Liens seulement** - Stockage de l'ID M-Files + URL
- Clic utilisateur → ouvre M-Files dans nouvel onglet

**Futur (post-MVP):**
- Scraper M-Files pour indexation
- Association automatique documents ↔ assets
- Preview dans SYNAPSE

---

## 2. Intégration Plant3D `[x]` VALIDÉ

### 2.1 Stratégie d'intégration
**Statut:** `[x]` Validé - Session #1 (2025-11-28)

**Contexte:**
- Plant3D 2025 (version unique)
- Accès direct à la DB SQL Server
- Besoin bidirectionnel

**Décision: Option B - Service intermédiaire**

**Architecture validée:**
```
┌─────────────┐       ┌─────────────────────┐       ┌─────────────┐
│   SYNAPSE   │       │    plant3d-sync     │       │  Plant3D    │
│   Frontend  │       │    (FastAPI)        │       │  SQL Server │
└──────┬──────┘       ├─────────────────────┤       └──────┬──────┘
       │              │ POST /sync/pull     │              │
       │              │ POST /sync/push     │              │
       ▼              │ GET  /sync/status   │              │
┌─────────────┐       │ GET  /sync/conflicts│              │
│   SYNAPSE   │◄─API─►│ POST /sync/resolve  │◄────SQL──────┘
│   Backend   │       ├─────────────────────┤
└─────────────┘       │ • Validation layer  │
                      │ • Conflict resolver │
                      │ • Audit logger      │
                      └──────────┬──────────┘
                                 │
                           ┌─────▼─────┐
                           │   Redis   │
                           │  (Queue)  │
                           └───────────┘
```

**Justification:**
- Isolation (pas de risque de corrompre Plant3D)
- Même stack Python/FastAPI
- Gestion des conflits centralisée
- Fonctionne même si Plant3D fermé

---

### 2.2 Fréquence de synchronisation
**Statut:** `[x]` Validé

**Décision: Hybride**
- **Auto:** Polling toutes les 5 minutes (configurable)
- **Manuel:** Bouton "Sync Now" dans l'UI
- **Queue Redis:** Pour jobs async et retry

---

### 2.3 Gestion des conflits - Split Ownership
**Statut:** `[x]` Validé

**Plant3D Master** (SYNAPSE lecture seule):
| Propriété | Source |
|-----------|--------|
| Tag | P&ID définit |
| Type d'équipement | P&ID définit |
| Line number | P&ID définit |
| P&ID Drawing ref | Plant3D |
| Specs techniques (size, rating, range) | Engineering data |

**SYNAPSE Master** (Plant3D lecture seule):
| Propriété | Source |
|-----------|--------|
| FBS (Functional Breakdown) | Structure projet |
| LBS (Location Breakdown) | Structure projet |
| WBS (Work Breakdown) | Structure projet |
| Priorité | Gestion projet |
| Tags custom | Métadonnées enrichies |
| Liens M-Files | Documents associés |
| Statut workflow | Approbation/révision |
| Notes / commentaires | Collaboration |
| Embeddings AI | Généré par SYNAPSE |

**Bidirectionnel** (timestamp gagne):
| Propriété | Règle |
|-----------|-------|
| Description | Le plus récent gagne |

---

### 2.4 Mapping des données Plant3D ↔ SYNAPSE
**Statut:** `[x]` Validé

```
Plant3D                          SYNAPSE
═══════════════════════════════════════════════════
Equipment (PnPDatabase)    ←→    Assets (type=Equipment)
├── Tag                    →     tag
├── Description            ↔     description
├── Class                  →     asset_type
├── Spec                   →     attributes.spec
└── Size                   →     attributes.size

Instruments               ←→    Assets (type=Instrument)
├── Tag                    →     tag
├── Loop                   →     attributes.loop
├── Type (FT, PT, TT...)   →     asset_subtype
├── Range                  →     attributes.range
└── Setpoint               →     attributes.setpoint

PipeLines                 ←→    Assets (type=Line) / Cables
├── Line Number            →     tag
├── Spec                   →     attributes.spec
├── Size                   →     attributes.size
└── From/To                →     connections

Valves                    ←→    Assets (type=Valve)
├── Tag                    →     tag
├── Type                   →     asset_subtype
└── Size                   →     attributes.size

P&ID Drawings             →     documents (liens)
├── Drawing Number         →     reference
└── Title                  →     description
```

---

## 3. UX/UI Design `[ ]`

### 3.1 Style visuel
**Statut:** `[ ]` En attente - Session #2

**Contexte actuel:**
- Thème VSCode-like (dark theme)
- Couleurs: `#1e1e1e` (fond), `#333333` (panels), `#007acc` (accent)
- Shadcn/ui + Tailwind CSS

**Questions à valider:**
- [ ] Le thème VSCode-like convient-il?
- [ ] Palette de couleurs définitive?
- [ ] Mode clair nécessaire?
- [ ] Branding Aurumax (logo, couleurs corporate)?

---

### 3.2 Composants critiques
**Statut:** `[ ]` En attente

**Questions à valider:**
- [ ] Design des tables (pagination, tri, filtres)
- [ ] Design des formulaires (validation inline?)
- [ ] Design du graphe métamodèle
- [ ] Design des règles (builder visuel?)

---

## 4. Modèle de données métier `[~]`

### 4.1 Structure des Assets
**Statut:** `[~]` Partiellement validé

**Structure validée:**
```
Asset
├── id (UUID)
├── tag (unique par projet)
├── description
├── asset_type (Equipment, Instrument, Line, Valve...)
├── asset_subtype (Pump, FT, PT, Gate Valve...)
├── discipline_id → Discipline
├── parent_asset_id → Asset (nullable)
├── status (enum: Design, Installed, Decommissioned)
├── attributes (JSONB - flexible par type)
│   ├── spec, size, range, setpoint...
│   └── custom fields
├── fbs_code → FBS (Functional Breakdown)
├── lbs_code → LBS (Location Breakdown)
├── wbs_code → WBS (Work Breakdown)
├── priority (1-5)
├── tags[] (custom tags pour search)
├── plant3d_id (sync reference)
├── project_id → Project
├── deleted_at (soft delete)
└── timestamps (created_at, updated_at)
```

**À valider Session #2:**
- [ ] Liste complète des disciplines
- [ ] Hiérarchie FBS/LBS/WBS
- [ ] Attributs par type d'asset

---

### 4.2 Disciplines
**Statut:** `[ ]` En attente - Session #2

**Proposition:**
| Code | Discipline | Couleur |
|------|------------|---------|
| `PROC` | Procédé (Process) | Bleu |
| `INST` | Instrumentation | Vert |
| `ELEC` | Électrique | Jaune |
| `PIPE` | Tuyauterie (Piping) | Rouge |
| `MECH` | Mécanique | Orange |
| `CIVL` | Civil/Structure | Gris |
| `HVAC` | CVC | Violet |

---

### 4.3 Types d'assets
**Statut:** `[ ]` En attente - Session #2

---

## 5. Règles métier (Rule Engine) `[ ]`

**Statut:** `[ ]` En attente

---

## 6. Import/Export `[ ]`

**Statut:** `[ ]` En attente

---

## 7. Authentification & Permissions `[ ]`

**Statut:** `[ ]` En attente

---

## 8. Workflow & Traçabilité `[ ]`

**Statut:** `[ ]` En attente

---

## 9. Performance & Scalabilité `[~]`

### 9.1 Volumes attendus
**Statut:** `[x]` Validé

| Métrique | Cible |
|----------|-------|
| Assets par projet | 5,000 - 50,000 |
| Projets simultanés | À définir |
| Utilisateurs concurrents | À définir |

---

## 10. Déploiement `[ ]`

**Statut:** `[ ]` En attente

---

## Historique des sessions

| Date | Participants | Sujets abordés | Décisions |
|------|--------------|----------------|-----------|
| 2025-11-28 | Seb + Claude | DB, Plant3D | PostgreSQL+pgvector+Redis, Service intermédiaire, Split ownership |

---

**Fichier créé:** 2025-11-28
**Mainteneur:** Équipe SYNAPSE
