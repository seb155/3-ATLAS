#!/bin/bash
# Start Workspace Infrastructure

echo "🚀 Starting Workspace Tools..."
echo ""

cd "$(dirname "$0")/.."

docker-compose up -d

echo ""
echo "✅ Workspace Started!"
echo ""
echo "  📊 Prisma Studio: http://localhost:5555"
echo "  🐘 pgAdmin:       http://localhost:5050 (dev@workspace.local / admin)"
echo "  💾 PostgreSQL:    localhost:5433"
echo "  🔴 Redis:         localhost:6379"
echo ""
echo "💡 Tip: Run 'docker-compose logs -f' to see logs"
