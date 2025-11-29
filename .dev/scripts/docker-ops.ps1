#Requires -Version 5.1
<#
.SYNOPSIS
    AXIOM Docker Operations - Start, Stop, Restart, Status, Test

.DESCRIPTION
    Manages all AXIOM and personal project Docker containers with proper
    startup/shutdown order respecting dependencies.

.PARAMETER Action
    The operation to perform:
    - start   : Start all containers (FORGE -> AXIOM -> Personal)
    - stop    : Stop all containers (reverse order)
    - restart : Stop then start
    - status  : Show container status
    - test    : Network connectivity test

.EXAMPLE
    .\docker-ops.ps1 start
    .\docker-ops.ps1 stop
    .\docker-ops.ps1 status
    .\docker-ops.ps1 test

.NOTES
    Author: AXIOM Team
    Version: 1.0.0
    Date: 2025-11-29
#>

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "restart", "status", "test")]
    [string]$Action = "status"
)

# Configuration
$ProjectsRoot = "D:\Projects"
$AxiomRoot = "$ProjectsRoot\AXIOM"

# Docker Compose paths (in startup order)
$ComposeProjects = @(
    @{ Name = "FORGE Core"; Path = "$AxiomRoot\forge"; File = "docker-compose.yml"; Services = @("forge-postgres", "forge-redis", "forge-traefik") }
    @{ Name = "FORGE Services"; Path = "$AxiomRoot\forge"; File = "docker-compose.yml"; Services = @() }
    @{ Name = "SYNAPSE"; Path = "$AxiomRoot\apps\synapse"; File = "docker-compose.dev.yml"; Services = @() }
    @{ Name = "Note_synch"; Path = "$ProjectsRoot\Note_synch"; File = "docker-compose.yml"; Services = @() }
    @{ Name = "Pulse"; Path = "$ProjectsRoot\8-Perso\Homelab_MSH\dashboard\pulse"; File = "docker-compose.yml"; Services = @() }
    @{ Name = "FinDash"; Path = "$ProjectsRoot\8-Perso\FinDash"; File = "docker-compose.yml"; Services = @() }
)

# Service ports for testing
$ServicePorts = @{
    "forge-grafana" = 3000
    "forge-loki" = 3100
    "forge-traefik" = 8888
    "synapse-backend" = 8001
    "synapse-frontend" = 4000
    "trilium-sync" = 6200
    "neo4j-browser" = 6201
    "graph-api" = 6203
    "pulse" = 6301
    "findash" = 6400
}

# Colors
function Write-Status($Status, $Message) {
    switch ($Status) {
        "ok"      { Write-Host "[OK] " -ForegroundColor Green -NoNewline; Write-Host $Message }
        "warn"    { Write-Host "[WARN] " -ForegroundColor Yellow -NoNewline; Write-Host $Message }
        "error"   { Write-Host "[FAIL] " -ForegroundColor Red -NoNewline; Write-Host $Message }
        "info"    { Write-Host "[INFO] " -ForegroundColor Cyan -NoNewline; Write-Host $Message }
        "skip"    { Write-Host "[SKIP] " -ForegroundColor DarkGray -NoNewline; Write-Host $Message }
    }
}

function Write-Header($Text) {
    Write-Host ""
    Write-Host "=== $Text ===" -ForegroundColor White
    Write-Host ""
}

# Actions
function Start-All {
    Write-Header "Starting AXIOM Infrastructure"

    foreach ($project in $ComposeProjects) {
        Write-Status "info" "Starting $($project.Name)..."

        if (-not (Test-Path $project.Path)) {
            Write-Status "skip" "$($project.Name) - path not found"
            continue
        }

        Push-Location $project.Path
        try {
            if ($project.Services.Count -gt 0) {
                # Start specific services first
                docker compose -f $project.File up -d $project.Services 2>&1 | Out-Null
                Start-Sleep -Seconds 3
            }
            docker compose -f $project.File up -d 2>&1 | Out-Null
            Write-Status "ok" "$($project.Name) started"
        }
        catch {
            Write-Status "error" "$($project.Name) failed: $_"
        }
        finally {
            Pop-Location
        }
    }

    Write-Header "Startup Complete"
    Get-Status
}

function Stop-All {
    Write-Header "Stopping AXIOM Infrastructure"

    # Reverse order for shutdown
    $reversed = $ComposeProjects[($ComposeProjects.Count - 1)..0]

    foreach ($project in $reversed) {
        Write-Status "info" "Stopping $($project.Name)..."

        if (-not (Test-Path $project.Path)) {
            Write-Status "skip" "$($project.Name) - path not found"
            continue
        }

        Push-Location $project.Path
        try {
            docker compose -f $project.File down 2>&1 | Out-Null
            Write-Status "ok" "$($project.Name) stopped"
        }
        catch {
            Write-Status "error" "$($project.Name) failed: $_"
        }
        finally {
            Pop-Location
        }
    }

    Write-Header "Shutdown Complete"
}

