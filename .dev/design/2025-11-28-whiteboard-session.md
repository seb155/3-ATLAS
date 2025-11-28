# Whiteboard Session - 2025-11-28

## Sprint Objectif: Design des Features Critiques MVP

**Date:** 2025-11-28
**Focus:** Architecture design AVANT implémentation
**Priorité #1:** Système de Logs & Traçabilité (CENTRAL pour la démo)

---

## 🎯 Vision Démo

**Ce que l'employeur doit voir:**
```
"Wow, je peux voir exactement ce qui se passe à chaque étape!"
"C'est comme avoir un X-ray de tout le processus d'ingénierie"
"Je peux tracer n'importe quel changement jusqu'à sa source"
"Je peux voir mes données par fonction, par location, par discipline!"
```

---

## 0. MULTI-VIEW ARCHITECTURE (Concept Fondamental)

### 0.1 Le Problème

En ingénierie EPCM, les mêmes données doivent être vues sous **différents angles**:
- Un électricien veut voir **par discipline** (tous les moteurs, tous les câbles)
- Un superviseur veut voir **par zone/location** (tout ce qui est dans Area 210)
- Un chef de projet veut voir **par fonction** (tout le système de pompage)
- Un planificateur veut voir **par work package** (ce qui doit être livré cette semaine)

**SYNAPSE doit permettre de filtrer/présenter TOUT par ces différentes vues.**

### 0.2 Les 6 Breakdown Structures

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BREAKDOWN STRUCTURES                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                     │
│  │     FBS     │    │     LBS     │    │     PBS     │                     │
│  │ Functional  │    │  Location   │    │  Product    │                     │
│  │ Breakdown   │    │  Breakdown  │    │  Breakdown  │                     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                     │
│         │                  │                  │                             │
│    "QUOI"             "OÙ"              "COMPOSANTS"                        │
│  (Fonction)        (Emplacement)        (Hiérarchie)                        │
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                     │
│  │     WBS     │    │    DISC     │    │     CBS     │                     │
│  │    Work     │    │ Discipline  │    │    Cost     │                     │
│  │  Breakdown  │    │  Breakdown  │    │  Breakdown  │                     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                     │
│         │                  │                  │                             │
│   "LIVRABLES"        "QUI FAIT"          "BUDGET"                          │
│   (Packages)        (Spécialité)         (Coûts)                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 0.3 Définitions Détaillées

#### FBS - Functional Breakdown Structure
**"Par quoi ça fait / À quoi ça sert"**

```
FBS (Functional)
├── 100 - Utilities
│   ├── 110 - Water Supply
│   ├── 120 - Air Supply
│   └── 130 - Power Distribution
├── 200 - Process
│   ├── 210 - Grinding Circuit
│   │   ├── 211 - Primary Grinding
│   │   └── 212 - Secondary Grinding
│   ├── 220 - Flotation Circuit
│   └── 230 - Thickening
├── 300 - Packaging
└── 400 - Shipping
```

**Usage:**
- Voir tous les équipements du circuit de broyage
- Comprendre les dépendances fonctionnelles
- Analyser l'impact si une fonction tombe en panne

#### LBS - Location Breakdown Structure
**"Où c'est physiquement"**

```
LBS (Location)
├── SITE-001 - Gold Mine Site
│   ├── AREA-100 - Process Plant
│   │   ├── BLDG-110 - Mill Building
│   │   │   ├── ROOM-111 - Control Room
│   │   │   ├── ROOM-112 - MCC Room
│   │   │   └── ROOM-113 - Grinding Hall
│   │   └── BLDG-120 - Flotation Building
│   ├── AREA-200 - Utilities
│   │   ├── EHOUSE-201 - Main E-House
│   │   └── SUBST-202 - Substation
│   └── AREA-300 - Tailings
└── SITE-002 - Camp
```

**Usage:**
- Voir tous les équipements dans une salle
- Calculer la charge thermique d'un E-House
- Planifier les routes de câbles

#### PBS - Product Breakdown Structure
**"Hiérarchie parent-enfant des assets"**

```
PBS (Product)
├── P-210-001 (Pump)
│   ├── MTR-210-001A (Motor)
│   │   ├── PWR-210-001 (Power Cable)
│   │   └── CTL-210-001 (Control Cable)
│   ├── VLV-210-001 (Discharge Valve)
│   └── PT-210-001 (Pressure Transmitter)
│       └── SIG-210-001 (Signal Cable)
├── P-210-002 (Pump)
│   └── ...
```

**Usage:**
- Voir tous les enfants d'un équipement
- Comprendre les dépendances
- Générer automatiquement les composants

#### WBS - Work Breakdown Structure
**"Packages de travail / Livrables"**

```
WBS (Work)
├── PKG-EL-001 - Electrical Installation Area 210
│   ├── DEL-001 - Cable Schedule (CA-P040)
│   ├── DEL-002 - Motor List (EL-M040)
│   └── DEL-003 - Single Line Diagram
├── PKG-IN-001 - Instrumentation Area 210
│   ├── DEL-004 - Instrument Index (IN-P040)
│   ├── DEL-005 - IO List (IO-P040)
│   └── DEL-006 - Loop Diagrams
└── PKG-ME-001 - Mechanical Area 210
    └── ...
```

**Usage:**
- Générer les packages livrables
- Suivre l'avancement par package
- Assigner le travail aux équipes

#### DISC - Discipline Breakdown
**"Par spécialité d'ingénierie"**

```
DISC (Discipline)
├── ELECTRICAL
│   ├── Motors
│   ├── Power Cables
│   ├── MCC
│   └── Transformers
├── INSTRUMENTATION
│   ├── Transmitters
│   ├── Control Valves
│   ├── Signal Cables
│   └── Junction Boxes
├── MECHANICAL
│   ├── Pumps
│   ├── Tanks
│   ├── Agitators
│   └── Piping
├── PROCESS
│   ├── P&ID Items
│   └── Process Data
└── CONTROL
    ├── PLC/DCS
    ├── IO Cards
    └── Networks
```

**Usage:**
- Filtrer par spécialité
- Assigner les reviews par discipline
- Générer les rapports par métier

#### CBS - Cost Breakdown Structure (Future)
**"Par budget / Centre de coûts"**

```
CBS (Cost)
├── CAPEX
│   ├── Equipment
│   ├── Installation
│   └── Engineering
└── OPEX
    ├── Maintenance
    └── Utilities
```

### 0.4 Comment Tout Se Connecte

**Chaque Asset a plusieurs "coordonnées":**

```python
class Asset:
    # Identité
    id: str
    tag: str                    # "LT-210-001"

    # PBS (Hiérarchie)
    parent_id: str | None       # Parent asset
    children: list[Asset]       # Child assets

    # FBS (Fonction)
    system: str                 # "210" (Grinding Circuit)
    function_code: str          # "211" (Primary Grinding)

    # LBS (Location)
    location_id: str            # FK to LBSNode
    area: str                   # "AREA-100"
    building: str               # "BLDG-110"
    room: str                   # "ROOM-112"

    # DISC (Discipline)
    discipline: str             # "INSTRUMENTATION"
    asset_type: str             # "TRANSMITTER"

    # WBS (Package)
    package_id: str | None      # FK to Package
    work_package: str           # "PKG-IN-001"
```

### 0.5 UI - Multi-View Navigator

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📊 Asset Explorer                                         [View: FBS ▼]    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─── View Selector ───┐   ┌─── Active Filters ──────────────────────────┐ │
│  │ ○ FBS (Function)    │   │ Discipline: [ELECTRICAL ▼]                  │ │
│  │ ● LBS (Location)    │   │ Area: [210 - Grinding ▼]                    │ │
│  │ ○ PBS (Product)     │   │ Type: [All Types ▼]                         │ │
│  │ ○ WBS (Package)     │   │ Status: [✓ Active] [✓ Draft] [○ Deleted]   │ │
│  │ ○ DISC (Discipline) │   │                                              │ │
│  └─────────────────────┘   │ [Clear All] [Save Filter] [Load Filter ▼]   │ │
│                             └────────────────────────────────────────────┘ │
│                                                                              │
│  ┌─── Tree View (LBS) ─────────────────┐  ┌─── Asset List ───────────────┐ │
│  │ 📁 SITE-001 - Gold Mine             │  │ Tag          │ Type    │ Loc │ │
│  │   📁 AREA-100 - Process Plant       │  │──────────────┼─────────┼─────│ │
│  │     📁 BLDG-110 - Mill Building     │  │ MTR-210-001A │ MOTOR   │ 112 │ │
│  │       📁 ROOM-111 - Control Room    │  │ MTR-210-002A │ MOTOR   │ 112 │ │
│  │       📁 ROOM-112 - MCC Room ◀──────│──│ MTR-210-003A │ MOTOR   │ 112 │ │
│  │         └─ 47 assets                │  │ VFD-210-001  │ VFD     │ 112 │ │
│  │       📁 ROOM-113 - Grinding Hall   │  │ VFD-210-002  │ VFD     │ 112 │ │
│  │   📁 AREA-200 - Utilities           │  │ ...          │         │     │ │
│  └─────────────────────────────────────┘  └──────────────────────────────┘ │
│                                                                              │
│  Status: 47 assets in ROOM-112 | 12 motors | 8 VFDs | 27 cables            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 0.6 Rules + Breakdown Structures

**Les règles peuvent être scopées par breakdown structure:**

```yaml
# Rule scoped by FBS (Function)
- name: "Create Motor for Pump in Grinding"
  scope:
    fbs: ["210", "211", "212"]  # Grinding circuit only
  conditions:
    - field: type
      operator: "=="
      value: "PUMP"
  actions:
    - CREATE_CHILD: {type: MOTOR}

# Rule scoped by LBS (Location)
- name: "Add Junction Box for E-House instruments"
  scope:
    lbs_type: "EHOUSE"  # Only in E-Houses
  conditions:
    - field: discipline
      operator: "=="
      value: "INSTRUMENTATION"
  actions:
    - CREATE_CHILD: {type: JUNCTION_BOX}

# Rule scoped by Discipline
- name: "Generate IO for all instruments"
  scope:
    discipline: "INSTRUMENTATION"
  conditions:
    - field: io_type
      operator: "IN"
      value: ["AI", "AO", "DI", "DO"]
  actions:
    - CREATE_IO_POINT: {}
```

### 0.7 Logs + Breakdown Structures

**Les logs sont filtrables par toutes les breakdown structures:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📊 DevConsole                                              [Filter ▼]      │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─── Filter by Breakdown ─────────────────────────────────────────────────┐│
│ │ FBS: [All ▼]  LBS: [ROOM-112 ▼]  DISC: [ELECTRICAL ▼]  WBS: [All ▼]   ││
│ └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Showing 23 events in ROOM-112 / ELECTRICAL                                 │
│                                                                              │
│  14:32:05 ✅ [RULE] Created MTR-210-001A in ROOM-112 (ELECTRICAL)          │
│  14:32:05 ✅ [RULE] Created MTR-210-002A in ROOM-112 (ELECTRICAL)          │
│  14:32:06 ✅ [RULE] Created PWR-210-001 (Cable to MTR-210-001A)            │
│  14:32:06 ⚠️ [RULE] Cable PWR-210-042 length 127m exceeds 100m limit       │
│  14:32:07 ✅ [RULE] Created VFD-210-001 for MTR-210-001A                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 0.8 Packages + Breakdown Structures

**Les packages sont générés par croisement de breakdowns:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📦 Package Generator                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Generate package by:                                                        │
│                                                                              │
│  ┌─── Primary Axis ────┐    ┌─── Secondary Filter ───┐                     │
│  │ ● LBS (Location)    │    │ Discipline: [ELECTRICAL ▼]                   │
│  │ ○ FBS (Function)    │    │ Type: [CABLE ▼]                              │
│  │ ○ DISC (Discipline) │    │                                               │
│  └─────────────────────┘    └───────────────────────────────────────────┘  │
│                                                                              │
│  ┌─── Select Scope ────────────────────────────────────────────────────┐   │
│  │ [x] AREA-100 - Process Plant (234 items)                            │   │
│  │   [x] BLDG-110 - Mill Building (156 items)                          │   │
│  │     [x] ROOM-112 - MCC Room (47 items)                              │   │
│  │     [ ] ROOM-113 - Grinding Hall (89 items)                         │   │
│  │   [ ] BLDG-120 - Flotation Building                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  Preview: CA-P040-ROOM112 (47 cables)                                       │
│  Template: [Cable Schedule - CA-P040 ▼]                                     │
│                                                                              │
│  [Preview] [Generate Package]                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 0.9 Database Schema pour Breakdowns

```sql
-- FBS Nodes (Functional Breakdown)
CREATE TABLE fbs_nodes (
    id UUID PRIMARY KEY,
    code VARCHAR(20) NOT NULL,        -- "210"
    name VARCHAR(200) NOT NULL,       -- "Grinding Circuit"
    parent_id UUID REFERENCES fbs_nodes(id),
    project_id UUID REFERENCES projects(id),
    level INTEGER NOT NULL,           -- 1, 2, 3...
    path VARCHAR(500),                -- "100/200/210"

    UNIQUE(code, project_id)
);

-- LBS Nodes (Location Breakdown) - Already exists, enhance
ALTER TABLE lbs_nodes ADD COLUMN code VARCHAR(20);
ALTER TABLE lbs_nodes ADD COLUMN path VARCHAR(500);
ALTER TABLE lbs_nodes ADD COLUMN level INTEGER;

-- Assets - Add FBS reference
ALTER TABLE assets ADD COLUMN fbs_id UUID REFERENCES fbs_nodes(id);
ALTER TABLE assets ADD COLUMN fbs_code VARCHAR(20);

-- Index for fast breakdown queries
CREATE INDEX ix_assets_fbs ON assets(fbs_id, project_id);
CREATE INDEX ix_assets_lbs ON assets(location_id, project_id);
CREATE INDEX ix_assets_discipline ON assets(discipline, project_id);
CREATE INDEX ix_assets_package ON assets(package_id, project_id);

-- Workflow events - Add breakdown context
ALTER TABLE workflow_events ADD COLUMN fbs_code VARCHAR(20);
ALTER TABLE workflow_events ADD COLUMN lbs_code VARCHAR(20);
ALTER TABLE workflow_events ADD COLUMN discipline VARCHAR(50);
ALTER TABLE workflow_events ADD COLUMN package_code VARCHAR(50);
```

### 0.10 Value Proposition pour la Démo

**Scénario Démo:**

> "Regardez, j'ai importé 100 instruments. Maintenant je veux voir
> uniquement ce qui est dans la salle MCC, en filtrant par discipline
> électrique..."
>
> *[Clique sur LBS → ROOM-112, puis DISC → ELECTRICAL]*
>
> "Voilà, 47 items. Et si je veux voir l'historique de ce qui s'est
> passé dans cette salle depuis l'import..."
>
> *[Ouvre DevConsole, applique le même filtre]*
>
> "Je vois que le Rule Engine a créé 12 moteurs et 35 câbles dans
> cette salle, avec un warning sur un câble trop long."
>
> "Maintenant je génère le package Cable Schedule pour cette salle..."
>
> *[Package Generator → LBS: ROOM-112 → Generate]*
>
> "CA-P040-ROOM112.xlsx téléchargé. 35 câbles, formaté selon le
> template standard du client."

---

## 1. SYSTÈME DE LOGS & TRAÇABILITÉ (Feature Centrale)

### 1.1 Architecture des Logs

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LOG ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   ACTION     │ →  │   EVENT      │ →  │   DISPLAY    │          │
│  │   (Backend)  │    │   (Stream)   │    │   (Frontend) │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│         │                   │                   │                   │
│         ▼                   ▼                   ▼                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │ PostgreSQL   │    │  WebSocket   │    │  DevConsole  │          │
│  │ (Persist)    │    │  (Real-time) │    │  (UI)        │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│         │                   │                   │                   │
│         ▼                   ▼                   ▼                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │ Loki/Grafana │    │  Timeline    │    │  Filters     │          │
│  │ (Analytics)  │    │  View        │    │  Search      │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Types de Logs (Hiérarchie)

```python
class LogLevel(Enum):
    TRACE = "TRACE"      # Détails techniques (debug only)
    DEBUG = "DEBUG"      # Info développeur
    INFO = "INFO"        # Actions normales
    WARN = "WARN"        # Attention requise
    ERROR = "ERROR"      # Erreur récupérable
    FATAL = "FATAL"      # Erreur critique

class LogSource(Enum):
    SYSTEM = "SYSTEM"        # Infra (DB, WebSocket)
    IMPORT = "IMPORT"        # CSV import pipeline
    RULE_ENGINE = "RULE"     # Rule execution
    PACKAGE = "PACKAGE"      # Package generation
    USER = "USER"            # User actions
    API = "API"              # API calls
```

### 1.3 Structure d'un Log Entry

```python
@dataclass
class WorkflowEvent:
    # Identité
    id: str                     # UUID
    timestamp: datetime         # ISO 8601

    # Classification
    level: LogLevel
    source: LogSource
    action_type: str            # CREATE, UPDATE, DELETE, EXECUTE, EXPORT

    # Contexte
    project_id: str
    user_id: str
    session_id: str             # Pour grouper les actions d'une session

    # Cible
    entity_type: str            # ASSET, CABLE, RULE, PACKAGE
    entity_id: str | None
    entity_tag: str | None      # Human-readable (ex: "LT-210-001")

    # Détails
    message: str                # Description human-readable
    details: dict               # Données structurées (avant/après, params)

    # Traçabilité
    parent_event_id: str | None # Pour chaîner les events (rule → created assets)
    correlation_id: str         # Groupe d'events liés (1 import = N events)

    # Status
    status: str                 # PENDING, IN_PROGRESS, COMPLETED, FAILED
    duration_ms: int | None     # Temps d'exécution
    error: str | None           # Message d'erreur si FAILED
```

### 1.4 Database Schema

