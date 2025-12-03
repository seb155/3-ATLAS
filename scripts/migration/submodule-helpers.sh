#!/bin/bash
# submodule-helpers.sh
# Helper functions pour gérer les submodules AXIOM
#
# Usage: source scripts/migration/submodule-helpers.sh
#        axiom-update-all
#        axiom-status

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─────────────────────────────────────────────────────────
# axiom-update-all: Met à jour tous les submodules
# ─────────────────────────────────────────────────────────
axiom-update-all() {
    echo -e "${CYAN}Updating all submodules...${NC}"
    git submodule update --remote --merge

    echo ""
    echo -e "${GREEN}Status:${NC}"
    git submodule status

    # Check for changes
    if ! git diff-index --quiet HEAD --; then
        echo ""
        echo -e "${YELLOW}⚠️  Submodule references changed. Commit with:${NC}"
        echo "  git add . && git commit -m 'chore: update submodules'"
    fi
}

# ─────────────────────────────────────────────────────────
# axiom-status: Affiche le status de tous les submodules
# ─────────────────────────────────────────────────────────
axiom-status() {
    echo -e "${CYAN}=== AXIOM Submodules Status ===${NC}"
    echo ""

    git submodule foreach --quiet '
        branch=$(git rev-parse --abbrev-ref HEAD)
        commit=$(git rev-parse --short HEAD)
        status=""

        # Check for local changes
        if ! git diff-index --quiet HEAD --; then
            status="${status}[modified] "
        fi

        # Check if ahead/behind
        ahead=$(git rev-list --count @{upstream}..HEAD 2>/dev/null || echo "?")
        behind=$(git rev-list --count HEAD..@{upstream} 2>/dev/null || echo "?")

        if [ "$ahead" != "0" ] && [ "$ahead" != "?" ]; then
            status="${status}[ahead:$ahead] "
        fi
        if [ "$behind" != "0" ] && [ "$behind" != "?" ]; then
            status="${status}[behind:$behind] "
        fi

        printf "%-20s %s @ %s %s\n" "$name" "$branch" "$commit" "$status"
    '
}

# ─────────────────────────────────────────────────────────
# axiom-clone: Clone AXIOM avec tous les submodules
# ─────────────────────────────────────────────────────────
axiom-clone() {
    local repo=${1:-"git@github.com:seb155/AXIOM.git"}
    local dest=${2:-"AXIOM"}

    echo -e "${CYAN}Cloning AXIOM with all submodules...${NC}"
    git clone --recurse-submodules "$repo" "$dest"

    echo ""
    echo -e "${GREEN}Done! cd $dest to start working.${NC}"
}

# ─────────────────────────────────────────────────────────
# axiom-work: Commence à travailler sur un submodule
# ─────────────────────────────────────────────────────────
axiom-work() {
    local submodule=$1
    local branch=$2

    if [ -z "$submodule" ]; then
        echo "Usage: axiom-work <submodule> [branch]"
        echo ""
        echo "Submodules:"
        echo "  forge"
        echo "  apps/synapse"
        echo "  apps/nexus"
        echo "  apps/cortex"
        echo "  .atlas"
        return 1
    fi

    if [ ! -d "$submodule" ]; then
        echo -e "${RED}ERROR: Submodule not found: $submodule${NC}"
        return 1
    fi

    cd "$submodule"

    if [ -n "$branch" ]; then
        echo -e "${CYAN}Creating branch: $branch${NC}"
        git checkout -b "$branch"
    fi

    echo -e "${GREEN}Now working in: $submodule${NC}"
    echo "Current branch: $(git rev-parse --abbrev-ref HEAD)"
    echo ""
    echo "When done:"
    echo "  git add . && git commit -m 'your message'"
    echo "  git push origin $(git rev-parse --abbrev-ref HEAD)"
    echo "  cd $(git rev-parse --show-toplevel)"
    echo "  git add $submodule && git commit -m 'chore: update $submodule'"
}

# ─────────────────────────────────────────────────────────
# axiom-sync: Synchronise un submodule avec son remote
# ─────────────────────────────────────────────────────────
axiom-sync() {
    local submodule=$1

    if [ -z "$submodule" ]; then
        echo "Usage: axiom-sync <submodule>"
        return 1
    fi

    echo -e "${CYAN}Syncing $submodule...${NC}"

    cd "$submodule"
    git fetch origin
    git checkout main
    git pull origin main
    cd -

    echo -e "${GREEN}✓ $submodule synced${NC}"
}

# ─────────────────────────────────────────────────────────
# Print available commands when sourced
# ─────────────────────────────────────────────────────────
echo -e "${GREEN}AXIOM submodule helpers loaded!${NC}"
echo ""
echo "Available commands:"
echo "  axiom-update-all  - Update all submodules to latest"
echo "  axiom-status      - Show status of all submodules"
echo "  axiom-clone       - Clone AXIOM with submodules"
echo "  axiom-work        - Start working on a submodule"
echo "  axiom-sync        - Sync a specific submodule"
