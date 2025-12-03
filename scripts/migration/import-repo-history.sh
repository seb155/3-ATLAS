#!/bin/bash
# import-repo-history.sh
# Importe l'historique d'un repo GitHub existant dans AXIOM
#
# Usage:
#   ./scripts/migration/import-repo-history.sh <repo-name> <target-path>
#
# Exemples:
#   ./scripts/migration/import-repo-history.sh atlas-framework modules/atlas-framework
#   ./scripts/migration/import-repo-history.sh nexus apps/nexus

set -e

REPO_NAME=$1
TARGET_PATH=$2
GITHUB_USER="${GITHUB_USER:-seb155}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$REPO_NAME" ] || [ -z "$TARGET_PATH" ]; then
    echo "Usage: $0 <repo-name> <target-path>"
    echo ""
    echo "Examples:"
    echo "  $0 atlas-framework modules/atlas-framework"
    echo "  $0 nexus apps/nexus"
    exit 1
fi

REPO_URL="git@github.com:$GITHUB_USER/$REPO_NAME.git"

echo -e "${YELLOW}=== Importing history from $REPO_NAME ===${NC}"
echo "Source: $REPO_URL"
echo "Target: $TARGET_PATH"
echo ""

# Check if target exists
if [ -d "$TARGET_PATH" ]; then
    echo -e "${YELLOW}Target path exists. Will merge histories.${NC}"

    # Remove current content (will be replaced by repo content with history)
    echo "Removing current $TARGET_PATH content..."
    git rm -rf "$TARGET_PATH"
    git commit -m "temp: remove $TARGET_PATH for history import"
fi

# Add remote for the repo
REMOTE_NAME="import-$REPO_NAME"
echo "Adding remote: $REMOTE_NAME -> $REPO_URL"
git remote add "$REMOTE_NAME" "$REPO_URL" 2>/dev/null || git remote set-url "$REMOTE_NAME" "$REPO_URL"

# Fetch the repo
echo "Fetching $REPO_NAME..."
git fetch "$REMOTE_NAME"

# Use subtree to add with history
echo "Adding subtree with history..."
git subtree add --prefix="$TARGET_PATH" "$REMOTE_NAME/main" --squash -m "feat: import $REPO_NAME history into $TARGET_PATH

Imported from: $REPO_URL
This preserves the commit history from the original repository."

# Or without squash to keep full history:
# git subtree add --prefix="$TARGET_PATH" "$REMOTE_NAME/main" -m "feat: import $REPO_NAME with full history"

# Clean up remote
echo "Cleaning up remote..."
git remote remove "$REMOTE_NAME"

echo ""
echo -e "${GREEN}✓ Successfully imported $REPO_NAME into $TARGET_PATH${NC}"
echo ""
echo "The history has been merged. You can now:"
echo "  git log --oneline $TARGET_PATH"
echo ""
echo "To push changes:"
echo "  git push origin main"
