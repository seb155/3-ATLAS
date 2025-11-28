# stop.ps1 - Stop All AXIOM Services

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "   AXIOM Platform - Shutting Down     " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Stop SYNAPSE
Write-Host "Stopping SYNAPSE..." -ForegroundColor Yellow
Set-Location apps\synapse
docker-compose -f docker-compose.dev.yml down 2>$null

# Stop NEXUS (if running)
Write-Host "Stopping NEXUS..." -ForegroundColor Yellow
Set-Location ..\nexus
docker-compose down 2>$null

# Stop PRISM (if running)
Write-Host "Stopping PRISM..." -ForegroundColor Yellow
Set-Location ..\prism
docker-compose down 2>$null

# Stop FORGE Infrastructure
Write-Host ""
Write-Host "Stopping FORGE Infrastructure..." -ForegroundColor Yellow
Set-Location ..\..\forge
docker-compose down

Write-Host ""
Write-Host "All AXIOM services stopped" -ForegroundColor Green
