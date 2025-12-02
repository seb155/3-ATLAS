<#
.SYNOPSIS
    ECHO Backend Process Manager with NPU Support
.DESCRIPTION
    Manages uvicorn backend with Ryzen AI NPU environment activated.
    Can be called from WSL via powershell.exe.
.PARAMETER Action
    start, stop, restart, status, logs
.PARAMETER Port
    Backend port (default: 7201)
.EXAMPLE
    .\echo-backend-manager.ps1 -Action start
    .\echo-backend-manager.ps1 -Action status
    .\echo-backend-manager.ps1 -Action logs -Lines 100
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "logs")]
    [string]$Action,

    [string]$Port = "7201",
    [string]$Host = "0.0.0.0",
    [int]$Lines = 50
)

# Configuration
$ECHO_ROOT = "D:\Projects\AXIOM\apps\echo"
$BACKEND_DIR = "$ECHO_ROOT\backend"
$PID_FILE = "$ECHO_ROOT\.dev\run\echo-backend.pid"
$LOG_DIR = "$ECHO_ROOT\.dev\logs"
$LOG_FILE = "$LOG_DIR\backend.log"
$CONDA_ENV = "ryzenai-1.6.1"

# Ryzen AI SDK Environment Variables
$NPU_ENV = @{
    "RYZEN_AI_INSTALLATION_PATH" = "C:\Program Files\RyzenAI\1.6.1"
    "XLNX_VART_FIRMWARE" = "C:\Program Files\RyzenAI\1.6.1\voe-4.0-win_amd64\xclbins\phoenix\4x4.xclbin"
    "XLNX_TARGET_NAME" = "AMD_AIE2_Nx4_Overlay"
}

# ECHO Backend Environment Variables
$ECHO_ENV = @{
    "WHISPER_DEVICE" = "auto"
    "WHISPER_MODEL" = "large-v3"
    "WHISPER_MODEL_NPU" = "medium"
    "WHISPER_COMPUTE_TYPE" = "int8"
    "WHISPER_PRECISION" = "bfp16"
    "DATABASE_URL" = "postgresql://postgres:postgres@localhost:5433/echo"
    "REDIS_URL" = "redis://localhost:6379"
    "AUDIO_STORAGE_PATH" = "D:/Projects/AXIOM/apps/echo/data"
    "CORS_ORIGINS" = "http://localhost:7200,http://localhost:5173,http://host.docker.internal:7200"
    "ENVIRONMENT" = "development"
    "DEBUG" = "true"
    "ECHO_HYBRID_MODE" = "true"
}

# Ensure directories exist
New-Item -ItemType Directory -Force -Path (Split-Path $PID_FILE) | Out-Null
New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null

function Get-BackendPid {
    # Try PID file first
    if (Test-Path $PID_FILE) {
        $pid = Get-Content $PID_FILE -ErrorAction SilentlyContinue
        if ($pid -and (Get-Process -Id $pid -ErrorAction SilentlyContinue)) {
            return [int]$pid
        }
    }
    # Fallback: find by command line
    $proc = Get-CimInstance Win32_Process | Where-Object {
        $_.CommandLine -like "*uvicorn*app.main*--port*$Port*"
    }
    if ($proc) { return $proc.ProcessId }
    return $null
}

