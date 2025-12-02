# ATLAS 2.0 - Progression

**Dernière mise à jour:** 2025-12-02
**Session:** Initial Planning

---

## Comment Continuer (IMPORTANT)

### Option 1: Commande rapide
```
/0-resume
```
Puis dire: "Continue ATLAS 2.0 depuis Phase [X]"

### Option 2: Contexte complet
Copier-coller ceci dans une nouvelle conversation:

```
Continue l'implémentation ATLAS 2.0:

1. Lis ces fichiers pour contexte:
   - .atlas/ATLAS-2.0-PLAN.md (plan complet)
   - .atlas/ATLAS-2.0-PROGRESS.md (où on en est)

2. Reprends à la Phase [VOIR PROGRESSION CI-DESSOUS]

3. Après chaque phase, update ATLAS-2.0-PROGRESS.md
```

### Option 3: Phase spécifique
```
Implémente Phase [X] de ATLAS 2.0.
Lis .atlas/ATLAS-2.0-PLAN.md pour les détails.
```

---

## Progression Globale

```
Phase 0: Migration Symlinks    [██████████] 100%  ✅ COMPLETE
Phase 1: Parallel Agents       [░░░░░░░░░░]   0%  ← PROCHAINE
Phase 2: Git Worktrees         [░░░░░░░░░░]   0%
Phase 3: Sandbox Pool          [░░░░░░░░░░]   0%
Phase 4: Monorepo Layers       [░░░░░░░░░░]   0%
Phase 5: Inter-Agent Comms     [░░░░░░░░░░]   0%
─────────────────────────────────────────────────
TOTAL                          [█░░░░░░░░░]  17%
```

---

## Détail par Phase

### Phase 0: Migration Symlinks → Local ✅ COMPLETE
**Status:** COMPLETE (2025-12-02)
**Bloquant:** OUI (toutes les autres phases) - RÉSOLU

| Tâche | Status | Notes |
|-------|--------|-------|
| Backup contenu symlink | [x] | Restauré depuis git history |
| Supprimer symlink | [x] | rm .claude (était cassé) |
| Copier contenu local | [x] | git checkout 7c995e0 -- .claude |
| Git add + commit | [x] | Commit ccb5914 |
| Tester /0-new-session | [x] | Commandes disponibles |
| Consolider .agent/ | [ ] | Optionnel - à faire plus tard |

**Résultat:**
- Symlink supprimé
- 30 fichiers restaurés depuis commit 7c995e0
- Structure complète: agents/, commands/, skills/, hooks/, context/
- Push effectué sur branche feature

---

### Phase 1: Parallel Agent Framework
**Status:** NOT STARTED
**Dépendance:** Phase 0

| Tâche | Status | Notes |
|-------|--------|-------|
| Créer .claude/agents/builders/ | [ ] | |
| Créer backend-builder.md | [ ] | |
| Créer frontend-builder.md | [ ] | |
| Créer qa-tester.md | [ ] | |
| Update atlas.md | [ ] | Section Parallel Execution |
| Tester dispatch parallèle | [ ] | |

**Fichiers à créer:**
- `.claude/agents/builders/backend-builder.md`
- `.claude/agents/builders/frontend-builder.md`
- `.claude/agents/builders/qa-tester.md`

---

### Phase 2: Git Worktrees Integration
**Status:** NOT STARTED
**Dépendance:** Phase 1

| Tâche | Status | Notes |
|-------|--------|-------|
| Créer worktree-manager.sh | [ ] | |
| Tester create worktree | [ ] | |
| Tester merge worktree | [ ] | |
| Intégrer avec agents | [ ] | |

**Fichiers à créer:**
- `.atlas/scripts/worktree-manager.sh`

---

### Phase 3: Sandbox Pool (FORGE)
**Status:** NOT STARTED
**Dépendance:** Phase 1, 2

| Tâche | Status | Notes |
|-------|--------|-------|
| Créer forge/sandbox/ directory | [ ] | |
| Créer Dockerfile.agent | [ ] | |
| Créer docker-compose.sandbox.yml | [ ] | |
| Créer sandbox-config.yml | [ ] | |
| Créer pool-manager.py | [ ] | |
| Build image | [ ] | |
| Test pool status | [ ] | |

**Fichiers à créer:**
- `forge/sandbox/Dockerfile.agent`
- `forge/sandbox/docker-compose.sandbox.yml`
- `forge/sandbox/sandbox-config.yml`
- `forge/sandbox/pool-manager.py`

---

### Phase 4: Monorepo Layer System
**Status:** NOT STARTED
**Dépendance:** Phase 0

| Tâche | Status | Notes |
|-------|--------|-------|
| Créer .atlas/config.yml | [ ] | |
| Update atlas.md layer resolution | [ ] | |
| Créer exemple override | [ ] | apps/synapse/.claude/ |
| Tester layers | [ ] | |

**Fichiers à créer:**
- `.atlas/config.yml`
- `apps/synapse/.claude/commands/` (exemple)

---

### Phase 5: Inter-Agent Communication
**Status:** NOT STARTED
**Dépendance:** Phase 3

| Tâche | Status | Notes |
|-------|--------|-------|
| Créer .atlas/runtime/ structure | [ ] | |
| Définir task schema | [ ] | |
| Définir result schema | [ ] | |
| Implémenter file-based comms | [ ] | |
| (Optional) Add Redis | [ ] | |

**Fichiers à créer:**
- `.atlas/runtime/tasks/`
- `.atlas/runtime/results/`
- `.atlas/runtime/status.json`

---

## Historique des Sessions

### 2025-12-02 - Session 2: Phase 0 Complete
**Durée:** ~15 minutes
**Accomplissements:**
- Migration symlink → local complétée
- Découverte: symlink était cassé (target n'existe pas)
- Solution: restauration depuis git history (commit 7c995e0)
- 30 fichiers .claude/ restaurés et commités

**Commits:**
- `ccb5914` - refactor(atlas): migrate from symlink to local .claude directory

**Prochaine action:**
Phase 1 - Créer les builder agents (backend, frontend, qa)

---

### 2025-12-02 - Session 1: Planning
**Durée:** ~45 minutes
**Accomplissements:**
- Analyse architecture ATLAS v1.0 actuelle
- Recherche best practices 2025 (Anthropic multi-agent, Kubernetes Agent Sandbox)
- Identification des gaps: parallélisme explicite, sandboxing, worktrees
- Création plan complet ATLAS 2.0 (5 phases)
- Création fichiers de tracking

**Fichiers créés:**
- `.atlas/ATLAS-2.0-PLAN.md` - Plan complet détaillé
- `.atlas/ATLAS-2.0-PROGRESS.md` - Ce fichier
- `.atlas/CONTINUE-SESSION.md` - Guide continuation

---

## Notes Importantes

### Symlink Actuel
```
.claude/ → /home/seb/atlas-framework/.claude
```
Ce symlink DOIT être supprimé et remplacé par contenu local.

### Ordre des Phases
```
Phase 0 (CRITIQUE) ──→ Phase 1 ──→ Phase 2 ──→ Phase 3
                 └──→ Phase 4                    │
                                                 ▼
                                            Phase 5
```
- Phase 0 est bloquante pour TOUT
- Phase 4 peut être faite en parallèle avec Phase 1-3
- Phase 5 nécessite Phase 3

### Ressources Externes
- [Anthropic Multi-Agent System](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Kubernetes Agent Sandbox](https://opensource.googleblog.com/2025/11/unleashing-autonomous-ai-agents-why-kubernetes-needs-a-new-standard-for-agent-execution.html)
- [Claude Agent SDK Best Practices](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)
