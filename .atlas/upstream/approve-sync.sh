#!/bin/bash
# Approve and sync upstream changes

REPO=$1
DATE=$(date +%Y-%m-%d)

if [ -z "$REPO" ]; then
    echo "Usage: ./approve-sync.sh [pai|fabric]"
    exit 1
fi

echo ""
echo "⚠️  SYNC REQUIRES YOUR EXPLICIT APPROVAL"
echo ""
read -p "Are you sure you want to sync $REPO from upstream? [y/N] " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Sync cancelled."
    exit 0
fi

case $REPO in
    pai)
        cd ~/.atlas-upstream/pai
        git fetch upstream
        git merge upstream/main
        COMMIT=$(git rev-parse --short HEAD)
        ;;
    fabric)
        cd ~/.atlas-upstream/fabric
        git fetch upstream
        git merge upstream/main
        COMMIT=$(git rev-parse --short HEAD)
        ;;
    *)
        echo "Unknown repo: $REPO"
        exit 1
        ;;
esac

# Log the sync
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "| $DATE | $REPO | $COMMIT | Manual approval |" >> "$SCRIPT_DIR/SYNC_LOG.md"

echo ""
echo "✅ Sync complete for $REPO"
echo "Logged to SYNC_LOG.md"
