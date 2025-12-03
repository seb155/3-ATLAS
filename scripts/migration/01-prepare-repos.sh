#!/bin/bash
# 01-prepare-repos.sh
# Prépare les repos séparés pour chaque composant
#
# Usage: ./01-prepare-repos.sh
#
# IMPORTANT: Sauvegarder AXIOM avant d'exécuter!

set -e  # Exit on error

AXIOM_DIR="${AXIOM_DIR:-/home/user/AXIOM}"
TEMP_DIR="${TEMP_DIR:-/tmp/axiom-migration-$(date +%Y%m%d)}"
GITHUB_USER="${GITHUB_USER:-seb155}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AXIOM Submodule Migration - Phase 1 ===${NC}"
echo "Source: $AXIOM_DIR"
echo "Temp:   $TEMP_DIR"
echo ""

# Vérifier que AXIOM existe
if [ ! -d "$AXIOM_DIR" ]; then
    echo -e "${RED}ERROR: AXIOM directory not found at $AXIOM_DIR${NC}"
    exit 1
fi

# Créer dossier temporaire
mkdir -p "$TEMP_DIR"
echo -e "${GREEN}Created temp directory: $TEMP_DIR${NC}"
echo ""

# ─────────────────────────────────────────────────────────
# Function: migrate_component
# ─────────────────────────────────────────────────────────
migrate_component() {
    local src=$1
    local dest=$2
    local name=$3
    local commit_msg=$4

    echo -e "${YELLOW}[Migrating] $name${NC}"

    if [ ! -d "$src" ]; then
        echo -e "${RED}  WARNING: Source not found: $src - Skipping${NC}"
        return 1
    fi

    # Copy
    cp -r "$src" "$dest"

    # Init git
    cd "$dest"
    rm -rf .git 2>/dev/null || true
    git init -q
    git add .
    git commit -q -m "$commit_msg"

    echo -e "${GREEN}  ✓ Ready at $dest${NC}"
    cd - > /dev/null
}

# ─────────────────────────────────────────────────────────
# 1. FORGE
# ─────────────────────────────────────────────────────────
migrate_component \
    "$AXIOM_DIR/forge" \
    "$TEMP_DIR/forge" \
    "FORGE" \
    "Initial commit: FORGE infrastructure

- Docker Compose configurations (main, traefik, observability)
- Traefik v3.6.2 reverse proxy with wildcard SSL
- Observability stack (Loki, Grafana, Prometheus, OpenTelemetry)
- Database configurations (PostgreSQL, Redis)
- SSL/TLS setup with mkcert
- Sandbox execution environment"

# ─────────────────────────────────────────────────────────
# 2. SYNAPSE
# ─────────────────────────────────────────────────────────
migrate_component \
    "$AXIOM_DIR/apps/synapse" \
    "$TEMP_DIR/synapse" \
    "SYNAPSE" \
    "Initial commit: SYNAPSE MBSE Platform v0.2.5

- FastAPI backend with SQLAlchemy 2.0
- React 19 frontend with TypeScript + Vite
- Rule Engine with event sourcing
- PostgreSQL + MeiliSearch integration
- Template generation (IN-P040, CA-P040)
- Real-time WebSocket DevConsole"

# ─────────────────────────────────────────────────────────
# 3. NEXUS
# ─────────────────────────────────────────────────────────
migrate_component \
    "$AXIOM_DIR/apps/nexus" \
    "$TEMP_DIR/nexus" \
    "NEXUS" \
    "Initial commit: NEXUS Knowledge Graph

- Knowledge graph visualization (3D/2D)
- FastAPI backend with graph traversal
- React frontend with force-directed layout
- Neo4j/TriliumNext integration
- Semantic search capabilities"

# ─────────────────────────────────────────────────────────
# 4. CORTEX
# ─────────────────────────────────────────────────────────
migrate_component \
    "$AXIOM_DIR/apps/cortex" \
    "$TEMP_DIR/cortex" \
    "CORTEX" \
    "Initial commit: CORTEX AI Ecosystem

- Hybrid AI orchestration architecture
- LiteLLM configuration (local Ollama + cloud providers)
- Memory Engine design (HOT/WARM/COLD tiers)
- Intelligence Router with complexity analysis
- Context caching and prompt optimization
- Budget tracking and cost optimization"

# ─────────────────────────────────────────────────────────
# 5. ATLAS-FRAMEWORK
# ─────────────────────────────────────────────────────────
migrate_component \
    "$AXIOM_DIR/.atlas" \
    "$TEMP_DIR/atlas-framework" \
    "ATLAS-FRAMEWORK" \
    "Initial commit: ATLAS Framework for Claude Code

- Agent orchestration system (18+ specialized agents)
- Slash commands (/0-new-session, /0-ship, etc.)
- Session management with hot files
- Context loading strategies
- Parallel agent execution support
- Token optimization guidelines"

# ─────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}=== Phase 1 Complete ===${NC}"
echo ""
echo "Repos prepared at: $TEMP_DIR"
ls -la "$TEMP_DIR"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Create repos on GitHub:"
echo "   https://github.com/new → forge"
echo "   https://github.com/new → synapse"
echo "   https://github.com/new → nexus"
echo "   https://github.com/new → cortex"
echo "   https://github.com/new → atlas-framework"
echo ""
echo "2. Push each repo (run 02-push-repos.sh)"
echo ""
echo -e "${RED}⚠️  DO NOT delete original AXIOM directories yet!${NC}"
