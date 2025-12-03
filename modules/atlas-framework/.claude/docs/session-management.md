# Session Management & Auto-Documentation

Guide complet pour le système de gestion de sessions et d'auto-documentation d'Atlas.

## Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Pourquoi ce système?](#pourquoi-ce-système)
3. [Architecture](#architecture)
4. [Commandes](#commandes)
5. [Structure .dev/](#structure-dev)
6. [Workflow typique](#workflow-typique)
7. [Récupération après crash](#récupération-après-crash)
8. [Auto-documentation](#auto-documentation)
9. [Templates](#templates)
10. [Règles](#règles)

---

## Vue d'ensemble

Le système de session management permet à Atlas de:

- **Tracker** les sessions de travail (dev, brainstorm, debug)
- **Sauvegarder** automatiquement le contexte important
- **Récupérer** après un `/compact` ou crash
- **Archiver** les sessions terminées pour référence future

```
┌─────────────────────────────────────────────────────────────┐
│                    SESSION LIFECYCLE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   /1-dev ──► Active Session ──► Auto-Save ──► /9-archive    │
│      │            │                 │              │         │
│      ▼            ▼                 ▼              ▼         │
│   Create      Update on        Checkpoint      Archive +     │
│   session     progress         on 70%         Journal        │
│   file                                                       │
│                                                              │
│   Recovery: /0-resume loads from session + checkpoint        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Pourquoi ce système?

### Le problème

Claude Code a une limite de contexte. Quand le contexte atteint ~80%, le système fait un `/compact` automatique qui résume la conversation. Cela peut causer:

- Perte de détails importants
- Oubli de décisions prises
- Difficulté à reprendre le travail
- Perte de brainstorms non documentés

### La solution

Atlas sauvegarde automatiquement les informations critiques dans `.dev/`:

| Événement | Action |
|-----------|--------|
| Début de session | Crée `current-session.md` |
| Brainstorm terminé | Archive + journal |
| Task list complétée | Update session + journal |
| Décision architecturale | `decisions.md` |
| 70% contexte | Checkpoint automatique |
| Fin de session | Archive complète |

---

## Architecture

### Fichiers principaux

```
atlas-agent-framework/
├── agents/rules/
│   ├── auto-documentation.md    # Quand sauvegarder
│   └── session-management.md    # Comment gérer les sessions
│
├── commands/
│   ├── 0-checkpoint.md          # Créer checkpoint manuel
│   ├── 0-new-session.md         # (modifié) Vérifie session active
│   ├── 0-resume.md              # (modifié) Charge session/checkpoint
│   ├── 1-dev.md                 # Démarrer session dev
│   ├── 1-brainstorm.md          # Démarrer session brainstorm
│   ├── 1-debug.md               # Démarrer session debug
│   ├── 1-init-project.md        # Initialiser .dev/
│   ├── 1-init-system.md         # Initialiser Atlas dans workspace
│   └── 9-archive.md             # Archiver session
│
└── templates/dev/
    ├── current-session.template.md
    ├── checkpoint.template.md
    ├── hot-context.template.md
    ├── journal-daily.template.md
    └── backlog-item.template.md
```

### Structure projet (.dev/)

Créée par `/1-init-project`:

```
project/
└── .dev/
    ├── 0-backlog/              # Backlog items
    │   ├── ideas.md            # Idées à explorer
    │   ├── bugs.md             # Bugs connus
    │   └── features.md         # Features à implémenter
    │
    ├── 1-sessions/             # Sessions de travail
    │   ├── active/             # Session en cours
    │   │   └── current-session.md
    │   └── archive/            # Sessions passées
    │       └── 2025-01/
    │           └── 20250129-1430-api-refactor.md
    │
    ├── context/                # Contexte projet
    │   ├── project-state.md    # État actuel du projet
    │   ├── hot-context.md      # Contexte rapide pour recovery
    │   └── decisions.md        # Décisions architecturales (ADR)
    │
    ├── journal/                # Logs quotidiens
    │   └── 2025-01/
    │       └── 2025-01-29.md
    │
    ├── checkpoints/            # Snapshots de contexte
    │   └── 20250129-1530-checkpoint.md
    │
    └── reports/                # Rapports générés
        └── .gitkeep
```

---

## Commandes

### Commandes de Session (0-*)

| Commande | Description |
|----------|-------------|
| `/0-new-session` | Charge contexte complet, vérifie session active |
| `/0-resume` | Récupère après /compact, charge session + checkpoint |
| `/0-checkpoint` | Crée un checkpoint manuel |

### Démarreurs de Workflow (1-*)

| Commande | Description |
|----------|-------------|
| `/1-dev` | Démarre session dev avec tracking |
| `/1-brainstorm` | Démarre session brainstorm avec auto-save |
| `/1-debug` | Démarre session debug avec investigation |
| `/1-init-system` | Initialise Atlas dans un workspace |
| `/1-init-project` | Initialise structure `.dev/` dans un projet |

### Finisseurs (9-*)

| Commande | Description |
|----------|-------------|
| `/9-archive` | Archive la session courante |
| `/9-ship` | Test + commit + push |

---

## Structure .dev/

### 0-backlog/

Contient les items de backlog organisés par type:

**ideas.md** - Idées à explorer
```markdown
## High Priority
### [Titre]
**Added:** 2025-01-29
**Description:** [Description de l'idée]

## Medium Priority
[...]

## Low Priority
[...]
```

**bugs.md** - Bugs connus
```markdown
## High Priority
### [BUG-001] Crash on save
**Added:** 2025-01-29
**Severity:** critical
**Steps to reproduce:** [...]
```

**features.md** - Features planifiées
```markdown
## High Priority
### [FEAT-001] Dark mode
**Added:** 2025-01-29
**Status:** ready
**Acceptance criteria:** [...]
```

### 1-sessions/

**active/current-session.md** - Session en cours
```markdown
# Session: API Refactoring

**Started:** 2025-01-29 14:30
**Type:** dev
**Branch:** feature/api-v2
**Status:** active

---

## Objective
Refactorer l'API pour supporter GraphQL

## Progress
- [x] Analyser API actuelle
- [x] Créer schéma GraphQL
- [ ] Implémenter resolvers

## Key Decisions
- Utiliser Apollo Server
- Garder REST pour backward compatibility

## Next Steps
1. Implémenter query resolvers
2. Ajouter mutations

---
**Last updated:** 2025-01-29 16:45
```

**archive/** - Sessions terminées
```
archive/
└── 2025-01/
    ├── 20250128-0900-auth-system.md
    └── 20250129-1430-api-refactor.md
```

### context/

**project-state.md** - État du projet
```markdown
# Project State

**Project:** my-app
**Status:** active
**Phase:** MVP Development

## Overview
Application de gestion de tâches

## Current Sprint
Sprint 3: User authentication

## Key Files
| File | Purpose |
|------|---------|
| src/auth/ | Authentication module |
| src/api/ | API endpoints |
```

**hot-context.md** - Contexte rapide
```markdown
# Hot Context

## Current Focus
Implementing JWT refresh tokens

## Active Session
- Topic: Auth System
- Started: 2025-01-29 14:30
- Progress: 3/5 tasks

## Key Files Being Modified
- src/auth/jwt.ts
- src/middleware/auth.ts

## Recent Decisions
- Use RS256 for JWT signing
- 15min access token, 7d refresh token

## Blockers
None currently
```

**decisions.md** - Architecture Decision Records
```markdown
# Architecture Decision Records

## ADR-001: Use PostgreSQL

**Date:** 2025-01-15
**Status:** accepted

**Context:** Need reliable database for production

**Decision:** Use PostgreSQL with Prisma ORM

**Consequences:**
- Need to learn Prisma
- Good TypeScript integration
- Reliable for production
```

### journal/

Logs quotidiens automatiques:

```markdown
# Journal: 2025-01-29

## Sessions

### [14:30] Started: API Refactoring (dev)
- Objective: Refactor API for GraphQL support

### [15:45] Checkpoint created
- Context at 65%
- 2 tasks completed

### [17:00] Archived: API Refactoring
- Duration: 2.5 hours
- Tasks: 4/5 completed
- Branch: feature/api-v2
```

### checkpoints/

Snapshots de contexte:

```markdown
# Checkpoint: Manual Checkpoint

**Created:** 2025-01-29 15:30
**Session:** API Refactoring
**Context Level:** 65%
**Branch:** feature/api-v2

---

## Context Summary
Refactoring API to support GraphQL alongside REST.
Currently implementing query resolvers.

## Active Tasks
- [x] Analyze current API
- [x] Create GraphQL schema
- [ ] Implement resolvers (in_progress)
- [ ] Add mutations
- [ ] Write tests

## Recent Changes
- f4a3b2c: Add GraphQL schema
- e1d2c3b: Setup Apollo Server

## Hot Files
- src/graphql/schema.ts - Schema definition
- src/graphql/resolvers/ - Resolver implementations

## Key Decisions
- Use Apollo Server for GraphQL
- Keep REST endpoints for backward compatibility

## Next Steps
1. Complete user query resolver
2. Add authentication middleware for GraphQL
```

---

## Workflow typique

### 1. Initialisation (une fois)

```bash
# Dans le workspace
/1-init-system

# Dans chaque projet
/1-init-project
```

### 2. Début de journée

```bash
/0-new-session
# ou
/1-dev
```

Atlas vérifie s'il y a une session active et propose de continuer.

### 3. Pendant le travail

Atlas auto-sauvegarde sur:
- Complétion de tâches majeures
- Décisions architecturales
- Fin de brainstorm
- Alerte de contexte (70%)

Checkpoint manuel si nécessaire:
```bash
/0-checkpoint "Before major refactor"
```

### 4. Fin de session

```bash
/9-archive
```

Ou si le travail est prêt:
```bash
/9-ship
```

### 5. Après /compact ou crash

```bash
/0-resume
```

Atlas charge:
1. Session active (si existe)
2. Dernier checkpoint
3. Hot-context
4. Compact summary

---

## Récupération après crash

### Scénario 1: /compact automatique

```
Avant compact:
- Session active dans .dev/1-sessions/active/
- Checkpoint récent dans .dev/checkpoints/
- Hot-context à jour

Après compact:
> /0-resume

ATLAS: "🔄 Reconstruction session...

Sources trouvées:
✅ Session active: API Refactoring
✅ Checkpoint: 20250129-1530
✅ Hot-context: Updated 16:45

Que veux-tu faire?
1. Continuer la session
2. Voir les détails
3. Commencer autre chose"
```

### Scénario 2: Crash navigateur

Même workflow - les fichiers `.dev/` sont persistés sur disque.

### Scénario 3: Nouvelle conversation

```
> /1-dev

ATLAS: "⚠️ Session active détectée!

Session: API Refactoring
Started: 2025-01-29 14:30
Progress: 3/5 tasks

1. Continuer cette session
2. Archiver et nouvelle
3. Ignorer"
```

---

## Auto-documentation

### Quand Atlas sauvegarde

| Trigger | Fichier(s) mis à jour |
|---------|----------------------|
| Fin brainstorm | journal, session archive |
| TodoWrite structuré | current-session.md |
| Task list complétée | journal, session |
| Décision architecturale | decisions.md |
| 70% contexte | checkpoint, hot-context |
| Fin session | archive, journal |

### Quand Atlas NE sauvegarde PAS

- Simple Recap
- Réponses courtes
- Questions/clarifications
- Modifications mineures

### Langue

Atlas documente dans la langue de l'utilisateur:
- Si tu parles français → documentation en français
- Si tu parles anglais → documentation en anglais

---

## Templates

Tous les templates sont dans `atlas-agent-framework/templates/dev/`:

| Template | Usage |
|----------|-------|
| `current-session.template.md` | Sessions actives |
| `checkpoint.template.md` | Checkpoints de contexte |
| `hot-context.template.md` | Contexte rapide |
| `journal-daily.template.md` | Logs quotidiens |
| `backlog-item.template.md` | Items de backlog |

---

## Règles

### auto-documentation.md

Définit:
- Quand déclencher l'auto-save
- Quels fichiers mettre à jour
- Format des entrées

### session-management.md

Définit:
- Cycle de vie des sessions
- Priorité de récupération
- Intégration avec backlog
- Gestion des conflits

---

## Bonnes pratiques

1. **Toujours initialiser** - `/1-init-project` avant de commencer
2. **Utiliser les commandes 1-*** - Pour le tracking automatique
3. **Checkpoint avant risque** - `/0-checkpoint` avant refactoring majeur
4. **Archiver proprement** - `/9-archive` pour fermer une session
5. **Documenter les décisions** - Elles vont dans `decisions.md`

---

## Troubleshooting

### "Session active non trouvée"

Vérifier que `.dev/1-sessions/active/` existe:
```bash
ls .dev/1-sessions/active/
```

Si vide, utiliser `/1-dev` pour créer une nouvelle session.

### "Checkpoint corrompu"

Les checkpoints sont des fichiers texte. Ouvrir le plus récent dans `.dev/checkpoints/` et vérifier le contenu.

### "Backlog vide"

Initialiser avec `/1-init-project` ou créer manuellement les fichiers dans `.dev/0-backlog/`.

---

## Voir aussi

- [Commands Reference](commands-reference.md)
- [Templates Reference](templates-reference.md)
- `agents/rules/auto-documentation.md`
- `agents/rules/session-management.md`
