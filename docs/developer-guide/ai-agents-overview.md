# AI Agents System - Guide Rapide

> **TL;DR:** Un systeme d'assistants AI specialises qui travaillent ensemble pour t'aider a developper plus vite.

---

## C'est Quoi?

Imagine une equipe de developpeurs AI, chacun expert dans son domaine:

```
Toi: "Ajoute un bouton refresh sur la liste des projets"
     ↓
ATLAS (chef): "OK, c'est du frontend simple. FRONTEND-BUILDER, a toi!"
     ↓
FRONTEND-BUILDER: "Je cree le bouton avec Zustand et Lucide icons..."
     ↓
QA-TESTER: "Je verifie que ca marche..."
     ↓
Resultat: Code propre, teste, pret a commit
```

---

## Les Agents en 30 Secondes

### Les Chefs (pensent, planifient)

| Agent | Role | Quand l'utiliser |
|-------|------|------------------|
| **ATLAS** | Chef d'orchestre | Toujours actif, il decide qui fait quoi |
| **BRAINSTORM** | Ideation | "Comment je pourrais faire X?" |
| **SYSTEM-ARCHITECT** | Meta-agent | "Les agents sont trop lents" |

### Les Planificateurs (analysent, decomposent)

| Agent | Role | Quand l'utiliser |
|-------|------|------------------|
| **PLANNER** | Decompose les taches | Taches complexes (>3 etapes) |
| **DEBUGGER** | Analyse les erreurs | "TypeError: Cannot read..." |
| **UX-DESIGNER** | Design UI/UX | "Ameliore l'interface de..." |

### Les Builders (codent)

| Agent | Role | Specialite |
|-------|------|------------|
| **BACKEND-BUILDER** | Code serveur | FastAPI, SQLAlchemy, APIs |
| **FRONTEND-BUILDER** | Code client | React, TypeScript, Zustand |
| **ARCHITECT-BUILDER** | Refactoring majeur | Migration, restructuration |
| **INTEGRATION-BUILDER** | Cross-app | Integration SYNAPSE/NEXUS |
| **DEVOPS-BUILDER** | Infrastructure | Docker, CI/CD |
| **DOC-WRITER** | Documentation | README, API docs |

### Les Validateurs (verifient)

| Agent | Role | Quand |
|-------|------|-------|
| **QA-TESTER** | Tests | Apres chaque changement |
| **ISSUE-REPORTER** | Bug reports | Problemes detectes |

### Les Trackers (suivent)

| Agent | Role | Quand |
|-------|------|-------|
| **DEV-TRACKER** | Journal dev | Fin de session |
| **GIT-MANAGER** | Git/GitHub | Commits, releases, PRs |

---

## Comment Utiliser?

### Methode 1: Parler naturellement

```
Toi: "Ajoute une feature de notifications"
ATLAS: "Je vois 3 approches possibles... [propose des options]"
```

### Methode 2: Slash Commands

| Commande | Action |
|----------|--------|
| `/new-session` | Demarre une nouvelle session |
| `/status` | Voir l'etat du projet |
| `/implement [feature]` | Implementer quelque chose |
| `/debug [erreur]` | Analyser une erreur |
| `/test` | Lancer les tests |
| `/commit` | Creer un commit propre |
| `/brainstorm [idee]` | Session creative |

### Methode 3: Commands avancees

| Commande | Pour quoi |
|----------|-----------|
| `/architect [tache]` | Refactoring majeur (utilise Opus) |
| `/integrate [apps]` | Integration entre apps (utilise Opus) |
| `/release [version]` | Preparer une release |
| `/system` | Parler directement au meta-agent |

---

## Exemples Concrets

### Exemple 1: Ajouter une feature simple

```
Toi: /implement ajouter un bouton de refresh

ATLAS: "Tache simple detectee. Je dispatch au FRONTEND-BUILDER..."

FRONTEND-BUILDER: "J'ajoute:
- handleRefresh() dans ProjectList.tsx
- Bouton avec icone RefreshCw
- Invalidation du cache Zustand
Done!"

QA-TESTER: "Tests passes. Pret a commit."

Toi: /commit
GIT-MANAGER: "feat(synapse): add refresh button to project list"
```

### Exemple 2: Debugger une erreur

```
Toi: /debug TypeError: Cannot read property 'id' of undefined

DEBUGGER: "J'analyse...

Cause: L'API retourne des nulls dans la liste.
Fichier: ProjectList.tsx:45

Solution recommandee: Filtrer les nulls cote API.

Tu veux que j'implemente?"

Toi: "oui"

BACKEND-BUILDER: "Fixed. L'API exclut maintenant les soft-deleted."
```

### Exemple 3: Refactoring majeur

```
Toi: /architect migrer de Context a Zustand

ARCHITECT-BUILDER (Opus): "Migration detectee.

Analyse:
- 5 Contexts a migrer
- 12 composants impactes

Plan:
1. Creer authStore, projectStore, uiStore
2. Migrer composant par composant
3. Supprimer les anciens Contexts

Tu approuves cette approche?"
```

---

## Les Modeles AI

Chaque agent utilise le bon modele pour sa tache:

| Modele | Usage | Agents |
|--------|-------|--------|
| **Opus** | Taches complexes | ATLAS, BRAINSTORM, ARCHITECT-BUILDER |
| **Sonnet** | Code/planning | PLANNER, DEBUGGER, BACKEND/FRONTEND |
| **Haiku** | Taches simples | QA-TESTER, DOC-WRITER, GIT-MANAGER |

---

## Structure des Fichiers

```
.claude/
├── agents/           # Definition des 15 agents
│   ├── orchestrators/    # ATLAS, BRAINSTORM, SYSTEM-ARCHITECT
│   ├── planners/         # PLANNER, DEBUGGER, UX-DESIGNER
│   ├── builders/         # BACKEND, FRONTEND, DEVOPS, DOCS
│   ├── builders-opus/    # ARCHITECT, INTEGRATION
│   ├── validators/       # QA-TESTER, ISSUE-REPORTER
│   └── trackers/         # DEV-TRACKER, GIT-MANAGER
│
├── commands/         # 13 slash commands
│   ├── new-session.md
│   ├── implement.md
│   ├── debug.md
│   └── ...
│
├── skills/           # Templates reutilisables
│   ├── api-endpoint/     # Template FastAPI
│   ├── react-component/  # Template React
│   └── docker-service/   # Template Docker
│
└── context/          # Memoire persistante
    ├── project.md        # Contexte projet
    ├── preferences.md    # Tes preferences
    └── session-history.md
```

---

## FAQ

### Q: Ca marche avec quel editeur?
**R:** Claude Code (VSCode extension ou CLI)

### Q: C'est specifique a AXIOM?
**R:** Non, le systeme est generique. Tu peux le copier dans un autre projet.

### Q: Ca coute combien?
**R:** Ca utilise ton quota Claude existant. Opus = plus cher, Haiku = moins cher.

### Q: Je peux modifier les agents?
**R:** Oui! Edite les fichiers `.claude/agents/*.md` ou utilise `/system` pour demander des changements.

### Q: Comment je sais quel agent est utilise?
**R:** ATLAS t'indique toujours quel agent il invoque.

---

## Pour Aller Plus Loin

- [Documentation complete](ai-agents-system.md) - Architecture detaillee
- [Checklist](ai-agents-checklist.md) - Etat d'implementation
- [CLAUDE.md](../../CLAUDE.md) - Instructions projet

---

**Version:** 1.0 | **Date:** 2025-11-28