function Start-Backend {
    $existingPid = Get-BackendPid
    if ($existingPid) {
        Write-Host "[WARNING] Backend already running (PID: $existingPid)" -ForegroundColor Yellow
        return
    }

    Write-Host "[STARTING] ECHO Backend with NPU environment..." -ForegroundColor Cyan
    Write-Host "  Working Dir: $BACKEND_DIR"
    Write-Host "  Port: $Port"
    Write-Host "  Conda Env: $CONDA_ENV"
    Write-Host "  Log: $LOG_FILE"

    # Find conda
    $condaPath = "$env:USERPROFILE\miniforge3\Scripts\conda.exe"
    if (-not (Test-Path $condaPath)) {
        $condaPath = "$env:USERPROFILE\miniconda3\Scripts\conda.exe"
    }
    if (-not (Test-Path $condaPath)) {
        $condaPath = (Get-Command conda -ErrorAction SilentlyContinue).Source
    }

    if (-not $condaPath -or -not (Test-Path $condaPath)) {
        Write-Host "[ERROR] conda not found" -ForegroundColor Red
        return
    }

    # Initialize log
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp [START] Backend starting with NPU environment..." | Out-File $LOG_FILE -Encoding utf8

    # Build environment setup commands
    $envSetup = ""
    foreach ($key in $NPU_ENV.Keys) {
        $envSetup += "set `"$key=$($NPU_ENV[$key])`"`n"
    }
    foreach ($key in $ECHO_ENV.Keys) {
        $envSetup += "set `"$key=$($ECHO_ENV[$key])`"`n"
    }

    # Create startup batch script
    $batchScript = @"
@echo off
cd /d "$BACKEND_DIR"
call "$condaPath" activate $CONDA_ENV
$envSetup
echo.
echo === ECHO Backend (NPU Mode) ===
echo Database: localhost:5433/echo
echo NPU Environment: Ryzen AI SDK 1.6.1
echo Port: $Port
echo.
python -m uvicorn app.main:app --host $Host --port $Port --reload
"@

    $batchPath = "$env:TEMP\echo-backend-start.bat"
    $batchScript | Out-File -FilePath $batchPath -Encoding ASCII

    # Start process in new window
    $process = Start-Process cmd -ArgumentList "/c", $batchPath -PassThru -WindowStyle Normal

    # Save PID
    $process.Id | Out-File -FilePath $PID_FILE -NoNewline

    Write-Host ""
    Write-Host "[OK] Backend starting (PID: $($process.Id))" -ForegroundColor Green
    Write-Host "     Health: http://localhost:$Port/api/v1/health"
    Write-Host "     Swagger: http://localhost:$Port/docs"
    Write-Host ""
    Write-Host "     Waiting for startup..." -ForegroundColor Gray

    # Wait for health check
    $maxAttempts = 30
    $attempt = 0
    while ($attempt -lt $maxAttempts) {
        Start-Sleep -Seconds 1
        $attempt++
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:$Port/api/v1/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.status) {
                Write-Host "     [READY] Backend is healthy!" -ForegroundColor Green
                Write-Host "     NPU Available: $($response.details.npu_available)" -ForegroundColor Cyan
                Write-Host "     Active Device: $($response.details.whisper_device_active)" -ForegroundColor Cyan
                return
            }
        }
        catch {
            Write-Host "." -NoNewline -ForegroundColor Gray
        }
    }
    Write-Host ""
    Write-Host "     [WARNING] Health check timed out - check logs" -ForegroundColor Yellow
}

function Stop-Backend {
    $pid = Get-BackendPid
    if (-not $pid) {
        Write-Host "[INFO] Backend not running" -ForegroundColor Yellow
        return
    }

    Write-Host "[STOPPING] ECHO Backend (PID: $pid)..." -ForegroundColor Cyan

    # Kill process tree
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue

    # Also kill any orphaned uvicorn processes on our port
    $netstat = netstat -ano | Select-String ":$Port.*LISTENING"
    if ($netstat) {
        $orphanPid = ($netstat -split '\s+')[-1]
        if ($orphanPid -and $orphanPid -ne $pid) {
            Stop-Process -Id $orphanPid -Force -ErrorAction SilentlyContinue
        }
    }

    # Cleanup
    Remove-Item $PID_FILE -Force -ErrorAction SilentlyContinue

    Write-Host "[OK] Backend stopped" -ForegroundColor Green
}

function Get-BackendStatus {
    $pid = Get-BackendPid

    $status = @{
        running = $false
        pid = $null
        health = "unknown"
        uptime = $null
        npu_available = $false
        gpu_available = $false
        active_device = "none"
    }

    if ($pid) {
        $status.running = $true
        $status.pid = $pid

        $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($proc) {
            $status.uptime = ((Get-Date) - $proc.StartTime).ToString("hh\:mm\:ss")
        }

        # Health check
        try {
            $health = Invoke-RestMethod -Uri "http://localhost:$Port/api/v1/health" -TimeoutSec 5
            $status.health = $health.status
            $status.npu_available = $health.details.npu_available
            $status.gpu_available = $health.details.gpu_available
            $status.active_device = $health.details.whisper_device_active
        }
        catch {
            $status.health = "unreachable"
        }
    }

    # Output as JSON
    $status | ConvertTo-Json -Compress
}

function Get-BackendLogs {
    if (-not (Test-Path $LOG_FILE)) {
        Write-Host "[INFO] No logs found at $LOG_FILE" -ForegroundColor Yellow
        return
    }

    Get-Content $LOG_FILE -Tail $Lines
}

# Main execution
switch ($Action) {
    "start" { Start-Backend }
    "stop" { Stop-Backend }
    "restart" {
        Stop-Backend
        Start-Sleep -Seconds 2
        Start-Backend
    }
    "status" { Get-BackendStatus }
    "logs" { Get-BackendLogs }
}
