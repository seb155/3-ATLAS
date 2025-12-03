# Architecture Submodules - AXIOM Monorepo

**Date:** 2025-12-03
**Objectif:** Structurer AXIOM avec des repos Git séparés pour chaque composant majeur

---

## Vue d'Ensemble

```
AXIOM/                                    # seb155/AXIOM (orchestrateur)
│
├── forge/ ─────────────────────────────► seb155/forge (submodule)
│   └── Infrastructure partagée
│
├── apps/
│   ├── synapse/ ───────────────────────► seb155/synapse (submodule)
│   │   └── MBSE Platform
│   │
│   ├── nexus/ ─────────────────────────► seb155/nexus (submodule)
│   │   └── Knowledge Graph
│   │
│   ├── cortex/ ────────────────────────► seb155/cortex (submodule)
│   │   └── AI Ecosystem
│   │
│   ├── apex/                            # Reste dans AXIOM (pas encore développé)
│   ├── echo/                            # Reste dans AXIOM (pas encore développé)
│   └── atlas/                           # Reste dans AXIOM (minimal)
│
├── .atlas/ ────────────────────────────► seb155/atlas-framework (submodule)
│   └── Claude Code Framework
│
├── .claude → .atlas/claude/             # Symlink (pas un submodule)
│
├── .dev/                                # Reste dans AXIOM (context local)
├── docs/                                # Reste dans AXIOM (docs générales)
└── CLAUDE.md                            # Reste dans AXIOM
```

---

## Décision par Composant

