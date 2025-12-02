<#
.SYNOPSIS
    ECHO Mode Switcher - Switch between Docker-only and Hybrid (NPU) modes
.DESCRIPTION
    Manages ECHO deployment modes:
    - Docker mode: Full Docker stack (CPU transcription)
    - Hybrid mode: Frontend in Docker + Backend native Windows (NPU acceleration)
.PARAMETER Mode
    docker: Full Docker stack (slower, CPU only)
    hybrid: Frontend Docker + Backend native (faster, NPU enabled)
.PARAMETER Action
    start: Start the specified mode
    stop: Stop all ECHO services
    status: Show current status
    switch: Stop current mode and start the other
.EXAMPLE
    .\echo-mode.ps1 -Mode hybrid -Action start
    .\echo-mode.ps1 -Mode docker -Action start
    .\echo-mode.ps1 -Action status
    .\echo-mode.ps1 -Action switch
#>

param(
    [ValidateSet("docker", "hybrid")]
    [string]$Mode = "hybrid",

    [ValidateSet("start", "stop", "status", "switch")]
    [string]$Action = "status"
)

$ECHO_ROOT = "D:\Projects\AXIOM\apps\echo"
$SCRIPT_DIR = "$ECHO_ROOT\.dev\scripts"

# Colors
$C_CYAN = "Cyan"
$C_GREEN = "Green"
$C_YELLOW = "Yellow"
$C_RED = "Red"
$C_GRAY = "Gray"

function Write-Banner {
    Write-Host ""
    Write-Host "  ======================================" -ForegroundColor $C_CYAN
    Write-Host "   ECHO Mode Manager" -ForegroundColor $C_CYAN
    Write-Host "  ======================================" -ForegroundColor $C_CYAN
    Write-Host ""
}

function Test-ForgeServices {
    <#
    .SYNOPSIS
        Check if FORGE infrastructure services are running
    #>
    $results = @{
        PostgreSQL = $false
        Redis = $false
    }

    # Test PostgreSQL (port 5433)
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("localhost", 5433)
        $tcp.Close()
        $results.PostgreSQL = $true
    } catch { }

    # Test Redis (port 6379)
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("localhost", 6379)
        $tcp.Close()
        $results.Redis = $true
    } catch { }

    return $results
}

function Get-CurrentMode {
    <#
    .SYNOPSIS
        Detect current running mode
    #>
    $frontendDocker = docker ps --filter "name=echo-frontend" --format "{{.Status}}" 2>$null
    $backendDocker = docker ps --filter "name=echo-backend" --format "{{.Status}}" 2>$null

    # Check for native backend
    $backendNative = $false
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:7201/api/v1/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($health.status -and -not $backendDocker) {
            $backendNative = $true
        }
    } catch { }

    if ($frontendDocker -and $backendDocker) {
        return "docker"
    } elseif ($frontendDocker -and $backendNative) {
        return "hybrid"
    } elseif ($frontendDocker -or $backendDocker -or $backendNative) {
        return "partial"
    } else {
        return "stopped"
    }
}

function Start-DockerMode {
    Write-Host "[DOCKER MODE] Starting full Docker stack..." -ForegroundColor $C_CYAN
    Write-Host "  This mode uses CPU for transcription (slower)" -ForegroundColor $C_GRAY

    # Check FORGE
    $forge = Test-ForgeServices
    if (-not $forge.PostgreSQL) {
        Write-Host ""
        Write-Host "[ERROR] FORGE PostgreSQL not running on port 5433" -ForegroundColor $C_RED
        Write-Host "        Start FORGE first:" -ForegroundColor $C_YELLOW
        Write-Host "        cd D:\Projects\AXIOM\forge && docker-compose up -d" -ForegroundColor $C_YELLOW
        return
    }

    # Stop any native backend
    & "$SCRIPT_DIR\echo-backend-manager.ps1" -Action stop 2>$null

    # Start full Docker stack
    Set-Location $ECHO_ROOT
    docker-compose -f docker-compose.dev.yml up -d

    Write-Host ""
    Write-Host "[OK] Docker mode started" -ForegroundColor $C_GREEN
    Write-Host "     Frontend: http://localhost:7200" -ForegroundColor $C_GRAY
    Write-Host "     Backend:  http://localhost:7201/docs" -ForegroundColor $C_GRAY
    Write-Host "     Mode:     CPU transcription (slower)" -ForegroundColor $C_YELLOW
}

