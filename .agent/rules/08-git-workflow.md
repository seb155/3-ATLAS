# Git Workflow Protocol

**Purpose:** Empêcher les conflits de merge et protéger la branche principale.

---

## 1. Branching Strategy (OBLIGATOIRE)

### Règle Fondamentale
```
main = PRODUCTION SEULEMENT
Tout développement = sur une branche séparée
```

### Branches Protégées (JAMAIS de commit direct)
- `main` - Code stable, déployé en production
- `develop` - Integration (si utilisé)

### Branches de Développement
| Type | Préfixe | Exemple | Usage |
|------|---------|---------|-------|
| Feature | `feat/` ou `feature/` | `feat/csv-import` | Nouvelle fonctionnalité |
| Bug Fix | `fix/` ou `bugfix/` | `fix/login-404` | Correction de bug |
| Hotfix | `hotfix/` | `hotfix/auth-token` | Fix urgent production |
| Release | `release/` | `release/v0.3.0` | Préparation release |
| Refactor | `refactor/` | `refactor/api-structure` | Refactoring code |
| Docs | `docs/` | `docs/api-guide` | Documentation |

### Convention de Nommage
```
<type>/<description-courte>

Exemples:
- feat/csv-import
- fix/multi-tenancy-filter
- refactor/zustand-stores
```

---

## 2. Vérification au Démarrage de Session (AI DOIT)

### Étape 1: Vérifier la branche actuelle
```bash
git branch --show-current
```

### Étape 2: Si sur `main` ou `master`
**STOP! Ne pas commencer à coder.**

**Action AI obligatoire:**
```
⚠️ ATTENTION: Vous êtes sur la branche 'main'.
Le développement direct sur main est interdit.

Options:
1. Créer une nouvelle branche: git checkout -b feat/<description>
2. Basculer sur une branche existante: git checkout <branch-name>

Quelle branche voulez-vous utiliser?
```

### Étape 3: Vérifier les changements non commités
```bash
git status --short
```
- Si changements sur `main` → **Avertir l'utilisateur** avant de créer une branche

---

## 3. Workflow de Développement

### Nouvelle Feature
```bash
# 1. Partir de main à jour
git checkout main
git pull origin main

# 2. Créer la branche
git checkout -b feat/<feature-name>

# 3. Développer + Commits réguliers
git add .
git commit -m "feat: description courte"

# 4. Push vers origin
git push -u origin feat/<feature-name>

# 5. Créer Pull Request (ou merge si solo dev)
```

### Bug Fix
```bash
git checkout main
git pull origin main
git checkout -b fix/<bug-description>
# ... développer ...
git push -u origin fix/<bug-description>
```

---

## 4. Pull Request Guidelines

### Quand créer une PR
- Toute feature complète
- Tout bug fix testé
- Avant de merger vers main

### Contenu de la PR
```markdown
## Description
[Résumé des changements]

## Type de changement
- [ ] Feature (nouvelle fonctionnalité)
- [ ] Fix (correction de bug)
- [ ] Refactor (pas de changement fonctionnel)
- [ ] Docs (documentation)

## Tests
- [ ] Tests auto passent
- [ ] Tests manuels effectués

## Checklist
- [ ] Code suit les conventions du projet
- [ ] Pas de secrets/credentials exposés
- [ ] Documentation mise à jour si nécessaire
```

---

## 5. Merge Strategy

### Pour les features
```bash
# Squash merge recommandé (garde historique propre)
git checkout main
git merge --squash feat/<feature-name>
git commit -m "feat: <description complète>"
git branch -d feat/<feature-name>
```

### Pour les releases
```bash
# Merge normal (préserve les commits)
git checkout main
git merge release/v0.3.0
git tag v0.3.0
```

---

## 6. Interdit (AI NE DOIT JAMAIS)

| Action | Pourquoi |
|--------|----------|
| ❌ `git push origin main` | Bypass protection |
| ❌ `git push --force` | Détruit l'historique |
| ❌ Commit sur main sans branche | Crée des conflits |
| ❌ Merge sans validation user | Risque de régression |

---

## 7. Résolution de Conflits

### Si conflit lors d'un merge
1. **Identifier les fichiers en conflit:** `git status`
2. **Résoudre manuellement** chaque conflit
3. **Tester** avant de committer
4. **Committer la résolution:** `git commit -m "merge: resolve conflicts"`

