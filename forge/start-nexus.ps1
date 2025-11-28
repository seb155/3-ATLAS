# ==============================================================================
# START NEXUS APPLICATION - Workspace Integration Mode
# ==============================================================================
# Starts Nexus with shared workspace infrastructure (PostgreSQL, Redis, Traefik)
#
# Usage: .\start-nexus.ps1
# ==============================================================================

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  NEXUS - Knowledge Graph Portal" -ForegroundColor Cyan
Write-Host "  Starting Workspace Integration Mode" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# Load .env file
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

$DOMAIN = $env:DOMAIN
if (-not $DOMAIN) {
    $DOMAIN = "localhost"
}

# Check if Nexus app directory exists
$NEXUS_PATH = "..\apps\nexus"
if (-not (Test-Path $NEXUS_PATH)) {
    # Try direct path
    $NEXUS_PATH = "D:\Projects\nexus"
    if (-not (Test-Path $NEXUS_PATH)) {
        Write-Host "ERROR: Nexus application not found!" -ForegroundColor Red
        Write-Host "Expected at: ..\apps\nexus or D:\Projects\nexus" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To fix:" -ForegroundColor Yellow
        Write-Host "  1. Create symlink: New-Item -ItemType SymbolicLink -Path ..\apps\nexus -Target D:\Projects\nexus" -ForegroundColor White
        Write-Host "  2. Or move Nexus: Move-Item D:\Projects\nexus ..\apps\nexus" -ForegroundColor White
        Write-Host ""
        exit 1
    }
}

Write-Host "[1/5] Starting Core Infrastructure..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start core infrastructure" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/5] Starting Traefik (Reverse Proxy)..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.traefik.yml up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Traefik failed to start (continuing anyway)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/5] Initializing Nexus Database..." -ForegroundColor Yellow
# Check if database is initialized
$DB_CHECK = docker exec forge-postgres psql -U postgres -d postgres -t -c "SELECT 1 FROM pg_database WHERE datname = 'nexus'" 2>$null

if ($DB_CHECK -match "1") {
    Write-Host "  Database 'nexus' already exists" -ForegroundColor Gray
} else {
    Write-Host "  Creating nexus database and workspace_auth schema..." -ForegroundColor Gray
    docker exec -i forge-postgres psql -U postgres < databases\postgres\init\04-nexus-init.sql
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Database initialized successfully" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: Database initialization failed" -ForegroundColor Red
        Write-Host "  Run manually: docker exec -i forge-postgres psql -U postgres < databases\postgres\init\04-nexus-init.sql" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[4/5] Starting Nexus Application..." -ForegroundColor Yellow
Push-Location $NEXUS_PATH
docker-compose -f docker-compose.dev.yml -f docker-compose.traefik-labels.yml up -d --build
$BUILD_EXIT_CODE = $LASTEXITCODE
Pop-Location

if ($BUILD_EXIT_CODE -ne 0) {
    Write-Host "ERROR: Nexus failed to start" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[5/5] Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  NEXUS APPLICATION READY" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXUS Application:" -ForegroundColor Yellow
Write-Host "  Frontend:        " -NoNewline -ForegroundColor Gray
Write-Host "https://nexus.$DOMAIN" -ForegroundColor White
Write-Host "  Backend API:     " -NoNewline -ForegroundColor Gray
Write-Host "https://api-nexus.$DOMAIN/docs" -ForegroundColor White
Write-Host ""
Write-Host "Direct Port Access (bypasses Traefik):" -ForegroundColor Yellow
Write-Host "  Frontend:        " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:5173" -ForegroundColor White
Write-Host "  Backend API:     " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Monitoring & Tools:" -ForegroundColor Yellow
Write-Host "  Grafana:         " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:3000" -ForegroundColor White
Write-Host "  Traefik:         " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8888" -ForegroundColor White
Write-Host "  pgAdmin:         " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:5050" -ForegroundColor White
Write-Host ""
Write-Host "Database:" -ForegroundColor Yellow
Write-Host "  PostgreSQL:      " -NoNewline -ForegroundColor Gray
Write-Host "localhost:5433 (forge-postgres)" -ForegroundColor White
Write-Host "  nexus DB:        " -NoNewline -ForegroundColor Gray
Write-Host "docker exec -it forge-postgres psql -U postgres -d nexus" -ForegroundColor White
Write-Host "  Auth schema:     " -NoNewline -ForegroundColor Gray
Write-Host "\c postgres; SET search_path TO workspace_auth;" -ForegroundColor White
Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "  View logs:       " -NoNewline -ForegroundColor Gray
Write-Host "docker-compose -f $NEXUS_PATH\docker-compose.dev.yml logs -f" -ForegroundColor White
Write-Host "  Stop Nexus:      " -NoNewline -ForegroundColor Gray
Write-Host ".\stop-nexus.ps1" -ForegroundColor White
Write-Host "  Shared auth:     " -NoNewline -ForegroundColor Gray
Write-Host "Login works across Nexus, Synapse, and other workspace apps" -ForegroundColor White
Write-Host ""
Write-Host "Default admin account:" -ForegroundColor Yellow
Write-Host "  Email:           " -NoNewline -ForegroundColor Gray
Write-Host "admin@localhost" -ForegroundColor White
Write-Host "  Password:        " -NoNewline -ForegroundColor Gray
Write-Host "admin" -ForegroundColor Red
Write-Host "                   " -NoNewline
Write-Host "(CHANGE THIS IN PRODUCTION!)" -ForegroundColor Red
Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Happy developing!" -ForegroundColor Green
Write-Host ""