function Stop-DockerMode {
    Write-Host "[DOCKER] Stopping Docker containers..." -ForegroundColor $C_CYAN
    Set-Location $ECHO_ROOT
    docker-compose -f docker-compose.dev.yml down 2>$null
    docker-compose -f docker-compose.hybrid.yml down 2>$null
}

function Start-HybridMode {
    Write-Host "[HYBRID MODE] Starting Frontend (Docker) + Backend (Native NPU)..." -ForegroundColor $C_CYAN
    Write-Host "  This mode uses AMD Ryzen AI NPU for transcription (faster)" -ForegroundColor $C_GRAY

    # Check FORGE
    $forge = Test-ForgeServices
    if (-not $forge.PostgreSQL) {
        Write-Host ""
        Write-Host "[ERROR] FORGE PostgreSQL not running on port 5433" -ForegroundColor $C_RED
        Write-Host "        Start FORGE first:" -ForegroundColor $C_YELLOW
        Write-Host "        cd D:\Projects\AXIOM\forge && docker-compose up -d" -ForegroundColor $C_YELLOW
        return
    }

    # Stop Docker backend if running
    docker stop echo-backend 2>$null
    docker rm echo-backend 2>$null

    # Start frontend only via hybrid compose
    Set-Location $ECHO_ROOT
    docker-compose -f docker-compose.hybrid.yml up -d

    # Start native backend with NPU
    Write-Host ""
    Write-Host "[BACKEND] Starting native backend with NPU..." -ForegroundColor $C_CYAN
    & "$SCRIPT_DIR\echo-backend-manager.ps1" -Action start

    Write-Host ""
    Write-Host "[OK] Hybrid mode started" -ForegroundColor $C_GREEN
    Write-Host "     Frontend: http://localhost:7200 (Docker)" -ForegroundColor $C_GRAY
    Write-Host "     Backend:  http://localhost:7201/docs (Native NPU)" -ForegroundColor $C_GRAY
    Write-Host "     Mode:     NPU transcription (3-5x faster)" -ForegroundColor $C_GREEN
}

function Stop-HybridMode {
    Write-Host "[HYBRID] Stopping all services..." -ForegroundColor $C_CYAN

    # Stop Docker frontend
    Set-Location $ECHO_ROOT
    docker-compose -f docker-compose.hybrid.yml down 2>$null

    # Stop native backend
    & "$SCRIPT_DIR\echo-backend-manager.ps1" -Action stop
}