### Si conflit entre branches
```bash
# Option 1: Rebase (historique linéaire)
git checkout feat/ma-feature
git rebase main
# Résoudre conflits
git push --force-with-lease origin feat/ma-feature

# Option 2: Merge (préserve historique)
git checkout feat/ma-feature
git merge main
# Résoudre conflits
git push origin feat/ma-feature
```

---

## 8. Récupération d'Erreurs

### Committed sur main par erreur
```bash
# 1. Créer une branche avec le commit
git branch feat/recovery-<description>

# 2. Reset main au commit précédent
git checkout main
git reset --hard HEAD~1

# 3. Continuer sur la nouvelle branche
git checkout feat/recovery-<description>
```

### Push sur main par erreur (si pas encore mergé par d'autres)
```bash
# ATTENTION: Dangereux - demander confirmation user
git push --force-with-lease origin main
```

---

## Checklist AI (à chaque session)

- [ ] Vérifier branche actuelle (`git branch --show-current`)
- [ ] Si sur main → Proposer création de branche
- [ ] Avant commit → Confirmer qu'on n'est PAS sur main
- [ ] Avant push → Vérifier la destination
- [ ] Avant merge → Obtenir validation utilisateur

---

## 9. Versioning & Tagging Strategy

### Semantic Versioning (MAJOR.MINOR.PATCH)

```
v0.3.0
│ │ └─ PATCH: Bug fixes, small improvements
│ └─── MINOR: New features, sprint completion
└───── MAJOR: Breaking changes, major phase completion
```

### Version ↔ MVP Phase Alignment

| Version Range | Phase | Description |
|---------------|-------|-------------|
| `v0.1.x` | Foundation | Initial prototype, basic features |
| `v0.2.x` | MVP Prep | UI foundation, architecture cleanup |
| `v0.3.x` | **MVP Week 1** | CSV Import + UI Polish |
| `v0.4.x` | **MVP Week 2** | Rule Engine + Workflow Logs |
| `v0.5.x` | **MVP Week 3** | Package Export + Templates |
| `v0.6.x` | **MVP Week 4** | Tests + CI/CD + Demo Prep |
| `v1.0.0` | **MVP Complete** | Demo-ready release (Dec 20) |

### Tag Naming Convention

```bash
# Release tags (on main after merge)
v0.3.0              # Sprint/feature release
v0.3.1              # Patch/hotfix
v1.0.0-rc.1         # Release candidate
v1.0.0              # Production release

# Milestone tags (optional - for easy navigation)
mvp-week-1-start    # Beginning of sprint
mvp-week-1-done     # Sprint completion
mvp-demo-ready      # Final demo version
```

### When to Create Tags

| Event | Tag Type | Example |
|-------|----------|---------|
| Sprint complet | MINOR bump | `v0.3.0` → `v0.4.0` |
| Feature merged | PATCH bump | `v0.3.0` → `v0.3.1` |
| Bug fix | PATCH bump | `v0.3.1` → `v0.3.2` |
| MVP Complete | MAJOR bump | `v0.6.x` → `v1.0.0` |

### Tag Commands

```bash
# Create annotated tag (recommended)
git tag -a v0.3.0 -m "MVP Week 1: CSV Import + UI Polish"

# Push tags to remote
git push origin v0.3.0
git push --tags  # Push all tags

# List tags
git tag -l "v0.*"

# View tag details
git show v0.3.0

# Delete tag (if error)
git tag -d v0.3.0
git push origin --delete v0.3.0
```

### AI Responsibilities for Versioning

**AI DOIT:**
- Proposer version bump après feature/sprint completion
- Créer tag annoté avec message descriptif
- Mettre à jour CHANGELOG.md
- Mettre à jour version dans package.json

**AI NE DOIT PAS:**
- Créer tag sans approbation User
- Changer MAJOR version sans discussion
- Skip la mise à jour du CHANGELOG

### CHANGELOG Format

```markdown
## [0.3.0] - 2025-12-02

### Added
- CSV Import: 5-stage pipeline with validation
- Upload UI component with progress indicator

### Changed
- AppLayout: improved error handling

### Fixed
- Multi-tenancy filter on assets endpoint
```

---

**Version:** 1.1
**Last Updated:** 2025-11-28
**Related:** `version-master` agent, `/10-new-feature-mvp` workflow
