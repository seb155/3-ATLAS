---
description: View and triage backlog - format, prioritize, suggest sprint items
---

# /0-view-backlog

Trie, reformate et priorise les items du backlog humain. Suggère quels items promouvoir vers le sprint ou roadmap.

## Usage

```bash
/0-view-backlog              # Backlog du projet courant
/0-view-backlog echo         # Backlog du projet ECHO
/0-view-backlog synapse      # Backlog du projet SYNAPSE
```

## Arguments

- `[project-id]` (optional): Identifiant du projet cible
  - Case-insensitive
  - Résolution via Rule 31 (project-resolution.md)

## Workflow

1. **Lecture** - Lit `.dev/0-backlog/backlog.md`
2. **Analyse** - Identifie et parse chaque item brut
3. **Reformatage** - Rephrase clairement (titre + description)
4. **Priorisation** - Score: Impact (40%) + Urgence (30%) + Effort (20%) + Deps (10%)
5. **Affichage** - Liste triée avec suggestions
6. **Approbation** - Attendre validation utilisateur
7. **Migration** - Déplacer items approuvés vers task-queue.md
8. **Historique** - Marquer `[Formaté: YYYY-MM-DD]` dans backlog.md

## Categories

| Type | Description |
|------|-------------|
| `FEATURE` | Nouvelle fonctionnalité |
| `BUG` | Correction de bug |
| `INFRA` | Infrastructure/DevOps |
| `DOC` | Documentation |
| `REFACTOR` | Refactoring/Tech debt |
| `TEST` | Tests |
| `RULE` | Règle pour agents AI |

## Format de Sortie

```text
📂 Projet: ECHO (Voice Assistant)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BACKLOG TRIAGE - 2025-MM-DD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Haute Priorité (Sprint Suggéré)

1. [TYPE] Titre reformaté
   Description claire en 1-2 phrases.
   Impact: Haut | Effort: Bas | Urgence: Moyen
   Source: "texte original..." (date)

## Moyenne Priorité (Roadmap)

2. [TYPE] Titre reformaté
   Description claire.
   Impact: Moyen | Effort: Moyen

## Basse Priorité (Garder en Backlog)

3. [TYPE] Titre reformaté
   Description.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Promouvoir vers task-queue?
1. Item #1 → Sprint   2. Item #2 → Backlog   3. Aucun
```

## Fichiers

| Fichier | Action |
|---------|--------|
| `.dev/0-backlog/backlog.md` | Lecture + mise à jour historique |
| `.dev/context/task-queue.md` | Écriture (items approuvés) |
| `.dev/context/project-state.md` | Lecture (contexte MVP) |

## When to use

**Use /0-view-backlog when:**
- Tu as accumulé des notes rapides dans le backlog
- Tu veux organiser tes idées
- Tu prépares un sprint
- Tu veux voir ce qui est important

**Ne pas utiliser si:**
- Le backlog est vide
- Tu veux juste voir les tâches actuelles → `/0-view-status`

## Skill associé

Ce command invoque le skill `backlog-manager`.

---

**Tip:** Écris tes idées brutes dans `.dev/0-backlog/backlog.md`, puis `/0-view-backlog` pour les organiser!

## See Also

- `/0-view-status` - Current session status
- `/0-view-roadmap` - Full roadmap
