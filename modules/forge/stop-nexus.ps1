# Stop NEXUS Application

Write-Host "Stopping Nexus..." -ForegroundColor Yellow

$NEXUS_PATH = "..\apps\nexus"
if (-not (Test-Path $NEXUS_PATH)) {
    $NEXUS_PATH = "D:\Projects\nexus"
}

Push-Location $NEXUS_PATH
docker-compose -f docker-compose.dev.yml down
Pop-Location

Write-Host "Nexus stopped. Core infrastructure still running." -ForegroundColor Green
Write-Host "To stop all: docker-compose down" -ForegroundColor Gray