| Composant | Submodule? | Raison |
|-----------|------------|--------|
| **forge/** | ✅ OUI | Infrastructure réutilisable, indépendant |
| **apps/synapse/** | ✅ OUI | App complète, cycle de vie indépendant |
| **apps/nexus/** | ✅ OUI | App complète, déjà bien structurée |
| **apps/cortex/** | ✅ OUI | AI Ecosystem, réutilisable ailleurs |
| **.atlas/** | ✅ OUI | Framework Claude, partageable |
| **apps/apex/** | ❌ NON | Pas encore développé |
| **apps/echo/** | ❌ NON | Pas encore développé |
| **apps/atlas/** | ❌ NON | Minimal, lié à .atlas |
| **.dev/** | ❌ NON | Context spécifique AXIOM |
| **docs/** | ❌ NON | Docs générales AXIOM |

---

## Repos à Créer sur GitHub

```bash
# Créer ces repos sur github.com/seb155/

1. seb155/forge           # Infrastructure Docker + configs
2. seb155/synapse         # MBSE Platform
3. seb155/nexus           # Knowledge Graph
4. seb155/cortex          # AI Ecosystem
5. seb155/atlas-framework # Claude Code Framework
```

---

## Scripts de Migration

### Étape 1: Préparer les repos séparés

```bash
#!/bin/bash
# migrate-to-submodules.sh
# ATTENTION: Sauvegarder AXIOM avant d'exécuter!

AXIOM_DIR="/home/user/AXIOM"
TEMP_DIR="/tmp/axiom-migration"
GITHUB_USER="seb155"

# Créer dossier temporaire
mkdir -p $TEMP_DIR

echo "=== Migration des composants vers repos séparés ==="

# ─────────────────────────────────────────────────────────
# 1. FORGE
# ─────────────────────────────────────────────────────────
echo "[1/5] Migrating FORGE..."
cp -r $AXIOM_DIR/forge $TEMP_DIR/forge
cd $TEMP_DIR/forge
git init
git add .
git commit -m "Initial commit: FORGE infrastructure

- Docker Compose configurations
- Traefik reverse proxy
- Observability stack (Loki, Grafana, Prometheus)
- Database configurations
- SSL/TLS setup scripts"

echo "FORGE ready at $TEMP_DIR/forge"

# ─────────────────────────────────────────────────────────
# 2. SYNAPSE
# ─────────────────────────────────────────────────────────
echo "[2/5] Migrating SYNAPSE..."
cp -r $AXIOM_DIR/apps/synapse $TEMP_DIR/synapse
cd $TEMP_DIR/synapse
git init
git add .
git commit -m "Initial commit: SYNAPSE MBSE Platform

- FastAPI backend with rule engine
- React 19 frontend with TypeScript
- PostgreSQL + MeiliSearch integration
- Docker deployment configurations"

echo "SYNAPSE ready at $TEMP_DIR/synapse"

# ─────────────────────────────────────────────────────────
# 3. NEXUS
# ─────────────────────────────────────────────────────────
echo "[3/5] Migrating NEXUS..."
cp -r $AXIOM_DIR/apps/nexus $TEMP_DIR/nexus
cd $TEMP_DIR/nexus
git init
git add .
git commit -m "Initial commit: NEXUS Knowledge Graph

- Knowledge graph visualization
- FastAPI backend
- React frontend
- Neo4j integration"

echo "NEXUS ready at $TEMP_DIR/nexus"

# ─────────────────────────────────────────────────────────
# 4. CORTEX
# ─────────────────────────────────────────────────────────
echo "[4/5] Migrating CORTEX..."
cp -r $AXIOM_DIR/apps/cortex $TEMP_DIR/cortex
cd $TEMP_DIR/cortex
git init
git add .
git commit -m "Initial commit: CORTEX AI Ecosystem

- Hybrid AI orchestration architecture
- LiteLLM configuration for local/cloud routing
- Memory engine design (HOT/WARM/COLD)
- Intelligence router with complexity analysis"

echo "CORTEX ready at $TEMP_DIR/cortex"

# ─────────────────────────────────────────────────────────
# 5. ATLAS-FRAMEWORK
# ─────────────────────────────────────────────────────────
echo "[5/5] Migrating ATLAS-FRAMEWORK..."
cp -r $AXIOM_DIR/.atlas $TEMP_DIR/atlas-framework
cd $TEMP_DIR/atlas-framework
git init
git add .
git commit -m "Initial commit: ATLAS Framework for Claude Code

- Agent orchestration system
- Slash commands (/0-new-session, /0-ship, etc.)
- Session management
- Context loading strategies"

echo "ATLAS-FRAMEWORK ready at $TEMP_DIR/atlas-framework"

echo ""
echo "=== Migration Phase 1 Complete ==="
echo ""
echo "Next steps:"
echo "1. Create repos on GitHub:"
echo "   - https://github.com/new → forge"
echo "   - https://github.com/new → synapse"
echo "   - https://github.com/new → nexus"
echo "   - https://github.com/new → cortex"
echo "   - https://github.com/new → atlas-framework"
echo ""
echo "2. Push each repo:"
echo "   cd $TEMP_DIR/forge && git remote add origin git@github.com:$GITHUB_USER/forge.git && git push -u origin main"
echo "   cd $TEMP_DIR/synapse && git remote add origin git@github.com:$GITHUB_USER/synapse.git && git push -u origin main"
echo "   cd $TEMP_DIR/nexus && git remote add origin git@github.com:$GITHUB_USER/nexus.git && git push -u origin main"
echo "   cd $TEMP_DIR/cortex && git remote add origin git@github.com:$GITHUB_USER/cortex.git && git push -u origin main"
echo "   cd $TEMP_DIR/atlas-framework && git remote add origin git@github.com:$GITHUB_USER/atlas-framework.git && git push -u origin main"
```

### Étape 2: Convertir AXIOM pour utiliser les submodules

```bash
#!/bin/bash
# convert-axiom-to-submodules.sh
# Exécuter APRÈS avoir pushé tous les repos séparés

AXIOM_DIR="/home/user/AXIOM"
GITHUB_USER="seb155"

cd $AXIOM_DIR

echo "=== Converting AXIOM to use submodules ==="

# ─────────────────────────────────────────────────────────
# 1. Supprimer les anciens dossiers (ATTENTION!)
# ─────────────────────────────────────────────────────────
echo "[1/6] Removing old directories..."
rm -rf forge
rm -rf apps/synapse
rm -rf apps/nexus
rm -rf apps/cortex
rm -rf .atlas

# ─────────────────────────────────────────────────────────
# 2. Ajouter les submodules
# ─────────────────────────────────────────────────────────
echo "[2/6] Adding FORGE submodule..."
git submodule add git@github.com:$GITHUB_USER/forge.git forge

echo "[3/6] Adding SYNAPSE submodule..."
git submodule add git@github.com:$GITHUB_USER/synapse.git apps/synapse

echo "[4/6] Adding NEXUS submodule..."
git submodule add git@github.com:$GITHUB_USER/nexus.git apps/nexus

echo "[5/6] Adding CORTEX submodule..."
git submodule add git@github.com:$GITHUB_USER/cortex.git apps/cortex

echo "[6/6] Adding ATLAS-FRAMEWORK submodule..."
git submodule add git@github.com:$GITHUB_USER/atlas-framework.git .atlas

# ─────────────────────────────────────────────────────────
# 3. Recréer le symlink .claude
# ─────────────────────────────────────────────────────────
echo "Recreating .claude symlink..."
ln -sf .atlas/claude .claude

# ─────────────────────────────────────────────────────────
# 4. Commit les changements
# ─────────────────────────────────────────────────────────
git add .gitmodules
git add forge apps/synapse apps/nexus apps/cortex .atlas
git commit -m "refactor: convert to submodules architecture

- forge → seb155/forge
- apps/synapse → seb155/synapse
- apps/nexus → seb155/nexus
- apps/cortex → seb155/cortex
- .atlas → seb155/atlas-framework

Each component now has its own repository with independent
version control while remaining part of the AXIOM monorepo."

echo ""
echo "=== Conversion Complete ==="
echo ""
echo "Your .gitmodules file:"
cat .gitmodules
```

---

## Structure .gitmodules Finale

```ini
# .gitmodules

[submodule "forge"]
    path = forge
    url = git@github.com:seb155/forge.git
    branch = main

[submodule "apps/synapse"]
    path = apps/synapse
    url = git@github.com:seb155/synapse.git
    branch = main

[submodule "apps/nexus"]
    path = apps/nexus
    url = git@github.com:seb155/nexus.git
    branch = main

[submodule "apps/cortex"]
    path = apps/cortex
    url = git@github.com:seb155/cortex.git
    branch = main

[submodule ".atlas"]
    path = .atlas
    url = git@github.com:seb155/atlas-framework.git
    branch = main
```

---

## Workflow Quotidien

### Cloner AXIOM (nouveau développeur)

```bash
# Clone avec tous les submodules
git clone --recurse-submodules git@github.com:seb155/AXIOM.git

# OU clone puis init submodules
git clone git@github.com:seb155/AXIOM.git
cd AXIOM
git submodule update --init --recursive
```

### Mettre à jour tous les submodules

```bash
# Depuis AXIOM
git submodule update --remote --merge

# OU pour un seul
git submodule update --remote apps/synapse
```

### Travailler sur un submodule (ex: SYNAPSE)

```bash
cd apps/synapse

# Créer une branche
git checkout -b feature/new-rule-type

# Faire des changements...
git add .
git commit -m "feat: add new rule type for cable sizing"
git push origin feature/new-rule-type

# Créer PR sur seb155/synapse
# Après merge...

# Revenir à AXIOM et mettre à jour la référence
cd ../..
git add apps/synapse
git commit -m "chore: update synapse to latest"
git push
```

### Script helper: update-all.sh

```bash
#!/bin/bash
# scripts/update-all-submodules.sh

echo "Updating all submodules to latest..."

git submodule foreach 'git fetch origin && git checkout main && git pull origin main'

echo ""
echo "Status of submodules:"
git submodule status

echo ""
echo "Don't forget to commit if references changed:"
echo "  git add . && git commit -m 'chore: update submodules'"
```

---

## Avantages de cette Architecture

| Avantage | Description |
|----------|-------------|
| **Isolation** | Chaque projet a son propre historique Git |
| **Réutilisation** | FORGE ou CORTEX peuvent être utilisés dans d'autres projets |
| **CI/CD Séparé** | GitHub Actions indépendantes par repo |
| **Permissions** | Collaborateurs différents par projet |
| **Versioning** | Versions stables de chaque composant |
| **Open Source** | Possibilité de rendre certains repos publics |

---

## Considérations

### Quand NE PAS utiliser de submodule

- Composant très petit (< 10 fichiers)
- Fortement couplé au monorepo
- Pas de réutilisation prévue
- Équipe unique travaillant sur tout

### Alternative: Git Subtree

Si tu trouves les submodules trop complexes :

```bash
# Push un dossier vers un repo séparé (sans submodule)
git subtree push --prefix=apps/cortex git@github.com:seb155/cortex.git main

# Pull les changements du repo
git subtree pull --prefix=apps/cortex git@github.com:seb155/cortex.git main
```

**Différence**: L'historique est fusionné, pas de `.gitmodules`

---

## Checklist de Migration

- [ ] Créer les 5 repos sur GitHub
- [ ] Exécuter `migrate-to-submodules.sh`
- [ ] Push chaque repo vers GitHub
- [ ] Exécuter `convert-axiom-to-submodules.sh`
- [ ] Vérifier que tout fonctionne avec `git submodule status`
- [ ] Mettre à jour le README.md d'AXIOM
- [ ] Tester le clone frais avec `--recurse-submodules`

---

*Document créé le 2025-12-03*