```sql
-- Table principale des événements
CREATE TABLE workflow_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Classification
    level VARCHAR(10) NOT NULL,
    source VARCHAR(20) NOT NULL,
    action_type VARCHAR(20) NOT NULL,

    -- Contexte
    project_id UUID NOT NULL REFERENCES projects(id),
    user_id UUID NOT NULL REFERENCES users(id),
    session_id UUID NOT NULL,

    -- Cible
    entity_type VARCHAR(20),
    entity_id UUID,
    entity_tag VARCHAR(100),

    -- Détails
    message TEXT NOT NULL,
    details JSONB DEFAULT '{}',

    -- Traçabilité
    parent_event_id UUID REFERENCES workflow_events(id),
    correlation_id UUID NOT NULL,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'COMPLETED',
    duration_ms INTEGER,
    error TEXT,

    -- Indexes
    INDEX ix_workflow_events_project (project_id),
    INDEX ix_workflow_events_timestamp (timestamp DESC),
    INDEX ix_workflow_events_correlation (correlation_id),
    INDEX ix_workflow_events_entity (entity_type, entity_id),
    INDEX ix_workflow_events_source (source),
    INDEX ix_workflow_events_session (session_id)
);

-- Vue pour les changements d'assets (audit trail)
CREATE TABLE asset_changes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES workflow_events(id),
    asset_id UUID NOT NULL REFERENCES assets(id),

    field_name VARCHAR(100) NOT NULL,
    old_value JSONB,
    new_value JSONB,

    INDEX ix_asset_changes_asset (asset_id),
    INDEX ix_asset_changes_event (event_id)
);
```

### 1.5 Frontend - DevConsole Enhanced

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📊 DevConsole                                          [_][□][X]   │
├─────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────┐│
│ │ 🔍 Filter: [All Sources ▼] [All Levels ▼] [Search...        ] ││
│ │ 📅 Time:   [Last 1 hour ▼] [▶ Live] [⏸ Pause]                 ││
│ └─────────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌─ 🔄 Import Session [abc123] ─────────────────────── 14:32:05 ───┐│
│ │  ✅ INFO  [IMPORT] Started CSV import: BBA-Instruments.csv      ││
│ │  ✅ INFO  [IMPORT] Parsed 100 rows, 0 errors                    ││
│ │  ├─ 🔄 Rule Execution [def456] ──────────────────── 14:32:06 ──┤││
│ │  │  ▶ INFO  [RULE] Executing: "Create Motor for Pump"          │││
│ │  │  │  ✅ Created: MTR-210-001A (Motor for P-210-001)          │││
│ │  │  │  ✅ Created: MTR-210-001B (Motor for P-210-002)          │││
│ │  │  │  ✅ Created: 47 more assets...                           │││
│ │  │  ▶ INFO  [RULE] Executing: "Generate Power Cables"          │││
│ │  │  │  ✅ Created: PWR-210-001 (Cable for MTR-210-001A)        │││
│ │  │  │  ⚠️ WARN: Cable length exceeds 100m, verify sizing       │││
│ │  │  │  ✅ Created: 94 more cables...                           │││
│ │  │  ✅ INFO  [RULE] Completed: 142 assets, 95 cables created   │││
│ │  └────────────────────────────────────────────────────────────┘││
│ │  ✅ INFO  [IMPORT] Import completed in 3.2s                     ││
│ └────────────────────────────────────────────────────────────────┘│
│                                                                      │
│ 📈 Stats: 247 events | 0 errors | 2 warnings | Latency: 12ms       │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.6 Timeline View (Traçabilité Visuelle)

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📜 Workflow Timeline - Project: Gold Mine Expansion                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  14:30 ──●── CSV Import Started                                     │
│           │   └─ BBA-Instruments.csv (100 rows)                     │
│           │                                                          │
│  14:32 ──●── Rules Executed                                         │
│           │   ├─ Rule: "Create Motor for Pump" (49 assets)          │
│           │   ├─ Rule: "Generate Power Cables" (95 cables)          │
│           │   └─ Rule: "Assign IO Points" (147 IOs)                 │
│           │                                                          │
│  14:35 ──●── Package Generated                                      │
│           │   └─ IN-P040-Area210 (Excel exported)                   │
│           │                                                          │
│  14:40 ──●── Manual Edit                                            │
│           │   └─ User changed MTR-210-001A.power: 15kW → 18.5kW     │
│           │                                                          │
│  14:45 ──●── Re-run Rules (Affected Only)                           │
│               └─ Cable PWR-210-001 resized: 4mm² → 6mm²             │
│                                                                      │
│  [◀ Earlier]                                        [Later ▶]       │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.7 Asset History (Diff View)

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📋 Asset History: MTR-210-001A                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ Version 3 (Current) ─────────────────────────── 14:45 Today        │
│ ┌─────────────────────────────────────────────────────────────────┐│
│ │ Changed by: Rule "Cable Resizing"                                ││
│ │ Trigger: Parent asset power changed                              ││
│ │                                                                   ││
│ │   cable_size:  4mm²  →  6mm²                                     ││
│ │   updated_at:  14:32 →  14:45                                    ││
│ └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
│ Version 2 ───────────────────────────────────── 14:40 Today        │
│ ┌─────────────────────────────────────────────────────────────────┐│
│ │ Changed by: admin@aurumax.com (Manual Edit)                      ││
│ │                                                                   ││
│ │   power:  15kW  →  18.5kW                                        ││
│ │   reason: "Client spec update REV-003"                           ││
│ └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
│ Version 1 (Created) ─────────────────────────── 14:32 Today        │
│ ┌─────────────────────────────────────────────────────────────────┐│
│ │ Created by: Rule "Create Motor for Pump"                         ││
│ │ Source: CSV Import (BBA-Instruments.csv, row 42)                 ││
│ │                                                                   ││
│ │   tag: MTR-210-001A                                              ││
│ │   type: MOTOR                                                     ││
│ │   power: 15kW                                                     ││
│ │   parent: P-210-001 (Pump)                                       ││
│ └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
│ [🔄 Rollback to Version 2] [📋 Compare Versions] [📤 Export Log]   │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.8 VERSIONING & ROLLBACK (Feature Critique)

**Pourquoi c'est important:**
- Erreur d'import? → Rollback les 100 assets en 1 clic
- Rule Engine a fait n'importe quoi? → Revert les changements
- Client veut voir l'évolution? → Comparer v1 vs v3
- Audit compliance? → Historique complet de chaque champ

