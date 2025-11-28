#!/bin/bash
# Start SYNAPSE in Development Mode

echo "🚀 Starting SYNAPSE (Dev Mode)..."
echo ""

cd "$(dirname "$0")/.."

# Check if workspace is running
if ! docker network ls | grep -q workspace-network; then
    echo "❌ Workspace not started!"
    echo "📝 Run: cd ../../workspace && ./scripts/start.sh"
    exit 1
fi

# Start SYNAPSE
docker-compose -f docker-compose.dev.yml up --build

echo ""
echo "✅ SYNAPSE Started!"
echo ""
echo "  🌐 Frontend:  http://localhost:4000"
echo "  🔌 Backend:   http://localhost:8001"
echo "  📊 API Docs:  http://localhost:8001/docs"
echo ""
