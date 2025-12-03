---
name: backlog-manager
description: |
  Trie, reformate et priorise les items du backlog humain.
  Suggere quels items ajouter au sprint ou roadmap.
---

# Skill: Backlog Manager

Analyse le backlog brut, reformate les items clairement, les priorise, et suggere lesquels promouvoir vers le sprint ou roadmap.

## Usage

```text
skill: "backlog-manager"
```

Ou via commande: `/0-backlog`

## Fichiers

| Fichier | Action |
|---------|--------|
| `.dev/0-backlog/backlog.md` | Lecture (source) |
| `.dev/context/task-queue.md` | Ecriture (destination) |
| `.dev/context/project-state.md` | Lecture (contexte) |

## Workflow

### Etape 1: Lecture

Lire le fichier `.dev/0-backlog/backlog.md` pour identifier tous les items bruts.

**Format d'entree typique:**
```markdown
2025-11-28: note brute de l'humain avec idee pas forcement claire...
2025-11-29: autre idee rapide a trier plus tard
```

### Etape 2: Analyse & Reformatage

Pour chaque item brut:

1. **Identifier le type:**
   - `FEATURE` - Nouvelle fonctionnalite
   - `BUG` - Correction de bug
   - `INFRA` - Infrastructure/DevOps
   - `DOC` - Documentation
   - `REFACTOR` - Refactoring/Tech debt
   - `TEST` - Tests
   - `RULE` - Regle pour agents AI

2. **Reformater clairement:**
   - Titre concis (max 10 mots)
   - Description claire (1-2 phrases)

3. **Evaluer la priorite:**

| Critere | Poids | Evaluation |
|---------|-------|------------|
| **Impact** | 40% | Haut / Moyen / Bas |
| **Urgence** | 30% | Haut / Moyen / Bas |
| **Effort** | 20% | Bas (rapide) / Moyen / Haut (long) |
| **Dependances** | 10% | Bloque autres? Oui/Non |

### Etape 3: Affichage

Presenter la liste triee au format suivant:

```markdown
## Backlog Trie (X items)

### Haute Priorite (Sprint Suggere)

1. **[TYPE]** Titre reformate
   - Description claire
   - Impact: X | Effort: Y | Urgence: Z
   - Source: "texte original..." (date)
   - Suggestion: Sprint actuel

### Moyenne Priorite (Roadmap)

2. **[TYPE]** Titre reformate
   - Description claire
   - Impact: X | Effort: Y
   - Source: "texte original..."
   - Suggestion: Phase X du roadmap

### Basse Priorite (Garder en Backlog)

3. **[TYPE]** Titre reformate
   - Description claire
   - Source: "texte original..."

---

## Actions Suggerees

Quels items veux-tu promouvoir vers task-queue?
- [ ] Item #1 → Sprint actuel
- [ ] Item #2 → Backlog task-queue
- [ ] Aucun pour l'instant
```

### Etape 4: Approbation

Attendre la reponse de l'utilisateur. Il peut:
- Approuver des items specifiques (ex: "1 et 2")
- Modifier la priorite
- Rejeter tous les items
- Demander des clarifications

### Etape 5: Migration

Pour chaque item approuve:

1. **Ajouter a task-queue.md:**
```markdown
## Backlog
- [ ] [TYPE] Titre reformate (Ajoute: YYYY-MM-DD)
```

2. **Mettre a jour backlog.md:**
```markdown
## Traite
- [Formate: YYYY-MM-DD] Texte original → Migre vers task-queue

## Brut (En attente)
- Items restants...
```

## Exemple Complet

**Input (backlog.md):**
```markdown
2025-11-28: rajoute linfo pour les agent ai quand il cree des mockup data il doivent les cree via un script seed pas juste inventer des choses
2025-11-28: cree un skill pour trier les backlog
```

**Output:**
```markdown
## Backlog Trie (2 items)

### Haute Priorite (Sprint Suggere)

1. **[RULE]** Regle: Mock data via seed scripts
   - Les agents AI doivent creer les donnees de test via des scripts seed pour populer la DB correctement, pas inventer des donnees fictives inline.
   - Impact: Haut | Effort: Bas | Urgence: Moyen
   - Source: "rajoute linfo pour les agent ai..." (2025-11-28)
   - Suggestion: Sprint actuel (regle a ajouter immediatement)

2. **[FEATURE]** Skill backlog-manager
   - Creer un skill pour trier, reformater et prioriser les items du backlog humain.
   - Impact: Moyen | Effort: Moyen | Urgence: Bas
   - Source: "cree un skill pour trier..." (2025-11-28)
   - Suggestion: Sprint actuel (en cours)

---

## Actions Suggerees

Quels items veux-tu promouvoir vers task-queue?
- [ ] Item #1 → Sprint actuel
- [ ] Item #2 → Backlog task-queue
```

## Notes

- **Conserver l'historique**: Toujours garder trace de la date de formatage
- **Ne pas supprimer**: Deplacer vers section "Traite", pas supprimer
- **Demander confirmation**: Ne jamais migrer sans approbation explicite
- **Contexte MVP**: Lire project-state.md pour comprendre les priorites actuelles