#### 1.8.1 Niveaux de Versioning

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VERSIONING HIERARCHY                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ LEVEL 1: ASSET VERSION (Snapshot complet)                     │  │
│  │ • Chaque modification = nouvelle version de l'asset           │  │
│  │ • Snapshot JSON complet de l'état                             │  │
│  │ • Rollback = restaure tout l'asset                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                         │                                           │
│                         ▼                                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ LEVEL 2: PROPERTY VERSION (Par champ)                         │  │
│  │ • Historique individuel par propriété                         │  │
│  │ • Ex: power: 15kW → 18.5kW → 22kW (3 versions)               │  │
│  │ • Rollback = restaure une propriété spécifique                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                         │                                           │
│                         ▼                                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ LEVEL 3: BATCH VERSION (Groupe d'opérations)                  │  │
│  │ • Groupe plusieurs assets modifiés ensemble                   │  │
│  │ • Ex: "Import CSV du 2025-11-28" = 100 assets                │  │
│  │ • Rollback = annule toute l'opération batch                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### 1.8.2 Database Schema - Versioning

```sql
-- Asset Versions (Snapshots complets)
CREATE TABLE asset_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES assets(id),
    version_number INTEGER NOT NULL,

    -- Snapshot complet de l'asset
    snapshot JSONB NOT NULL,           -- {"tag": "MTR-210-001A", "power": 15, ...}

    -- Métadonnées
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    change_reason VARCHAR(500),         -- "Manual edit", "Rule execution", "CSV Import"
    change_source VARCHAR(50),          -- USER, RULE, IMPORT, API
    event_id UUID REFERENCES workflow_events(id),
    batch_id UUID,                       -- Pour grouper les changements

    -- Index
    UNIQUE(asset_id, version_number),
    INDEX ix_asset_versions_asset (asset_id, version_number DESC),
    INDEX ix_asset_versions_batch (batch_id)
);

-- Property Changes (Historique par champ)
CREATE TABLE property_changes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES assets(id),
    version_id UUID NOT NULL REFERENCES asset_versions(id),

    -- Le champ modifié
    property_name VARCHAR(100) NOT NULL,  -- "power", "tag", "location_id"
    property_path VARCHAR(500),            -- Pour nested: "specs.electrical.voltage"

    -- Valeurs
    old_value JSONB,                       -- null si création
    new_value JSONB,                       -- null si suppression

    -- Métadonnées
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    changed_by UUID NOT NULL REFERENCES users(id),

    -- Index pour requêtes rapides
    INDEX ix_property_changes_asset (asset_id, property_name),
    INDEX ix_property_changes_version (version_id)
);

-- Batch Operations (Pour rollback groupé)
CREATE TABLE batch_operations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Description
    operation_type VARCHAR(50) NOT NULL,  -- IMPORT, RULE_EXECUTION, BULK_UPDATE
    description TEXT,

    -- Scope
    project_id UUID NOT NULL REFERENCES projects(id),
    affected_assets INTEGER NOT NULL,      -- Nombre d'assets touchés

    -- Timing
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,

    -- Rollback info
    is_rolled_back BOOLEAN DEFAULT FALSE,
    rolled_back_at TIMESTAMPTZ,
    rolled_back_by UUID REFERENCES users(id),

    -- Lien vers l'événement parent
    correlation_id UUID NOT NULL,

    INDEX ix_batch_operations_project (project_id, started_at DESC)
);
```

#### 1.8.3 UI - Version Comparison (Diff View)

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🔍 Compare Versions: MTR-210-001A                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Compare: [Version 1 ▼]  ←→  [Version 3 (Current) ▼]               │
│                                                                      │
│  ┌─────────────────────────┬─────────────────────────┐              │
│  │     VERSION 1           │     VERSION 3           │              │
│  │     (14:32 - Created)   │     (14:45 - Current)   │              │
│  ├─────────────────────────┼─────────────────────────┤              │
│  │ tag: MTR-210-001A       │ tag: MTR-210-001A       │  (unchanged) │
│  │ type: MOTOR             │ type: MOTOR             │  (unchanged) │
│  │─────────────────────────┼─────────────────────────│              │
│  │ power: 15kW             │ power: 18.5kW           │  ← CHANGED   │
│  │─────────────────────────┼─────────────────────────│              │
│  │ cable_size: 4mm²        │ cable_size: 6mm²        │  ← CHANGED   │
│  │─────────────────────────┼─────────────────────────│              │
│  │ (n/a)                   │ efficiency: 94.5%       │  ← ADDED     │
│  │─────────────────────────┼─────────────────────────│              │
│  │ old_field: "value"      │ (deleted)               │  ← REMOVED   │
│  └─────────────────────────┴─────────────────────────┘              │
│                                                                      │
│  Summary: 2 changed | 1 added | 1 removed                           │
│                                                                      │
│  [◀ Rollback to V1] [📋 Copy Diff] [📤 Export Comparison]          │
└─────────────────────────────────────────────────────────────────────┘
```

#### 1.8.4 UI - Property History (Single Field)

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📊 Property History: MTR-210-001A.power                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Timeline of "power" field:                                         │
│                                                                      │
│  ●─────────●─────────●─────────●─────────●                          │
│  │         │         │         │         │                          │
│  15kW     18.5kW    22kW      20kW      22kW                        │
│  v1       v2        v3        v4        v5 (current)                │
│  14:32    14:40     15:10     15:25     15:30                       │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ Version │ Value   │ Changed By        │ Reason                  ││
│  ├─────────┼─────────┼───────────────────┼─────────────────────────┤│
│  │ v5      │ 22kW    │ Rule Engine       │ Re-calculated from spec ││
│  │ v4      │ 20kW    │ admin@aurumax.com │ Client revision REV-004 ││
│  │ v3      │ 22kW    │ Rule Engine       │ Auto-calc from load     ││
│  │ v2      │ 18.5kW  │ admin@aurumax.com │ Client spec REV-003     ││
│  │ v1      │ 15kW    │ CSV Import        │ Initial value           ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  [🔄 Rollback "power" to:] [v1 ▼]  [Execute Rollback]              │
│                                                                      │
│  ⚠️ Warning: Rolling back this property may trigger rules           │
│     that depend on this value.                                       │
└─────────────────────────────────────────────────────────────────────┘
```

#### 1.8.5 UI - Batch Rollback

```
┌─────────────────────────────────────────────────────────────────────┐
│ ⚠️ Batch Rollback                                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Operation to rollback:                                              │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ 📥 CSV Import: BBA-Instruments.csv                              ││
│  │ Date: 2025-11-28 14:32:05                                       ││
│  │ User: admin@aurumax.com                                         ││
│  │                                                                  ││
│  │ Assets affected: 100 instruments                                 ││
│  │ Related changes:                                                 ││
│  │   - 49 motors created (Rule: Create Motor for Pump)             ││
│  │   - 95 cables created (Rule: Generate Power Cables)             ││
│  │   - 147 IO points created (Rule: Assign IO Points)              ││
│  │                                                                  ││
│  │ Total: 391 assets will be affected                              ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  Rollback options:                                                   │
│  ○ Rollback import only (100 instruments)                           │
│  ○ Rollback import + triggered rules (391 assets)                   │
│  ● Rollback everything to state before import                       │
│                                                                      │
│  ⚠️ This action cannot be undone. Consider exporting a backup first.│
│                                                                      │
│  [Cancel] [📤 Export Backup First] [🔄 Execute Rollback]           │
└─────────────────────────────────────────────────────────────────────┘
```

#### 1.8.6 Rollback Service (Backend)

```python
class RollbackService:
    """Service pour gérer les rollbacks à différents niveaux"""

    async def rollback_asset_to_version(
        self,
        asset_id: str,
        target_version: int,
        reason: str
    ) -> RollbackResult:
        """Rollback un asset complet à une version antérieure"""

        # 1. Récupérer le snapshot de la version cible
        target_snapshot = await self.get_version_snapshot(asset_id, target_version)

        # 2. Créer une nouvelle version (v+1) avec l'état restauré
        new_version = await self.create_version(
            asset_id=asset_id,
            snapshot=target_snapshot,
            change_reason=f"Rollback to v{target_version}: {reason}",
            change_source="ROLLBACK"
        )

        # 3. Mettre à jour l'asset actuel
        await self.update_asset_from_snapshot(asset_id, target_snapshot)

        # 4. Logger l'événement
        await self.workflow_logger.log(
            level="INFO",
            source="ROLLBACK",
            action_type="ROLLBACK_ASSET",
            entity_type="ASSET",
            entity_id=asset_id,
            message=f"Asset rolled back to version {target_version}",
            details={
                "from_version": new_version - 1,
                "to_version": target_version,
                "new_version": new_version,
                "reason": reason
            }
        )

        return RollbackResult(
            success=True,
            asset_id=asset_id,
            restored_version=target_version,
            new_version=new_version
        )

    async def rollback_property(
        self,
        asset_id: str,
        property_name: str,
        target_version: int,
        reason: str
    ) -> RollbackResult:
        """Rollback une propriété spécifique à une version antérieure"""

        # 1. Récupérer la valeur de la propriété à cette version
        old_value = await self.get_property_at_version(
            asset_id, property_name, target_version
        )

        # 2. Mettre à jour uniquement cette propriété
        current_asset = await self.get_asset(asset_id)
        setattr(current_asset, property_name, old_value)

        # 3. Créer une nouvelle version (snapshot complet)
        await self.create_version_from_asset(
            asset=current_asset,
            change_reason=f"Property '{property_name}' rolled back to v{target_version}",
            change_source="ROLLBACK"
        )

        # 4. Logger le changement de propriété
        await self.log_property_change(
            asset_id=asset_id,
            property_name=property_name,
            old_value=getattr(current_asset, property_name),
            new_value=old_value,
            reason=reason
        )

        return RollbackResult(success=True, property_restored=property_name)

    async def rollback_batch(
        self,
        batch_id: str,
        rollback_triggered_rules: bool = True,
        reason: str = ""
    ) -> BatchRollbackResult:
        """Rollback une opération batch complète (import, rule execution)"""

        # 1. Récupérer tous les assets affectés
        affected_assets = await self.get_batch_affected_assets(batch_id)

        # 2. Si on rollback aussi les règles déclenchées
        if rollback_triggered_rules:
            triggered_assets = await self.get_triggered_assets(batch_id)
            affected_assets.extend(triggered_assets)

        # 3. Rollback chaque asset à sa version pré-batch
        results = []
        for asset_info in affected_assets:
            result = await self.rollback_asset_to_version(
                asset_id=asset_info.asset_id,
                target_version=asset_info.version_before_batch,
                reason=f"Batch rollback: {reason}"
            )
            results.append(result)

        # 4. Marquer le batch comme rolled back
        await self.mark_batch_rolled_back(batch_id)

        # 5. Logger l'événement batch
        await self.workflow_logger.log(
            level="WARN",
            source="ROLLBACK",
            action_type="ROLLBACK_BATCH",
            message=f"Batch operation rolled back: {len(results)} assets restored",
            details={
                "batch_id": batch_id,
                "assets_restored": len(results),
                "include_triggered_rules": rollback_triggered_rules
            }
        )

        return BatchRollbackResult(
            success=True,
            batch_id=batch_id,
            assets_restored=len(results),
            results=results
        )
```

#### 1.8.7 Value Proposition pour la Démo

**Scénario Démo - Rollback:**

> "Oups, j'ai importé le mauvais fichier CSV. Pas de panique..."
>
> *[Ouvre Batch Operations → Sélectionne l'import]*
>
> "Je vois que 100 instruments ont été créés, plus 144 assets par les règles.
> Je rollback le tout..."
>
> *[Clique Rollback Everything → Confirme]*
>
> "Voilà, tout est revenu à l'état précédent. Je peux même voir dans
> le Timeline que le rollback a été fait, avec la raison."
>
> "Maintenant, imaginons que seulement UNE propriété était erronée..."
>
> *[Ouvre Asset → Property History → power]*
>
> "Je vois l'historique de cette propriété: 15kW → 18.5kW → 22kW.
> Je rollback juste 'power' à v1..."
>
> *[Rollback power to v1]*
>
> "Seule cette propriété est revenue à 15kW. Le reste de l'asset
> est intact."

---

## 2. RULE ENGINE (Avec Logging Intégré)

### 2.1 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      RULE ENGINE ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐                                                   │
│  │  TRIGGER     │  Manual | On Import | On Change | Scheduled       │
│  └──────┬───────┘                                                   │
│         │                                                            │
│         ▼                                                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    RULE SELECTOR                              │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │  │
│  │  │ Priority 1 │  │ Priority 2 │  │ Priority 3 │  ...        │  │
│  │  │ (Critical) │  │ (High)     │  │ (Normal)   │             │  │
│  │  └────────────┘  └────────────┘  └────────────┘             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│         │                                                            │
│         ▼                                                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    CONDITION EVALUATOR                        │  │
│  │                                                                │  │
│  │  IF asset.type == "PUMP"                                      │  │
│  │  AND asset.power > 5kW                                        │  │
│  │  AND NOT EXISTS(child WHERE type == "MOTOR")                  │  │
│  │                                                                │  │
│  │  → Evaluate against each asset in scope                       │  │
│  │  → Log: "Evaluating rule X on asset Y: MATCH/NO_MATCH"       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│         │                                                            │
│         ▼                                                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    ACTION EXECUTOR                            │  │
│  │                                                                │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │  │
│  │  │CREATE_CHILD │  │CREATE_CABLE │  │CREATE_PKG   │          │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │  │
│  │  │ SET_FIELD   │  │ LINK_ASSET  │  │ NOTIFY      │          │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │  │
│  │                                                                │  │
│  │  → Each action logged with before/after state                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│         │                                                            │
│         ▼                                                            │
│  ┌──────────────┐                                                   │
│  │  RESULT      │  Created: 47 | Updated: 12 | Errors: 0          │
│  │  SUMMARY     │  Duration: 2.3s | Events logged: 156             │
│  └──────────────┘                                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Rule Definition Schema

```python
@dataclass
class RuleDefinition:
    # Identité
    id: str
    name: str                    # "Create Motor for Pump"
    description: str

    # Classification
    priority: int               # 1=Critical, 2=High, 3=Normal, 4=Low
    category: str               # CREATION, LINKING, VALIDATION, CALCULATION
    discipline: str             # ELECTRICAL, INSTRUMENTATION, MECHANICAL

    # Trigger
    trigger_type: str           # MANUAL, ON_IMPORT, ON_CHANGE, SCHEDULED
    trigger_conditions: dict    # When to auto-trigger

    # Scope
    source_entity_type: str     # ASSET, CABLE, LOCATION
    source_filter: dict         # {"type": "PUMP", "power_gt": 5}

    # Conditions (ALL must be true)
    conditions: list[RuleCondition]

    # Actions (executed in order)
    actions: list[RuleAction]

    # Metadata
    is_active: bool
    created_by: str
    version: int

@dataclass
class RuleCondition:
    field: str                  # "type", "power", "area"
    operator: str               # ==, !=, >, <, IN, NOT_IN, EXISTS, NOT_EXISTS
    value: Any                  # "PUMP", 5, ["A", "B"]

@dataclass
class RuleAction:
    action_type: str            # CREATE_CHILD, CREATE_CABLE, SET_FIELD, etc.
    parameters: dict            # Action-specific params

    # Pour CREATE_CHILD
    # {
    #   "child_type": "MOTOR",
    #   "tag_template": "{parent.tag}A",
    #   "copy_fields": ["area", "system"],
    #   "set_fields": {"power": "{parent.power * 1.1}"}
    # }
```

### 2.3 Actions MVP (3 prioritaires)

#### ACTION 1: CREATE_CHILD
```python
class CreateChildAction:
    """Crée un asset enfant lié au parent"""

    parameters = {
        "child_type": "MOTOR",           # Type de l'enfant
        "tag_template": "{parent.tag}A", # Template pour le tag
        "copy_fields": [                 # Champs copiés du parent
            "area", "system", "location_id"
        ],
        "set_fields": {                  # Champs calculés
            "power": "{parent.power * 1.1}",
            "description": "Motor for {parent.description}"
        },
        "relationship_type": "DRIVES"    # Type de relation
    }

    def execute(self, parent_asset, rule, context):
        # 1. Log start
        log_event(RULE, "CREATE_CHILD", f"Creating child for {parent_asset.tag}")

        # 2. Generate tag
        child_tag = render_template(self.tag_template, parent=parent_asset)

        # 3. Check if already exists
        if asset_exists(child_tag, context.project_id):
            log_event(WARN, f"Child {child_tag} already exists, skipping")
            return None

        # 4. Create child
        child = Asset(
            tag=child_tag,
            type=self.child_type,
            project_id=context.project_id,
            parent_id=parent_asset.id,
            # Copy fields
            **{f: getattr(parent_asset, f) for f in self.copy_fields},
            # Set fields
            **self.evaluate_set_fields(parent_asset)
        )

        # 5. Log creation with full details
        log_event(INFO, "ASSET_CREATED",
            entity_id=child.id,
            entity_tag=child.tag,
            details={
                "parent_tag": parent_asset.tag,
                "rule_name": rule.name,
                "fields": child.to_dict()
            }
        )

        return child
```

#### ACTION 2: CREATE_CABLE
```python
class CreateCableAction:
    """Crée un câble entre deux assets"""

    parameters = {
        "cable_type": "POWER",           # POWER, SIGNAL, NETWORK
        "from_field": "parent",          # Source (parent ou field)
        "to_field": "location_id",       # Destination
        "tag_template": "PWR-{from.area}-{seq:03d}",
        "auto_size": True,               # Calcul automatique de la section
        "sizing_rules": {
            "method": "IEC_60364",
            "voltage": 400,
            "power_factor": 0.85,
            "ambient_temp": 40
        }
    }

    def execute(self, source_asset, rule, context):
        # 1. Log start
        log_event(RULE, "CREATE_CABLE", f"Creating cable for {source_asset.tag}")

        # 2. Determine endpoints
        from_point = self.resolve_endpoint(source_asset, self.from_field)
        to_point = self.resolve_endpoint(source_asset, self.to_field)

        # 3. Calculate cable size if auto_size
        if self.auto_size:
            cable_size = self.calculate_size(source_asset, self.sizing_rules)
            log_event(DEBUG, f"Calculated cable size: {cable_size}mm²")

        # 4. Create cable
        cable = Cable(
            tag=self.generate_tag(source_asset, context),
            cable_type=self.cable_type,
            from_asset_id=from_point.id,
            to_asset_id=to_point.id,
            size_mm2=cable_size,
            project_id=context.project_id
        )

        # 5. Log with details
        log_event(INFO, "CABLE_CREATED",
            entity_id=cable.id,
            entity_tag=cable.tag,
            details={
                "from": from_point.tag,
                "to": to_point.tag,
                "size": f"{cable_size}mm²",
                "rule_name": rule.name
            }
        )

        # 6. Warn if cable exceeds limits
        if cable.length > 100:
            log_event(WARN, f"Cable {cable.tag} length {cable.length}m exceeds 100m")

        return cable
```

#### ACTION 3: CREATE_PACKAGE
```python
class CreatePackageAction:
    """Groupe des assets dans un package livrable"""

    parameters = {
        "package_type": "INSTRUMENT_INDEX",  # Type de package
        "code_template": "IN-P040-{area}",   # Code du package
        "include_filter": {                   # Assets à inclure
            "type_in": ["INSTRUMENT", "TRANSMITTER", "VALVE"],
            "area": "{trigger.area}"
        },
        "template_file": "IN-P040.xlsx"      # Template Excel
    }

    def execute(self, trigger_asset, rule, context):
        # 1. Log start
        log_event(RULE, "CREATE_PACKAGE", f"Creating package for area {trigger_asset.area}")

        # 2. Find matching assets
        assets = self.find_assets(self.include_filter, context)
        log_event(DEBUG, f"Found {len(assets)} assets for package")

        # 3. Create package
        package = Package(
            code=self.generate_code(trigger_asset),
            package_type=self.package_type,
            project_id=context.project_id,
            asset_count=len(assets)
        )

        # 4. Link assets to package
        for asset in assets:
            asset.package_id = package.id
            log_event(DEBUG, f"Added {asset.tag} to package {package.code}")

        # 5. Log completion
        log_event(INFO, "PACKAGE_CREATED",
            entity_id=package.id,
            entity_tag=package.code,
            details={
                "asset_count": len(assets),
                "assets": [a.tag for a in assets[:10]],  # First 10
                "template": self.template_file
            }
        )

        return package
```

### 2.4 Rule Examples (MVP)

```yaml
# Rule 1: Create Motor for Pump
- id: "rule-001"
  name: "Create Motor for Pump"
  description: "Automatically creates a motor asset for each pump > 5kW"
  priority: 1
  category: CREATION
  discipline: ELECTRICAL

  trigger_type: ON_IMPORT

  source_entity_type: ASSET
  source_filter:
    type: PUMP

  conditions:
    - field: power
      operator: ">"
      value: 5
    - field: children
      operator: NOT_EXISTS
      value: {type: MOTOR}

  actions:
    - action_type: CREATE_CHILD
      parameters:
        child_type: MOTOR
        tag_template: "MTR-{parent.area}-{parent.seq:03d}A"
        copy_fields: [area, system, location_id]
        set_fields:
          power: "{parent.power * 1.15}"
          voltage: 400

# Rule 2: Generate Power Cable
- id: "rule-002"
  name: "Generate Power Cable for Motor"
  description: "Creates power cable from MCC to motor"
  priority: 2
  category: CREATION
  discipline: ELECTRICAL

  trigger_type: ON_CHANGE
  trigger_conditions:
    entity_type: ASSET
    field_changed: [power, location_id]

  source_entity_type: ASSET
  source_filter:
    type: MOTOR

  conditions:
    - field: power
      operator: ">"
      value: 0
    - field: cables
      operator: NOT_EXISTS
      value: {type: POWER}

  actions:
    - action_type: CREATE_CABLE
      parameters:
        cable_type: POWER
        from_field: location_id  # MCC location
        to_field: self           # Motor
        tag_template: "PWR-{from.area}-{seq:03d}"
        auto_size: true
```

---

## 3. CSV IMPORT (Avec Logging Complet)

### 3.1 Import Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                      CSV IMPORT PIPELINE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  STAGE 1: UPLOAD                                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ User drops CSV file                                          │   │
│  │ → Log: "File received: BBA.csv (245KB, 100 rows)"           │   │
│  │ → Validate: UTF-8, <10MB, CSV format                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│         │                                                            │
│         ▼                                                            │
│  STAGE 2: PARSE & PREVIEW                                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Parse CSV headers + first 10 rows                            │   │
│  │ → Log: "Parsed 15 columns, detected delimiter: ;"           │   │
│  │ → Show preview to user                                       │   │
│  │ → User maps columns to fields                                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│         │                                                            │
│         ▼                                                            │
│  STAGE 3: VALIDATE                                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ For each row:                                                │   │
│  │ → Check required fields (tag, type)                         │   │
│  │ → Check data types (number, date, enum)                     │   │
│  │ → Check uniqueness (tag not duplicate)                      │   │
│  │ → Log: "Row 42 validation failed: missing 'tag'"           │   │
│  │                                                              │   │
│  │ Summary: 95 valid, 5 errors                                 │   │
│  │ → User can fix or skip errors                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│         │                                                            │
│         ▼                                                            │
│  STAGE 4: IMPORT                                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ For each valid row:                                          │   │
│  │ → Create Asset in staging                                   │   │
│  │ → Log: "Created asset LT-210-001 from row 1"               │   │
│  │                                                              │   │
│  │ On complete:                                                 │   │
│  │ → Move from staging to production                           │   │
│  │ → Log: "Import completed: 95 assets created in 2.1s"       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│         │                                                            │
│         ▼                                                            │
│  STAGE 5: POST-IMPORT (Optional)                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ → Trigger rules if configured                               │   │
│  │ → Log: "Triggering 3 rules on imported assets"             │   │
│  │ → Generate initial packages                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Column Mapping UI

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📁 Import CSV - Step 2: Map Columns                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  CSV Column              →    SYNAPSE Field         Status          │
│  ─────────────────────────────────────────────────────────────────  │
│  [TAG_NUMBER      ▼]    →    [tag            ▼]    ✅ Required     │
│  [DESCRIPTION     ▼]    →    [description    ▼]    ✅ Mapped       │
│  [INSTRUMENT_TYPE ▼]    →    [type           ▼]    ✅ Required     │
│  [AREA            ▼]    →    [area           ▼]    ✅ Mapped       │
│  [RANGE_MIN       ▼]    →    [process.min    ▼]    ✅ Mapped       │
│  [RANGE_MAX       ▼]    →    [process.max    ▼]    ✅ Mapped       │
│  [UNIT            ▼]    →    [-- Skip --     ▼]    ⏭️ Skipped     │
│  [MANUFACTURER    ▼]    →    [-- Auto-map -- ▼]    🔄 Detecting   │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 💡 Auto-detected mappings:                                   │   │
│  │    • TAG_NUMBER → tag (100% match)                          │   │
│  │    • DESCRIPTION → description (95% match)                  │   │
│  │    • INSTRUMENT_TYPE → type (90% match, needs transform)    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 🔧 Transform: INSTRUMENT_TYPE → type                        │   │
│  │    [ ] Direct mapping (no transform)                        │   │
│  │    [x] Value mapping:                                       │   │
│  │        "LT" → "LEVEL_TRANSMITTER"                          │   │
│  │        "PT" → "PRESSURE_TRANSMITTER"                       │   │
│  │        "FT" → "FLOW_TRANSMITTER"                           │   │
│  │    [ ] Custom formula: {value.upper().replace("-", "_")}   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  [◀ Back]                              [Preview] [Import ▶]        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. PACKAGE EXPORT (Avec Logging)

### 4.1 Package Generation Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PACKAGE EXPORT FLOW                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐                                                   │
│  │ SELECT       │  User selects package or area                     │
│  │ SCOPE        │  → Log: "Export scope: Area 210, 47 assets"      │
│  └──────┬───────┘                                                   │
│         │                                                            │
│         ▼                                                            │
│  ┌──────────────┐                                                   │
│  │ SELECT       │  IN-P040, CA-P040, EL-M040, IO-P040              │
│  │ TEMPLATE     │  → Log: "Template selected: IN-P040.xlsx"        │
│  └──────┬───────┘                                                   │
│         │                                                            │
│         ▼                                                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ GENERATE                                                      │  │
│  │                                                                │  │
│  │ 1. Load template (Jinja2 + openpyxl)                         │  │
│  │ 2. Query assets matching scope                                │  │
│  │ 3. Apply sorting (by tag, by area, by type)                  │  │
│  │ 4. Render template with data                                  │  │
│  │ 5. Apply formatting (borders, colors, column widths)         │  │
│  │                                                                │  │
│  │ → Log progress: "Rendering row 1/47... 47/47"                │  │
│  │ → Log: "Generated IN-P040-Area210.xlsx (125KB)"              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│         │                                                            │
│         ▼                                                            │
│  ┌──────────────┐                                                   │
│  │ DOWNLOAD     │  Direct download or email                         │
│  │ / EMAIL      │  → Log: "Package downloaded by admin@..."        │
│  └──────────────┘                                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Template Structure (IN-P040)

```
┌─────────────────────────────────────────────────────────────────────┐
│ IN-P040 - Instrument Index                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Project: {{ project.name }}                                        │
│  Area: {{ area.name }}                                              │
│  Generated: {{ now | date("YYYY-MM-DD HH:mm") }}                   │
│  Revision: {{ package.revision }}                                   │
│                                                                      │
│  ┌───────┬─────────────┬──────────┬────────┬────────┬───────────┐ │
│  │ Tag   │ Description │ Type     │ Range  │ Unit   │ Location  │ │
│  ├───────┼─────────────┼──────────┼────────┼────────┼───────────┤ │
│  {% for asset in assets %}                                         │
│  │{{ asset.tag }}│{{ asset.description }}│{{ asset.type }}│...   │ │
│  {% endfor %}                                                       │
│  └───────┴─────────────┴──────────┴────────┴────────┴───────────┘ │
│                                                                      │
│  Total: {{ assets | length }} instruments                           │
│                                                                      │
│  Signature: ________________    Date: ________________              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. DÉCISIONS ARCHITECTURE

### 5.1 Questions à Résoudre

| # | Question | Options | Décision |
|---|----------|---------|----------|
| 1 | Stockage des logs | PostgreSQL vs TimescaleDB vs Loki seul | **PostgreSQL** (workflow_events) + Loki (observability) |
| 2 | Real-time updates | WebSocket vs SSE vs Polling | **WebSocket** (déjà implémenté) |
| 3 | Rule storage | YAML files vs Database vs Both | **Database** (rules table) avec export YAML |
| 4 | Template engine | Jinja2 vs Mako vs Custom | **Jinja2** (standard Python) |
| 5 | Excel generation | openpyxl vs xlsxwriter vs pandas | **openpyxl** (template support) |
| 6 | Event sourcing | Full vs Partial | **Partial** (changes only, not full snapshots) |

### 5.2 Database Tables Nouvelles

```sql
-- Tables à créer pour MVP

-- 1. Workflow Events (logs)
workflow_events (voir section 1.4)

-- 2. Asset Changes (audit trail)
asset_changes (voir section 1.4)

-- 3. Rules
CREATE TABLE rules (
    id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 3,
    category VARCHAR(50),
    discipline VARCHAR(50),

    trigger_type VARCHAR(20) NOT NULL,
    trigger_conditions JSONB,

    source_entity_type VARCHAR(50) NOT NULL,
    source_filter JSONB,

    conditions JSONB NOT NULL,
    actions JSONB NOT NULL,

    is_active BOOLEAN DEFAULT true,
    project_id UUID REFERENCES projects(id),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    version INTEGER DEFAULT 1
);

-- 4. Rule Executions (history)
CREATE TABLE rule_executions (
    id UUID PRIMARY KEY,
    rule_id UUID REFERENCES rules(id),
    correlation_id UUID NOT NULL,

    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,

    status VARCHAR(20) NOT NULL,  -- PENDING, RUNNING, COMPLETED, FAILED

    assets_processed INTEGER DEFAULT 0,
    assets_created INTEGER DEFAULT 0,
    assets_updated INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,

    error_details JSONB,

    triggered_by UUID REFERENCES users(id),
    project_id UUID REFERENCES projects(id)
);

-- 5. Packages
CREATE TABLE packages (
    id UUID PRIMARY KEY,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(200),
    package_type VARCHAR(50) NOT NULL,

    project_id UUID REFERENCES projects(id),
    area VARCHAR(50),

    asset_count INTEGER DEFAULT 0,

    template_id VARCHAR(50),
    last_generated_at TIMESTAMPTZ,
    last_generated_by UUID REFERENCES users(id),

    revision INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'DRAFT',

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(code, project_id)
);
```

---

## 5. UI ARCHITECTURE (Split View + VSCode Style)

### 5.1 Concept: "Mission Control for Engineering"

**Philosophie:**
- Sentiment de **contrôle total** sur les données d'ingénierie
- Visibilité **temps réel** de ce qui se passe
- Navigation **multi-vue** fluide
- Style professionnel **VSCode dark theme**

**Combinaison choisie: Option C (Split View) + Option A (VSCode Activity Bar)**

### 5.2 Layout Principal

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ ┌─ Header ─────────────────────────────────────────────────────────────────────┐ │
│ │ 🔷 SYNAPSE    Gold Mine Expansion ▼               admin@aurumax.com  🔔  ⚙️  │ │
│ └──────────────────────────────────────────────────────────────────────────────┘ │
├──┬───────────────────────────────────────────────────────────────────────────────┤
│  │  ┌─ Sidebar (280px) ────────────────────┐  ┌─ Main Content ───────────────┐  │
│ A│  │                                       │  │                               │  │
│ c│  │  ┌─ View Toggle ───────────────────┐ │  │  ┌─ Tabs ───────────────────┐ │  │
│ t│  │  │ View: [LBS ▼]  │ DISC: [ALL ▼] │ │  │  │ Assets │ Detail │ History │ │  │
│ i│  │  └─────────────────────────────────┘ │  │  └─────────────────────────────┘ │  │
│ v│  │                                       │  │                               │  │
│ i│  │  ┌─ Tree Navigator ────────────────┐ │  │  ┌─ Content Area ───────────┐ │  │
│ t│  │  │ 📁 SITE-001                     │ │  │  │                           │ │  │
│ y│  │  │   📁 AREA-100 (234)             │ │  │  │   [ Table / Detail /      │ │  │
│  │  │  │     📁 BLDG-110                 │ │  │  │     Timeline / Form ]     │ │  │
│ B│  │  │       📁 ROOM-112 (47) ◀        │ │  │  │                           │ │  │
│ a│  │  │       📁 ROOM-113 (89)          │ │  │  │                           │ │  │
│ r│  │  │     📁 BLDG-120                 │ │  │  │                           │ │  │
│  │  │  │   📁 AREA-200                   │ │  │  │                           │ │  │
│  │  │  └─────────────────────────────────┘ │  │  │                           │ │  │
│ 48│  │                                       │  │  │                           │ │  │
│ px│  │  ┌─ Quick Filters ────────────────┐ │  │  │                           │ │  │
│  │  │  │ Type: [MOTOR ▼]                 │ │  │  │                           │ │  │
│  │  │  │ Status: [● Active] [○ Draft]    │ │  │  │                           │ │  │
│  │  │  │ 🔍 Search: [_______________]    │ │  │  │                           │ │  │
│  │  │  └─────────────────────────────────┘ │  │  └───────────────────────────┘ │  │
│  │  └───────────────────────────────────────┘  └───────────────────────────────┘  │
├──┴───────────────────────────────────────────────────────────────────────────────┤
│ ┌─ DevConsole (Collapsible, 200px default) ────────────────────────── [▲▼] ────┐ │
│ │ 14:32:05 ✅ [RULE] Created MTR-210-001A in ROOM-112 (ELECTRICAL)             │ │
│ │ 14:32:06 ⚠️ [RULE] Cable PWR-210-042 length exceeds 100m                     │ │
│ │ 14:32:07 ✅ [IMPORT] Completed: 100 instruments imported                      │ │
│ └──────────────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────┤
│ ┌─ Status Bar ─────────────────────────────────────────────────────────────────┐ │
│ │ 📂 Gold Mine │ 547 assets │ 95 cables │ ROOM-112 │ v0.2.2 │ ● Connected      │ │
│ └──────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Activity Bar (Left - 48px)

```
┌────┐
│ 📊 │  Dashboard (Home)
├────┤
│ 📁 │  Explorer (Assets) ← DEFAULT
├────┤
│ ⚙️  │  Rules Engine
├────┤
│ 📥 │  Import CSV
├────┤
│ 📦 │  Export Packages
├────┤
│ 📜 │  Timeline / History
├────┤
│ 🔧 │  Settings
└────┘

Couleurs:
- Background: #333333
- Icon inactive: #858585
- Icon active: #FFFFFF
- Active indicator: #007ACC (barre gauche 2px)
```

### 5.4 Écran: Explorer (Assets) - Mode Principal

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 🔷 SYNAPSE    Gold Mine Expansion ▼                    admin@aurumax.com  🔔  ⚙️ │
├──┬───────────────────────────────────────────────────────────────────────────────┤
│📊│ ┌─ Navigator ─────────────────────────┐ ┌─ Asset Table ─────────────────────┐ │
│📁│ │ View: [LBS ▼]   DISC: [ELEC ▼]      │ │                                    │ │
│◀─│ │                                      │ │ ┌────────────────────────────────┐ │ │
│⚙️│ │ 📁 SITE-001 - Gold Mine             │ │ │ □ │ Tag         │ Type   │ kW   │ │ │
│📥│ │   📁 AREA-100 - Process Plant       │ │ ├────────────────────────────────┤ │ │
│📦│ │     📁 BLDG-110 - Mill Building     │ │ │ ☑ │ MTR-210-001A│ MOTOR  │ 18.5 │ │ │
│📜│ │       📁 ROOM-111 (23)              │ │ │ □ │ MTR-210-002A│ MOTOR  │ 15   │ │ │
│🔧│ │       📁 ROOM-112 (47) ◀────────────│─│ │ □ │ MTR-210-003A│ MOTOR  │ 22   │ │ │
│  │ │         └─ 12 motors, 35 cables     │ │ │ □ │ VFD-210-001 │ VFD    │ 18.5 │ │ │
│  │ │       📁 ROOM-113 (89)              │ │ │ □ │ PWR-210-001 │ CABLE  │ -    │ │ │
│  │ │     📁 BLDG-120 - Flotation         │ │ │ ... (47 items)                   │ │ │
│  │ │   📁 AREA-200 - Utilities           │ │ └────────────────────────────────┘ │ │
│  │ │                                      │ │                                    │ │
│  │ │ ─────────────────────────────────── │ │ Actions: [+ New] [Edit] [Delete]   │ │
│  │ │ Type: [MOTOR ▼] [CABLE ▼] [VFD ▼]   │ │ Bulk: [Run Rules ▼] [Export ▼]    │ │
│  │ │ Status: [● Active]                   │ │                                    │ │
│  │ │ 🔍 [______________________]          │ │ Showing 47 of 547 │ Page 1 of 1   │ │
│  │ └──────────────────────────────────────┘ └────────────────────────────────────┘ │
├──┴───────────────────────────────────────────────────────────────────────────────┤
│ DevConsole ──────────────────────────────────────────────────────────── [▲▼] ──  │
│ 14:32:06 ⚠️ [RULE] Cable PWR-210-042 length 127m exceeds 100m limit              │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 📂 Gold Mine │ 547 assets │ ROOM-112 selected │ v0.2.2 │ ● Online                │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 5.5 Écran: Asset Detail (Click on asset)

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 🔷 SYNAPSE    Gold Mine Expansion ▼                    admin@aurumax.com  🔔  ⚙️ │
├──┬───────────────────────────────────────────────────────────────────────────────┤
│📊│ ┌─ Navigator ─────────────────────────┐ ┌─ Asset Detail ────────────────────┐ │
│📁│ │ (same as above)                     │ │                                    │ │
│◀─│ │                                      │ │ MTR-210-001A                       │ │
│⚙️│ │ 📁 ROOM-112 (47)                    │ │ Motor for Pump P-210-001           │ │
│📥│ │   MTR-210-001A ◀                    │ │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │ │
│📦│ │   MTR-210-002A                      │ │                                    │ │
│📜│ │   MTR-210-003A                      │ │ ┌─ Properties ─────────────────┐   │ │
│🔧│ │   VFD-210-001                       │ │ │ Tag:       MTR-210-001A      │   │ │
│  │ │   ...                                │ │ │ Type:      MOTOR             │   │ │
│  │ │                                      │ │ │ Power:     18.5 kW [📜 v3]   │   │ │
│  │ │                                      │ │ │ Voltage:   480V              │   │ │
│  │ │                                      │ │ │ FLA:       28A               │   │ │
│  │ │                                      │ │ │ Efficiency: 94.5%            │   │ │
│  │ │                                      │ │ │ ─────────────────────────── │   │ │
│  │ │                                      │ │ │ Location:  ROOM-112          │   │ │
│  │ │                                      │ │ │ System:    210 (Grinding)    │   │ │
│  │ │                                      │ │ │ Parent:    P-210-001 (Pump)  │   │ │
│  │ │                                      │ │ └─────────────────────────────┘   │ │
│  │ │                                      │ │                                    │ │
│  │ │                                      │ │ ┌─ Children (2) ──────────────┐   │ │
│  │ │                                      │ │ │ 🔌 PWR-210-001 (Power Cable) │   │ │
│  │ │                                      │ │ │ 🔌 CTL-210-001 (Control)     │   │ │
│  │ │                                      │ │ └─────────────────────────────┘   │ │
│  │ │                                      │ │                                    │ │
│  │ │                                      │ │ ┌─ Version Info ──────────────┐   │ │
│  │ │                                      │ │ │ Version: 3 (Current)         │   │ │
│  │ │                                      │ │ │ Created: 14:32 (CSV Import)  │   │ │
│  │ │                                      │ │ │ Modified: 14:45 (Rule)       │   │ │
│  │ │                                      │ │ │ [📜 History] [🔄 Rollback]   │   │ │
│  │ │                                      │ │ └─────────────────────────────┘   │ │
│  │ └──────────────────────────────────────┘ └────────────────────────────────────┘ │
├──┴───────────────────────────────────────────────────────────────────────────────┤
│ DevConsole (collapsed) ─────────────────────────────────────────────── [▼] ────  │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 📂 Gold Mine │ MTR-210-001A │ v3 │ Modified 14:45 │ v0.2.2 │ ● Online            │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 5.6 Écran: Rules Engine

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 🔷 SYNAPSE    Gold Mine Expansion ▼                    admin@aurumax.com  🔔  ⚙️ │
├──┬───────────────────────────────────────────────────────────────────────────────┤
│📊│ ┌─ Rules List ─────────────────────────┐ ┌─ Rule Editor ────────────────────┐ │
│📁│ │                                       │ │                                   │ │
│⚙️│ │ Active Rules (8)                     │ │ Create Motor for Pump             │ │
│◀─│ │ ┌───────────────────────────────────┐│ │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │ │
│📥│ │ │ ⚡ Create Motor for Pump      [▶] ││ │                                   │ │
│📦│ │ │    Trigger: ON_IMPORT             ││ │ ┌─ Scope ───────────────────────┐ │ │
│📜│ │ │    Last run: 14:32 (49 created)   ││ │ │ FBS: [210, 211, 212]          │ │ │
│🔧│ │ ├───────────────────────────────────┤│ │ │ LBS: [All]                    │ │ │
│  │ │ │ ⚡ Generate Power Cables      [▶] ││ │ │ Discipline: [All]             │ │ │
│  │ │ │    Trigger: ON_IMPORT             ││ │ └───────────────────────────────┘ │ │
│  │ │ │    Last run: 14:32 (95 created)   ││ │                                   │ │
│  │ │ ├───────────────────────────────────┤│ │ ┌─ Conditions (ALL must match) ─┐ │ │
│  │ │ │ ⚡ Assign IO Points           [▶] ││ │ │ type == "PUMP"                 │ │ │
│  │ │ │    Trigger: ON_IMPORT             ││ │ │ AND power > 5kW               │ │ │
│  │ │ ├───────────────────────────────────┤│ │ │ AND NOT EXISTS(child.MOTOR)   │ │ │
│  │ │ │ ⏸ Cable Sizing Check         [▶] ││ │ │ [+ Add Condition]             │ │ │
│  │ │ │    Trigger: ON_CHANGE             ││ │ └───────────────────────────────┘ │ │
│  │ │ └───────────────────────────────────┘│ │                                   │ │
│  │ │                                       │ │ ┌─ Actions ─────────────────────┐ │ │
│  │ │ [+ New Rule]                          │ │ │ 1. CREATE_CHILD               │ │ │
│  │ │                                       │ │ │    type: MOTOR                │ │ │
│  │ │ ─────────────────────────────────────│ │ │    tag: {parent.tag}A         │ │ │
│  │ │ Quick Actions:                        │ │ │    copy: [area, system, loc]  │ │ │
│  │ │ [▶ Run All Active]                   │ │ │ [+ Add Action]                │ │ │
│  │ │ [▶ Run Selected on Area 210]         │ │ └───────────────────────────────┘ │ │
│  │ │ [📋 Import Rules JSON]               │ │                                   │ │
│  │ └───────────────────────────────────────┘ │ [Save] [Test on 10 assets] [▶ Run] │ │
│  │                                           └───────────────────────────────────┘ │
├──┴───────────────────────────────────────────────────────────────────────────────┤
│ DevConsole ── [Filter: RULE ▼] ──────────────────────────────────────── [▲▼] ──  │
│ 14:32:05 ✅ [RULE] Executing "Create Motor for Pump" on 100 assets...            │
│ 14:32:06 ✅ [RULE] Created: MTR-210-001A, MTR-210-002A, ... (49 total)            │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 📂 Gold Mine │ 8 rules active │ Last run: 14:32 │ 144 assets created │ ● Online  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 5.7 Écran: CSV Import

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 🔷 SYNAPSE    Gold Mine Expansion ▼                    admin@aurumax.com  🔔  ⚙️ │
├──┬───────────────────────────────────────────────────────────────────────────────┤
│📊│ ┌─ Import Wizard ───────────────────────────────────────────────────────────┐ │
│📁│ │                                                                            │ │
│⚙️│ │  Step: [1.Upload]──[2.Map]──[3.Preview]──[●4.Import]──[5.Done]            │ │
│📥│ │                                                                            │ │
│◀─│ │  ┌─ Import Progress ──────────────────────────────────────────────────┐   │ │
│📦│ │  │                                                                     │   │ │
│📜│ │  │  📄 BBA-Instruments.csv                                            │   │ │
│🔧│ │  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 78%           │   │ │
│  │ │  │                                                                     │   │ │
│  │ │  │  ✅ Parsed: 100 rows                                               │   │ │
│  │ │  │  ✅ Validated: 100 rows (0 errors)                                 │   │ │
│  │ │  │  🔄 Importing: 78/100 instruments...                               │   │ │
│  │ │  │  ⏳ Rules pending: 3 rules queued                                  │   │ │
│  │ │  │                                                                     │   │ │
│  │ │  │  ┌─ Live Stats ─────────────────────────────────────────────────┐  │   │ │
│  │ │  │  │ Created:  78 instruments                                      │  │   │ │
│  │ │  │  │ Updated:  0                                                   │  │   │ │
│  │ │  │  │ Skipped:  0                                                   │  │   │ │
│  │ │  │  │ Errors:   0                                                   │  │   │ │
│  │ │  │  └──────────────────────────────────────────────────────────────┘  │   │ │
│  │ │  │                                                                     │   │ │
│  │ │  │  ☑ Run rules after import (3 rules match)                          │   │ │
│  │ │  │  ☐ Create new version for existing assets                          │   │ │
│  │ │  │                                                                     │   │ │
│  │ │  └─────────────────────────────────────────────────────────────────────┘   │ │
│  │ │                                                                            │ │
│  │ │  [Cancel Import]                                                           │ │
│  │ └────────────────────────────────────────────────────────────────────────────┘ │
├──┴───────────────────────────────────────────────────────────────────────────────┤
│ DevConsole ── [Filter: IMPORT ▼] ─────────────────────────────────────── [▲] ──  │
│ 14:32:01 ✅ [IMPORT] Started: BBA-Instruments.csv (100 rows)                     │
│ 14:32:02 ✅ [IMPORT] Row 1: Created LT-210-001 (Level Transmitter)               │
│ 14:32:02 ✅ [IMPORT] Row 2: Created PT-210-001 (Pressure Transmitter)            │
│ 14:32:03 ✅ [IMPORT] Row 3: Created FT-210-001 (Flow Transmitter)                │
│ 14:32:03 ... importing ...                                                        │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 📂 Gold Mine │ Importing... 78/100 │ ETA: 5s │ v0.2.2 │ ● Online                 │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 5.8 Écran: Timeline / History

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 🔷 SYNAPSE    Gold Mine Expansion ▼                    admin@aurumax.com  🔔  ⚙️ │
├──┬───────────────────────────────────────────────────────────────────────────────┤
│📊│ ┌─ Timeline ────────────────────────────────────────────────────────────────┐ │
│📁│ │                                                                            │ │
│⚙️│ │ Filter: [All Sources ▼] [All Levels ▼] [Today ▼]  🔍 [_______________]    │ │
│📥│ │ Scope:  [All ▼] FBS: [All ▼] LBS: [ROOM-112 ▼] DISC: [All ▼]              │ │
│📦│ │                                                                            │ │
│📜│ │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │ │
│◀─│ │                                                                            │ │
│🔧│ │   14:45  ──●── Rule Engine: Cable Resizing                                │ │
│  │ │             │   └─ Updated 12 cables (size changed)                        │ │
│  │ │             │   └─ MTR-210-001A.power triggered recalc                     │ │
│  │ │                                                                            │ │
│  │ │   14:40  ──●── Manual Edit by admin@aurumax.com                           │ │
│  │ │             │   └─ MTR-210-001A.power: 15kW → 18.5kW                       │ │
│  │ │             │   └─ Reason: "Client spec REV-003"                           │ │
│  │ │                                                                            │ │
│  │ │   14:32  ──●── Rule Engine Execution                                      │ │
│  │ │             │   ├─ Rule: "Create Motor for Pump" (49 created)              │ │
│  │ │             │   ├─ Rule: "Generate Power Cables" (95 created)              │ │
│  │ │             │   │   └─ ⚠️ Warning: PWR-210-042 length 127m > 100m          │ │
│  │ │             │   └─ Rule: "Assign IO Points" (147 created)                  │ │
│  │ │                                                                            │ │
│  │ │   14:30  ──●── CSV Import: BBA-Instruments.csv                            │ │
│  │ │             │   └─ 100 instruments created                                 │ │
│  │ │             │   └─ User: admin@aurumax.com                                 │ │
│  │ │                                                                            │ │
│  │ │   14:25  ──●── Project Created                                            │ │
│  │ │                                                                            │ │
│  │ │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │ │
│  │ │                                                                            │ │
│  │ │ [◀ Earlier]                                              [Load More ▼]    │ │
│  │ └────────────────────────────────────────────────────────────────────────────┘ │
├──┴───────────────────────────────────────────────────────────────────────────────┤
│ DevConsole (hidden) ────────────────────────────────────────────────── [▼] ────  │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 📂 Gold Mine │ 247 events │ Showing: ROOM-112 │ v0.2.2 │ ● Online                │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 5.9 Color Palette (VSCode Dark Theme)

```css
/* === BASE COLORS === */
--bg-primary:     #1e1e1e;    /* Main background */
--bg-secondary:   #252526;    /* Sidebar, panels */
--bg-tertiary:    #2d2d2d;    /* Cards, elevated */
--bg-hover:       #2a2d2e;    /* Hover states */
--bg-active:      #37373d;    /* Active/selected */

/* === BORDERS === */
--border-primary: #3c3c3c;    /* Main borders */
--border-focus:   #007acc;    /* Focus rings */

/* === TEXT === */
--text-primary:   #cccccc;    /* Main text */
--text-secondary: #858585;    /* Muted text */
--text-bright:    #ffffff;    /* Headings, emphasis */

/* === ACCENT (Blue) === */
--accent-primary: #007acc;    /* Primary actions */
--accent-hover:   #1c86c7;    /* Hover state */
--accent-active:  #0e639c;    /* Active state */

/* === STATUS COLORS === */
--success:        #4ec9b0;    /* Success, created */
--warning:        #dcdcaa;    /* Warnings */
--error:          #f14c4c;    /* Errors */
--info:           #3794ff;    /* Info */

/* === ACTIVITY BAR === */
--activity-bg:    #333333;
--activity-icon:  #858585;
--activity-active:#ffffff;
--activity-indicator: #007acc;

/* === TAGS/BADGES === */
--tag-electrical:   #569cd6;   /* Blue */
--tag-instrument:   #4ec9b0;   /* Teal */
--tag-mechanical:   #ce9178;   /* Orange */
--tag-process:      #dcdcaa;   /* Yellow */
```

### 5.10 Component Library (Shadcn/ui)

```
Composants principaux:
├── Layout
│   ├── AppLayout (shell principal)
│   ├── Sidebar (resizable avec Allotment)
│   ├── ActivityBar (icônes navigation)
│   └── StatusBar (footer info)
│
├── Navigation
│   ├── TreeView (FBS/LBS/PBS navigator)
│   ├── Tabs (Asset/Detail/History)
│   └── Breadcrumb (location path)
│
├── Data Display
│   ├── DataTable (assets list, sortable/filterable)
│   ├── Card (asset detail)
│   ├── Badge (type, status, discipline)
│   ├── Timeline (history events)
│   └── DiffView (version comparison)
│
├── Forms
│   ├── Select (view selector, filters)
│   ├── Input (search)
│   ├── Checkbox (multi-select)
│   └── Button (actions)
│
├── Feedback
│   ├── Toast (notifications)
│   ├── Progress (import progress)
│   ├── Skeleton (loading states)
│   └── Alert (warnings, errors)
│
└── DevConsole
    ├── LogEntry (single log line)
    ├── LogFilter (source, level)
    └── LogStream (websocket live)
```

### 5.11 Responsive Breakpoints

```
Desktop (>1200px):  Full layout avec sidebar + main + DevConsole
Laptop (992-1200px): Sidebar collapsible, reduced padding
Tablet (768-992px):  Sidebar overlay, touch-friendly
Mobile (<768px):    Non supporté MVP (focus desktop pour démo)
```

### 5.12 Key Interactions

```
1. View Switch (FBS/LBS/PBS/DISC)
   - Dropdown in sidebar header
   - Tree re-renders with new structure
   - Filters reset to "All"
   - URL updates: /assets?view=lbs&node=room-112

2. Asset Selection
   - Click row → Right panel shows detail
   - Double-click → Open in modal for edit
   - Checkbox → Multi-select for bulk actions

3. DevConsole Toggle
   - Click [▲▼] → Expand/collapse
   - Drag handle → Resize
   - Double-click → Full height
   - Filter dropdown → By source/level

4. Keyboard Shortcuts
   - Ctrl+K: Global search
   - Ctrl+I: Open import
   - Ctrl+Shift+C: Toggle DevConsole
   - ↑↓: Navigate asset list
   - Enter: Open detail
   - Esc: Close modals/panels
```

### 5.13 Demo Flow (UI Perspective)

```
1. [Dashboard] Vue d'ensemble
   → Stats: 0 assets, 8 rules ready
   → "Import your first data"

2. [Import] Wizard CSV
   → Upload BBA.csv
   → Auto-map columns
   → Preview 100 rows
   → Import avec progress bar
   → DevConsole shows live logs

3. [Explorer] Assets créés
   → 100 instruments in tree
   → Switch to LBS view
   → Navigate to ROOM-112

4. [Rules] Exécution
   → Select "Run All Active"
   → Watch DevConsole explode with activity
   → 291 assets created live

5. [Explorer] Résultat
   → ROOM-112 now has 47 assets
   → Click MTR-210-001A
   → See detail + children + history

6. [Timeline] Traçabilité
   → Full history of session
   → Filter by ROOM-112
   → See all events

7. [Export] Package
   → Select ROOM-112
   → Generate CA-P040
   → Download Excel
```

### 5.14 DATA GRID (AG Grid Style) - Feature Critique

**Librairie recommandée:** AG Grid Community (gratuit) ou TanStack Table + custom

#### 5.14.1 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ ┌─ Toolbar ──────────────────────────────────────────────────────────────────────┐  │
│ │ View: [Flat ▼] [Grouped ▼]  │  Columns: [Customize ▼]  │  [↓ Export] [⟳ Reset] │  │
│ └────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
│ ┌─ Data Grid ────────────────────────────────────────────────────────────────────┐  │
│ │┌──┬────────────┬──────────┬────────┬─────────┬──────────┬────────┬───────────┐│  │
│ ││☐ │ Tag ▼      │ Type ▼   │ Disc ▼ │ Power ▼ │ Location │ Parent │ Status    ││  │
│ │├──┼────────────┼──────────┼────────┼─────────┼──────────┼────────┼───────────┤│  │
│ ││  │ [*______]  │ [All ▼]  │[ELEC▼] │ [>10__] │ [_____]  │ [____] │ [●Act ▼]  ││  │
│ │├──┼────────────┼──────────┼────────┼─────────┼──────────┼────────┼───────────┤│  │
│ ││☐ │ MTR-210-001│ MOTOR    │ ELEC   │ 18.5 kW │ ROOM-112 │ P-210… │ ● Active  ││  │
│ ││☑ │ MTR-210-002│ MOTOR    │ ELEC   │ 15 kW   │ ROOM-112 │ P-210… │ ● Active  ││  │
│ ││☐ │ VFD-210-001│ VFD      │ ELEC   │ 18.5 kW │ ROOM-112 │ MTR-2… │ ● Active  ││  │
│ ││☐ │ PWR-210-001│ CABLE    │ ELEC   │ -       │ ROOM-112 │ MTR-2… │ ● Active  ││  │
│ ││▶ │ P-210-001  │ PUMP     │ MECH   │ 15 kW   │ ROOM-113 │ -      │ ● Active  ││  │
│ ││  │  └─ MTR-210│ MOTOR    │ ELEC   │ 15 kW   │ ROOM-112 │ ↑      │ ● Active  ││  │
│ ││  │  └─ VFD-210│ VFD      │ ELEC   │ 15 kW   │ ROOM-112 │ ↑      │ ● Active  ││  │
│ ││  │  └─ PWR-210│ CABLE    │ ELEC   │ -       │ ROOM-112 │ ↑      │ ● Active  ││  │
│ │├──┴────────────┴──────────┴────────┴─────────┴──────────┴────────┴───────────┤│  │
│ ││ Showing 47 of 547 │ Selected: 1 │ Filtered: Type=MOTOR │ Page 1/2 [◀][▶]    ││  │
│ │└─────────────────────────────────────────────────────────────────────────────┘│  │
│ └────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### 5.14.2 Filtres par Colonne (Control Characters)

**Syntaxe de filtrage avancé:**

| Pattern | Description | Exemple |
|---------|-------------|---------|
| `texte` | Contient | `pump` → "PUMP", "Pump Station" |
| `=texte` | Égal exact | `=MOTOR` → seulement "MOTOR" |
| `*texte` | Commence par | `*MTR` → "MTR-210-001", "MTR-220-005" |
| `texte*` | Finit par | `001*` → "MTR-210-001", "P-210-001" |
| `*text*` | Contient (wildcard) | `*210*` → tout avec "210" |
| `!texte` | Ne contient pas | `!CABLE` → exclut les câbles |
| `>nombre` | Plus grand que | `>10` → power > 10 kW |
| `<nombre` | Plus petit que | `<5` → power < 5 kW |
| `>=nombre` | Plus grand ou égal | `>=15` |
| `a..b` | Entre (range) | `10..20` → 10 ≤ x ≤ 20 |
| `val1,val2` | OU multiple | `MOTOR,VFD` → MOTOR ou VFD |
| `(vide)` | Cellules vides | filtre les nulls |

**Exemple visuel:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Tag         │ Type       │ Power     │ Location   │ Status     │
├─────────────┼────────────┼───────────┼────────────┼────────────┤
│ [*MTR-210_] │ [MOTOR,VFD]│ [>10____] │ [ROOM-112] │ [Active ▼] │
├─────────────┼────────────┼───────────┼────────────┼────────────┤
│ MTR-210-001 │ MOTOR      │ 18.5 kW   │ ROOM-112   │ ● Active   │
│ MTR-210-002 │ MOTOR      │ 15 kW     │ ROOM-112   │ ● Active   │
│ VFD-210-001 │ VFD        │ 18.5 kW   │ ROOM-112   │ ● Active   │
└─────────────┴────────────┴───────────┴────────────┴────────────┘
  Résultat: 3 assets (filtrés de 547)
```

#### 5.14.3 Context Menu (Right-Click)

```
┌─────────────────────────────────────────┐
│ MTR-210-001 (MOTOR)                     │
├─────────────────────────────────────────┤
│ 📋 Copy Tag                             │
│ 📋 Copy Row (JSON)                      │
│ ─────────────────────────────────────── │
│ 🔍 Filter by "MOTOR"              →     │
│    ├─ Type = MOTOR                      │
│    ├─ Add to current filter             │
│    └─ Exclude MOTOR                     │
│ 🔍 Filter by "ROOM-112"           →     │
│    ├─ Location = ROOM-112               │
│    └─ Exclude ROOM-112                  │
│ 🔍 Filter by "18.5 kW"            →     │
│    ├─ Power = 18.5                      │
│    ├─ Power > 18.5                      │
│    └─ Power < 18.5                      │
│ ─────────────────────────────────────── │
│ 👁️ Show Children                        │
│ 👁️ Show Parent (P-210-001)              │
│ 📜 View History                         │
│ 🔗 Show Related Cables                  │
│ ─────────────────────────────────────── │
│ ✏️ Edit Asset                           │
│ 📑 Duplicate                            │
│ 🗑️ Delete                              │
│ ─────────────────────────────────────── │
│ ▶ Run Rules on Selection                │
│ 📦 Add to Package                       │
└─────────────────────────────────────────┘
```

#### 5.14.4 Expand/Collapse (Hierarchical View)

```
Mode: [Flat ▼] → [Grouped by Parent ▼]

┌──┬────────────┬──────────┬────────┬─────────┐
│  │ Tag        │ Type     │ Power  │ Status  │
├──┼────────────┼──────────┼────────┼─────────┤
│▼ │ P-210-001  │ PUMP     │ 15 kW  │ Active  │  ← Parent (expandable)
│  │  ├─ MTR-210│ MOTOR    │ 15 kW  │ Active  │  ← Child level 1
│  │  │  └─ PWR │ CABLE    │ -      │ Active  │  ← Child level 2
│  │  │  └─ CTL │ CABLE    │ -      │ Active  │
│  │  └─ VFD-210│ VFD      │ 15 kW  │ Active  │
│  │     └─ SIG │ CABLE    │ -      │ Active  │
│▶ │ P-210-002  │ PUMP     │ 22 kW  │ Active  │  ← Collapsed
│▼ │ P-210-003  │ PUMP     │ 18 kW  │ Active  │
│  │  └─ ...    │          │        │         │
└──┴────────────┴──────────┴────────┴─────────┘

Controls:
[Expand All] [Collapse All] [Expand Level 1] [Expand Level 2]
```

#### 5.14.5 Inline Editing

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Tag         │ Type        │ Power       │ Voltage     │ Status             │
├─────────────┼─────────────┼─────────────┼─────────────┼────────────────────┤
│ MTR-210-001 │ MOTOR     ▼ │ [18.5____]  │ [480V   ▼]  │ ● Active         ▼ │
│             │  ┌────────┐ │  ↑ Editable │  ↑ Dropdown │                    │
│             │  │ MOTOR  │ │   (number)  │  ┌────────┐ │   ↑ Dropdown       │
│             │  │ VFD    │ │             │  │ 120V   │ │   ┌──────────────┐ │
│             │  │ PUMP   │ │             │  │ 240V   │ │   │ ● Active     │ │
│             │  │ CABLE  │ │             │  │ 480V ✓ │ │   │ ○ Draft      │ │
│             │  │ XFMR   │ │             │  │ 600V   │ │   │ ○ Deprecated │ │
│             │  └────────┘ │             │  │ 4160V  │ │   │ ○ Archived   │ │
│             │             │             │  └────────┘ │   └──────────────┘ │
├─────────────┼─────────────┼─────────────┼─────────────┼────────────────────┤
│ 🔒 PWR-210  │ CABLE       │ -           │ -           │ ● Active           │
│ (locked)    │ (readonly)  │             │             │ (no edit - linked) │
└─────────────┴─────────────┴─────────────┴─────────────┴────────────────────┘

Lock states:
🔒 Locked (generated by rule, cannot edit)
🔓 Editable (user created or unlocked)
⚠️ Warning (edit will trigger recalc)
```

**Règles d'édition:**
- **Locked fields**: Générés par rules, affichés avec 🔒
- **Dropdown fields**: Type, Status, Discipline, Location
- **Number fields**: Power, Voltage, FLA - validation inline
- **Text fields**: Tag (unique check), Description
- **Calculated fields**: Read-only, grayed out

#### 5.14.6 Column Customization

```
┌─────────────────────────────────────────┐
│ 📊 Customize Columns                    │
├─────────────────────────────────────────┤
│ Visible Columns:          [Drag to reorder]
│ ┌─────────────────────────────────────┐ │
│ │ ☑ Tag           [≡]                 │ │
│ │ ☑ Type          [≡]                 │ │
│ │ ☑ Discipline    [≡]                 │ │
│ │ ☑ Power         [≡]                 │ │
│ │ ☑ Voltage       [≡]                 │ │
│ │ ☐ FLA           [≡]  ← Hidden       │ │
│ │ ☐ Efficiency    [≡]  ← Hidden       │ │
│ │ ☑ Location      [≡]                 │ │
│ │ ☑ Parent        [≡]                 │ │
│ │ ☑ Status        [≡]                 │ │
│ │ ☐ Created At    [≡]  ← Hidden       │ │
│ │ ☐ Modified At   [≡]  ← Hidden       │ │
│ │ ☐ Version       [≡]  ← Hidden       │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Presets:                                │
│ [Default] [Electrical] [Mechanical]     │
│ [Import View] [Export View] [+ Save]    │
│                                         │
│ [Reset to Default]           [Apply]    │
└─────────────────────────────────────────┘
```

#### 5.14.7 Group By / Pivot

```
Group By: [None ▼] → [Type ▼] [+ Location ▼]

┌──┬────────────────────────┬───────┬─────────────────┐
│  │ Group                  │ Count │ Power (Sum)     │
├──┼────────────────────────┼───────┼─────────────────┤
│▼ │ 📁 MOTOR               │ 49    │ 735.5 kW        │
│  │  ├─ 📁 ROOM-112        │ 12    │ 198 kW          │
│  │  │   └─ MTR-210-001    │       │ 18.5 kW         │
│  │  │   └─ MTR-210-002    │       │ 15 kW           │
│  │  │   └─ ...            │       │                 │
│  │  ├─ 📁 ROOM-113        │ 23    │ 345 kW          │
│  │  └─ 📁 ROOM-114        │ 14    │ 192.5 kW        │
│▶ │ 📁 VFD                 │ 35    │ 525 kW          │
│▶ │ 📁 CABLE               │ 95    │ -               │
│▶ │ 📁 PUMP                │ 49    │ 892 kW          │
└──┴────────────────────────┴───────┴─────────────────┘

Aggregations disponibles: Sum, Avg, Min, Max, Count
```

#### 5.14.8 Quick Actions Bar

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Selection: 5 assets                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ [✏️ Bulk Edit] [🗑️ Delete] [📦 Add to Package] [▶ Run Rules] [📤 Export]    │
│                                                                              │
│ Bulk Edit Panel (if opened):                                                 │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Set for 5 selected assets:                                               │ │
│ │                                                                          │ │
│ │ Status:    [● Active ▼]     □ Apply                                     │ │
│ │ Location:  [ROOM-112 ▼]     □ Apply                                     │ │
│ │ Discipline:[ELECTRICAL ▼]   ☑ Apply ← Will change                       │ │
│ │                                                                          │ │
│ │ [Cancel]                                               [Apply Changes]  │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 5.14.9 Keyboard Shortcuts (Grid)

```
Navigation:
  ↑↓←→      Navigate cells
  Tab       Next cell
  Shift+Tab Previous cell
  Home/End  First/Last column
  Ctrl+Home First cell
  Ctrl+End  Last cell
  Page Up   Previous page
  Page Down Next page

Selection:
  Space     Toggle row selection
  Ctrl+A    Select all
  Shift+↑↓  Extend selection
  Ctrl+Click Multi-select

Editing:
  Enter     Start editing / Confirm
  Escape    Cancel editing
  F2        Edit current cell
  Delete    Clear cell content

Filtering:
  Ctrl+F    Focus filter row
  Escape    Clear filters

Actions:
  Ctrl+C    Copy selection
  Ctrl+V    Paste (if editable)
  Ctrl+D    Duplicate selected
  Delete    Delete selected (with confirm)
```

#### 5.14.10 Export Options

```
┌─────────────────────────────────────────┐
│ 📤 Export Data                          │
├─────────────────────────────────────────┤
│ Format:                                 │
│ ○ Excel (.xlsx)                         │
│ ● CSV (.csv)                            │
│ ○ JSON (.json)                          │
│                                         │
│ Scope:                                  │
│ ○ All assets (547)                      │
│ ● Filtered view (47)                    │
│ ○ Selected only (5)                     │
│                                         │
│ Options:                                │
│ ☑ Include headers                       │
│ ☑ Apply current column order            │
│ ☐ Include hidden columns                │
│ ☑ Export grouped structure              │
│                                         │
│ [Cancel]                    [Export]    │
└─────────────────────────────────────────┘
```

#### 5.14.11 Implementation Notes

```typescript
// Librairie recommandée: AG Grid Community (free)
// Alternative: TanStack Table + custom components

interface GridConfig {
  // Colonnes avec types
  columns: ColumnDef[];

  // Données
  data: Asset[];

  // Features
  features: {
    filtering: true,           // Filtres par colonne
    sorting: true,             // Tri multi-colonnes
    grouping: true,            // Group by
    pivoting: false,           // MVP: pas de pivot
    rowSelection: 'multiple',  // Selection multiple
    cellEditing: true,         // Edition inline
    columnReorder: true,       // Drag & drop colonnes
    columnResize: true,        // Resize colonnes
    rowExpansion: true,        // Expand children
    contextMenu: true,         // Right-click menu
    quickFilter: true,         // Global search
    pagination: true,          // 50 rows par page
    infiniteScroll: false,     // MVP: pagination
  };

  // Callbacks
  onCellEdit: (asset: Asset, field: string, newValue: any) => void;
  onSelectionChange: (selected: Asset[]) => void;
  onFilterChange: (filters: FilterState) => void;
  onContextMenuAction: (action: string, asset: Asset) => void;
}

// Column definition example
const columns: ColumnDef[] = [
  {
    field: 'tag',
    header: 'Tag',
    filter: 'text',
    sortable: true,
    editable: (row) => !row.isLocked,
    cellRenderer: 'tagCell',  // Custom avec icône type
  },
  {
    field: 'type',
    header: 'Type',
    filter: 'select',
    filterOptions: ['MOTOR', 'VFD', 'PUMP', 'CABLE', ...],
    editable: true,
    cellEditor: 'dropdown',
  },
  {
    field: 'power',
    header: 'Power',
    filter: 'number',
    sortable: true,
    editable: (row) => row.type !== 'CABLE',
    cellRenderer: 'powerCell',  // Avec unité kW
    aggregation: 'sum',
  },
  // ...
];
```

### 5.15 CLIENT & PROJECT MANAGEMENT (Multi-Tenancy)

#### 5.15.1 Hiérarchie des Données

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DATA HIERARCHY                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                              SYSTEM                                      │   │
│   │  • Users (authentication)                                               │   │
│   │  • System settings                                                       │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                             │
│                                    ▼                                             │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                              CLIENT                                      │   │
│   │  • Aurumax Mining Corp.                                                  │   │
│   │  • BBA Engineering (test)                                                │   │
│   │  • Demo Client                                                           │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                    │                              │                              │
│                    ▼                              ▼                              │
│   ┌────────────────────────────┐   ┌────────────────────────────┐              │
│   │         PROJECT            │   │         PROJECT            │              │
│   │  • Gold Mine Expansion     │   │  • Test Import Project     │              │
│   │  • Copper Processing       │   │                            │              │
│   └────────────────────────────┘   └────────────────────────────┘              │
│              │                                    │                              │
│              ▼                                    ▼                              │
│   ┌────────────────────────────────────────────────────────────────────────┐   │
│   │  PROJECT DATA (Isolated)                                                │   │
│   │  • Assets      • Cables      • Rules       • Packages                   │   │
│   │  • FBS/LBS     • Events      • Versions    • Exports                    │   │
│   └────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

#### 5.15.2 Database Schema - Multi-Tenancy

```sql
-- Clients (Organizations)
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identity
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,        -- "AURUMAX", "BBA", "DEMO"
    logo_url VARCHAR(500),

    -- Contact
    contact_name VARCHAR(100),
    contact_email VARCHAR(255),

    -- Settings
    settings JSONB DEFAULT '{}',             -- Client-specific config

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Limits (future billing)
    max_projects INTEGER DEFAULT 10,
    max_assets_per_project INTEGER DEFAULT 10000,

    INDEX ix_clients_code (code),
    INDEX ix_clients_active (is_active)
);

-- Projects (per Client)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Ownership
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,

    -- Identity
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50) NOT NULL,               -- "GOLD-MINE-EXP", "TEST-001"
    description TEXT,

    -- Location info
    location VARCHAR(200),                   -- "Northern Quebec, Canada"
    timezone VARCHAR(50) DEFAULT 'America/Toronto',

    -- Project settings
    settings JSONB DEFAULT '{}',
    default_discipline VARCHAR(50),
    tag_prefix VARCHAR(10),                  -- "GM-" for Gold Mine

    -- Status
    status VARCHAR(20) DEFAULT 'ACTIVE',     -- ACTIVE, ARCHIVED, TEMPLATE
    is_demo BOOLEAN DEFAULT FALSE,           -- Demo project flag

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    archived_at TIMESTAMPTZ,

    -- Stats (denormalized for quick display)
    asset_count INTEGER DEFAULT 0,
    cable_count INTEGER DEFAULT 0,
    last_activity_at TIMESTAMPTZ,

    UNIQUE(client_id, code),
    INDEX ix_projects_client (client_id),
    INDEX ix_projects_status (status),
    INDEX ix_projects_demo (is_demo)
);

