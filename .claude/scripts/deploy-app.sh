#!/bin/bash
# ============================================================================
# ATLAS Deploy Script - Deploy apps to forge (dev) or homelab (prod)
# ============================================================================
#
# Usage: deploy-app.sh <app> <env>
#
# Examples:
#   deploy-app.sh findash forge     # Deploy to local Docker
#   deploy-app.sh findash homelab   # Deploy to Homelab Docker VM
#
# ============================================================================

set -e

APP=$1
ENV=$2

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# App configurations (path to docker-compose)
declare -A APP_PATHS
APP_PATHS["findash"]="/home/seb/projects/perso/FinDash"
APP_PATHS["nexus"]="/home/seb/projects/AXIOM/apps/nexus"
APP_PATHS["echo"]="/home/seb/projects/AXIOM/apps/echo"
APP_PATHS["synapse"]="/home/seb/projects/AXIOM/apps/synapse"
APP_PATHS["mechvision"]="/home/seb/projects/mechvision"

# Homelab Docker VM
HOMELAB_HOST="docker@192.168.10.55"
HOMELAB_APPS_DIR="/apps"

# Validate arguments
if [ -z "$APP" ] || [ -z "$ENV" ]; then
    echo -e "${RED}Error: Missing arguments${NC}"
    echo "Usage: deploy-app.sh <app> <env>"
    echo ""
    echo "Available apps:"
    for app in "${!APP_PATHS[@]}"; do
        echo "  - $app"
    done
    echo ""
    echo "Environments:"
    echo "  - forge    (local Docker)"
    echo "  - homelab  (Proxmox Docker VM)"
    exit 1
fi

# Check if app exists
if [ -z "${APP_PATHS[$APP]}" ]; then
    echo -e "${RED}Error: Unknown app '$APP'${NC}"
    echo "Available apps: ${!APP_PATHS[@]}"
    exit 1
fi

APP_PATH="${APP_PATHS[$APP]}"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Deploying $APP to $ENV${NC}"
echo -e "${YELLOW}========================================${NC}"

case $ENV in
    forge)
        echo -e "${GREEN}[FORGE]${NC} Local Docker deployment"

        if [ ! -f "$APP_PATH/docker-compose.yml" ]; then
            echo -e "${RED}Error: No docker-compose.yml found at $APP_PATH${NC}"
            exit 1
        fi

        cd "$APP_PATH"

        echo "Building and starting containers..."
        docker-compose down 2>/dev/null || true
        docker-compose build --no-cache
        docker-compose up -d

        echo ""
        echo -e "${GREEN}Deployed successfully!${NC}"
        echo "Container status:"
        docker-compose ps
        ;;

    homelab)
        echo -e "${GREEN}[HOMELAB]${NC} Remote Docker deployment to $HOMELAB_HOST"

        # Check SSH connectivity
        echo "Checking SSH connection..."
        if ! ssh -o ConnectTimeout=5 "$HOMELAB_HOST" "echo 'Connected'" 2>/dev/null; then
            echo -e "${RED}Error: Cannot connect to $HOMELAB_HOST${NC}"
            echo "Make sure:"
            echo "  1. The Homelab is accessible"
            echo "  2. SSH key is configured"
            echo "  3. VPN/Tailscale is connected if remote"
            exit 1
        fi

        # Sync files to homelab
        echo "Syncing files to homelab..."
        rsync -avz --exclude 'node_modules' --exclude '.git' --exclude 'dist' \
            "$APP_PATH/" "$HOMELAB_HOST:$HOMELAB_APPS_DIR/$APP/"

        # Deploy on homelab
        echo "Starting containers on homelab..."
        ssh "$HOMELAB_HOST" "cd $HOMELAB_APPS_DIR/$APP && docker-compose down 2>/dev/null || true && docker-compose up -d --build"

        echo ""
        echo -e "${GREEN}Deployed successfully to homelab!${NC}"
        echo "Container status:"
        ssh "$HOMELAB_HOST" "cd $HOMELAB_APPS_DIR/$APP && docker-compose ps"
        ;;

    *)
        echo -e "${RED}Error: Unknown environment '$ENV'${NC}"
        echo "Available environments: forge, homelab"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}========================================${NC}"
