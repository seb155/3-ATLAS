# Workshop - {{PROJECT_NAME}}

> Documentation complete du processus de discovery et reconception.
> **Derniere mise a jour**: {{DATE}}

---

## Resume Executif

**{{PROJECT_NAME}}** est [DESCRIPTION A COMPLETER].

**Utilisateur principal**: [A COMPLETER]
**Objectif principal**: [A COMPLETER]

Voir [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md) pour le resume complet.

---

## Structure du Dossier

```
workshop-{{PROJECT_NAME}}/
├── README.md                       # Ce fichier (index)
├── EXECUTIVE_SUMMARY.md            # Resume executif du workshop
├── 00_SESSION_RECOVERY.md          # Pour reprendre si session perdue
├── 00_PROCESS_FRAMEWORK.md         # Methodologie Design Thinking
│
├── sessions/                       # Sessions de travail
│   ├── 01_DISCOVERY_INTERVIEW.md   # Phase 1
│   ├── 02_PROBLEM_DEFINITION.md    # Phase 2
│   ├── 03_IDEATION.md              # Phase 3
│   ├── 04_CONCEPT_VALIDATION.md    # Phase 4
│   └── 05_SPECIFICATION.md         # Phase 5
│
├── artifacts/                      # Livrables produits
│   └── (generes pendant workshop)
│
└── decisions/                      # Decisions architecturales (ADR)
    └── (generes phase 3+)
```

---

## Progression

| # | Phase | Statut | Date | Document |
|---|-------|--------|------|----------|
| 1 | Discovery Interview | EN COURS | - | [01_DISCOVERY_INTERVIEW.md](./sessions/01_DISCOVERY_INTERVIEW.md) |
| 2 | Problem Definition | - | - | [02_PROBLEM_DEFINITION.md](./sessions/02_PROBLEM_DEFINITION.md) |
| 3 | Ideation | - | - | [03_IDEATION.md](./sessions/03_IDEATION.md) |
| 4 | Concept Validation | - | - | [04_CONCEPT_VALIDATION.md](./sessions/04_CONCEPT_VALIDATION.md) |
| 5 | Specification | - | - | [05_SPECIFICATION.md](./sessions/05_SPECIFICATION.md) |

---

## Insights Cles

### Probleme Principal
> [A COMPLETER APRES PHASE 1]

### Besoins Prioritaires (MoSCoW Must Have)
1. [A COMPLETER APRES PHASE 2]

### Decisions Techniques
- [A COMPLETER APRES PHASE 3]

---

## Comment Reprendre une Session

Si la conversation Claude est perdue:

```
/0-workshop resume {{PROJECT_NAME}}
```

### Fichiers a lire en priorite
1. `00_SESSION_RECOVERY.md` - Statut et derniere action
2. `EXECUTIVE_SUMMARY.md` - Vision globale
3. La derniere session en cours (selon le statut)

---

## Participants

- **Client/Stakeholder**: [NOM]
- **Facilitateur**: Claude (AI)

---

## Livrables Attendus

| Phase | Livrable | Format |
|-------|----------|--------|
| Phase 1-2 | Problem Statements + Bilan | Markdown |
| Phase 3 | Solutions techniques + Trade-offs | Markdown |
| Phase 4 | Prototypes/Wireframes | ASCII/Diagrams |
| Phase 5 | PRD + Roadmap + Epics | Markdown |