-- User-Client-Project Access (RBAC future)
CREATE TABLE user_project_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL REFERENCES users(id),
    project_id UUID NOT NULL REFERENCES projects(id),

    -- Role (future RBAC)
    role VARCHAR(20) DEFAULT 'MEMBER',       -- OWNER, ADMIN, MEMBER, VIEWER

    -- Permissions (bitmask or JSONB for future)
    permissions JSONB DEFAULT '{"read": true, "write": true}',

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, project_id),
    INDEX ix_user_project_user (user_id),
    INDEX ix_user_project_project (project_id)
);

-- All data tables have project_id
-- Example: Assets
ALTER TABLE assets ADD COLUMN project_id UUID NOT NULL REFERENCES projects(id);
CREATE INDEX ix_assets_project ON assets(project_id);

-- Row-Level Security (PostgreSQL)
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;

CREATE POLICY assets_project_isolation ON assets
    USING (project_id = current_setting('app.current_project_id')::uuid);
```

#### 5.15.3 UI - Project Switcher (Header)

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 🔷 SYNAPSE    [Aurumax Mining ▼] / [Gold Mine Expansion ▼]     admin  🔔  ⚙️     │
├──────────────────────────────────────────────────────────────────────────────────┤
│                │                                                                  │
│                ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐            │
│  │ 🏢 Select Client                                                 │            │
│  ├─────────────────────────────────────────────────────────────────┤            │
│  │ 🔍 Search clients...                                            │            │
│  ├─────────────────────────────────────────────────────────────────┤            │
│  │ ⭐ Aurumax Mining Corp.           2 projects              ✓    │            │
│  │    BBA Engineering                 1 project                    │            │
│  │ 🎭 Demo Client                     1 project (demo)             │            │
│  ├─────────────────────────────────────────────────────────────────┤            │
│  │ [+ New Client]                                      [Manage →]  │            │
│  └─────────────────────────────────────────────────────────────────┘            │
│                                                                                  │
│                                    │                                             │
│                                    ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────┐            │
│  │ 📁 Select Project (Aurumax Mining)                              │            │
│  ├─────────────────────────────────────────────────────────────────┤            │
│  │ 🔍 Search projects...                                           │            │
│  ├─────────────────────────────────────────────────────────────────┤            │
│  │ ⭐ Gold Mine Expansion              547 assets      ✓           │            │
│  │    └─ Last activity: 5 min ago                                  │            │
│  │    Copper Processing Plant          0 assets                    │            │
│  │    └─ Created: Yesterday                                        │            │
│  ├─────────────────────────────────────────────────────────────────┤            │
│  │ [+ New Project]  [📋 From Template]             [Manage →]      │            │
│  └─────────────────────────────────────────────────────────────────┘            │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

#### 5.15.4 UI - Project Management Page

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 🔷 SYNAPSE    Settings > Projects                          admin@aurumax.com  ⚙️ │
├──┬───────────────────────────────────────────────────────────────────────────────┤
│📊│ ┌─ Projects ──────────────────────────────────────────────────────────────┐   │
│📁│ │                                                                          │   │
│⚙️│ │ Client: [Aurumax Mining Corp. ▼]                    [+ New Project]     │   │
│📥│ │                                                                          │   │
│📦│ │ ┌────────────────────────────────────────────────────────────────────┐  │   │
│📜│ │ │  Project              │ Code      │ Assets │ Status   │ Actions    │  │   │
│🔧│ │ ├───────────────────────┼───────────┼────────┼──────────┼────────────┤  │   │
│◀─│ │ │ ⭐ Gold Mine Expansion│ GOLD-EXP  │ 547    │ ● Active │ [⚙️][🗑️]   │  │   │
│  │ │ │    Northern Quebec    │           │        │          │            │  │   │
│  │ │ ├───────────────────────┼───────────┼────────┼──────────┼────────────┤  │   │
│  │ │ │ Copper Processing     │ COPPER-01 │ 0      │ ● Active │ [⚙️][🗑️]   │  │   │
│  │ │ │    Chile Site         │           │        │          │            │  │   │
│  │ │ └───────────────────────┴───────────┴────────┴──────────┴────────────┘  │   │
│  │ │                                                                          │   │
│  │ │ ── Templates ──────────────────────────────────────────────────────────  │   │
│  │ │ ┌────────────────────────────────────────────────────────────────────┐  │   │
│  │ │ │ 📋 Mining Project Template    │ 8 rules │ 3 FBS │ Use as template  │  │   │
│  │ │ │ 📋 Process Plant Template     │ 12 rules│ 5 FBS │ Use as template  │  │   │
│  │ │ └────────────────────────────────────────────────────────────────────┘  │   │
│  │ │                                                                          │   │
│  │ └──────────────────────────────────────────────────────────────────────────┘   │
├──┴───────────────────────────────────────────────────────────────────────────────┤
│ 2 projects │ 547 total assets │ Client: Aurumax Mining                           │
└──────────────────────────────────────────────────────────────────────────────────┘
```

