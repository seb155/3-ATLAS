# Système d'Agents AI - AXIOM

> **Status:** En planification
> **Dernière mise à jour:** 2025-11-28
> **Prochaine session:** Implémenter les agents de base

Ce document décrit l'architecture du système d'agents AI pour le développement collaboratif de la plateforme AXIOM.

---

## Vision

Créer un système d'agents **générique et réutilisable** pour tous projets (actuels et futurs), avec **ATLAS** comme chef d'orchestre intelligent qui s'adapte au style de l'utilisateur.

---

## Structure Monorepo AXIOM

```text
AXIOM/                              # 🏠 Monorepo racine
│
├── apps/                           # 📱 Applications
│   ├── synapse/                    # MBSE Platform (MVP prioritaire)
│   │   ├── backend/                # FastAPI + SQLAlchemy
│   │   └── frontend/               # React 19 + TypeScript
│   │
│   ├── nexus/                      # Knowledge Graph + Notes
│   │   └── frontend/               # React 19 + TypeScript
│   │
│   ├── prism/                      # Enterprise Dashboard
│   │   └── frontend/               # React 19 + TypeScript
│   │
│   └── atlas/                      # AI Collaboration (Planning)
│       └── (à créer)
│
├── forge/                          # ⚙️ Infrastructure partagée
│   ├── docker-compose.yml          # PostgreSQL, Redis, Grafana, Loki
│   ├── config/                     # Configurations partagées
│   └── scripts/                    # Scripts d'infra
│
├── docs/                           # 📖 Documentation (Docsify)
├── .claude/                        # 🤖 Agents AI
├── .dev/                           # 📊 Tracking développement
└── CLAUDE.md                       # Instructions pour Claude Code
```

### Applications et Stacks

| App | Purpose | Stack | Port | Status |
|-----|---------|-------|------|--------|
| **SYNAPSE** | MBSE Platform | FastAPI + React 19 | 4000 | MVP Dec 2025 |
| **NEXUS** | Knowledge Graph | React 19 (backend planifié) | 5173 | Phase 1.5 |
| **PRISM** | Enterprise Dashboard | React 19 | 5174 | Development |
| **ATLAS** | AI Collaboration | TBD | 5175 | Planning |
| **FORGE** | Shared Infrastructure | Docker (PostgreSQL, Redis, Grafana) | - | Active |

### Conventions Partagées (Cross-App)

**Frontend (Toutes les apps React):**

