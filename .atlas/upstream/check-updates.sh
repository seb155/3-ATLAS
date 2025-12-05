#!/bin/bash
# Check for upstream updates from Miessler Suite

echo "Checking upstream repositories..."
echo ""

# PAI
echo "=== Personal AI Infrastructure ==="
if [ -d ~/.atlas-upstream/pai ]; then
    cd ~/.atlas-upstream/pai
    git fetch upstream --dry-run 2>&1 | head -5
    BEHIND=$(git rev-list HEAD..upstream/main --count 2>/dev/null || echo "0")
    echo "Commits behind upstream: $BEHIND"
else
    echo "Not cloned yet. Run: git clone https://github.com/seb155/Personal_AI_Infrastructure ~/.atlas-upstream/pai"
fi
echo ""

# Fabric
echo "=== Fabric ==="
if [ -d ~/.atlas-upstream/fabric ]; then
    cd ~/.atlas-upstream/fabric
    git fetch upstream --dry-run 2>&1 | head -5
    BEHIND=$(git rev-list HEAD..upstream/main --count 2>/dev/null || echo "0")
    echo "Commits behind upstream: $BEHIND"
else
    echo "Not cloned yet. Run: git clone https://github.com/seb155/Fabric ~/.atlas-upstream/fabric"
fi

echo ""
echo "Done."
