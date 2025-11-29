---
description: Trie et priorise le backlog brut - reformate, suggere sprint/roadmap
---

# /0-backlog

Trie, reformate et priorise les items du backlog humain. Suggere quels items promouvoir vers le sprint ou roadmap.

## Workflow

1. **Lecture** - Lit `.dev/0-backlog/backlog.md`
2. **Analyse** - Identifie et parse chaque item brut
3. **Reformatage** - Rephrase clairement (titre + description)
4. **Priorisation** - Score: Impact (40%) + Urgence (30%) + Effort (20%) + Deps (10%)
5. **Affichage** - Liste triee avec suggestions
6. **Approbation** - Attendre validation utilisateur
7. **Migration** - Deplacer items approuves vers task-queue.md
8. **Historique** - Marquer `[Formate: YYYY-MM-DD]` dans backlog.md

## Categories

| Type | Description |
|------|-------------|
| `FEATURE` | Nouvelle fonctionnalite |
| `BUG` | Correction de bug |
| `INFRA` | Infrastructure/DevOps |
| `DOC` | Documentation |
| `REFACTOR` | Refactoring/Tech debt |
| `TEST` | Tests |
| `RULE` | Regle pour agents AI |

## Format de Sortie

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BACKLOG TRIAGE - 2025-MM-DD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Haute Priorite (Sprint Suggere)

1. [TYPE] Titre reformate
   Description claire en 1-2 phrases.
   Impact: Haut | Effort: Bas | Urgence: Moyen
   Source: "texte original..." (date)

## Moyenne Priorite (Roadmap)

2. [TYPE] Titre reformate
   Description claire.
   Impact: Moyen | Effort: Moyen

## Basse Priorite (Garder en Backlog)

3. [TYPE] Titre reformate
   Description.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Promouvoir vers task-queue?
1. Item #1 → Sprint   2. Item #2 → Backlog   3. Aucun
```

## Fichiers

| Fichier | Action |
|---------|--------|
| `.dev/0-backlog/backlog.md` | Lecture + mise a jour historique |
| `.dev/context/task-queue.md` | Ecriture (items approuves) |
| `.dev/context/project-state.md` | Lecture (contexte MVP) |

## Format Historique

Apres migration, backlog.md devient:

```markdown
## Traite
- [Formate: 2025-11-28] Texte original → Migre vers task-queue

## Brut (En attente)
- 2025-11-29: Nouvelle idee...
```

## When to use

**Use /0-backlog when:**
- Tu as accumule des notes rapides dans le backlog
- Tu veux organiser tes idees
- Tu prepares un sprint
- Tu veux voir ce qui est important

**Ne pas utiliser si:**
- Le backlog est vide
- Tu veux juste voir les taches actuelles → `/0-dashboard`

## Skill associe

Ce command invoque le skill `backlog-manager`.

```text
skill: "backlog-manager"
```

---

**Tip:** Ecris tes idees brutes dans `.dev/0-backlog/backlog.md`, puis `/0-backlog` pour les organiser!
