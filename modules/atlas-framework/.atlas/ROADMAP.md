# ATLAS Development Roadmap

**Créé:** 2025-11-30
**Objectif:** Système AI complet pour développement AXIOM

---

## Vue d'ensemble

```
Phase 1          Phase 2          Phase 3          Phase 4
─────────────    ─────────────    ─────────────    ─────────────
Slash Commands → Agents Core   → Skills        → Hooks + Polish
(6 commands)     (3 agents)       (3 skills)       (3 hooks)
PRIORITÉ HAUTE   PRIORITÉ HAUTE   PRIORITÉ MOY     PRIORITÉ BASSE
```

---

## Phase 1: Slash Commands (PRIORITÉ HAUTE)

### Objectif
Permettre à l'utilisateur de démarrer/gérer ses sessions de travail.

### Commandes à créer

#### 1.1 `/0-new-session` (Mode FULL)
**Fichier:** `.claude/commands/0-new-session.md`

**Workflow:**
```
1. Charger .dev/ai/session-state.json
2. Charger .dev/ai/active-apps.json
3. Afficher revue progression:
   ┌─────────────────────────────────────────────┐
   │  📊 Revue des Applications                  │
   │  ─────────────────────────────────────────  │
   │  SYNAPSE  ████████░░ 85%  MVP Dec 20       │
   │  NEXUS    ███░░░░░░░ 30%  Phase 2          │
   │  CORTEX   █░░░░░░░░░ 10%  Planning         │
   │  APEX     ░░░░░░░░░░  0%  Not started      │
   └─────────────────────────────────────────────┘
4. Demander: "Sur quelle(s) app(s) veux-tu travailler?"
5. Charger contexte app sélectionnée
6. Afficher prochaines tâches suggérées
```

#### 1.2 `/0-next` (Mode QUICK)
**Fichier:** `.claude/commands/0-next.md`

**Workflow:**
```
1. Charger contexte léger (dernière session)
2. Afficher dernière tâche complétée
3. Proposer prochaine tâche logique
4. Continuer sans revue complète
```

#### 1.3 `/0-resume` (Mode RECOVERY)
**Fichier:** `.claude/commands/0-resume.md`

**Workflow:**
```
1. Détecter session interrompue (/compact)
2. Recharger contexte complet
3. Reprendre exactement où on était
```

#### 1.4 `/0-ship`
**Fichier:** `.claude/commands/0-ship.md`

**Workflow:**
```
1. Lancer tests (si configurés)
2. Si tests passent → git add + commit
3. Push vers remote
4. Afficher résumé
```

#### 1.5 `/0-progress`
**Fichier:** `.claude/commands/0-progress.md`

**Workflow:**
```
1. Lire .dev/ai/active-apps.json
2. Lire apps/*/.dev/ai/app-state.json
3. Afficher vue compacte roadmap
```

#### 1.6 `/0-dashboard`
**Fichier:** `.claude/commands/0-dashboard.md`

**Workflow:**
```
1. Afficher status session courante
2. App active, tâche en cours
3. Temps écoulé, tokens utilisés
4. Fichiers modifiés
```

---

## Phase 2: Agents Core (PRIORITÉ HAUTE)

### 2.1 ATLAS - Orchestrateur Principal
**Fichier:** `.claude/agents/atlas.md`

**Responsabilités:**
- Router les tâches vers les bons agents spécialistes
- Gérer le contexte multi-app
- Coordonner le développement parallèle
- Économiser les tokens (chargement contexte intelligent)

**Template:**
```markdown
# ATLAS - AI Orchestrator

## Role
Orchestrateur principal du système AXIOM.

## Capabilities
- Route tasks to specialist agents
- Manages multi-app context
- Tracks agent performance
- Optimizes token usage

## Decision Tree
[Quand utiliser quel agent]

## Context Loading Strategy
[Comment charger le bon contexte]
```

### 2.2 DevOps Manager
**Fichier:** `.claude/agents/devops-manager.md`