function Restart-All {
    Stop-All
    Write-Host ""
    Write-Status "info" "Waiting 5 seconds..."
    Start-Sleep -Seconds 5
    Start-All
}

function Get-Status {
    Write-Header "Docker Status"

    # Get all containers
    $containers = docker ps -a --format "{{.Names}}|{{.Status}}|{{.Ports}}" 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Status "error" "Docker not responding"
        return
    }

    # Group by project
    $forge = $containers | Where-Object { $_ -match "^forge-" }
    $synapse = $containers | Where-Object { $_ -match "^synapse-" }
    $nexus = $containers | Where-Object { $_ -match "^nexus-" }
    $personal = $containers | Where-Object { $_ -match "^(trilium|notes-|pulse|findash|homelab|pilote)" }

    # Display
    Write-Host "FORGE Infrastructure:" -ForegroundColor Cyan
    foreach ($c in $forge) {
        $parts = $c -split '\|'
        $name = $parts[0]
        $status = $parts[1]
        if ($status -match "Up") {
            Write-Status "ok" "$name - $status"
        } else {
            Write-Status "error" "$name - $status"
        }
    }

    Write-Host ""
    Write-Host "AXIOM Applications:" -ForegroundColor Cyan
    foreach ($c in $synapse) {
        $parts = $c -split '\|'
        $name = $parts[0]
        $status = $parts[1]
        if ($status -match "Up") {
            Write-Status "ok" "$name - $status"
        } else {
            Write-Status "error" "$name - $status"
        }
    }

    Write-Host ""
    Write-Host "Personal Projects:" -ForegroundColor Cyan
    foreach ($c in $personal) {
        $parts = $c -split '\|'
        $name = $parts[0]
        $status = $parts[1]
        if ($status -match "Up") {
            if ($status -match "unhealthy|restarting") {
                Write-Status "warn" "$name - $status"
            } else {
                Write-Status "ok" "$name - $status"
            }
        } else {
            Write-Status "error" "$name - $status"
        }
    }

    # Summary
    $running = ($containers | Where-Object { $_ -match "Up" }).Count
    $total = $containers.Count
    Write-Host ""
    Write-Host "Summary: $running/$total containers running" -ForegroundColor White
}

function Test-Network {
    Write-Header "Network Connectivity Test"

    # Check forge-network
    Write-Host "Docker Network:" -ForegroundColor Cyan
    $network = docker network inspect forge-network --format "{{range .Containers}}{{.Name}} {{end}}" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $count = ($network -split ' ' | Where-Object { $_ }).Count
        Write-Status "ok" "forge-network exists with $count containers"
    } else {
        Write-Status "error" "forge-network not found!"
        Write-Host "  Fix: docker network create forge-network" -ForegroundColor Yellow
    }

    # Check Traefik
    Write-Host ""
    Write-Host "Traefik Status:" -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8888/api/http/routers" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        $routes = ($response.Content | ConvertFrom-Json).Count
        Write-Status "ok" "Traefik responding - $routes routes"
    } catch {
        Write-Status "error" "Traefik not responding"
    }

    # Check HTTP services
    Write-Host ""
    Write-Host "HTTP Services:" -ForegroundColor Cyan
    $ok = 0
    $fail = 0

    foreach ($svc in $ServicePorts.GetEnumerator()) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$($svc.Value)" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            Write-Status "ok" "$($svc.Key) (:$($svc.Value)) - HTTP $($response.StatusCode)"
            $ok++
        } catch {
            if ($_.Exception.Response) {
                $code = [int]$_.Exception.Response.StatusCode
                Write-Status "warn" "$($svc.Key) (:$($svc.Value)) - HTTP $code"
                $ok++
            } else {
                Write-Status "error" "$($svc.Key) (:$($svc.Value)) - Not responding"
                $fail++
            }
        }
    }

    # Summary
    Write-Host ""
    Write-Host "Summary: $ok/$($ok + $fail) services responding" -ForegroundColor White
    if ($fail -gt 0) {
        Write-Host "  $fail services down - check logs with: docker logs <container>" -ForegroundColor Yellow
    }
}

# Main
switch ($Action) {
    "start"   { Start-All }
    "stop"    { Stop-All }
    "restart" { Restart-All }
    "status"  { Get-Status }
    "test"    { Test-Network }
}