#### 5.15.5 Quick Actions - Create/Delete Project

```
┌─────────────────────────────────────────────────────────────────┐
│ 📁 Create New Project                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Client:       Aurumax Mining Corp.                              │
│                                                                  │
│ Project Name: [________________________________]                 │
│               e.g., "Gold Mine Expansion Phase 2"               │
│                                                                  │
│ Project Code: [____________]  (auto-generated from name)        │
│               e.g., "GOLD-EXP-P2"                                │
│                                                                  │
│ Location:     [________________________________]                 │
│               e.g., "Northern Quebec, Canada"                   │
│                                                                  │
│ Tag Prefix:   [____]  (optional)                                │
│               e.g., "GM2-"                                       │
│                                                                  │
│ ─────────────────────────────────────────────────────────────── │
│                                                                  │
│ Initialize from:                                                 │
│ ○ Empty project                                                  │
│ ○ Copy from existing: [Gold Mine Expansion ▼]                   │
│   ☑ Copy FBS/LBS structure                                      │
│   ☑ Copy Rules                                                   │
│   ☐ Copy Assets (0 assets)                                      │
│ ○ Template: [Mining Project Template ▼]                         │
│                                                                  │
│ [Cancel]                                       [Create Project]  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ⚠️ Delete Project                                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Are you sure you want to delete this project?                   │
│                                                                  │
│ Project: Gold Mine Expansion (GOLD-EXP)                         │
│ Client:  Aurumax Mining Corp.                                   │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ This will permanently delete:                                │ │
│ │   • 547 assets                                               │ │
│ │   • 95 cables                                                │ │
│ │   • 8 rules                                                  │ │
│ │   • 1,247 workflow events                                    │ │
│ │   • 3 exported packages                                      │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ☐ I understand this action cannot be undone                     │
│                                                                  │
│ Type project code to confirm: [____________]                    │
│                                GOLD-EXP                         │
│                                                                  │
│ [Cancel]                                       [Delete Project]  │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.15.6 Demo Data - Gold Mine Project (Mockup Complet)

**Project: Gold Mine Expansion**
```yaml
Client: Aurumax Mining Corp.
Project Code: GOLD-EXP
Location: Northern Quebec, Canada
Tag Prefix: GM-

