# ==============================================================================
# NEXUS - Standalone Development Mode
# ==============================================================================
# Runs Nexus with its own PostgreSQL and Redis (NOT workspace integration)
# ==============================================================================

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  NEXUS - Standalone Mode" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Nexus in standalone mode..." -ForegroundColor Yellow
Write-Host "(Uses local PostgreSQL and Redis, not workspace)" -ForegroundColor Gray
Write-Host ""

docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Nexus standalone mode started successfully" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access:" -ForegroundColor Yellow
    Write-Host "  Frontend:  http://localhost:5173" -ForegroundColor White
    Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  Database:  localhost:5432" -ForegroundColor White
    Write-Host "  Redis:     localhost:6379" -ForegroundColor White
    Write-Host ""
    Write-Host "To use workspace integration instead, run from workspace:" -ForegroundColor Gray
    Write-Host "  cd D:\Projects\EPCB-Tools\workspace" -ForegroundColor Gray
    Write-Host "  .\start-nexus.ps1" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "ERROR: Failed to start Nexus" -ForegroundColor Red
}
