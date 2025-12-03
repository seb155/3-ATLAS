#!/bin/bash
# import-all-history.sh
# Importe l'historique de tous les repos GitHub existants dans AXIOM
#
# Usage:
#   cd /path/to/AXIOM
#   ./scripts/migration/import-all-history.sh
#
# Prérequis:
#   - SSH configuré pour GitHub
#   - Les repos doivent exister sur GitHub avec du contenu

set -e

GITHUB_USER="${GITHUB_USER:-seb155}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}=== AXIOM - Import Repository Histories ===${NC}"
echo ""

# Define repos to import
# Format: "repo-name:target-path"
REPOS=(
    "atlas-framework:modules/atlas-framework"
    "nexus:apps/nexus"
    # Ajoute d'autres repos ici si nécessaire
    # "synapse:apps/synapse"
    # "forge:modules/forge"
    # "cortex:apps/cortex"
)

echo "Repos to import:"
for entry in "${REPOS[@]}"; do
    repo="${entry%%:*}"
    path="${entry##*:}"
    echo "  - $repo -> $path"
done
echo ""

read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Import each repo
for entry in "${REPOS[@]}"; do
    repo="${entry%%:*}"
    path="${entry##*:}"

    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Importing: $repo -> $path${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    REPO_URL="git@github.com:$GITHUB_USER/$repo.git"

    # Check if repo exists and has content
    if ! git ls-remote "$REPO_URL" HEAD &>/dev/null; then
        echo -e "${RED}✗ Repo $repo not found or empty. Skipping.${NC}"
        continue
    fi

    # Check if target exists and has content
    if [ -d "$path" ] && [ "$(ls -A $path 2>/dev/null)" ]; then
        echo "Target $path exists with content."

        # Backup current content
        echo "Creating backup..."
        BACKUP_DIR="/tmp/axiom-backup-$(date +%Y%m%d)/$path"
        mkdir -p "$(dirname "$BACKUP_DIR")"
        cp -r "$path" "$BACKUP_DIR"

        # Remove from git (but keep backup)
        echo "Removing current $path from git..."
        git rm -rf "$path"
        git commit -m "temp: remove $path for history import from $repo"
    fi

    # Add remote
    REMOTE_NAME="import-$repo"
    git remote remove "$REMOTE_NAME" 2>/dev/null || true
    git remote add "$REMOTE_NAME" "$REPO_URL"

    # Fetch
    echo "Fetching $repo..."
    git fetch "$REMOTE_NAME"

    # Detect default branch
    DEFAULT_BRANCH=$(git remote show "$REMOTE_NAME" | grep "HEAD branch" | cut -d: -f2 | tr -d ' ')
    if [ -z "$DEFAULT_BRANCH" ]; then
        DEFAULT_BRANCH="main"
    fi
    echo "Default branch: $DEFAULT_BRANCH"

    # Add subtree
    echo "Adding as subtree..."
    git subtree add --prefix="$path" "$REMOTE_NAME/$DEFAULT_BRANCH" --squash \
        -m "feat: import $repo history into $path

Imported from: $REPO_URL
Branch: $DEFAULT_BRANCH
This merges the commit history from the original repository."

    # Cleanup
    git remote remove "$REMOTE_NAME"

    echo -e "${GREEN}✓ $repo imported successfully${NC}"
done

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}All imports complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "To view imported history:"
echo "  git log --oneline modules/atlas-framework"
echo "  git log --oneline apps/nexus"
echo ""
echo "To push changes:"
echo "  git push origin main"