# Structure FBS (Functional)
FBS:
  100-UTILITIES:
    110-WATER: "Water Supply System"
    120-AIR: "Compressed Air System"
    130-POWER: "Power Distribution"

  200-PROCESS:
    210-CRUSHING: "Crushing Circuit"
      211: "Primary Crusher"
      212: "Secondary Crusher"
      213: "Tertiary Crusher"
    220-GRINDING: "Grinding Circuit"
      221: "SAG Mill"
      222: "Ball Mill"
      223: "Cyclones"
    230-LEACHING: "Leaching Circuit"          # ← Gold extraction
      231: "CIL Tanks"                        # Carbon-in-Leach
      232: "Cyanide Addition"
      233: "Carbon Handling"
    240-ELUTION: "Elution & Recovery"
      241: "Elution Column"
      242: "Electrowinning"
      243: "Smelting"
    250-TAILINGS: "Tailings Management"
      251: "Thickener"
      252: "Tailings Pumps"
      253: "TSF (Tailings Storage)"

  300-INFRASTRUCTURE:
    310-ADMIN: "Administration Building"
    320-WAREHOUSE: "Warehouse & Maintenance"
    330-LAB: "Assay Laboratory"

# Structure LBS (Location)
LBS:
  SITE-GOLDMINE:
    AREA-100: "Process Plant"
      BLDG-110: "Crushing Building"
        ROOM-111: "Primary Crusher Hall"
        ROOM-112: "Crusher Control Room"
      BLDG-120: "Mill Building"
        ROOM-121: "SAG Mill Hall"
        ROOM-122: "Ball Mill Hall"
        ROOM-123: "Mill Control Room"
        ROOM-124: "Mill MCC Room"
      BLDG-130: "Leach Building"
        ROOM-131: "CIL Tank Area"
        ROOM-132: "Carbon Handling"
        ROOM-133: "Leach Control Room"
      BLDG-140: "Gold Room"
        ROOM-141: "Elution Area"
        ROOM-142: "Electrowinning"
        ROOM-143: "Smelting Room"
        ROOM-144: "Gold Room Control"
    AREA-200: "Utilities"
      EHOUSE-201: "Main Electrical Room"
      EHOUSE-202: "Mill Substation"
      PUMP-210: "Raw Water Pump House"
      COMP-220: "Compressor Building"
    AREA-300: "Tailings"
      THICK-301: "Thickener Area"
      PUMP-302: "Tailings Pump Station"
    AREA-400: "Infrastructure"
      ADMIN-401: "Admin & Dry"
      MAINT-402: "Maintenance Shop"
      LAB-403: "Assay Lab"

