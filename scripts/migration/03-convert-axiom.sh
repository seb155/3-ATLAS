#!/bin/bash
# 03-convert-axiom.sh
# Convertit AXIOM pour utiliser les submodules
#
# Usage: ./03-convert-axiom.sh
#
# ⚠️  ATTENTION: Ce script supprime des dossiers! Sauvegarder d'abord!
# Prérequis: Avoir exécuté 01 et 02

set -e

AXIOM_DIR="${AXIOM_DIR:-/home/user/AXIOM}"
GITHUB_USER="${GITHUB_USER:-seb155}"
BACKUP_DIR="${BACKUP_DIR:-/tmp/axiom-backup-$(date +%Y%m%d-%H%M%S)}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${GREEN}=== AXIOM Submodule Migration - Phase 3 ===${NC}"
echo "AXIOM: $AXIOM_DIR"
echo "GitHub: $GITHUB_USER"
echo ""

# ─────────────────────────────────────────────────────────
# Safety checks
# ─────────────────────────────────────────────────────────
if [ ! -d "$AXIOM_DIR/.git" ]; then
    echo -e "${RED}ERROR: Not a git repository: $AXIOM_DIR${NC}"
    exit 1
fi

cd "$AXIOM_DIR"

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}ERROR: You have uncommitted changes in AXIOM${NC}"
    echo "Please commit or stash them first."
    git status --short
    exit 1
fi

echo -e "${YELLOW}⚠️  WARNING: This will:${NC}"
echo "  1. Create a backup at $BACKUP_DIR"
echo "  2. Remove forge/, apps/synapse/, apps/nexus/, apps/cortex/, .atlas/"
echo "  3. Add them back as git submodules"
echo ""
echo -e "${RED}This is a destructive operation!${NC}"
echo ""
read -p "Type 'YES' to continue: " confirm
if [ "$confirm" != "YES" ]; then
    echo "Aborted."
    exit 1
fi

# ─────────────────────────────────────────────────────────
# Backup
# ─────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}[1/7] Creating backup...${NC}"
mkdir -p "$BACKUP_DIR"
cp -r forge "$BACKUP_DIR/" 2>/dev/null || true
cp -r apps/synapse "$BACKUP_DIR/" 2>/dev/null || true
cp -r apps/nexus "$BACKUP_DIR/" 2>/dev/null || true
cp -r apps/cortex "$BACKUP_DIR/" 2>/dev/null || true
cp -r .atlas "$BACKUP_DIR/" 2>/dev/null || true
echo -e "${GREEN}  ✓ Backup created at $BACKUP_DIR${NC}"

# ─────────────────────────────────────────────────────────
# Remove old directories
# ─────────────────────────────────────────────────────────
echo -e "${CYAN}[2/7] Removing old directories...${NC}"

# Remove from git tracking first
git rm -rf --cached forge 2>/dev/null || true
git rm -rf --cached apps/synapse 2>/dev/null || true
git rm -rf --cached apps/nexus 2>/dev/null || true
git rm -rf --cached apps/cortex 2>/dev/null || true
git rm -rf --cached .atlas 2>/dev/null || true

# Remove directories
rm -rf forge
rm -rf apps/synapse
rm -rf apps/nexus
rm -rf apps/cortex
rm -rf .atlas

# Remove .claude symlink
rm -f .claude

echo -e "${GREEN}  ✓ Old directories removed${NC}"

# ─────────────────────────────────────────────────────────
# Add submodules
# ─────────────────────────────────────────────────────────
echo -e "${CYAN}[3/7] Adding FORGE submodule...${NC}"
git submodule add "git@github.com:$GITHUB_USER/forge.git" forge
echo -e "${GREEN}  ✓ forge${NC}"

echo -e "${CYAN}[4/7] Adding SYNAPSE submodule...${NC}"
git submodule add "git@github.com:$GITHUB_USER/synapse.git" apps/synapse
echo -e "${GREEN}  ✓ apps/synapse${NC}"

echo -e "${CYAN}[5/7] Adding NEXUS submodule...${NC}"
git submodule add "git@github.com:$GITHUB_USER/nexus.git" apps/nexus
echo -e "${GREEN}  ✓ apps/nexus${NC}"

echo -e "${CYAN}[6/7] Adding CORTEX submodule...${NC}"
git submodule add "git@github.com:$GITHUB_USER/cortex.git" apps/cortex
echo -e "${GREEN}  ✓ apps/cortex${NC}"

echo -e "${CYAN}[7/7] Adding ATLAS-FRAMEWORK submodule...${NC}"
git submodule add "git@github.com:$GITHUB_USER/atlas-framework.git" .atlas
echo -e "${GREEN}  ✓ .atlas${NC}"

# ─────────────────────────────────────────────────────────
# Recreate .claude symlink
# ─────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}Recreating .claude symlink...${NC}"
if [ -d ".atlas/claude" ]; then
    ln -sf .atlas/claude .claude
    echo -e "${GREEN}  ✓ .claude → .atlas/claude${NC}"
else
    echo -e "${YELLOW}  ⚠ .atlas/claude not found, skipping symlink${NC}"
fi

# ─────────────────────────────────────────────────────────
# Commit
# ─────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}Committing changes...${NC}"

git add .gitmodules
git add forge apps/synapse apps/nexus apps/cortex .atlas
git add .claude 2>/dev/null || true

git commit -m "refactor: migrate to submodules architecture

Components migrated to separate repositories:
- forge → $GITHUB_USER/forge
- apps/synapse → $GITHUB_USER/synapse
- apps/nexus → $GITHUB_USER/nexus
- apps/cortex → $GITHUB_USER/cortex
- .atlas → $GITHUB_USER/atlas-framework

Benefits:
- Independent version control per component
- Reusable across projects
- Separate CI/CD pipelines
- Clear ownership boundaries

Clone with: git clone --recurse-submodules <repo>"

echo -e "${GREEN}  ✓ Changes committed${NC}"

# ─────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}=== Migration Complete! ===${NC}"
echo ""
echo ".gitmodules:"
cat .gitmodules
echo ""
echo "Submodule status:"
git submodule status
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Push AXIOM: git push origin main"
echo "2. Test fresh clone: git clone --recurse-submodules git@github.com:$GITHUB_USER/AXIOM.git"
echo ""
echo -e "${CYAN}Daily workflow:${NC}"
echo "  # Update all submodules"
echo "  git submodule update --remote --merge"
echo ""
echo "  # Work on a submodule"
echo "  cd apps/synapse"
echo "  git checkout -b feature/xxx"
echo "  # ... make changes ..."
echo "  git commit && git push"
echo ""
echo "  # Update reference in AXIOM"
echo "  cd ../.."
echo "  git add apps/synapse"
echo "  git commit -m 'chore: update synapse'"
echo ""
echo -e "${GREEN}Backup preserved at: $BACKUP_DIR${NC}"
echo "You can delete it once you've verified everything works."
