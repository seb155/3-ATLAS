# Commands Reference

Référence complète de toutes les commandes Atlas.

## Convention de nommage

| Préfixe | Catégorie | Invoqué par |
|---------|-----------|-------------|
| `0-*` | Session management | User |
| `1-*` | Workflow starters | User |
| `9-*` | Workflow finishers | User |
| `zz-*` | Agent-internal | Auto |
| (none) | Standard commands | User |

---

## Commandes de Session (0-*)

### /0-new-session

**Description:** Démarre une nouvelle session avec chargement complet du contexte.

**Usage:**
```bash
/0-new-session
```

**Actions:**
1. Vérifie s'il y a une session active
2. Si oui, propose de continuer/archiver/ignorer
3. Charge le contexte complet (project-state, hot-context, journal)
4. Détecte l'environnement
5. Propose les priorités

**Quand utiliser:**
- Première session du jour
- Après une longue pause
- Pour charger tout le contexte

---

### /0-resume

**Description:** Récupère le contexte après un `/compact` ou crash.

**Usage:**
```bash
/0-resume
```

**Actions:**
1. Cherche session active dans `.dev/1-sessions/active/`
2. Charge le dernier checkpoint de `.dev/checkpoints/`
3. Lit `.dev/context/hot-context.md`
4. Parse le compact summary
5. Reconstruit la todo list
6. Reprend où c'était rendu

**Quand utiliser:**
- Après un `/compact` automatique
- Après un crash de navigateur
- Pour reprendre une session interrompue

---

### /0-checkpoint

**Description:** Crée un checkpoint manuel du contexte.

**Usage:**
```bash
/0-checkpoint              # Checkpoint simple
/0-checkpoint [note]       # Avec une note
```

**Actions:**
1. Collecte le contexte actuel (session, tasks, git)
2. Crée `.dev/checkpoints/YYYYMMDD-HHMM-checkpoint.md`
3. Met à jour hot-context.md
4. Confirme la création

**Quand utiliser:**
- Avant un refactoring majeur
- Avant une opération risquée
- Quand le contexte atteint 60-70%
- À des points stratégiques du travail

---

### /0-dashboard

**Description:** Affiche l'état actuel de la session.

**Usage:**
```bash
/0-dashboard
```

**Affiche:**
- Session active
- Tâches en cours
- Temps écoulé
- Progression

---

### /0-progress

**Description:** Vue d'ensemble de la roadmap.

**Usage:**
```bash
/0-progress
```

**Affiche:**
- Sprint actuel
- Tâches complétées
- Prochaines étapes
- Blockers

---

### /0-backlog

**Description:** Gestion du backlog.

**Usage:**
```bash
/0-backlog
```

**Actions:**
- Liste les items du backlog
- Permet d'ajouter/modifier/prioriser

---

### /0-workshop

**Description:** Démarre une session de Design Thinking.

**Usage:**
```bash
/0-workshop new [topic]    # Nouvelle session
/0-workshop resume         # Reprendre
```

---

## Démarreurs de Workflow (1-*)

### /1-dev

**Description:** Démarre une session de développement avec tracking.

**Usage:**
```bash
/1-dev              # Démarre ou reprend
/1-dev [topic]      # Nouvelle session avec topic
```

**Actions:**
1. Vérifie s'il y a une session active
2. Vérifie le backlog pour items urgents
3. Crée `.dev/1-sessions/active/current-session.md`
4. Charge le contexte (hot-context, project-state)
5. Propose les prochaines actions

**Fichier créé:**
```markdown
# Session: [Topic]

**Started:** 2025-01-29 14:30
**Type:** dev
**Branch:** [git branch]
**Status:** active

---

## Objective
[Objectif de la session]

## Progress
- [ ] Task 1

## Next Steps
1. [Action suivante]
```

---

### /1-brainstorm

**Description:** Démarre une session de brainstorm avec auto-documentation.

**Usage:**
```bash
/1-brainstorm              # Sans topic
/1-brainstorm [topic]      # Avec topic
```

**Actions:**
1. Vérifie session active
2. Crée session type "brainstorm"
3. Propose techniques (mind mapping, crazy 8s, decision matrix)
4. Auto-sauvegarde à la fin

**Techniques disponibles:**
- Mind mapping
- Crazy 8s
- Decision matrix
- Trade-off analysis

