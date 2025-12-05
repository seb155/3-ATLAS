# Templates Reference

Référence complète des templates Atlas pour la gestion de sessions.

## Vue d'ensemble

Les templates sont dans `atlas-agent-framework/templates/dev/` et définissent la structure des fichiers créés dans `.dev/`.

| Template | Fichier(s) créé(s) | Par |
|----------|-------------------|-----|
| `current-session.template.md` | `.dev/1-sessions/active/current-session.md` | `/1-dev`, `/1-brainstorm`, `/1-debug` |
| `checkpoint.template.md` | `.dev/checkpoints/YYYYMMDD-HHMM-checkpoint.md` | `/0-checkpoint`, auto |
| `hot-context.template.md` | `.dev/context/hot-context.md` | Auto-updated |
| `journal-daily.template.md` | `.dev/journal/YYYY-MM/YYYY-MM-DD.md` | Auto |
| `backlog-item.template.md` | `.dev/0-backlog/*.md` | `/1-init-project` |

---

## current-session.template.md

**Usage:** Tracker les sessions de travail actives.

**Créé par:** `/1-dev`, `/1-brainstorm`, `/1-debug`

**Emplacement:** `.dev/1-sessions/active/current-session.md`

### Structure

```markdown
# Session: [Topic]

**Started:** YYYY-MM-DD HH:MM
**Type:** dev | brainstorm | debug | workshop
**Branch:** [git-branch]
**Status:** active | paused | completed

---

## Objective

[Ce qu'on veut accomplir dans cette session]

## Context

[Fichiers clés, état du projet pertinent]

## Progress

- [x] Tâche complétée
- [ ] Tâche en cours
- [ ] Tâche à faire

## Key Decisions

- [Décision 1 avec justification]
- [Décision 2 avec justification]

## Blockers

- [Blocker actuel si applicable]

## Next Steps

1. [Prochaine action]
2. [Action suivante]

## Notes

[Notes additionnelles de session]

---

**Last updated:** YYYY-MM-DD HH:MM
```

### Champs

| Champ | Description | Valeurs |
|-------|-------------|---------|
| `Started` | Timestamp de début | Format: YYYY-MM-DD HH:MM |
| `Type` | Type de session | `dev`, `brainstorm`, `debug`, `workshop` |
| `Branch` | Branche Git actuelle | String |
| `Status` | État de la session | `active`, `paused`, `completed` |

### Exemple rempli

```markdown
# Session: API GraphQL Migration

**Started:** 2025-01-29 14:30
**Type:** dev
**Branch:** feature/graphql-api
**Status:** active

---

## Objective

Migrer l'API REST vers GraphQL tout en maintenant la compatibilité backward.

## Context

- API REST actuelle dans `src/api/rest/`
- 15 endpoints à migrer
- Tests existants à adapter

## Progress

- [x] Setup Apollo Server
- [x] Créer schéma GraphQL de base
- [ ] Implémenter User queries
- [ ] Implémenter User mutations
- [ ] Ajouter authentification

## Key Decisions

- **Apollo Server** choisi pour son écosystème mature
- **Code-first** approach avec TypeGraphQL
- **REST maintenu** en parallèle pour 6 mois

## Blockers

- Attendre validation du schéma par l'équipe frontend

## Next Steps

1. Finaliser le schéma User
2. Review avec frontend
3. Implémenter les resolvers

## Notes

- Performance: batch les queries N+1
- Voir spec dans `docs/graphql-migration.md`

---

**Last updated:** 2025-01-29 16:45
```

---

## checkpoint.template.md

**Usage:** Sauvegarder un snapshot du contexte pour recovery.

**Créé par:** `/0-checkpoint`, automatiquement à 70% contexte

**Emplacement:** `.dev/checkpoints/YYYYMMDD-HHMM-checkpoint.md`

### Structure

```markdown
# Checkpoint: [Note or "Manual Checkpoint"]

**Created:** YYYY-MM-DD HH:MM
**Session:** [current session topic if any]
**Context Level:** [estimated percentage]
**Branch:** [git branch]

---

## Context Summary

[Résumé de ce qu'on fait et l'état actuel]

## Active Tasks

From TodoWrite:
- [x] Tâche complétée
- [ ] Tâche en cours (in_progress)
- [ ] Tâche pending

## Recent Changes

From git:
- [hash] [message]
- [hash] [message]

## Hot Files

Fichiers en cours de modification:
- [file1] - [ce qui est fait]
- [file2] - [ce qui est fait]

## Key Decisions

Décisions prises cette session:
- [Décision 1]
- [Décision 2]

## Next Steps

Quoi faire après recovery:
1. [Action suivante]
2. [Action d'après]

## Notes

[Notes additionnelles ou contexte utilisateur]

---

**Recovery command:** `/0-resume` puis charger ce checkpoint
```