# Sample Assets (547 total)
Assets:
  # Crushing
  - tag: "CR-211-001"
    type: "CRUSHER"
    description: "Primary Jaw Crusher"
    fbs: "211"
    lbs: "ROOM-111"
    power: 250kW
    children:
      - "MTR-211-001" (Motor 250kW)
      - "VFD-211-001" (VFD)
      - "LT-211-001" (Level Transmitter)

  # SAG Mill
  - tag: "ML-221-001"
    type: "MILL"
    description: "SAG Mill 28' x 14'"
    fbs: "221"
    lbs: "ROOM-121"
    power: 8500kW
    children:
      - "MTR-221-001" (Gearless Motor 8.5MW)
      - "LUB-221-001" (Lube System)
      - "WT-221-001" (Weight Transmitter)
      - "ST-221-001" (Speed Transmitter)

  # Ball Mill
  - tag: "ML-222-001"
    type: "MILL"
    description: "Ball Mill 22' x 36'"
    fbs: "222"
    lbs: "ROOM-122"
    power: 6500kW

  # Leaching - CIL Tanks (6 tanks)
  - tag: "TK-231-001" to "TK-231-006"
    type: "TANK"
    description: "CIL Tank #1-6"
    fbs: "231"
    lbs: "ROOM-131"
    volume: 1500m³
    children:
      - "AG-231-001" (Agitator 75kW)
      - "LT-231-001" (Level)
      - "PT-231-001" (Pressure)
      - "AT-231-001" (pH Analyzer)
      - "DT-231-001" (Density)

  # Cyanide System
  - tag: "TK-232-001"
    type: "TANK"
    description: "Cyanide Mixing Tank"
    fbs: "232"
    lbs: "ROOM-131"
    hazard: "TOXIC"

  - tag: "PP-232-001"
    type: "PUMP"
    description: "Cyanide Dosing Pump"
    fbs: "232"
    children:
      - "MTR-232-001" (Motor 5.5kW)
      - "FT-232-001" (Flow Transmitter)

  # Elution
  - tag: "CL-241-001"
    type: "COLUMN"
    description: "Elution Column"
    fbs: "241"
    lbs: "ROOM-141"

  # Electrowinning
  - tag: "EW-242-001"
    type: "ELECTROWIN"
    description: "Electrowinning Cell Bank"
    fbs: "242"
    lbs: "ROOM-142"
    power: 150kW DC

  # Tailings
  - tag: "TH-251-001"
    type: "THICKENER"
    description: "Tailings Thickener 45m"
    fbs: "251"
    lbs: "THICK-301"
    diameter: 45m
    children:
      - "MTR-251-001" (Rake Drive 30kW)
      - "PP-251-001" (Underflow Pump)
      - "DT-251-001" (Density Transmitter)
      - "LT-251-001" (Level Transmitter)

  - tag: "PP-252-001A/B"
    type: "PUMP"
    description: "Tailings Pump (Duty/Standby)"
    fbs: "252"
    lbs: "PUMP-302"
    power: 450kW

  # Utilities
  - tag: "PP-110-001A/B"
    type: "PUMP"
    description: "Raw Water Pump"
    fbs: "110"
    lbs: "PUMP-210"
    power: 150kW

  - tag: "CP-120-001A/B/C"
    type: "COMPRESSOR"
    description: "Plant Air Compressor"
    fbs: "120"
    lbs: "COMP-220"
    power: 200kW

  # Electrical
  - tag: "XFMR-130-001"
    type: "TRANSFORMER"
    description: "Main Transformer 25MVA"
    fbs: "130"
    lbs: "EHOUSE-201"
    rating: "25MVA 69kV/4.16kV"

  - tag: "MCC-130-001"
    type: "MCC"
    description: "Mill MCC #1"
    fbs: "130"
    lbs: "ROOM-124"

# Cables (95 total)
Cables:
  - tag: "PWR-221-001"
    from: "MCC-130-001"
    to: "MTR-221-001"
    type: "POWER"
    size: "3x500 MCM"
    length: 125m

  - tag: "SIG-231-001"
    from: "LT-231-001"
    to: "PLC-133-001"
    type: "SIGNAL"
    size: "2x1.5mm²"
    length: 45m

# Rules (8)
Rules:
  - "Create Motor for Pump"
  - "Create Motor for Crusher"
  - "Create Motor for Agitator"
  - "Generate Power Cable"
  - "Generate Signal Cable"
  - "Assign IO Points"
  - "Calculate Cable Size"
  - "Create Instrument Children"
```

#### 5.15.7 Demo Data - Test Project (Pour Import CSV)

**Project: Test Import**
```yaml
Client: Demo Client
Project Code: TEST-IMPORT
Location: Test Environment
Tag Prefix: TST-

# Empty project pour tester l'import CSV
# Permet de:
# - Importer le fichier BBA-Instruments.csv
# - Voir les rules s'exécuter
# - Tester le rollback
# - Recommencer facilement (delete + recreate)

# Structure minimale pré-configurée
FBS:
  100-UTILITIES: "Utilities"
  200-PROCESS: "Process"

LBS:
  SITE-TEST:
    AREA-100: "Test Area"
      ROOM-101: "Test Room"

Rules: (same as Gold Mine - copied from template)
```

#### 5.15.8 Backend - Project Context Middleware

```python
# app/api/middleware/project_context.py

from fastapi import Request, HTTPException
from app.core.database import SessionLocal

class ProjectContextMiddleware:
    """
    Middleware qui extrait et valide le project_id du header X-Project-ID
    et le rend disponible pour toutes les requêtes.
    """

    async def __call__(self, request: Request, call_next):
        # Skip pour routes publiques
        if request.url.path in ["/api/v1/auth/login", "/health", "/docs"]:
            return await call_next(request)

        # Extraire project_id du header
        project_id = request.headers.get("X-Project-ID")

        if not project_id:
            raise HTTPException(
                status_code=400,
                detail="X-Project-ID header is required"
            )

        # Valider que le projet existe et user a accès
        async with SessionLocal() as db:
            project = await db.get(Project, project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

            # TODO: Vérifier accès user au projet
            # access = await check_user_project_access(user_id, project_id)

            # Stocker dans request state
            request.state.project_id = project_id
            request.state.project = project
            request.state.client_id = project.client_id

            # Set PostgreSQL session variable pour RLS
            await db.execute(
                f"SET app.current_project_id = '{project_id}'"
            )

        response = await call_next(request)
        return response


# Dependency pour injecter project_id
def get_current_project(request: Request) -> str:
    """Récupère le project_id depuis le request state."""
    project_id = getattr(request.state, 'project_id', None)
    if not project_id:
        raise HTTPException(status_code=400, detail="Project context not set")
    return project_id


# Usage dans endpoints
@router.get("/assets")
async def get_assets(
    project_id: str = Depends(get_current_project),
    db: AsyncSession = Depends(get_db)
):
    # project_id automatiquement filtré
    assets = await db.execute(
        select(Asset).where(Asset.project_id == project_id)
    )
    return assets.scalars().all()
```

#### 5.15.9 Frontend - Project Store

```typescript
// stores/useProjectStore.ts

interface Client {
  id: string;
  name: string;
  code: string;
  logoUrl?: string;
  projectCount: number;
}

interface Project {
  id: string;
  clientId: string;
  name: string;
  code: string;
  location?: string;
  status: 'ACTIVE' | 'ARCHIVED' | 'TEMPLATE';
  isDemo: boolean;
  assetCount: number;
  cableCount: number;
  lastActivityAt: string;
}

interface ProjectState {
  // Current selection
  currentClient: Client | null;
  currentProject: Project | null;

  // Lists
  clients: Client[];
  projects: Project[];  // Projects for current client

  // Actions
  setCurrentClient: (client: Client) => void;
  setCurrentProject: (project: Project) => void;
  fetchClients: () => Promise<void>;
  fetchProjects: (clientId: string) => Promise<void>;
  createProject: (data: CreateProjectDTO) => Promise<Project>;
  deleteProject: (projectId: string) => Promise<void>;

  // Persisted
  lastClientId: string | null;
  lastProjectId: string | null;
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set, get) => ({
      currentClient: null,
      currentProject: null,
      clients: [],
      projects: [],
      lastClientId: null,
      lastProjectId: null,

      setCurrentClient: async (client) => {
        set({ currentClient: client, lastClientId: client.id });
        // Fetch projects for this client
        await get().fetchProjects(client.id);
      },

      setCurrentProject: (project) => {
        set({ currentProject: project, lastProjectId: project.id });
        // Update axios default header
        apiClient.defaults.headers['X-Project-ID'] = project.id;
      },

      createProject: async (data) => {
        const response = await apiClient.post('/projects', data);
        const newProject = response.data;
        set((state) => ({
          projects: [...state.projects, newProject]
        }));
        return newProject;
      },

      deleteProject: async (projectId) => {
        await apiClient.delete(`/projects/${projectId}`);
        set((state) => ({
          projects: state.projects.filter(p => p.id !== projectId),
          currentProject: state.currentProject?.id === projectId
            ? null
            : state.currentProject
        }));
      },
    }),
    {
      name: 'synapse-project-store',
      partialize: (state) => ({
        lastClientId: state.lastClientId,
        lastProjectId: state.lastProjectId,
      }),
    }
  )
);
```

#### 5.15.10 Demo Flow - Multi-Project

```
DÉMO SCENARIO:

1. [Login] Admin se connecte
   → Arrive sur Dashboard
   → Header: "Aurumax Mining / Gold Mine Expansion"

2. [Explorer] Montrer le projet Gold Mine
   → 547 assets, structure complète
   → "Voici un projet réel avec des données de mine d'or"
   → Montrer FBS: Crushing → Grinding → Leaching → Elution
   → Montrer les CIL tanks, Electrowinning, etc.

3. [Switch Project] Créer nouveau projet pour test
   → Click "Gold Mine Expansion ▼"
   → "+ New Project"
   → Name: "Import Test"
   → Initialize: Empty
   → [Create]

4. [Import] Importer dans le nouveau projet
   → Le projet est vide (0 assets)
   → Upload BBA-Instruments.csv
   → Watch import + rules execute

5. [Switch Back] Retourner au Gold Mine
   → "Gold Mine Expansion ▼"
   → Les données sont séparées
   → "Le projet Gold Mine n'a pas été affecté"

6. [Cleanup] Supprimer le projet test
   → Settings → Projects
   → Delete "Import Test"
   → Confirmer
   → "Prêt pour une nouvelle démo"
```

### 5.16 USER INBOX & NOTIFICATIONS (Collaboration)

#### 5.16.1 Concept: "Personal Engineering Dashboard"

**Problème:**
- Les ingénieurs travaillent sur des centaines d'assets
- Les changements d'une discipline affectent les autres
- Besoin de suivre les items importants
- Besoin d'être notifié des changements critiques

**Solution:**
- **Inbox personnel** pour chaque utilisateur
- **Pins (📌)** pour les favoris
- **Flags (🚩)** pour marquer à réviser
- **Watches (👁️)** pour suivre les changements
- **Notifications** intelligentes par discipline

#### 5.16.2 Types d'Items dans l'Inbox

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           INBOX ITEM TYPES                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  📌 PIN (Favoris)                                                               │
│  • Assets fréquemment consultés                                                  │
│  • Accès rapide depuis l'inbox                                                   │
│  • Pas de notification automatique                                               │
│                                                                                  │
│  🚩 FLAG (À réviser)                                                            │
│  • Asset marqué pour révision                                                    │
│  • Avec raison: "Vérifier sizing câble"                                         │
│  • Avec priorité: High, Medium, Low                                             │
│  • Peut être assigné à soi ou autre                                             │
│                                                                                  │
│  👁️ WATCH (Surveillance)                                                        │
│  • Surveille un asset pour changements                                           │
│  • Surveille une propriété spécifique (ex: power)                               │
│  • Surveille un groupe (ex: tous les moteurs ROOM-112)                          │
│  • Génère notifications quand changement détecté                                 │
│                                                                                  │
│  🔔 NOTIFICATION (Auto-générée)                                                 │
│  • Changement sur asset surveillé                                                │
│  • Mention dans un commentaire                                                   │
│  • Rule a modifié un asset important                                            │
│  • Révision requise par changement upstream                                      │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

#### 5.16.3 Database Schema - User Inbox

```sql
-- Pins, Flags, Watches
CREATE TABLE user_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Ownership
    user_id UUID NOT NULL REFERENCES users(id),
    project_id UUID NOT NULL REFERENCES projects(id),

    -- Type
    item_type VARCHAR(20) NOT NULL,  -- PIN, FLAG, WATCH

    -- Target
    target_type VARCHAR(20) NOT NULL,  -- ASSET, CABLE, RULE, PACKAGE
    target_id UUID NOT NULL,
    target_tag VARCHAR(100),           -- Denormalized for display

    -- For FLAG: additional info
    flag_reason TEXT,
    flag_priority VARCHAR(10),         -- HIGH, MEDIUM, LOW
    flag_assigned_to UUID REFERENCES users(id),
    flag_due_date DATE,
    flag_status VARCHAR(20) DEFAULT 'OPEN',  -- OPEN, IN_PROGRESS, RESOLVED

    -- For WATCH: what to watch
    watch_properties TEXT[],           -- ['power', 'voltage'] or NULL for all
    watch_scope VARCHAR(20),           -- SELF, CHILDREN, RELATED

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT,

    INDEX ix_user_items_user (user_id, project_id),
    INDEX ix_user_items_target (target_type, target_id),
    INDEX ix_user_items_type (item_type)
);

-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Recipient
    user_id UUID NOT NULL REFERENCES users(id),
    project_id UUID NOT NULL REFERENCES projects(id),

    -- Type
    notification_type VARCHAR(50) NOT NULL,
    -- Types: ASSET_CHANGED, PROPERTY_CHANGED, MENTION, FLAG_ASSIGNED,
    --        REVIEW_REQUIRED, RULE_AFFECTED, COMMENT_ADDED

    -- Source
    source_type VARCHAR(20),           -- WATCH, RULE, USER, SYSTEM
    source_event_id UUID REFERENCES workflow_events(id),

    -- Target
    target_type VARCHAR(20),
    target_id UUID,
    target_tag VARCHAR(100),

    -- Content
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    details JSONB DEFAULT '{}',        -- {property: "power", old: 15, new: 18.5}

    -- Priority
    priority VARCHAR(10) DEFAULT 'NORMAL',  -- LOW, NORMAL, HIGH, URGENT

    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    is_actioned BOOLEAN DEFAULT FALSE,
    actioned_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,            -- Auto-dismiss old notifications

    INDEX ix_notifications_user (user_id, is_read, created_at DESC),
    INDEX ix_notifications_target (target_type, target_id)
);

-- Discipline Review Triggers (quand Process change, Electrical doit réviser)
CREATE TABLE discipline_triggers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    project_id UUID NOT NULL REFERENCES projects(id),

    -- When this changes...
    source_discipline VARCHAR(50) NOT NULL,  -- PROCESS
    source_property VARCHAR(100) NOT NULL,   -- power, flow_rate

    -- ...notify this discipline
    target_discipline VARCHAR(50) NOT NULL,  -- ELECTRICAL
    notification_template TEXT NOT NULL,     -- "Power changed on {asset.tag}, verify cable sizing"

    -- Conditions (optional)
    condition_expression TEXT,               -- "new_value > old_value * 1.1"

    is_active BOOLEAN DEFAULT TRUE,

    UNIQUE(project_id, source_discipline, source_property, target_discipline)
);
```

#### 5.16.4 UI - Activity Bar Icon (Inbox)

```
┌────┐
│ 📊 │  Dashboard
├────┤
│ 📁 │  Explorer
├────┤
│ ⚙️  │  Rules
├────┤
│ 📥 │  Import
├────┤
│ 📦 │  Export
├────┤
│ 📜 │  Timeline
├────┤
│ 📬 │  Inbox (12)  ← NEW! Badge avec count
│ ●  │  └─ 3 unread notifications
├────┤
│ 🔧 │  Settings
└────┘
```

#### 5.16.5 UI - Inbox Panel

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ 🔷 SYNAPSE    Aurumax Mining / Gold Mine                    admin@aurumax.com  ⚙️│
├──┬───────────────────────────────────────────────────────────────────────────────┤
│📊│ ┌─ Inbox ─────────────────────────────────────────────────────────────────┐   │
│📁│ │                                                                          │   │
│⚙️│ │ ┌─ Tabs ──────────────────────────────────────────────────────────────┐ │   │
│📥│ │ │ [🔔 Notifications (3)] [📌 Pins (12)] [🚩 Flags (5)] [👁️ Watches (8)]│ │   │
│📦│ │ └──────────────────────────────────────────────────────────────────────┘ │   │
│📜│ │                                                                          │   │
│📬│ │ ═══════════════════════════════════════════════════════════════════════ │   │
│◀─│ │                                                                          │   │
│🔧│ │ 🔔 NOTIFICATIONS                                           [Mark all read]│   │
│  │ │                                                                          │   │
│  │ │ ┌─ Today ─────────────────────────────────────────────────────────────┐ │   │
│  │ │ │                                                                      │ │   │
│  │ │ │ ● 🔴 URGENT                                              10 min ago │ │   │
│  │ │ │   Power changed on P-210-001: 15kW → 22kW                          │ │   │
│  │ │ │   ⚡ Review required: Cable PWR-210-001 may need resizing          │ │   │
│  │ │ │   [View Asset] [Open Cable] [Dismiss]                               │ │   │
│  │ │ │                                                                      │ │   │
│  │ │ │ ● 🟡 HIGH                                                  2 hrs ago │ │   │
│  │ │ │   MTR-221-001 (SAG Mill Motor) - voltage changed                    │ │   │
│  │ │ │   Triggered by: Rule "Update Motor Specs"                           │ │   │
│  │ │ │   [View Asset] [View History] [Dismiss]                             │ │   │
│  │ │ │                                                                      │ │   │
│  │ │ │ ○ 🔵 NORMAL                                                5 hrs ago │ │   │
│  │ │ │   @admin mentioned you in comment on TK-231-001                     │ │   │
│  │ │ │   "Can you verify the level transmitter range?"                     │ │   │
│  │ │ │   [View Comment] [Reply] [Dismiss]                                  │ │   │
│  │ │ │                                                                      │ │   │
│  │ │ └──────────────────────────────────────────────────────────────────────┘ │   │
│  │ │                                                                          │   │
│  │ │ ┌─ Earlier ───────────────────────────────────────────────────────────┐ │   │
│  │ │ │ ○ Import completed: 100 instruments added           Yesterday 14:32 │ │   │
│  │ │ │ ○ Flag resolved: Cable sizing verified              Yesterday 10:15 │ │   │
│  │ │ └──────────────────────────────────────────────────────────────────────┘ │   │
│  │ │                                                                          │   │
│  │ └──────────────────────────────────────────────────────────────────────────┘   │
├──┴───────────────────────────────────────────────────────────────────────────────┤
│ 3 unread │ 5 flags open │ 8 watches active │ v0.2.2 │ ● Online                   │
└──────────────────────────────────────────────────────────────────────────────────┘
```

