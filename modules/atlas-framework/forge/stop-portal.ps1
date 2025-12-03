# Stop SYNAPSE Portal (All Services)

Write-Host "Stopping SYNAPSE Platform..." -ForegroundColor Yellow
Write-Host ""

# Stop Synapse app
Write-Host "  Stopping SYNAPSE Application..." -ForegroundColor Gray
cd ..\apps\synapse
docker-compose -f docker-compose.dev.yml down
cd ..\..\workspace

# Stop ReportPortal (if running)
Write-Host "  Stopping ReportPortal..." -ForegroundColor Gray
docker-compose -f docker-compose.reportportal.yml down 2>$null

# Stop Homepage
Write-Host "  Stopping Homepage..." -ForegroundColor Gray
docker-compose -f docker-compose.homepage.yml down

# Stop Traefik
Write-Host "  Stopping Traefik..." -ForegroundColor Gray
docker-compose -f docker-compose.traefik.yml down

# Stop core infrastructure
Write-Host "  Stopping Core Infrastructure..." -ForegroundColor Gray
docker-compose down

Write-Host ""
Write-Host "✅ All services stopped" -ForegroundColor Green
Write-Host ""
Write-Host "Network still exists for fast restart." -ForegroundColor Gray
Write-Host "To remove everything: docker-compose down -v --remove-orphans" -ForegroundColor Gray
Write-Host ""
