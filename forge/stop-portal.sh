#!/usr/bin/env bash
# Stop SYNAPSE Portal (All Services) for Linux/macOS

set -euo pipefail

cd "$(dirname "$0")"

echo "Stopping SYNAPSE Platform..."
echo

echo "  Stopping SYNAPSE Application..."
cd ../apps/synapse
docker-compose -f docker-compose.dev.yml down || true
cd ../../workspace

echo "  Stopping ReportPortal..."
docker-compose -f docker-compose.reportportal.yml down 2>/dev/null || true

echo "  Stopping Homepage..."
docker-compose -f docker-compose.homepage.yml down || true

echo "  Stopping Traefik..."
docker-compose -f docker-compose.traefik.yml down || true

echo "  Stopping Core Infrastructure..."
docker-compose down || true

echo
echo "✅ All services stopped"
echo
echo "Network still exists for fast restart."
echo "To remove everything: docker-compose down -v --remove-orphans"
echo

