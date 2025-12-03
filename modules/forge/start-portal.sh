#!/usr/bin/env bash
# Start SYNAPSE Portal (Traefik + Homepage + All Services) for Linux/macOS

set -euo pipefail

cd "$(dirname "$0")"

echo "========================================================"
echo "  🚀 SYNAPSE PLATFORM - Starting Portal"
echo "========================================================"
echo

if [ -f ".env" ]; then
  export $(grep -v '^\s*#' .env | grep -E '^\s*[A-Za-z_][A-Za-z0-9_]*=' | xargs -d '\n')
  echo "  ✓ Loaded environment variables from .env"
  echo
else
  echo "  ⚠ No .env file found. Using defaults."
  echo
fi

DOMAIN="${DOMAIN:-localhost}"

echo "[1/5] Starting Core Infrastructure..."
docker-compose up -d

echo
echo "[2/5] Starting Traefik (Reverse Proxy)..."
docker-compose -f docker-compose.yml -f docker-compose.traefik.yml up -d

echo
echo "[3/5] Starting Homepage (Portal)..."
docker-compose \
  -f docker-compose.yml \
  -f docker-compose.traefik.yml \
  -f docker-compose.homepage.yml \
  -f docker-compose.traefik-labels.yml \
  up -d

echo
echo "[4/5] Starting SYNAPSE Application..."
cd ../apps/synapse
docker-compose \
  -f docker-compose.dev.yml \
  -f docker-compose.traefik-labels.yml \
  up -d
cd ../../workspace

echo
echo "========================================================"
echo "  ✅ SYNAPSE PLATFORM READY"
echo "========================================================"
echo
echo "📱 Portal & Services:"
echo "  Portal:        https://portal.$DOMAIN"
echo "  Traefik:       http://localhost:8888"
echo
echo "🎯 SYNAPSE Application:"
echo "  Frontend:      https://synapse.$DOMAIN"
echo "  API:           https://api.$DOMAIN/docs"
echo
echo "🧪 Testing:"
echo "  (Start ReportPortal separately if needed: ./start-reportportal.sh)"
echo
echo "📊 Monitoring:"
echo "  Grafana:       https://grafana.$DOMAIN"
echo "  Loki:          https://loki.$DOMAIN"
echo
echo "💾 Databases:"
echo "  pgAdmin:       https://pgadmin.$DOMAIN"
echo "  Prisma:        https://prisma.$DOMAIN"
echo
echo "========================================================"
echo
echo "💡 Tips:"
echo "  • Open Portal first: https://portal.$DOMAIN"
echo "  • All services behind Traefik have SSL (auto-generated)"
echo "  • Credentials: .dev/context/credentials.md"
echo "  • Stop all: ./stop-portal.sh"
echo
echo "🚀 Happy developing!"
echo

