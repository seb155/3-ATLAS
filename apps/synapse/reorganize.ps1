# Reorganize SYNAPSE File Structure
# Create clean frontend/ backend/ separation

Write-Host "🗂️  Reorganizing SYNAPSE structure..." -ForegroundColor Cyan
Write-Host ""

$synapseRoot = "d:\Projects\EPCB-Tools\apps\synapse"

# 1. Create proper frontend structure
Write-Host "📁 Creating frontend/ directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "$synapseRoot\frontend" | Out-Null

# 2. Move frontend files to frontend/
Write-Host "📦 Moving frontend files..." -ForegroundColor Yellow

# Move source code
Move-Item -Path "$synapseRoot\src" -Destination "$synapseRoot\frontend\src" -Force
Move-Item -Path "$synapseRoot\index.tsx" -Destination "$synapseRoot\frontend\index.tsx" -Force
Move-Item -Path "$synapseRoot\index.html" -Destination "$synapseRoot\frontend\index.html" -Force

# Move config files
Move-Item -Path "$synapseRoot\package.json" -Destination "$synapseRoot\frontend\package.json" -Force
Move-Item -Path "$synapseRoot\package-lock.json" -Destination "$synapseRoot\frontend\package-lock.json" -Force
Move-Item -Path "$synapseRoot\tsconfig.json" -Destination "$synapseRoot\frontend\tsconfig.json" -Force
Move-Item -Path "$synapseRoot\vite.config.ts" -Destination "$synapseRoot\frontend\vite.config.ts" -Force

# Move build files
Move-Item -Path "$synapseRoot\Dockerfile.frontend" -Destination "$synapseRoot\frontend\Dockerfile" -Force
Move-Item -Path "$synapseRoot\nginx.conf" -Destination "$synapseRoot\frontend\nginx.conf" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ Reorganization Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📂 New Structure:" -ForegroundColor Cyan
Write-Host "  apps/synapse/"
Write-Host "    ├── backend/          # Backend API"
Write-Host "    ├── frontend/         # Frontend React app"
Write-Host "    ├── docker-compose.dev.yml"
Write-Host "    └── scripts/"
