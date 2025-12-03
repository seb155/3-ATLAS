# Start SYNAPSE Portal (Traefik + Homepage + All Services)
# Complete development environment with reverse proxy

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  🚀 SYNAPSE PLATFORM - Starting Portal" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Load .env file
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            Write-Host "  ✓ Loaded $name" -ForegroundColor Gray
        }
    }
    Write-Host ""
} else {
    Write-Host "  ⚠ No .env file found. Using defaults." -ForegroundColor Yellow
    Write-Host ""
}

$DOMAIN = $env:DOMAIN
if (-not $DOMAIN) {
    $DOMAIN = "localhost"
}

Write-Host "[1/5] Starting Core Infrastructure..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "[2/5] Starting Traefik (Reverse Proxy)..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.traefik.yml up -d

Write-Host ""
Write-Host "[3/5] Starting Homepage (Portal)..." -ForegroundColor Yellow
docker-compose `
    -f docker-compose.yml `
    -f docker-compose.traefik.yml `
    -f docker-compose.homepage.yml `
    -f docker-compose.traefik-labels.yml `
    up -d

Write-Host ""
Write-Host "[4/5] Starting SYNAPSE Application..." -ForegroundColor Yellow
cd ..\apps\synapse
docker-compose `
    -f docker-compose.dev.yml `
    -f docker-compose.traefik-labels.yml `
    up -d
cd ..\..\workspace

Write-Host ""
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  ✅ SYNAPSE PLATFORM READY" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📱 Portal & Services:" -ForegroundColor Yellow
Write-Host "  Portal:       " -NoNewline -ForegroundColor Gray
Write-Host "https://portal.$DOMAIN" -ForegroundColor White
Write-Host "  Traefik:      " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8888" -ForegroundColor White
Write-Host ""
Write-Host "🎯 SYNAPSE Application:" -ForegroundColor Yellow
Write-Host "  Frontend:     " -NoNewline -ForegroundColor Gray
Write-Host "https://synapse.$DOMAIN" -ForegroundColor White
Write-Host "  API:          " -NoNewline -ForegroundColor Gray
Write-Host "https://api.$DOMAIN/docs" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Testing:" -ForegroundColor Yellow
Write-Host "  (Start ReportPortal separately if needed: .\start-reportportal.ps1)" -ForegroundColor Gray
Write-Host ""
Write-Host "📊 Monitoring:" -ForegroundColor Yellow
Write-Host "  Grafana:      " -NoNewline -ForegroundColor Gray
Write-Host "https://grafana.$DOMAIN" -ForegroundColor White
Write-Host "  Loki:         " -NoNewline -ForegroundColor Gray
Write-Host "https://loki.$DOMAIN" -ForegroundColor White
Write-Host ""
Write-Host "💾 Databases:" -ForegroundColor Yellow
Write-Host "  pgAdmin:      " -NoNewline -ForegroundColor Gray
Write-Host "https://pgadmin.$DOMAIN" -ForegroundColor White
Write-Host "  Prisma:       " -NoNewline -ForegroundColor Gray
Write-Host "https://prisma.$DOMAIN" -ForegroundColor White
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "  • Open Portal first: https://portal.$DOMAIN" -ForegroundColor White
Write-Host "  • All services behind Traefik have SSL (auto-generated)" -ForegroundColor White
Write-Host "  • Credentials: .dev/context/credentials.md" -ForegroundColor White
Write-Host "  • Stop all: .\stop-portal.ps1" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Happy developing!" -ForegroundColor Green
Write-Host ""