**À la fin:**
- Résume les insights clés
- Liste les actions
- Archive dans journal
- Propose de créer des items backlog

---

### /1-debug

**Description:** Démarre une session de debug avec investigation.

**Usage:**
```bash
/1-debug              # Général
/1-debug [error]      # Avec contexte d'erreur
```

**Phases:**
1. **Information Gathering** - Collecte erreur, logs, fichiers
2. **Hypothesis** - Formule des hypothèses
3. **Root Cause** - Identifie la cause
4. **Fix** - Applique et vérifie le fix

**Documentation automatique:**
```markdown
## Investigation

### Hypothesis 1: [Description]
- Evidence for: [...]
- Evidence against: [...]
- Status: testing | confirmed | rejected

## Root Cause
**Identified:** 2025-01-29 15:30
**Description:** [Cause]
**Location:** file:line

## Fix
**Applied:** 2025-01-29 16:00
**Solution:** [Solution]
```

---

### /1-init-system

**Description:** Initialise Atlas dans un workspace.

**Usage:**
```bash
/1-init-system              # Workspace courant
/1-init-system [path]       # Workspace spécifié
```

**Actions:**
1. Vérifie si `.claude/` existe
2. Localise atlas-agent-framework
3. Crée junction/symlink vers `.claude/`
4. Valide la structure
5. Crée CLAUDE.md workspace si nécessaire

**Windows:**
```powershell
cmd /c mklink /J ".claude" "C:\path\to\atlas-agent-framework"
```

**Linux/macOS:**
```bash
ln -s ~/path/to/atlas-agent-framework .claude
```

---

### /1-init-project

**Description:** Initialise la structure `.dev/` dans un projet.

**Usage:**
```bash
/1-init-project              # Projet courant
/1-init-project [path]       # Projet spécifié
```

**Structure créée:**
```
.dev/
├── 0-backlog/
│   ├── ideas.md
│   ├── bugs.md
│   └── features.md
├── 1-sessions/
│   ├── active/
│   └── archive/
├── context/
│   ├── project-state.md
│   ├── decisions.md
│   └── hot-context.md
├── journal/
├── reports/
└── checkpoints/
```

**Fichiers initialisés:**
- `project-state.md` - Template avec placeholders
- `decisions.md` - Template ADR
- Backlog files - Templates vides avec priorités

---

## Finisseurs de Workflow (9-*)

### /9-archive

**Description:** Archive la session courante proprement.

**Usage:**
```bash
/9-archive              # Archive avec résumé auto
/9-archive [summary]    # Avec résumé custom
```

**Actions:**
1. Vérifie qu'il y a une session active
2. Génère un résumé
3. Déplace vers `.dev/1-sessions/archive/YYYY-MM/`
4. Ajoute entrée au journal
5. Propose d'ajouter tasks incomplètes au backlog
6. Nettoie le dossier active/

**Statuts possibles:**
- `completed` - Tout terminé
- `abandoned` - Changement de priorité
- `paused` - Stop temporaire

---

### /9-ship

**Description:** Workflow Git complet (test + commit + push).

**Usage:**
```bash
/9-ship
```

**Actions:**
1. Exécute les tests
2. Vérifie le linting
3. Build le projet
4. Propose message de commit
5. Commit et push

---

## Commandes Standard

| Commande | Description |
|----------|-------------|
| `/app` | Application-specific actions |
| `/architect` | Architecture decisions |
| `/brainstorm` | Quick brainstorm (legacy) |
| `/commit` | Create commit |
| `/debug` | Quick debug (legacy) |
| `/docs` | Update documentation |
| `/genesis` | Meta-agent evolution |
| `/implement` | Implement feature |
| `/integrate` | Integration tasks |
| `/release` | Release workflow |
| `/status` | Project status |
| `/system` | System commands |
| `/test` | Run tests |

---

## Commandes Internes (zz-*)

Ces commandes sont utilisées automatiquement par les agents:

| Commande | Description |
|----------|-------------|
| `zz-infra` | Infrastructure management |
| `zz-agent-draft` | Create new agents |
| `zz-api-endpoint` | API scaffolding |
| `zz-docker-service` | Docker services |
| `zz-react-component` | React components |
| `zz-backlog-manager` | Backlog operations |

---

## Voir aussi

- [Session Management](session-management.md)
- [Templates Reference](templates-reference.md)
