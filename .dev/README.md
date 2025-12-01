# .dev - Development Tracking System

> **Centre de commande pour le developpement AXIOM**
>
> Ce dossier contient tout le contexte necessaire pour les agents AI et developpeurs.

---

## Quick Start

### Premiere fois?

1. Lire [`ARCHITECTURE.md`](./ARCHITECTURE.md) - Vue complete du systeme
2. Lire [`context/project-state.md`](./context/project-state.md) - Etat MVP courant
3. Lire [`infra/registry.yml`](./infra/registry.yml) - Registre des ports

### Session de developpement

```bash
# Demarrer une nouvelle session
/0-new-session

# Continuer le travail
/0-next

# Voir la progression
/0-progress
```

---

## Structure du Dossier

```
.dev/
├── ARCHITECTURE.md          # Vue complete architecture systeme
├── README.md                # Ce fichier (index)
├── index.md                 # Index alternatif
│
├── context/                 # Contexte projet
│   ├── project-state.md     # ETAT MVP COURANT (lire en premier!)
│   ├── credentials.md       # Identifiants (admin, DB, etc.)
│   ├── task-queue.md        # File de taches prioritaires
│   ├── test-coverage.md     # Couverture tests
│   └── shared-context.md    # Contexte partage entre agents
│
├── infra/                   # Infrastructure
│   ├── registry.yml         # REGISTRE PORTS (CRITIQUE!)
│   ├── infrastructure.md    # Documentation complete infra
│   ├── INFRASTRUCTURE-POLICY.md  # Politiques obligatoires
│   ├── AGENT-QUICK-REFERENCE.md  # Reference rapide agents
│   └── CHANGELOG.md         # Historique modifications
│
├── journal/                 # Logs quotidiens
│   ├── session-template.md  # Template pour nouvelles sessions
│   └── 2025-11/             # Logs novembre 2025
│       ├── 2025-11-23.md
│       ├── 2025-11-24.md
│       ├── 2025-11-25.md
│       ├── 2025-11-27.md
│       └── 2025-11-28-*.md
│
├── roadmap/                 # Planning
│   ├── README.md            # Index roadmap
│   ├── current-sprint.md    # Sprint actuel
│   ├── next-sprint.md       # Prochain sprint
│   ├── mvp-week-2-sprint.md # Sprint semaine 2
│   ├── nexus-development-plan.md  # NEXUS full plan + TriliumNext
│   ├── nexus-phase-2-sprint.md    # NEXUS Phase 2 sprint (4 weeks)
│   └── backlog/             # Backlog detaille
│       ├── ai-strategy.md
│       ├── rule-engine-event-sourcing.md
│       ├── package-generation.md
│       └── [14 autres items]
│
├── decisions/               # Architecture Decision Records (ADR)
│   ├── 001-workspace-monorepo.md
│   ├── 002-devconsole-v3-architecture.md
│   └── 003-rule-engine-event-sourcing.md
│
├── testing/                 # Suivi des tests
│   ├── test-status.md       # Status courant
│   └── asset-history-integration-test-guide.md
│
├── analysis/                # Analyses techniques
│   └── 2025-11-28-architecture-review.md
│
├── design/                  # Sessions design
│   └── 2025-11-28-whiteboard-session.md
│
├── whiteboard/              # Ideas en cours
│   ├── pending-decisions.md
│   └── plant3d-sync-plan.md
│
├── 0-backlog/               # Backlog brut
│   └── backlog.md
│
└── scripts/                 # Automatisation
    ├── smart-resume-enhanced.ps1
    └── validate-infra.ps1
```

---

## Fichiers Critiques

### A Lire en Debut de Session

| Fichier | Purpose | Frequence |
|:---|:---|:---|
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | Architecture complete systeme | Reference |
| **[context/project-state.md](./context/project-state.md)** | Etat MVP courant | Chaque session |
| **[infra/registry.yml](./infra/registry.yml)** | Registre ports/services | Avant ops infra |
| **[roadmap/current-sprint.md](./roadmap/current-sprint.md)** | Sprint actuel | Planning |

### Reference Rapide

| Besoin | Fichier |
|:---|:---|
| Architecture systeme | `ARCHITECTURE.md` |
| Identifiants | `context/credentials.md` |
| Status tests | `testing/test-status.md` |
| Decisions architecture | `decisions/` |
| Historique infra | `infra/CHANGELOG.md` |
| **NEXUS Plan** | `roadmap/nexus-development-plan.md` |
| **NEXUS Sprint** | `roadmap/nexus-phase-2-sprint.md` |

---

## Conventions

### Journal Quotidien

Creer un fichier `journal/YYYY-MM/YYYY-MM-DD.md` pour chaque session:

```markdown
# Session 2025-11-29

## Objectif
[Ce qu'on veut accomplir]

## Accompli
- [x] Task 1
- [x] Task 2

## Decisions
- Decision 1: [rationale]

## Problemes
- Issue rencontre

## Prochaines etapes
- [ ] Next task
```

### Architecture Decision Record (ADR)

Pour les decisions importantes, creer `decisions/XXX-title.md`:

```markdown
# ADR-XXX: Titre

## Statut
Accepted | Proposed | Deprecated

## Contexte
[Pourquoi cette decision]

## Decision
[Ce qu'on a decide]

## Consequences
[Impact positif et negatif]
```

---

## Workflows

### Nouveau Sprint

1. Creer `roadmap/current-sprint.md` avec les objectifs
2. Mettre a jour `context/project-state.md`
3. Lancer `/0-new-session`

### Fin de Session

1. Mettre a jour le journal du jour
2. Commit les changements `.dev/`
3. Mettre a jour `project-state.md` si necessaire

### Modification Infrastructure

1. **LIRE** `infra/registry.yml` d'abord!
2. Utiliser l'agent DevOps-Manager pour les changements
3. Mettre a jour le registry
4. Documenter dans `infra/CHANGELOG.md`

---

## Pour les Agents AI

### Debut de Session

```
1. Lire .dev/context/project-state.md
2. Lire .dev/roadmap/current-sprint.md
3. Verifier git status
```

### Pendant le Travail

```
1. Mettre a jour journal/YYYY-MM/YYYY-MM-DD.md
2. Creer ADR pour decisions importantes
3. Mettre a jour sprint si progress
```

### Avant Operations Infra

```
1. TOUJOURS lire .dev/infra/registry.yml
2. Ne jamais deviner les ports
3. Utiliser DevOps-Manager pour changements complexes
```

---

## Commandes Disponibles

| Commande | Description |
|:---|:---|
| `/0-new-session` | Nouvelle session (contexte complet) |
| `/0-next` | Continuer tache suivante |
| `/0-resume` | Reprendre apres /compact |
| `/0-progress` | Vue roadmap compacte |
| `/0-dashboard` | Status session courante |
| `/0-ship` | Git workflow (test + commit + push) |
| `/0-backlog` | Trier et prioriser le backlog |

---

## Liens Rapides

| Destination | Chemin |
|:---|:---|
| README principal | [`../README.md`](../README.md) |
| Instructions AI | [`../CLAUDE.md`](../CLAUDE.md) |
| Agents | [`../.claude/agents/`](../.claude/agents/) |
| Documentation publique | [`../docs/`](../docs/) |
| SYNAPSE backend | [`../apps/synapse/backend/`](../apps/synapse/backend/) |
| SYNAPSE frontend | [`../apps/synapse/frontend/`](../apps/synapse/frontend/) |
| FORGE infra | [`../forge/`](../forge/) |

---

*Maintenu par le systeme d'agents AI - Derniere mise a jour: 2025-11-29*