### Exemple rempli

```markdown
# Checkpoint: Before major refactor

**Created:** 2025-01-29 15:30
**Session:** API GraphQL Migration
**Context Level:** 68%
**Branch:** feature/graphql-api

---

## Context Summary

Migration de l'API REST vers GraphQL. Le schéma de base est fait,
en train d'implémenter les resolvers pour User.

## Active Tasks

- [x] Setup Apollo Server
- [x] Create base GraphQL schema
- [ ] Implement User queries (in_progress)
- [ ] Implement User mutations
- [ ] Add authentication middleware

## Recent Changes

- a1b2c3d: Add GraphQL schema types
- d4e5f6a: Setup Apollo Server config
- b7c8d9e: Add User type definition

## Hot Files

- src/graphql/schema.ts - Type definitions
- src/graphql/resolvers/user.ts - User resolvers (WIP)
- src/graphql/context.ts - Context setup

## Key Decisions

- Use TypeGraphQL for code-first approach
- Keep REST API running in parallel
- Use DataLoader for N+1 prevention

## Next Steps

1. Complete userById query resolver
2. Add error handling
3. Test with GraphQL Playground

## Notes

Après ce checkpoint, faire le refactor du User resolver
pour utiliser le repository pattern.

---

**Recovery command:** `/0-resume` puis charger ce checkpoint
```

---

## hot-context.template.md

**Usage:** Référence rapide pour recovery et context switching.

**Mis à jour:** Automatiquement pendant la session

**Emplacement:** `.dev/context/hot-context.md`

### Structure

```markdown
# Hot Context

Quick reference pour session recovery.

---

## Current Focus

[Ce sur quoi on travaille actuellement]

## Active Session

- **Topic:** [session topic]
- **Type:** [dev/brainstorm/debug]
- **Started:** YYYY-MM-DD HH:MM
- **Progress:** X/Y tasks

## Key Files Being Modified

- [file1] - [purpose]
- [file2] - [purpose]

## Recent Decisions

- [Décision 1]
- [Décision 2]

## Blockers

- [Blocker si applicable]
- None currently

## Quick Commands

- `/0-resume` - Reprendre après compact
- `/1-dev` - Vérifier/continuer session
- `/9-archive` - Archiver quand fini

---

**Last checkpoint:** [path to checkpoint if exists]
**Updated:** YYYY-MM-DD HH:MM
```

### Exemple rempli

```markdown
# Hot Context

Quick reference pour session recovery.

---

## Current Focus

Implementing GraphQL User query resolvers with proper error handling.

## Active Session

- **Topic:** API GraphQL Migration
- **Type:** dev
- **Started:** 2025-01-29 14:30
- **Progress:** 2/5 tasks

## Key Files Being Modified

- src/graphql/resolvers/user.ts - Main resolver file
- src/graphql/schema.ts - Type definitions
- tests/graphql/user.test.ts - Resolver tests

## Recent Decisions

- Use DataLoader for batching
- Return null instead of throwing for not found
- Use cursor-based pagination

## Blockers

- None currently

## Quick Commands

- `/0-resume` - Reprendre après compact
- `/1-dev` - Vérifier/continuer session
- `/9-archive` - Archiver quand fini

---

**Last checkpoint:** .dev/checkpoints/20250129-1530-checkpoint.md
**Updated:** 2025-01-29 16:45
```

---

## journal-daily.template.md

**Usage:** Log quotidien des activités et événements.

**Créé par:** Automatiquement au premier événement du jour

**Emplacement:** `.dev/journal/YYYY-MM/YYYY-MM-DD.md`

### Structure

```markdown
# Journal: YYYY-MM-DD

Daily activity log.

---

## Sessions

### [HH:MM] Event Type: Description

**Context:** [Contexte si pertinent]
**Action:** [Ce qui a été fait]
**Outcome:** [Résultat]
**Duration:** [Si applicable]

---

## Summary

**Sessions:** X
**Tasks Completed:** Y
**Key Accomplishments:**
- [Accomplissement 1]
- [Accomplissement 2]

**Tomorrow:**
- [À faire demain]
```

### Types d'événements

| Type | Description |
|------|-------------|
| `Started` | Début de session |
| `Checkpoint` | Checkpoint créé |
| `Decision` | Décision architecturale |
| `Completed` | Tâche majeure complétée |
| `Archived` | Session archivée |
| `Brainstorm` | Fin de brainstorm |

### Exemple rempli

