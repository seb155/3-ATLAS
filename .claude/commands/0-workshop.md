# /0-workshop

Lance ou gere un workshop Design Thinking pour un projet.

## Usage

```text
/0-workshop new [nom-projet]     # Demarrer nouveau workshop
/0-workshop resume [nom-projet]  # Reprendre workshop existant
/0-workshop status [nom-projet]  # Voir progression
/0-workshop list                 # Lister tous les workshops
```

## Actions

### /0-workshop new [nom-projet]

1. Cree la structure de dossiers dans `workshop-[nom-projet]/`
2. Genere les fichiers depuis templates
3. Lance Phase 1: Discovery Interview avec WORKSHOP-FACILITATOR

### /0-workshop resume [nom-projet]

1. Lit `00_SESSION_RECOVERY.md`
2. Charge le contexte de la derniere session
3. Reprend exactement ou c'etait rendu

### /0-workshop status [nom-projet]

1. Affiche progression des 5 phases
2. Liste les artifacts produits
3. Montre prochaine etape

### /0-workshop list

1. Scanne les dossiers `workshop-*/`
2. Affiche chaque workshop avec son status

## Agent Invoque

- **WORKSHOP-FACILITATOR** (opus) - Pour sessions interactives (new, resume)

## Phases du Workshop

| # | Phase | Objectif |
|---|-------|----------|
| 1 | Discovery Interview | Comprendre contexte, frustrations, vision |
| 2 | Problem Definition | Problem statements, personas, MoSCoW |
| 3 | Ideation | Crazy 8s, HMW, solutions |
| 4 | Concept Validation | Prototypes, storyboards, feedback |
| 5 | Specification | PRD, wireframes, roadmap, MVP |

## Structure Creee

```
workshop-[nom-projet]/
├── README.md                    # Index et progression
├── EXECUTIVE_SUMMARY.md         # Resume executif
├── 00_PROCESS_FRAMEWORK.md      # Methodologie
├── 00_SESSION_RECOVERY.md       # Recovery si session perdue
├── sessions/
│   ├── 01_DISCOVERY_INTERVIEW.md
│   ├── 02_PROBLEM_DEFINITION.md
│   ├── 03_IDEATION.md
│   ├── 04_CONCEPT_VALIDATION.md
│   └── 05_SPECIFICATION.md
├── artifacts/                   # Livrables (analyses, bilans)
└── decisions/                   # ADRs
```

## Exemples

```text
# Nouveau projet
User: /0-workshop new app-fitness

WORKSHOP-FACILITATOR:
"Bienvenue dans le Workshop Design Thinking pour app-fitness!

Structure creee dans workshop-app-fitness/

Commencons par la Phase 1: Discovery Interview.

Parle-moi de toi et de ta relation avec le fitness/la sante.
- Comment geres-tu ton entrainement aujourd'hui?
- Quels outils/apps utilises-tu?
- Qu'est-ce qui te frustre le plus?"
```

```text
# Reprendre
User: /0-workshop resume app-fitness

WORKSHOP-FACILITATOR:
"Workshop app-fitness - Reprise

Etat retrouve:
- Phase: 2 - Problem Definition
- Derniere action: Persona principal complete
- Prochaine etape: Criteres de succes

On continue avec les criteres de succes mesurables.
Quels sont les indicateurs qui te diraient que l'app est un succes?"
```

```text
# Status
User: /0-workshop status app-fitness

"Workshop: app-fitness

Progression: 40% (Phase 2/5)

| Phase | Status |
|-------|--------|
| 1. Discovery Interview | COMPLETE |
| 2. Problem Definition | IN PROGRESS |
| 3. Ideation | PENDING |
| 4. Concept Validation | PENDING |
| 5. Specification | PENDING |

Prochaine etape: Finaliser criteres de succes

/0-workshop resume app-fitness pour continuer"
```

## Voir Aussi

- Agent: `.claude/agents/workshop-facilitator.md`
- Skill: `.claude/skills/0_workshop.md`
- Templates: `.claude/templates/workshop/`
- Exemple complet: `workshop/` (Pilote-Patrimoine)