function Get-EchoStatus {
    Write-Banner

    $currentMode = Get-CurrentMode
    $forge = Test-ForgeServices

    # FORGE Status
    Write-Host "  FORGE Infrastructure:" -ForegroundColor $C_CYAN
    if ($forge.PostgreSQL) {
        Write-Host "    PostgreSQL (5433): " -NoNewline; Write-Host "Running" -ForegroundColor $C_GREEN
    } else {
        Write-Host "    PostgreSQL (5433): " -NoNewline; Write-Host "Stopped" -ForegroundColor $C_RED
    }
    if ($forge.Redis) {
        Write-Host "    Redis (6379):      " -NoNewline; Write-Host "Running" -ForegroundColor $C_GREEN
    } else {
        Write-Host "    Redis (6379):      " -NoNewline; Write-Host "Stopped" -ForegroundColor $C_RED
    }

    Write-Host ""
    Write-Host "  ECHO Services:" -ForegroundColor $C_CYAN

    # Frontend
    $frontendStatus = docker ps --filter "name=echo-frontend" --format "{{.Status}}" 2>$null
    if ($frontendStatus) {
        Write-Host "    Frontend (7200):   " -NoNewline; Write-Host "Running (Docker)" -ForegroundColor $C_GREEN
    } else {
        Write-Host "    Frontend (7200):   " -NoNewline; Write-Host "Stopped" -ForegroundColor $C_GRAY
    }

    # Backend
    $backendDocker = docker ps --filter "name=echo-backend" --format "{{.Status}}" 2>$null
    if ($backendDocker) {
        Write-Host "    Backend (7201):    " -NoNewline; Write-Host "Running (Docker/CPU)" -ForegroundColor $C_YELLOW
    } else {
        try {
            $health = Invoke-RestMethod -Uri "http://localhost:7201/api/v1/health" -TimeoutSec 2 -ErrorAction Stop
            $npuStatus = if ($health.details.npu_available) { "NPU" } else { "CPU" }
            Write-Host "    Backend (7201):    " -NoNewline
            if ($npuStatus -eq "NPU") {
                Write-Host "Running (Native/$npuStatus)" -ForegroundColor $C_GREEN
            } else {
                Write-Host "Running (Native/$npuStatus)" -ForegroundColor $C_YELLOW
            }
        } catch {
            Write-Host "    Backend (7201):    " -NoNewline; Write-Host "Stopped" -ForegroundColor $C_GRAY
        }
    }

    Write-Host ""
    Write-Host "  Current Mode: " -NoNewline -ForegroundColor $C_CYAN
    switch ($currentMode) {
        "docker" { Write-Host "Docker (CPU - slower)" -ForegroundColor $C_YELLOW }
        "hybrid" { Write-Host "Hybrid (NPU - faster)" -ForegroundColor $C_GREEN }
        "partial" { Write-Host "Partial (inconsistent state)" -ForegroundColor $C_RED }
        "stopped" { Write-Host "Stopped" -ForegroundColor $C_GRAY }
    }

    Write-Host ""
    Write-Host "  Commands:" -ForegroundColor $C_CYAN
    Write-Host "    .\echo-mode.ps1 -Mode hybrid -Action start  # NPU mode (fast)" -ForegroundColor $C_GRAY
    Write-Host "    .\echo-mode.ps1 -Mode docker -Action start  # Docker mode (slow)" -ForegroundColor $C_GRAY
    Write-Host "    .\echo-mode.ps1 -Action stop                # Stop all" -ForegroundColor $C_GRAY
    Write-Host ""
}

function Stop-AllServices {
    Write-Host "[STOPPING] All ECHO services..." -ForegroundColor $C_CYAN

    # Stop Docker containers
    Set-Location $ECHO_ROOT
    docker-compose -f docker-compose.dev.yml down 2>$null
    docker-compose -f docker-compose.hybrid.yml down 2>$null

    # Stop native backend
    & "$SCRIPT_DIR\echo-backend-manager.ps1" -Action stop 2>$null

    Write-Host "[OK] All services stopped" -ForegroundColor $C_GREEN
}

function Switch-Mode {
    $currentMode = Get-CurrentMode

    if ($currentMode -eq "stopped") {
        Write-Host "[INFO] No services running. Starting $Mode mode..." -ForegroundColor $C_YELLOW
        if ($Mode -eq "docker") { Start-DockerMode } else { Start-HybridMode }
        return
    }

    # Determine target mode (opposite of current or specified)
    $targetMode = $Mode
    if ($currentMode -eq "docker") {
        $targetMode = "hybrid"
    } elseif ($currentMode -eq "hybrid") {
        $targetMode = "docker"
    }

    Write-Host "[SWITCH] Changing from $currentMode to $targetMode..." -ForegroundColor $C_CYAN

    Stop-AllServices
    Start-Sleep -Seconds 2

    if ($targetMode -eq "docker") {
        Start-DockerMode
    } else {
        Start-HybridMode
    }
}

# Main execution
switch ($Action) {
    "start" {
        if ($Mode -eq "docker") {
            Start-DockerMode
        } else {
            Start-HybridMode
        }
    }
    "stop" {
        Stop-AllServices
    }
    "status" {
        Get-EchoStatus
    }
    "switch" {
        Switch-Mode
    }
}
