# ============================================
# AXIOM - Script d'Arret
# ============================================
# Usage: .\stop.ps1 [app]
#
# Options:
#   .\stop.ps1           # Arrete SYNAPSE + NEXUS (garde FORGE)
#   .\stop.ps1 all       # Arrete TOUT (incluant FORGE)
#   .\stop.ps1 synapse   # Arrete seulement SYNAPSE
#   .\stop.ps1 nexus     # Arrete seulement NEXUS
# ============================================

param(
    [string]$App = "apps"
)

$ErrorActionPreference = "SilentlyContinue"
$BaseDir = $PSScriptRoot

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  AXIOM - Arret des Services" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

function Stop-Service {
    param(
        [string]$Name,
        [string]$Path
    )

    if (-not (Test-Path $Path)) {
        return
    }

    Write-Host ">> Arret de $Name..." -ForegroundColor Yellow

    Push-Location $Path
    try {
        docker compose down 2>$null
        Write-Host "   $Name arrete." -ForegroundColor Green
    }
    finally {
        Pop-Location
    }
}

switch ($App) {
    "all" {
        Stop-Service -Name "CORTEX" -Path "$BaseDir\apps\cortex"
        Stop-Service -Name "NEXUS" -Path "$BaseDir\apps\nexus"
        Stop-Service -Name "SYNAPSE" -Path "$BaseDir\apps\synapse"
        Stop-Service -Name "FORGE" -Path "$BaseDir\forge"
        Write-Host "`nTous les services arretes." -ForegroundColor Green
    }
    "synapse" {
        Stop-Service -Name "SYNAPSE" -Path "$BaseDir\apps\synapse"
    }
    "nexus" {
        Stop-Service -Name "NEXUS" -Path "$BaseDir\apps\nexus"
    }
    "cortex" {
        Stop-Service -Name "CORTEX" -Path "$BaseDir\apps\cortex"
    }
    default {
        # Arrete les apps mais garde FORGE
        Stop-Service -Name "CORTEX" -Path "$BaseDir\apps\cortex"
        Stop-Service -Name "NEXUS" -Path "$BaseDir\apps\nexus"
        Stop-Service -Name "SYNAPSE" -Path "$BaseDir\apps\synapse"
        Write-Host "`nApps arretees. FORGE reste actif." -ForegroundColor Yellow
        Write-Host "Pour arreter FORGE: .\stop.ps1 all" -ForegroundColor Gray
    }
}