```markdown
# Journal: 2025-01-29

Daily activity log.

---

## Sessions

### [09:15] Started: Morning standup review

**Context:** Review des PRs et planning du jour
**Action:** Revue de 3 PRs, merge de 2
**Outcome:** PR backlog cleared

### [10:00] Started: API GraphQL Migration (dev)

**Context:** Continuer migration GraphQL
**Action:** Setup Apollo Server, créer schéma de base
**Outcome:** Schéma prêt pour implémentation

### [12:30] Checkpoint: Before lunch

**Context:** Context à 55%
**Action:** Checkpoint manuel créé
**Outcome:** .dev/checkpoints/20250129-1230-checkpoint.md

### [14:00] Decision: Pagination approach

**Context:** Besoin de choisir pagination style
**Decision:** Cursor-based pagination pour GraphQL
**Rationale:** Meilleure performance avec grands datasets

### [16:45] Completed: User query resolvers

**Context:** Partie de la migration GraphQL
**Action:** Implémenté userById, users, usersByRole
**Outcome:** 3 queries fonctionnelles avec tests

### [17:30] Archived: API GraphQL Migration

**Duration:** 7.5 hours
**Status:** completed (session partielle, suite demain)
**Progress:** 3/5 tasks

---

## Summary

**Sessions:** 2
**Tasks Completed:** 4
**Key Accomplishments:**
- Apollo Server configuré
- Schéma GraphQL User complet
- 3 query resolvers implémentés
- Tests passent

**Tomorrow:**
- Implémenter mutations User
- Ajouter authentification GraphQL
- Review avec frontend
```

---

## backlog-item.template.md

**Usage:** Structure pour items de backlog.

**Créé par:** `/1-init-project`, manuellement

**Emplacement:** `.dev/0-backlog/ideas.md`, `bugs.md`, `features.md`

### Structure

```markdown
# [Type] Backlog

## High Priority

### [ID] [Title]

**Added:** YYYY-MM-DD
**Priority:** high | medium | low
**Type:** idea | bug | feature
**Status:** new | ready | in-progress | blocked | done

**Description:**
[Description détaillée]

**Acceptance Criteria:**
- [ ] Critère 1
- [ ] Critère 2

**Notes:**
[Notes additionnelles]

---

## Medium Priority

[Items...]

## Low Priority

[Items...]

---

## Completed

### [ID] [Title] ✓

**Completed:** YYYY-MM-DD
[...]
```

### Exemple: features.md

```markdown
# Features Backlog

## High Priority

### [FEAT-001] GraphQL API

**Added:** 2025-01-20
**Priority:** high
**Type:** feature
**Status:** in-progress

**Description:**
Ajouter une API GraphQL en parallèle de REST pour meilleure
flexibilité frontend.

**Acceptance Criteria:**
- [x] Apollo Server setup
- [x] User schema
- [ ] All REST endpoints migrated
- [ ] Authentication middleware
- [ ] Documentation

**Notes:**
Voir ADR-003 pour décisions techniques

---

### [FEAT-002] Real-time notifications

**Added:** 2025-01-22
**Priority:** high
**Type:** feature
**Status:** ready

**Description:**
Notifications push en temps réel via WebSocket.

**Acceptance Criteria:**
- [ ] WebSocket server
- [ ] Client SDK
- [ ] Notification types defined
- [ ] User preferences

---

## Medium Priority

### [FEAT-003] Dark mode

**Added:** 2025-01-25
**Priority:** medium
**Type:** feature
**Status:** new

**Description:**
Support du dark mode dans l'interface.

**Acceptance Criteria:**
- [ ] Theme system
- [ ] Toggle component
- [ ] Persistence user preference

---

## Low Priority

### [FEAT-004] Export to PDF

**Added:** 2025-01-28
**Priority:** low
**Type:** feature
**Status:** new

**Description:**
Permettre l'export des rapports en PDF.

---

## Completed

### [FEAT-000] User authentication ✓

**Completed:** 2025-01-15
**Duration:** 3 days

JWT-based authentication avec refresh tokens.
```

---

## Utilisation des templates

### Dans les commandes

Les commandes utilisent ces templates comme base:

```javascript
// Pseudo-code
const template = read('templates/dev/current-session.template.md');
const filled = template
  .replace('[Topic]', sessionTopic)
  .replace('YYYY-MM-DD HH:MM', getCurrentTimestamp())
  .replace('[git-branch]', getCurrentBranch());
write('.dev/1-sessions/active/current-session.md', filled);
```

### Personnalisation

Tu peux modifier les templates dans `atlas-agent-framework/templates/dev/` pour adapter la structure à tes besoins.

**Attention:** Les commandes attendent certains champs. Garde la structure de base.

---

## Voir aussi

- [Session Management](session-management.md)
- [Commands Reference](commands-reference.md)