- Framework: React 19 + TypeScript (strict mode)
- State: Zustand avec persist middleware
- UI: Shadcn/ui + Radix UI + Tailwind CSS
- Theme: VSCode Dark (#1e1e1e, #333333, #007acc)
- Testing: Vitest + React Testing Library (>70% coverage)

**Backend (SYNAPSE, futurs backends):**

- Framework: FastAPI + Python 3.10+
- Database: PostgreSQL 15 via SQLAlchemy 2.0+
- Auth: JWT + OAuth2
- Pattern: Multi-tenancy (project_id filtering)
- Testing: pytest (>70% coverage)

**Infrastructure (FORGE):**

- Container: Docker Compose
- Database: `forge-postgres:5433`
- Cache: `forge-redis:6379`
- Logging: Loki + Grafana + Promtail

---

## Détection d'Application

Les agents détectent automatiquement l'application courante:

```text
Détection basée sur:
1. Working directory (cwd)
2. Fichiers de contexte (.claude/context/current-app.md)
3. Commande explicite (/app synapse)

Exemples:
- cwd = "D:\Projects\AXIOM\apps\synapse\backend" → App: SYNAPSE, Layer: Backend
- cwd = "D:\Projects\AXIOM\apps\nexus\frontend"  → App: NEXUS, Layer: Frontend
- cwd = "D:\Projects\AXIOM\forge"                → App: FORGE, Layer: Infrastructure
- cwd = "D:\Projects\AXIOM"                      → App: Global (monorepo root)
```

---

## Détection de l'Environnement

Les agents comprennent automatiquement l'environnement d'exécution:

### Plateforme

```text
Détection automatique:
- OS: Windows (laptop dev) vs Linux (server prod)
- Shell: PowerShell vs Bash
- Paths: D:\Projects\ vs /home/user/projects/

Adaptation des commandes:
- Windows: .\dev.ps1, docker compose, npm run
- Linux: ./dev.sh, docker-compose, npm run
```

### Mode Développement vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| **Docker Compose** | `docker-compose.dev.yml` | `docker-compose.yml` |
| **Hot Reload** | Activé (volumes montés) | Désactivé (images built) |
| **Variables** | `.env.development` | `.env.production` |
| **Logs** | Debug, verbose | Info, structured |
| **Database** | `forge-postgres:5433` (local) | `db.axiom.com:5432` (remote) |
| **SSL** | Non (`http://localhost`) | Oui (`https://axiom.com`) |

### Architecture Docker (FORGE)

```text
┌─────────────────────────────────────────────────────────────┐
│                    FORGE Infrastructure                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Traefik   │    │  PostgreSQL │    │    Redis    │     │
│  │   (Proxy)   │    │  (forge-pg) │    │ (forge-red) │     │
│  │   :80/:443  │    │    :5433    │    │    :6379    │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                   │            │
│         │    ┌─────────────┴───────────────────┤            │
│         │    │         forge-network           │            │
│         │    └─────────────┬───────────────────┘            │
│         ▼                  ▼                                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   SYNAPSE   │    │    NEXUS    │    │    PRISM    │     │
│  │   Backend   │    │  Frontend   │    │  Frontend   │     │
│  │    :8000    │    │    :5173    │    │    :5174    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Grafana   │    │    Loki     │    │  Promtail   │     │
│  │    :3000    │    │    :3100    │    │  (logs)     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Ressources Partagées

| Ressource | Service | Accès Interne | Accès Externe |
|-----------|---------|---------------|---------------|
| **Database** | `forge-postgres` | `postgres://forge-postgres:5432` | `localhost:5433` |
| **Cache** | `forge-redis` | `redis://forge-redis:6379` | `localhost:6379` |
| **Logs** | `forge-loki` | `http://forge-loki:3100` | `localhost:3100` |
| **Monitoring** | `forge-grafana` | `http://forge-grafana:3000` | `localhost:3000` |
| **Proxy** | `forge-traefik` | - | `:80`, `:443` |

### Fichier de Contexte Environnement

```markdown
# .claude/context/environment.md (auto-généré)

## Platform
- OS: Windows 11
- Shell: PowerShell 7
- Docker: Docker Desktop 4.x

## Mode
- Environment: development
- Docker Compose: docker-compose.dev.yml

## Services Running
- forge-postgres: healthy (port 5433)
- forge-redis: healthy (port 6379)
- synapse-backend: running (port 8000)
- synapse-frontend: running (port 4000)

## Network
- forge-network: bridge
- All services connected

## Volumes
- postgres-data: /var/lib/postgresql/data
- redis-data: /data
```

---

## Architecture Hiérarchique

```text
┌─────────────────────────────────────────────────────────────┐
│                        👤 UTILISATEUR                        │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     🧠 ATLAS (Orchestrator)                  │
│  • Communication principale avec l'utilisateur              │
│  • S'adapte au style de communication                       │
│  • Roadmap status & brainstorm sessions                     │
│  • Dispatch les tâches aux agents intermédiaires            │
│  • Exécute commandes directes si simples                    │
└─────────────────────────────┬───────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  📋 PLANNER     │ │  🔧 BUILDER     │ │  ✅ VALIDATOR   │
│  (Intermediate) │ │  (Junior)       │ │  (Junior)       │
│                 │ │                 │ │                 │
│ • Break down    │ │ • Backend code  │ │ • Run tests     │
│ • Plan tasks    │ │ • Frontend code │ │ • Quality check │
│ • Estimate      │ │ • Docker/DevOps │ │ • Build verify  │
│ • Dependencies  │ │ • Documentation │ │ • Report issues │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## Agents de Base (4)

### 1. 🧠 ATLAS - Chef d'Orchestre

**Rôle:** Interface principale avec l'utilisateur

**Responsabilités:**

- **Communication adaptative** - Apprend et s'adapte au style de l'utilisateur
- **Session management** - Démarre sessions, charge contexte projet
- **Roadmap awareness** - Montre l'état du roadmap, propose priorités
- **Brainstorm sessions** - Propose whiteboard/clarification pour points flous
- **Task dispatch** - Délègue aux agents PLANNER, BUILDER, VALIDATOR
- **Direct execution** - Exécute commandes simples directement

**Comportement:**

- Proactif mais respectueux des décisions utilisateur
- Propose options avec recommandations
- Apprend les préférences (horaires, style code, priorités)
- Maintient le contexte entre sessions

---

### 2. 📋 PLANNER - Architecte de Tâches

**Rôle:** Décompose et planifie le travail

**Responsabilités:**

- **Task breakdown** - Décompose features complexes en sous-tâches
- **Implementation planning** - Crée plans d'implémentation détaillés
- **Dependency analysis** - Identifie dépendances et ordre d'exécution
- **Estimation** - Estime effort/complexité
- **Architecture decisions** - Propose patterns et structures

**Invoqué par:** ATLAS quand tâche complexe (>3 étapes)

---

### 3. 🔧 BUILDER - Exécuteur de Code

**Rôle:** Implémente le code

**Responsabilités:**

- **Backend** - FastAPI endpoints, SQLAlchemy models, migrations
- **Frontend** - React components, Zustand stores, Tailwind styling
- **DevOps** - Docker services, configurations, scripts
- **Documentation** - README, docs, commentaires

**Patterns inclus:**

- Multi-tenancy (project_id filtering)
- JWT authentication
- Tests >70% coverage
- Conventional commits

**Invoqué par:** ATLAS ou PLANNER après planification

---

### 4. ✅ VALIDATOR - Contrôle Qualité

**Rôle:** Valide et teste le travail

**Responsabilités:**

- **Build verification** - Vérifie que le build passe
- **Test execution** - Lance pytest/vitest
- **Quality checks** - Lint, type-check, coverage
- **Docker health** - Vérifie containers healthy
- **Report** - Rapport clair (✅/⚠️/❌) avec actions

**Invoqué par:** ATLAS automatiquement après BUILDER, ou sur demande

---

## Structure des Fichiers

```text
.claude/
├── agents/
│   ├── atlas.md           # 🧠 Chef d'orchestre
│   ├── planner.md         # 📋 Planificateur
│   ├── builder.md         # 🔧 Constructeur
│   └── validator.md       # ✅ Validateur
│
├── context/               # Fichiers de contexte (template)
│   ├── project.md.template    # Template état projet
│   └── preferences.md         # Préférences utilisateur (auto-généré)
│
├── scripts/
│   └── statusline.ps1
│
└── settings.json
```

---

## Flux de Travail Typique

### Exemple: "Ajoute une feature de notifications"

```text
1. 👤 User: "Ajoute un système de notifications"

2. 🧠 ATLAS:
   - Analyse la demande
   - Vérifie le contexte projet
   - Propose: "Je vois 3 approches possibles..."
   - Demande confirmation

3. 👤 User: "Option 2, avec websockets"

4. 🧠 ATLAS → 📋 PLANNER:
   - "Planifie feature notifications websocket"

5. 📋 PLANNER retourne:
   - 5 sous-tâches identifiées
   - Backend: WebSocket endpoint + Redis pub/sub
   - Frontend: Hook + UI component
   - Tests: Unit + integration

6. 🧠 ATLAS → 🔧 BUILDER:
   - Exécute tâche 1: Backend WebSocket
   - Exécute tâche 2: Frontend hook
   - ...

7. 🧠 ATLAS → ✅ VALIDATOR:
   - Valide le build
   - Lance tests
   - Vérifie Docker

8. 🧠 ATLAS → 👤 User:
   - "Feature notifications implémentée ✅"
   - "Tests: 87% coverage"
   - "Prêt pour test manuel"
```

---

## Caractéristiques Génériques

### Adaptable à tout projet

- Détection auto du stack (FastAPI/Express, React/Vue, etc.)
- Patterns configurables via context files
- Fonctionne avec ou sans Docker
- Supporte mono-repo et multi-repo

### Fichiers de contexte standards

```markdown
# .claude/context/project.md (généré au premier run)

## Project: [Auto-detected]

## Stack: [Auto-detected]

## Structure: [Scanned]

## Conventions: [From CLAUDE.md or detected]
```

### Préférences utilisateur (apprises par ATLAS)

```markdown
# .claude/context/preferences.md (auto-généré)

## Communication Style

- Language: fr/en mix
- Detail level: medium
- Proactivity: high

## Work Patterns

- Prefers: incremental commits
- Testing: always before PR
- Documentation: minimal but clear
```

---

## Agents Spécialisés (À Définir)

### 📋 PLANNERS (Intermédiaires)

| Agent | Rôle | Invoqué quand |
|-------|------|---------------|
| `brainstorm-facilitator` | Sessions whiteboard, clarification de specs floues | Points d'architecture non clairs |
| `ux-designer` | Design UX/UI, wireframes, user flows | Nouvelles features UI |

### 🔧 BUILDERS (Juniors)

| Agent | Rôle | Invoqué quand |
|-------|------|---------------|
| `backend-builder` | FastAPI, SQLAlchemy, migrations, tests pytest | Code backend |
| `frontend-builder` | React, Zustand, Tailwind, tests vitest | Code frontend |
| `devops-builder` | Docker, configs, scripts | Infrastructure |
| `doc-writer` | README, docs/, guides utilisateur | Documentation publique |

### ✅ VALIDATORS (Juniors)

| Agent | Rôle | Invoqué quand |
|-------|------|---------------|
| `debugger` | Debug errors, analyse logs, propose fixes | Erreurs détectées |
| `qa-tester` | Lance tests, vérifie coverage, builds | Après code changes |
| `issue-reporter` | Rapporte bugs, crée issues formatées | Problèmes détectés |

### 📊 TRACKERS (Maintenance continue)

| Agent | Rôle | Invoqué quand |
|-------|------|---------------|
| `dev-tracker` | Maintient `.dev/` (journal, project-state, test-status) | Chaque session |
| `git-manager` | Branches, commits, versions, tags, releases GitHub | Commits/releases |

---

## Système de Partage d'Information

```text
┌─────────────────────────────────────────────────────────────────┐
│                    📁 FICHIERS PARTAGÉS (.md)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  .dev/                          .claude/                        │
│  ├── context/                   ├── agents/                     │
│  │   ├── project-state.md  ◄──────── Tous les agents lisent     │
│  │   └── current-task.md            et mettent à jour           │
│  ├── journal/                   │                               │
│  │   └── YYYY-MM-DD.md     ◄──────── dev-tracker maintient      │
│  ├── testing/                   │                               │
│  │   └── test-status.md    ◄──────── qa-tester met à jour       │
│  └── issues/                    │                               │
│      └── active-issues.md  ◄──────── issue-reporter crée        │
│                                 │                               │
│                                 ├── context/                    │
│                                 │   ├── preferences.md          │
│                                 │   └── session-history.md      │
│                                 │                               │
└─────────────────────────────────────────────────────────────────┘
```

### Flux d'Information

```text
1. ATLAS charge le contexte au début
   ├── Lit: project-state.md, test-status.md, journal récent
   └── Met à jour: session-history.md

2. Pendant le travail
   ├── dev-tracker: Met à jour journal en temps réel
   ├── qa-tester: Met à jour test-status.md
   ├── issue-reporter: Crée entries dans active-issues.md
   └── git-manager: Log commits/branches dans git-history.md

3. ATLAS synthétise pour l'utilisateur
   └── Remonte: Progrès, blockers, prochaines étapes
```

---

## Questions à Résoudre

1. **Granularité**: Faut-il séparer `backend-builder` et `frontend-builder` ou garder un seul `builder`?

2. **Brainstorm format**: Comment structurer les sessions whiteboard? (Mermaid diagrams? ASCII? Liste de questions?)

3. **Issue tracking**: Format des issues? (Titre, description, severity, assignee, status?)

4. **Git workflow**: Préfères-tu GitHub Flow (simple) ou Git Flow (release branches)?

5. **Préférences UX/UI**: L'agent `ux-designer` doit-il générer des mockups ou juste proposer des patterns?

---

## Choix des Modèles AI (Claude Code)

### Modèles Disponibles

| Modèle | Force | Coût | Latence | Usage Recommandé |
|--------|-------|------|---------|------------------|
| `opus` | Raisonnement complexe, créativité | $$$ | Lent | Orchestration, architecture, brainstorm |
| `sonnet` | Équilibré, polyvalent | $$ | Moyen | Code, planification, debug |
| `haiku` | Rapide, efficace | $ | Rapide | Tâches simples, répétitives, validation |

### Attribution des Modèles par Agent

**🧠 Orchestrateurs (Opus):**

| Agent | Modèle | Justification |
|-------|--------|---------------|
| `atlas` | **opus** | Chef d'orchestre, décisions stratégiques |
| `brainstorm-facilitator` | **opus** | Créativité, exploration de solutions |
| `system-architect` | **opus** | **BYPASS TOTAL** - Gère et met à jour le système d'agents AI lui-même |

**🔧 Builders Complexes (Opus):**

| Agent | Modèle | Justification |
|-------|--------|---------------|
| `architect-builder` | **opus** | Refactoring majeur, nouvelles architectures complexes |
| `integration-builder` | **opus** | Intégrations cross-app, systèmes distribués |

**📋 Planificateurs (Sonnet):**

| Agent | Modèle | Justification |
|-------|--------|---------------|
| `planner` | **sonnet** | Décomposition de tâches, plans |
| `ux-designer` | **sonnet** | Design patterns, wireframes |
| `debugger` | **sonnet** | Analyse d'erreurs, raisonnement |

**🔧 Builders (Sonnet/Haiku):**

| Agent | Modèle | Justification |
|-------|--------|---------------|
| `backend-builder` | **sonnet** | Code complexe, patterns multi-tenancy |
| `frontend-builder` | **sonnet** | Components React, state management |
| `devops-builder` | **haiku** | Docker patterns, configurations |
| `doc-writer` | **haiku** | Documentation structurée |

**✅ Validators (Haiku):**

| Agent | Modèle | Justification |
|-------|--------|---------------|
| `qa-tester` | **haiku** | Exécution de tests, rapports |
| `issue-reporter` | **haiku** | Formatage d'issues, templates |

**📊 Trackers (Haiku):**

| Agent | Modèle | Justification |
|-------|--------|---------------|
| `dev-tracker` | **haiku** | Mise à jour de fichiers .md |
| `git-manager` | **haiku** | Commandes git, workflows |

---

## Slash Commands

| Commande | Description | Agent(s) Invoqué(s) |
|----------|-------------|---------------------|
| `/new-session` | Démarre une session, charge contexte | atlas |
| `/status` | Affiche l'état du projet, tests, roadmap | atlas → dev-tracker |
| `/app [name]` | Change le contexte d'application | atlas |
| `/brainstorm [topic]` | Lance une session whiteboard | atlas → brainstorm |
| `/implement [feature]` | Planifie et implémente une feature | atlas → planner → builder |
| `/architect [task]` | Tâche complexe (refactoring, nouvelle archi) | architect-builder (opus) |
| `/integrate [systems]` | Intégration cross-app ou système distribué | integration-builder (opus) |
| `/test` | Lance tous les tests et rapporte | atlas → qa-tester |
| `/debug [error]` | Analyse et propose fix | atlas → debugger |
| `/commit [message]` | Commit avec conventional commits | git-manager |
| `/release [version]` | Crée une release avec changelog | git-manager |
| `/docs [topic]` | Met à jour la documentation | doc-writer |
| `/system` | **BYPASS** - Accès direct au system-architect | system-architect (opus) |

### Commande `/app` - Gestion Multi-App

```text
/app                    # Affiche l'app courante et liste toutes les apps
/app synapse            # Switch vers SYNAPSE (backend + frontend)
/app synapse backend    # Switch vers SYNAPSE backend uniquement
/app nexus              # Switch vers NEXUS
/app forge              # Switch vers FORGE (infrastructure)
/app global             # Mode monorepo (cross-app)
```

---

## Agent Spécial: SYSTEM-ARCHITECT (Opus)

### Mission

Agent **autonome** avec **bypass total** de la hiérarchie. Il gère, maintient et améliore le système d'agents AI lui-même.

### Caractéristiques

- **Modèle**: Opus (raisonnement complexe)
- **Accès**: Direct à l'utilisateur (bypass ATLAS)
- **Scope**: Tous les fichiers `.claude/`, documentation agents, workflows

### Responsabilités

- **Auto-maintenance**: Crée, modifie, supprime des agents
- **Évolution**: Propose des améliorations au système
- **Documentation**: Met à jour cette documentation automatiquement
- **Diagnostic**: Analyse les performances des agents
- **Questions directes**: Pose des questions à l'utilisateur sans passer par ATLAS

### Invocation

- Automatique quand modifications au système d'agents détectées
- Manuelle via `/system` command
- Proactive quand problèmes de workflow détectés

### Exemple

```text
👤 User: "Les agents prennent trop de temps sur les tâches simples"

🏗️ SYSTEM-ARCHITECT (direct, bypass ATLAS):
"Je vois que le debugger utilise Sonnet pour toutes les tâches.
Je propose de créer un debugger-quick (Haiku) pour les erreurs simples.

Options:
1. Créer debugger-quick + modifier le routing
2. Ajouter un mode 'quick' au debugger existant
3. Autre suggestion?

Quelle option préfères-tu?"
```

---

## Structure Complète .claude/

```text
.claude/
│
├── agents/                          # Définitions des agents
│   ├── orchestrators/
│   │   ├── atlas.md                 # 🧠 opus - Chef d'orchestre
│   │   ├── brainstorm.md            # 🧠 opus - Sessions créatives
│   │   └── system-architect.md      # 🏗️ opus - BYPASS - Gestion du système AI
│   │
│   ├── builders-opus/               # 🔧 Builders complexes (opus)
│   │   ├── architect-builder.md     # Refactoring majeur
│   │   └── integration-builder.md   # Cross-app, systèmes distribués
│   │
│   ├── planners/
│   │   ├── planner.md               # 📋 sonnet - Décomposition
│   │   ├── ux-designer.md           # 📋 sonnet - Design UX/UI
│   │   └── debugger.md              # 📋 sonnet - Analyse erreurs
│   │
│   ├── builders/
│   │   ├── backend.md               # 🔧 sonnet - FastAPI/Python
│   │   ├── frontend.md              # 🔧 sonnet - React/TypeScript
│   │   ├── devops.md                # 🔧 haiku - Docker/Infra
│   │   └── docs.md                  # 🔧 haiku - Documentation
│   │
│   ├── validators/
│   │   ├── qa-tester.md             # ✅ haiku - Tests
│   │   └── issue-reporter.md        # ✅ haiku - Rapports bugs
│   │
│   └── trackers/
│       ├── dev-tracker.md           # 📊 haiku - Suivi .dev/
│       └── git-manager.md           # 📊 haiku - Git/GitHub
│
├── skills/                          # Templates réutilisables
│   ├── api-endpoint/
│   ├── react-component/
│   ├── docker-service/
│   └── README.md
│
├── commands/                        # Slash commands
│   ├── new-session.md
│   ├── status.md
│   ├── app.md
│   ├── brainstorm.md
│   ├── implement.md
│   ├── test.md
│   ├── commit.md
│   └── release.md
│
├── context/                         # Contexte partagé
│   ├── project.md
│   ├── preferences.md
│   └── session-history.md
│
└── settings.json
```

---

## Workflows Automatiques

### 1. Session Start Workflow

```yaml
trigger: /new-session ou début de conversation
steps:
  1. atlas: Charge contexte projet
  2. dev-tracker: Lit journal récent, project-state
  3. qa-tester: Vérifie état des tests
  4. atlas: Synthétise et propose priorités
```

### 2. Feature Implementation Workflow

```yaml
trigger: /implement [feature]
steps:
  1. atlas: Analyse la demande
  2. brainstorm (si flou): Clarification avec l'utilisateur
  3. planner: Décompose en tâches
  4. atlas: Présente plan, demande confirmation
  5. builder(s): Exécute chaque tâche
  6. qa-tester: Valide après chaque étape
  7. doc-writer: Met à jour docs si nécessaire
  8. git-manager: Commit avec message approprié
  9. dev-tracker: Met à jour journal
```

### 3. Release Workflow

```yaml
trigger: /release [version]
steps:
  1. atlas: Vérifie que tout est prêt
  2. qa-tester: Lance suite de tests complète
  3. git-manager: Crée tag, met à jour CHANGELOG
  4. git-manager: Push et crée GitHub release
  5. doc-writer: Met à jour version dans docs
  6. dev-tracker: Archive sprint, prépare suivant
```

---

## Plan d'Implémentation

### Phase 1: Core (Session 1)

- [ ] `atlas.md` - Orchestrateur principal (opus)
- [ ] `planner.md` - Planificateur (sonnet)
- [ ] `/new-session` command
- [ ] `/status` command

### Phase 2: Builders (Session 2)

- [ ] `backend.md` - Builder backend (sonnet)
- [ ] `frontend.md` - Builder frontend (sonnet)
- [ ] `/implement` command
- [ ] Skills: api-endpoint, react-component

### Phase 3: Validation (Session 3)

- [ ] `qa-tester.md` - Tests (haiku)
- [ ] `debugger.md` - Debug (sonnet)
- [ ] `/test` command
- [ ] `/debug` command

### Phase 4: DevOps & Tracking (Session 4)

- [ ] `git-manager.md` - Git (haiku)
- [ ] `dev-tracker.md` - Suivi (haiku)
- [ ] `/commit`, `/release` commands

### Phase 5: Creative & Docs (Session 5)

- [ ] `brainstorm.md` - Sessions créatives (opus)
- [ ] `doc-writer.md` - Documentation (haiku)
- [ ] `ux-designer.md` - Design (sonnet)
- [ ] `/brainstorm`, `/docs` commands

---

## Référence

Les agents existants dans `D:\Projects\9-Archive\.claude\agents\` servent de base:

- `dev-session-orchestrator.md`
- `sprint-orchestrator.md`
- `synapse-feature-orchestrator.md`
- `fastapi-endpoint-builder.md`
- `react-page-scaffolder.md`
- `qa-test-runner.md`
- `documentation-master.md`
- `docker-service-builder.md`
- `version-master.md`
