#!/bin/bash
# 02-push-repos.sh
# Push les repos préparés vers GitHub
#
# Usage: ./02-push-repos.sh
#
# Prérequis: Avoir créé les repos sur GitHub et exécuté 01-prepare-repos.sh

set -e

TEMP_DIR="${TEMP_DIR:-/tmp/axiom-migration-$(date +%Y%m%d)}"
GITHUB_USER="${GITHUB_USER:-seb155}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== AXIOM Submodule Migration - Phase 2 ===${NC}"
echo "Pushing repos from: $TEMP_DIR"
echo "GitHub user: $GITHUB_USER"
echo ""

# Vérifier que les repos existent
if [ ! -d "$TEMP_DIR" ]; then
    echo -e "${RED}ERROR: Migration directory not found at $TEMP_DIR${NC}"
    echo "Run 01-prepare-repos.sh first!"
    exit 1
fi

# ─────────────────────────────────────────────────────────
# Function: push_repo
# ─────────────────────────────────────────────────────────
push_repo() {
    local dir=$1
    local repo_name=$2

    echo -e "${YELLOW}[Pushing] $repo_name${NC}"

    if [ ! -d "$dir" ]; then
        echo -e "${RED}  WARNING: Directory not found: $dir - Skipping${NC}"
        return 1
    fi

    cd "$dir"

    # Check if remote already exists
    if git remote get-url origin &>/dev/null; then
        echo "  Remote already configured"
    else
        git remote add origin "git@github.com:$GITHUB_USER/$repo_name.git"
    fi

    # Rename branch to main if needed
    git branch -M main 2>/dev/null || true

    # Push
    if git push -u origin main; then
        echo -e "${GREEN}  ✓ Pushed to github.com/$GITHUB_USER/$repo_name${NC}"
    else
        echo -e "${RED}  ✗ Failed to push. Check if repo exists on GitHub.${NC}"
        return 1
    fi

    cd - > /dev/null
}

# ─────────────────────────────────────────────────────────
# Push all repos
# ─────────────────────────────────────────────────────────

echo "Make sure you've created these repos on GitHub:"
echo "  - https://github.com/$GITHUB_USER/forge"
echo "  - https://github.com/$GITHUB_USER/synapse"
echo "  - https://github.com/$GITHUB_USER/nexus"
echo "  - https://github.com/$GITHUB_USER/cortex"
echo "  - https://github.com/$GITHUB_USER/atlas-framework"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""

push_repo "$TEMP_DIR/forge" "forge"
push_repo "$TEMP_DIR/synapse" "synapse"
push_repo "$TEMP_DIR/nexus" "nexus"
push_repo "$TEMP_DIR/cortex" "cortex"
push_repo "$TEMP_DIR/atlas-framework" "atlas-framework"

echo ""
echo -e "${GREEN}=== Phase 2 Complete ===${NC}"
echo ""
echo "All repos pushed to GitHub!"
echo ""
echo -e "${YELLOW}Next step:${NC}"
echo "Run 03-convert-axiom.sh to convert AXIOM to use submodules"
echo ""
echo -e "${RED}⚠️  Make sure all pushes succeeded before continuing!${NC}"