#### 5.16.6 UI - Pins Tab

```
┌─ 📌 My Pins (12) ───────────────────────────────────────────────────────────────┐
│                                                                                  │
│ Quick access to your frequently used assets                    [+ Add Current]  │
│                                                                                  │
│ ┌────────────────────────────────────────────────────────────────────────────┐  │
│ │ 📌 │ Tag          │ Type     │ Description              │ Last Viewed     │  │
│ ├────┼──────────────┼──────────┼──────────────────────────┼─────────────────┤  │
│ │ ★  │ ML-221-001   │ MILL     │ SAG Mill 28'x14'        │ 5 min ago       │  │
│ │ ★  │ ML-222-001   │ MILL     │ Ball Mill 22'x36'       │ 1 hour ago      │  │
│ │ ★  │ TK-231-001   │ TANK     │ CIL Tank #1             │ 2 hours ago     │  │
│ │ ★  │ EW-242-001   │ ELECTROWIN│ Electrowinning Cells   │ Yesterday       │  │
│ │ ★  │ MCC-130-001  │ MCC      │ Mill MCC #1             │ Yesterday       │  │
│ │    │ ...          │          │                          │                 │  │
│ └────┴──────────────┴──────────┴──────────────────────────┴─────────────────┘  │
│                                                                                  │
│ Organize: [By Type ▼] [By Recent ▼]                              [Manage Pins]  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

#### 5.16.7 UI - Flags Tab (Review Queue)

```
┌─ 🚩 Flags (5 Open) ─────────────────────────────────────────────────────────────┐
│                                                                                  │
│ Items requiring your attention                                      [+ New Flag]│
│                                                                                  │
│ Filter: [All ▼] [My Flags ▼] [Assigned to Me ▼]   Status: [Open ▼]             │
│                                                                                  │
│ ┌────────────────────────────────────────────────────────────────────────────┐  │
│ │                                                                            │  │
│ │ 🚩 🔴 HIGH - PWR-210-042                                        Due: Today │  │
│ │    Cable may be undersized after power increase                            │  │
│ │    Asset: PWR-210-042 (Power Cable)                                        │  │
│ │    Created by: System (auto) │ Assigned to: You                            │  │
│ │    [Open Asset] [Resolve] [Reassign] [Snooze]                              │  │
│ │                                                                            │  │
│ │ ─────────────────────────────────────────────────────────────────────────  │  │
│ │                                                                            │  │
│ │ 🚩 🟡 MEDIUM - MTR-231-003                                   Due: Tomorrow │  │
│ │    Verify motor efficiency rating                                          │  │
│ │    Note: "Client requested 95%+ efficiency for new specs"                  │  │
│ │    Created by: @john.doe │ Assigned to: You                                │  │
│ │    [Open Asset] [Resolve] [Reassign] [Snooze]                              │  │
│ │                                                                            │  │
│ │ ─────────────────────────────────────────────────────────────────────────  │  │
│ │                                                                            │  │
│ │ 🚩 🔵 LOW - TK-231-004                                       Due: Next Week│  │
│ │    Review tank capacity with process team                                  │  │
│ │    Created by: You │ Assigned to: You                                      │  │
│ │    [Open Asset] [Resolve] [Reassign] [Snooze]                              │  │
│ │                                                                            │  │
│ └────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│ Resolved this week: 12                                     [View Resolved →]    │
└──────────────────────────────────────────────────────────────────────────────────┘
```

#### 5.16.8 UI - Watches Tab

```
┌─ 👁️ Watches (8 Active) ─────────────────────────────────────────────────────────┐
│                                                                                  │
│ Get notified when these items change                               [+ New Watch]│
│                                                                                  │
│ ┌────────────────────────────────────────────────────────────────────────────┐  │
│ │                                                                            │  │
│ │ 👁️ Watching: P-210-001 (Pump)                                              │  │
│ │    Properties: power, flow_rate                                            │  │
│ │    Scope: Asset + Children                                                 │  │
│ │    Last change: 2 hours ago (power: 15kW → 22kW)                          │  │
│ │    [Edit] [Pause] [Remove]                                                 │  │
│ │                                                                            │  │
│ │ ─────────────────────────────────────────────────────────────────────────  │  │
│ │                                                                            │  │
│ │ 👁️ Watching: All Motors in ROOM-124                                        │  │
│ │    Properties: All changes                                                 │  │
│ │    Scope: 12 assets (MOTOR where location = ROOM-124)                     │  │
│ │    Last change: Yesterday                                                  │  │
│ │    [Edit] [Pause] [Remove]                                                 │  │
│ │                                                                            │  │
│ │ ─────────────────────────────────────────────────────────────────────────  │  │
│ │                                                                            │  │
│ │ 👁️ Watching: Electrical properties on FBS-230 (Leaching)                   │  │
│ │    Properties: power, voltage, fla                                         │  │
│ │    Scope: All assets in FBS 230-239                                       │  │
│ │    Last change: 3 days ago                                                 │  │
│ │    [Edit] [Pause] [Remove]                                                 │  │
│ │                                                                            │  │
│ └────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│ ⚡ Pro tip: Watch electrical properties to catch process changes!               │
└──────────────────────────────────────────────────────────────────────────────────┘
```

#### 5.16.9 UI - Create Watch Dialog

```
┌─────────────────────────────────────────────────────────────────┐
│ 👁️ Create New Watch                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ What to watch:                                                   │
│ ○ Single asset: [MTR-210-001 ▼]                                 │
│ ○ Multiple assets by filter:                                     │
│   Type: [MOTOR ▼]  Location: [ROOM-124 ▼]  FBS: [All ▼]        │
│ ● Group: [All Electrical in Leaching (FBS 230) ▼]               │
│                                                                  │
│ Properties to watch:                                             │
│ ○ All properties                                                 │
│ ● Specific properties:                                           │
│   ☑ power                                                        │
│   ☑ voltage                                                      │
│   ☑ fla                                                          │
│   ☐ efficiency                                                   │
│   ☐ cable_size                                                   │
│                                                                  │
│ Include scope:                                                   │
│ ☑ Asset itself                                                   │
│ ☑ Children (motors, cables, etc.)                               │
│ ☐ Related cables                                                 │
│                                                                  │
│ Notification settings:                                           │
│ ● Immediate (real-time)                                          │
│ ○ Daily digest                                                   │
│ ○ Weekly summary                                                 │
│                                                                  │
│ [Cancel]                                        [Create Watch]   │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.16.10 UI - Asset Context Menu (Pin/Flag/Watch)

```
Right-click on any asset:

┌─────────────────────────────────────────┐
│ MTR-210-001 (MOTOR)                     │
├─────────────────────────────────────────┤
│ 📋 Copy Tag                             │
│ ─────────────────────────────────────── │
│ 📌 Pin to Inbox                         │  ← Quick pin
│ 🚩 Flag for Review...              →    │
│    ├─ 🔴 High Priority                  │
│    ├─ 🟡 Medium Priority                │
│    ├─ 🔵 Low Priority                   │
│    └─ Custom Flag...                    │
│ 👁️ Watch for Changes...           →    │
│    ├─ Watch all changes                 │
│    ├─ Watch electrical properties       │
│    ├─ Watch with children               │
│    └─ Custom Watch...                   │
│ ─────────────────────────────────────── │
│ 🔍 Filter by Type                       │
│ 👁️ Show Children                        │
│ ...                                     │
└─────────────────────────────────────────┘
```

#### 5.16.11 Discipline Triggers - Auto Notifications

**Scénario: Process change → Electrical review**

```yaml
# Configuration des triggers inter-disciplines
discipline_triggers:
  - name: "Power Change → Cable Review"
    source:
      discipline: PROCESS
      property: power
      condition: "new_value != old_value"
    target:
      discipline: ELECTRICAL
      notification:
        priority: HIGH
        title: "Power changed on {asset.tag}"
        message: |
          Power changed from {old_value} kW to {new_value} kW.
          Please verify:
          - Cable sizing (current: {cable.size})
          - Protection settings
          - Transformer capacity
        auto_flag: true
        flag_priority: HIGH

  - name: "Flow Change → Instrument Review"
    source:
      discipline: PROCESS
      property: flow_rate
      condition: "abs(new_value - old_value) / old_value > 0.2"  # >20% change
    target:
      discipline: INSTRUMENTATION
      notification:
        priority: MEDIUM
        title: "Flow rate changed significantly on {asset.tag}"
        message: "Verify instrument range for {related.flow_transmitter.tag}"

  - name: "Motor Added → Cable Required"
    source:
      discipline: ELECTRICAL
      event: ASSET_CREATED
      condition: "asset.type == 'MOTOR'"
    target:
      discipline: ELECTRICAL
      notification:
        priority: NORMAL
        title: "New motor {asset.tag} needs cables"
        auto_flag: true
        flag_reason: "Generate power and control cables"
```

#### 5.16.12 Notification Service (Backend)

```python
# app/services/notification_service.py

class NotificationService:
    """Service pour gérer les notifications utilisateur"""

    async def notify_asset_change(
        self,
        event: WorkflowEvent,
        asset: Asset,
        changes: list[PropertyChange]
    ):
        """Notifie les utilisateurs qui surveillent cet asset"""

        # 1. Trouver les watches qui matchent
        watches = await self.find_matching_watches(asset, changes)

        for watch in watches:
            # 2. Vérifier si les propriétés changées sont surveillées
            if not self.properties_match(watch.watch_properties, changes):
                continue

            # 3. Créer la notification
            notification = await self.create_notification(
                user_id=watch.user_id,
                notification_type="PROPERTY_CHANGED",
                target_type="ASSET",
                target_id=asset.id,
                target_tag=asset.tag,
                title=f"Changes detected on {asset.tag}",
                message=self.format_changes_message(changes),
                details={
                    "changes": [
                        {"property": c.property_name, "old": c.old_value, "new": c.new_value}
                        for c in changes
                    ]
                },
                priority=self.calculate_priority(changes),
                source_event_id=event.id
            )

            # 4. Envoyer notification real-time (WebSocket)
            await self.websocket_manager.send_notification(
                user_id=watch.user_id,
                notification=notification
            )

    async def check_discipline_triggers(
        self,
        asset: Asset,
        changes: list[PropertyChange]
    ):
        """Vérifie et exécute les triggers inter-disciplines"""

        triggers = await self.get_discipline_triggers(asset.project_id)

        for change in changes:
            for trigger in triggers:
                if (trigger.source_property == change.property_name and
                    trigger.source_discipline == asset.discipline):

                    # Évaluer la condition
                    if self.evaluate_condition(trigger.condition_expression, change):

                        # Trouver les users de la discipline cible
                        target_users = await self.get_users_by_discipline(
                            project_id=asset.project_id,
                            discipline=trigger.target_discipline
                        )

                        for user in target_users:
                            # Créer notification
                            await self.create_notification(
                                user_id=user.id,
                                notification_type="REVIEW_REQUIRED",
                                title=trigger.notification_template.format(asset=asset),
                                message=trigger.notification_message.format(
                                    asset=asset,
                                    old_value=change.old_value,
                                    new_value=change.new_value
                                ),
                                priority=trigger.notification_priority,
                                auto_flag=trigger.auto_flag
                            )

                            # Auto-créer un flag si configuré
                            if trigger.auto_flag:
                                await self.create_auto_flag(
                                    user_id=user.id,
                                    asset=asset,
                                    reason=trigger.flag_reason,
                                    priority=trigger.flag_priority
                                )
```

#### 5.16.13 Frontend Store - Inbox

```typescript
// stores/useInboxStore.ts

interface Notification {
  id: string;
  type: 'ASSET_CHANGED' | 'PROPERTY_CHANGED' | 'MENTION' | 'FLAG_ASSIGNED' | 'REVIEW_REQUIRED';
  title: string;
  message: string;
  targetType: string;
  targetId: string;
  targetTag: string;
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'URGENT';
  isRead: boolean;
  createdAt: string;
  details?: Record<string, any>;
}

interface Pin {
  id: string;
  targetType: string;
  targetId: string;
  targetTag: string;
  createdAt: string;
}

interface Flag {
  id: string;
  targetType: string;
  targetId: string;
  targetTag: string;
  reason: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED';
  assignedTo?: string;
  dueDate?: string;
  createdAt: string;
}

interface Watch {
  id: string;
  targetType: string;
  targetId?: string;
  targetFilter?: Record<string, any>;
  watchProperties: string[] | null;  // null = all
  scope: 'SELF' | 'CHILDREN' | 'RELATED';
  isActive: boolean;
}

interface InboxState {
  notifications: Notification[];
  pins: Pin[];
  flags: Flag[];
  watches: Watch[];

  unreadCount: number;
  openFlagsCount: number;

  // Actions
  fetchInbox: () => Promise<void>;
  markAsRead: (notificationId: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  dismissNotification: (id: string) => Promise<void>;

  addPin: (targetType: string, targetId: string) => Promise<void>;
  removePin: (pinId: string) => Promise<void>;

  createFlag: (data: CreateFlagDTO) => Promise<Flag>;
  resolveFlag: (flagId: string) => Promise<void>;
  reassignFlag: (flagId: string, userId: string) => Promise<void>;

  createWatch: (data: CreateWatchDTO) => Promise<Watch>;
  pauseWatch: (watchId: string) => Promise<void>;
  removeWatch: (watchId: string) => Promise<void>;

  // WebSocket
  subscribeToNotifications: () => void;
  handleNewNotification: (notification: Notification) => void;
}
```

#### 5.16.14 Demo Scenario - Cross-Discipline Notification

```
SCÉNARIO:

1. [Process Engineer] Modifie la puissance d'une pompe
   → P-210-001.power: 15kW → 22kW
   → Raison: "Increased throughput requirement"

2. [System] Détecte le changement via discipline trigger
   → Source: PROCESS, property: power
   → Target: ELECTRICAL

3. [Electrical Engineer] Reçoit notification
   ┌────────────────────────────────────────────────┐
   │ 🔔 🔴 URGENT                         Just now  │
   │ Power changed on P-210-001: 15kW → 22kW       │
   │ ⚡ Review required: Verify cable sizing        │
   │ Cable PWR-210-001 may need upgrade            │
   │ [View Asset] [Open Cable] [Acknowledge]       │
   └────────────────────────────────────────────────┘

4. [Electrical Engineer] Click "Open Cable"
   → Voit PWR-210-001 (current: 4mm²)
   → Flag auto-créé: "Verify cable sizing"

5. [Electrical Engineer] Résout le flag
   → Update cable: 4mm² → 6mm²
   → Marque flag "Resolved"
   → Ajoute note: "Resized per new motor load"

6. [System] Log l'événement complet
   → Timeline montre: Process change → Notification → Review → Resolution
```

---

## 6. PLAN D'IMPLÉMENTATION

### Sprint Aujourd'hui (Whiteboard)
- [x] Design système de logs
- [x] Design UI Architecture
- [x] Design Data Grid (AG Grid)
- [x] Design Client/Project Multi-Tenancy
- [x] Design Demo Data (Gold Mine)
- [x] Design Rule Engine
- [x] Design CSV Import
- [x] Design Package Export
- [x] Design User Inbox & Notifications
- [ ] Décisions architecture finales
- [ ] Update documentation

### Sprint Semaine Prochaine (Implementation)
| Jour | Focus | Livrables |
|------|-------|-----------|
| Lun | DB Schema | workflow_events, rules, packages tables |
| Mar | Log Service | WorkflowLogger class + WebSocket |
| Mer | Rule Engine Core | Condition evaluator + 3 actions |
| Jeu | CSV Import | Pipeline complet avec logging |
| Ven | Integration | Tests manuels end-to-end |

### Sprint Semaine +2 (Polish)
| Jour | Focus | Livrables |
|------|-------|-----------|
| Lun | Package Export | Templates IN-P040, CA-P040 |
| Mar | Timeline View | Frontend component |
| Mer | Asset History | Diff view component |
| Jeu | Tests | Coverage 70%+ |
| Ven | Demo Prep | Script + rehearsal |

---

## 7. RISQUES & MITIGATIONS

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Rule Engine trop complexe | MEDIUM | HIGH | MVP: 3 actions simples, JSON config |
| Logs trop volumineux | LOW | MEDIUM | Retention policy, pagination |
| WebSocket instable | LOW | HIGH | Fallback polling, reconnect auto |
| Templates Excel bugs | MEDIUM | MEDIUM | Tests manuels exhaustifs |
| Performance 1000+ assets | LOW | LOW | Pagination, lazy loading |

---

**Document créé:** 2025-11-28
**Prochaine révision:** Après implémentation Sprint 1
