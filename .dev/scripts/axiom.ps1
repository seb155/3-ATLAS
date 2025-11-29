# ==============================================================================
# AXIOM Infrastructure CLI
# ==============================================================================
# Quick commands for managing AXIOM infrastructure
# Usage: .\axiom.ps1 <command> [service] [options]
# ==============================================================================

param(
    [Parameter(Position=0)]
    [string]$Command,

    [Parameter(Position=1)]
    [string]$Service,

    [switch]$Help,
    [switch]$Verbose
)

$script:RegistryPath = "D:\Projects\AXIOM\.dev\infra\registry.yml"
$script:RootPath = "D:\Projects\AXIOM"

# Color output helpers
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Info { param($Message) Write-Host "📋 $Message" -ForegroundColor Cyan }
function Write-Header { param($Message) Write-Host "`n$Message" -ForegroundColor Cyan; Write-Host ("=" * $Message.Length) -ForegroundColor Cyan }

# ==============================================================================
# Help Function
# ==============================================================================

function Show-Help {
    Write-Host "`nAXIOM Infrastructure CLI" -ForegroundColor Cyan
    Write-Host ("=" * 50) -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\axiom.ps1 <command> [service] [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  status              Show infrastructure status" -ForegroundColor White
    Write-Host "  ports               List allocated ports" -ForegroundColor White
    Write-Host "  start <service>     Start a service or stack" -ForegroundColor White
    Write-Host "  stop <service>      Stop a service or stack" -ForegroundColor White
    Write-Host "  restart <service>   Restart a service" -ForegroundColor White
    Write-Host "  logs <service>      Show service logs (follow mode)" -ForegroundColor White
    Write-Host "  validate            Validate infrastructure configuration" -ForegroundColor White
    Write-Host "  health              Check health of all services" -ForegroundColor White
    Write-Host "  networks            List Docker networks and memberships" -ForegroundColor White
    Write-Host "  urls                Show all access URLs" -ForegroundColor White
    Write-Host ""
    Write-Host "Services:" -ForegroundColor Yellow
    Write-Host "  forge               FORGE infrastructure stack" -ForegroundColor White
    Write-Host "  traefik             Traefik reverse proxy" -ForegroundColor White
    Write-Host "  synapse             SYNAPSE application" -ForegroundColor White
    Write-Host "  nexus               NEXUS application" -ForegroundColor White
    Write-Host "  <container_name>    Specific container (e.g., synapse-backend)" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\axiom.ps1 status" -ForegroundColor Gray
    Write-Host "  .\axiom.ps1 start synapse" -ForegroundColor Gray
    Write-Host "  .\axiom.ps1 logs synapse-backend" -ForegroundColor Gray
    Write-Host "  .\axiom.ps1 validate" -ForegroundColor Gray
    Write-Host "  .\axiom.ps1 ports" -ForegroundColor Gray
    Write-Host ""
}

# ==============================================================================
# Status Command
# ==============================================================================

function Get-Status {
    Write-Header "AXIOM Infrastructure Status"
    Write-Host ""

    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    Write-Host ""
    Write-Info "Tip: Use 'axiom.ps1 health' for detailed health checks"
}

# ==============================================================================
# Ports Command
# ==============================================================================

function Get-Ports {
    Write-Header "Port Allocations"

    # Load registry
    if (-not (Test-Path $script:RegistryPath)) {
        Write-Error "Registry not found at $script:RegistryPath"
        return
    }

    Import-Module powershell-yaml -ErrorAction SilentlyContinue
    $registryContent = Get-Content $script:RegistryPath -Raw
    $registry = ConvertFrom-Yaml $registryContent

    $allocatedPorts = $registry.port_registry.allocated

    Write-Host ""
    Write-Host "Allocated Ports:" -ForegroundColor Yellow

    # Sort ports numerically
    $sortedPorts = $allocatedPorts.Keys | Sort-Object { [int]$_ }

    foreach ($portKey in $sortedPorts) {
        $port = [int]$portKey
        $service = $allocatedPorts[$portKey]

        $portStr = $port.ToString().PadRight(6)
        $serviceStr = $service.service.PadRight(25)
        $typeStr = "[$($service.type)]".PadRight(15)

        Write-Host "  $portStr → $serviceStr $typeStr $($service.description)" -ForegroundColor White
    }

    # Show available ports
    Write-Host ""
    Write-Host "Available Ports by Application:" -ForegroundColor Yellow

    $ranges = $registry.port_registry.ranges

    foreach ($app in $ranges.Keys) {
        $range = $ranges[$app]
        $start = $range.start
        $end = $range.end

        # Count allocated ports in this range
        $allocatedInRange = 0
        foreach ($portKey in $allocatedPorts.Keys) {
            $port = [int]$portKey
            if ($port -ge $start -and $port -le $end) {
                $allocatedInRange++
            }
        }

        $available = ($end - $start + 1) - $allocatedInRange
        $appStr = $app.ToUpper().PadRight(10)

        Write-Host "  $appStr ($start-$end): $allocatedInRange allocated, $available available" -ForegroundColor Cyan
    }

    Write-Host ""
}

# ==============================================================================
# Start Command
# ==============================================================================

function Start-AxiomService {
    param([string]$ServiceName)

    Write-Header "Starting $ServiceName"
    Write-Host ""

    switch -Wildcard ($ServiceName.ToLower()) {
        "forge" {
            Write-Info "Starting FORGE infrastructure..."
            Set-Location "$script:RootPath\forge"
            docker-compose up -d
        }
        "traefik" {
            Write-Info "Starting Traefik reverse proxy..."
            Set-Location "$script:RootPath\forge"
            docker-compose -f docker-compose.yml -f docker-compose.traefik.yml up -d traefik
        }
        "synapse" {
            Write-Info "Starting SYNAPSE application..."
            Set-Location "$script:RootPath\apps\synapse"

            # Check if FORGE is running
            $forgeRunning = docker ps --filter "name=forge-postgres" --format "{{.Names}}"
            if (-not $forgeRunning) {
                Write-Warning "FORGE infrastructure is not running. Starting FORGE first..."
                Set-Location "$script:RootPath\forge"
                docker-compose up -d
                Start-Sleep -Seconds 5
                Set-Location "$script:RootPath\apps\synapse"
            }

            docker-compose -f docker-compose.dev.yml up -d --build
        }
        "nexus" {
            Write-Info "Starting NEXUS application..."
            Set-Location "$script:RootPath\apps\nexus\standalone"

            # Check if FORGE is running
            $forgeRunning = docker ps --filter "name=forge-postgres" --format "{{.Names}}"
            if (-not $forgeRunning) {
                Write-Warning "FORGE infrastructure is not running. Starting FORGE first..."
                Set-Location "$script:RootPath\forge"
                docker-compose up -d
                Start-Sleep -Seconds 5
                Set-Location "$script:RootPath\apps\nexus\standalone"
            }

            docker-compose -f docker-compose.dev.yml up -d --build
        }
        default {
            # Assume it's a container name
            Write-Info "Starting container: $ServiceName"
            docker start $ServiceName

            if ($LASTEXITCODE -eq 0) {
                Write-Success "$ServiceName started successfully"
            } else {
                Write-Error "Failed to start $ServiceName"
                Write-Info "Available services: forge, traefik, synapse, nexus, or any container name"
            }
        }
    }

    # Return to original directory
    Set-Location $script:RootPath

    Write-Host ""
    Write-Success "Done! Use 'axiom.ps1 status' to verify."
}

# ==============================================================================
# Stop Command
# ==============================================================================

function Stop-AxiomService {
    param([string]$ServiceName)

    Write-Header "Stopping $ServiceName"
    Write-Host ""

    switch -Wildcard ($ServiceName.ToLower()) {
        "forge" {
            Write-Info "Stopping FORGE infrastructure..."
            Set-Location "$script:RootPath\forge"
            docker-compose down
        }
        "synapse" {
            Write-Info "Stopping SYNAPSE application..."
            Set-Location "$script:RootPath\apps\synapse"
            docker-compose -f docker-compose.dev.yml down
        }
        "nexus" {
            Write-Info "Stopping NEXUS application..."
            Set-Location "$script:RootPath\apps\nexus\standalone"
            docker-compose -f docker-compose.dev.yml down
        }
        default {
            Write-Info "Stopping container: $ServiceName"
            docker stop $ServiceName

            if ($LASTEXITCODE -eq 0) {
                Write-Success "$ServiceName stopped successfully"
            } else {
                Write-Error "Failed to stop $ServiceName"
            }
        }
    }

    Set-Location $script:RootPath
    Write-Host ""
}

# ==============================================================================
# Restart Command
# ==============================================================================

function Restart-AxiomService {
    param([string]$ServiceName)

    Write-Header "Restarting $ServiceName"
    Write-Host ""

    Write-Info "Restarting container: $ServiceName"
    docker restart $ServiceName

    if ($LASTEXITCODE -eq 0) {
        Write-Success "$ServiceName restarted successfully"
    } else {
        Write-Error "Failed to restart $ServiceName"
        Write-Info "Use 'axiom.ps1 status' to see available containers"
    }

    Write-Host ""
}

# ==============================================================================
# Logs Command
# ==============================================================================

function Get-Logs {
    param([string]$ServiceName)

    if (-not $ServiceName) {
        Write-Error "Please specify a service name"
        Write-Info "Example: axiom.ps1 logs synapse-backend"
        return
    }

    Write-Info "Showing logs for $ServiceName (follow mode, Ctrl+C to exit)"
    Write-Host ""

    docker logs $ServiceName -f --tail 100
}

# ==============================================================================
# Validate Command
# ==============================================================================

function Invoke-Validation {
    Write-Header "Validating Infrastructure"
    Write-Host ""

    $validateScript = Join-Path $script:RootPath ".dev\scripts\validate-infra.ps1"

    if (Test-Path $validateScript) {
        & $validateScript
    } else {
        Write-Error "Validation script not found at $validateScript"
    }
}

# ==============================================================================
# Health Command
# ==============================================================================

function Get-Health {
    Write-Header "Infrastructure Health Check"
    Write-Host ""

    # Check FORGE services
    Write-Host "FORGE Infrastructure:" -ForegroundColor Yellow

    $forgeServices = @(
        @{ Name = "forge-postgres"; Check = "pg_isready -U postgres" },
        @{ Name = "forge-redis"; Check = "redis-cli ping" },
        @{ Name = "forge-loki"; Check = "wget --spider -q http://localhost:3100/ready" },
        @{ Name = "forge-grafana"; Check = "wget --spider -q http://localhost:3000/api/health" }
    )

    foreach ($svc in $forgeServices) {
        $running = docker ps --filter "name=$($svc.Name)" --format "{{.Names}}"

        if ($running) {
            $result = docker exec $svc.Name sh -c $svc.Check 2>$null

            if ($LASTEXITCODE -eq 0) {
                Write-Success "$($svc.Name.PadRight(20)) - healthy"
            } else {
                Write-Warning "$($svc.Name.PadRight(20)) - degraded"
            }
        } else {
            Write-Error "$($svc.Name.PadRight(20)) - not running"
        }
    }

    # Check application services
    Write-Host ""
    Write-Host "Application Services:" -ForegroundColor Yellow

    $appServices = @("synapse-backend", "synapse-frontend", "nexus-backend", "nexus-frontend")

    foreach ($svc in $appServices) {
        $running = docker ps --filter "name=$svc" --format "{{.Names}}"

        if ($running) {
            Write-Success "$($svc.PadRight(20)) - running"
        } else {
            Write-Info "$($svc.PadRight(20)) - not running"
        }
    }

    Write-Host ""
}

# ==============================================================================
# Networks Command
# ==============================================================================

function Get-Networks {
    Write-Header "Docker Networks"
    Write-Host ""

    Write-Host "Network List:" -ForegroundColor Yellow
    docker network ls

    Write-Host ""
    Write-Host "forge-network Members:" -ForegroundColor Yellow

    $forgeNetwork = docker network inspect forge-network 2>$null | ConvertFrom-Json

    if ($forgeNetwork) {
        $containers = $forgeNetwork.Containers
        if ($containers) {
            foreach ($key in $containers.Keys) {
                $container = $containers[$key]
                Write-Host "  - $($container.Name)" -ForegroundColor Cyan
            }
        } else {
            Write-Info "No containers currently on forge-network"
        }
    } else {
        Write-Error "forge-network does not exist!"
        Write-Info "Create it with: docker network create forge-network"
    }

    Write-Host ""
}

# ==============================================================================
# URLs Command
# ==============================================================================

function Get-URLs {
    Write-Header "Access URLs"
    Write-Host ""

    Write-Host "Development (Direct Ports):" -ForegroundColor Yellow
    Write-Host "  SYNAPSE Frontend:      http://localhost:4000" -ForegroundColor Cyan
    Write-Host "  SYNAPSE API Docs:      http://localhost:8001/docs" -ForegroundColor Cyan
    Write-Host "  Grafana:               http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
    Write-Host "  Wiki:                  http://localhost:3080" -ForegroundColor Cyan
    Write-Host "  Traefik Dashboard:     http://localhost:8888" -ForegroundColor Cyan
    Write-Host "  pgAdmin:               http://localhost:5050" -ForegroundColor Cyan
    Write-Host "  Prisma Studio:         http://localhost:5555" -ForegroundColor Cyan
    Write-Host "  MeiliSearch:           http://localhost:7700" -ForegroundColor Cyan

    Write-Host ""
    Write-Host "Development (with Traefik SSL):" -ForegroundColor Yellow
    Write-Host "  SYNAPSE Frontend:      https://synapse.axoiq.com" -ForegroundColor Cyan
    Write-Host "  SYNAPSE API:           https://api.axoiq.com/docs" -ForegroundColor Cyan
    Write-Host "  Traefik Dashboard:     https://traefik.axoiq.com:8888" -ForegroundColor Cyan
    Write-Host "  Grafana:               https://grafana.axoiq.com" -ForegroundColor Cyan

    Write-Host ""
}

# ==============================================================================
# Main
# ==============================================================================

if ($Help -or -not $Command) {
    Show-Help
    exit 0
}

# Execute command
switch ($Command.ToLower()) {
    "status"   { Get-Status }
    "ports"    { Get-Ports }
    "start"    { Start-AxiomService -ServiceName $Service }
    "stop"     { Stop-AxiomService -ServiceName $Service }
    "restart"  { Restart-AxiomService -ServiceName $Service }
    "logs"     { Get-Logs -ServiceName $Service }
    "validate" { Invoke-Validation }
    "health"   { Get-Health }
    "networks" { Get-Networks }
    "urls"     { Get-URLs }
    default {
        Write-Error "Unknown command: $Command"
        Show-Help
        exit 1
    }
}
