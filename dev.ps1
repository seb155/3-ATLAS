# dev.ps1 - Start AXIOM Development Environment
# Simple 1-command dev environment startup

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "   AXIOM Platform - Development Mode  " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 1. Start FORGE (Infrastructure)
Write-Host "Starting FORGE Infrastructure..." -ForegroundColor Yellow
Set-Location forge
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start FORGE infrastructure" -ForegroundColor Red
    exit 1
}

Write-Host "Waiting for infrastructure to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 2. Start SYNAPSE (Primary App)
Write-Host ""
Write-Host "Starting SYNAPSE Application..." -ForegroundColor Yellow
Set-Location ..\apps\synapse
docker-compose -f docker-compose.dev.yml up --build

# This blocks until you Ctrl+C
# Then runs cleanup automatically
Write-Host ""
Write-Host "Shutting down SYNAPSE..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml down

Write-Host ""
Write-Host "Development session ended" -ForegroundColor Green
Write-Host "FORGE still running. Use .\stop.ps1 to stop everything." -ForegroundColor Cyan
