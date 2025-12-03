#!/bin/bash
# push-all-repos.sh
# Exécuter depuis ta machine locale après avoir cloné AXIOM
#
# Usage:
#   cd /path/to/AXIOM
#   chmod +x scripts/migration/push-all-repos.sh
#   ./scripts/migration/push-all-repos.sh

set -e

GITHUB_USER="seb155"
TEMP_DIR="/tmp/axiom-submodules-$(date +%Y%m%d)"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== AXIOM Submodules - Push to GitHub ===${NC}"
echo ""

# Detect AXIOM directory
AXIOM_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
echo "AXIOM directory: $AXIOM_DIR"
echo "Temp directory: $TEMP_DIR"
echo ""

mkdir -p "$TEMP_DIR"

# Function to prepare and push a repo
push_repo() {
    local src_path=$1
    local repo_name=$2
    local commit_msg=$3

    echo -e "${YELLOW}[$repo_name]${NC} Preparing..."

    # Copy to temp
    rm -rf "$TEMP_DIR/$repo_name"
    cp -r "$src_path" "$TEMP_DIR/$repo_name"
    cd "$TEMP_DIR/$repo_name"

    # Remove any existing .git
    rm -rf .git

    # Init and commit
    git init -q
    git add .
    git commit -q -m "$commit_msg"
    git branch -M main

    # Add remote and push
    git remote add origin "git@github.com:$GITHUB_USER/$repo_name.git"

    echo -e "${YELLOW}[$repo_name]${NC} Pushing to GitHub..."
    if git push -u origin main --force; then
        echo -e "${GREEN}[$repo_name]${NC} ✓ Success"
    else
        echo -e "${RED}[$repo_name]${NC} ✗ Failed"
        return 1
    fi

    cd - > /dev/null
}

# Push all repos
push_repo "$AXIOM_DIR/forge" "forge" "Initial commit: FORGE infrastructure

- Docker Compose configurations
- Traefik reverse proxy
- Observability stack (Loki, Grafana, Prometheus)
- Database configurations"

push_repo "$AXIOM_DIR/apps/synapse" "synapse" "Initial commit: SYNAPSE MBSE Platform

- FastAPI backend with SQLAlchemy 2.0
- React 19 frontend with TypeScript
- Rule Engine with event sourcing
- PostgreSQL + MeiliSearch integration"

push_repo "$AXIOM_DIR/apps/nexus" "nexus" "Initial commit: NEXUS Knowledge Graph

- Knowledge graph visualization
- FastAPI backend
- React frontend
- TriliumNext integration"

push_repo "$AXIOM_DIR/apps/cortex" "cortex" "Initial commit: CORTEX AI Ecosystem

- Hybrid AI orchestration
- LiteLLM configuration
- Memory Engine design
- Intelligence Router"

push_repo "$AXIOM_DIR/.atlas" "atlas-framework" "Initial commit: ATLAS Framework

- Agent orchestration system
- Slash commands
- Session management
- Context loading strategies"

echo ""
echo -e "${GREEN}=== All repos pushed! ===${NC}"
echo ""
echo "Next step: Run convert-axiom.sh to add them as submodules"
echo "  ./scripts/migration/convert-axiom.sh"