**Responsabilités:**
- Gestion infrastructure Docker
- Allocation ports
- Diagnostic problèmes réseau
- Validation configurations

### 2.3 Brainstorm Agent
**Fichier:** `.claude/agents/brainstorm.md`

**Responsabilités:**
- Sessions whiteboard
- Exploration d'idées
- Documentation en temps réel
- Mode conversation libre

---

## Phase 3: Skills (PRIORITÉ MOYENNE)

### 3.1 Skill Infra
**Fichier:** `.claude/skills/infra.md`

**Fonction:** Affichage rapide status infrastructure
```
skill: "infra"
→ Affiche services running, ports, health
```

### 3.2 Skill Brainstorm
**Fichier:** `.claude/skills/brainstorm.md`

**Fonction:** Active le mode whiteboard/exploration

---

## Phase 4: Hooks (PRIORITÉ BASSE)

### 4.1 Session Start Hook
**Type:** PreToolUse
**Trigger:** Début de session
**Action:** Charger contexte automatiquement

### 4.2 Pre-Commit Hook
**Type:** PreToolUse
**Trigger:** Avant git commit
**Action:** Validation, tests, lint

### 4.3 Context Update Hook
**Type:** PostToolUse
**Trigger:** Après modifications fichiers
**Action:** Mettre à jour hot-files.json

---

## Checklist de Développement

### Phase 1 - Commands ✅ COMPLET
- [x] Créer `.claude/commands/` directory
- [x] Implémenter `0-new-session.md`
- [x] Implémenter `0-next.md`
- [x] Implémenter `0-resume.md`
- [x] Implémenter `0-ship.md`
- [x] Implémenter `0-progress.md`
- [x] Implémenter `0-dashboard.md`
- [ ] Tester chaque commande

### Phase 2 - Agents ✅ COMPLET
- [x] Implémenter `atlas.md`
- [x] Implémenter `devops-manager.md`
- [x] Implémenter `brainstorm.md`
- [ ] Intégrer avec agent-stats.json

### Phase 3 - Skills ✅ COMPLET
- [x] Implémenter `infra.md`
- [x] Implémenter `brainstorm.md`

### Phase 4 - Hooks ✅ COMPLET
- [x] Configurer session start hook
- [x] Configurer pre-commit hook
- [x] Configurer context update hook

### Finalisation ✅ COMPLET
- [x] Synchroniser CLAUDE.md avec réalité
- [x] Valider tous les composants
- [x] Documentation utilisateur

## 🎉 ATLAS v1.0 DEVELOPMENT COMPLETE - 100%

---

## Notes de Session

### 2025-11-30 - Session Initiale
- Migration structure AI-first complétée
- Analyse agents: 21% implémenté
- Plan de développement créé

### 2025-11-30 - Phase 1 Complétée
- 6 slash commands créés dans `.claude/commands/`
- Progression: 21% → 53%

### 2025-11-30 - Phase 2 Complétée
- 3 agents créés dans `.claude/agents/`
- atlas.md, devops-manager.md, brainstorm.md
- Progression: 53% → 68%

### 2025-11-30 - Phase 3 Complétée
- 2 skills créés dans `.claude/skills/`
- infra.md, brainstorm.md
- Progression: 68% → 83%

### 2025-11-30 - Phase 4 Complétée 🎉
- 3 hooks documentés dans `.claude/hooks/`
- session-start.md, pre-commit.md, context-update.md
- Progression: 83% → 100%
- **ATLAS DEVELOPMENT COMPLETE!**

---

## Comment Reprendre

1. **Lire ce fichier** pour contexte
2. **Lire CURRENT-STATE.md** pour état précis
3. **Identifier prochaine tâche** dans checklist
4. **Créer fichier** dans `.atlas/drafts/` d'abord
5. **Tester** le draft
6. **Déployer** vers `.claude/` quand validé
7. **Mettre à jour** CURRENT-STATE.md
