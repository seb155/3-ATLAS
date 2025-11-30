# ============================================
# AXIOM - Script de Demarrage Unifie
# ============================================
# Usage: .\start.ps1 [app]
#
# Options:
#   .\start.ps1           # Demarre FORGE + SYNAPSE + NEXUS
#   .\start.ps1 forge     # Demarre seulement FORGE (infrastructure)
#   .\start.ps1 synapse   # Demarre FORGE + SYNAPSE
#   .\start.ps1 nexus     # Demarre FORGE + NEXUS
#   .\start.ps1 all       # Demarre tout (FORGE + SYNAPSE + NEXUS + CORTEX)
#
# Acces:
#   SYNAPSE:  https://synapse.axoiq.com
#   NEXUS:    https://nexus.axoiq.com
#   Grafana:  https://grafana.axoiq.com
#   Traefik:  http://localhost:8888
# ============================================

param(
    [string]$App = "default"
)

$ErrorActionPreference = "Stop"
$BaseDir = $PSScriptRoot

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  AXIOM - Demarrage avec Traefik" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Fonction pour demarrer un service
function Start-Service {
    param(
        [string]$Name,
        [string]$Path,
        [string[]]$ComposeFiles
    )

    Write-Host ">> Demarrage de $Name..." -ForegroundColor Yellow

    $composeArgs = @()
    foreach ($file in $ComposeFiles) {
        $composeArgs += "-f"
        $composeArgs += $file
    }
    $composeArgs += "up"
    $composeArgs += "-d"

    Push-Location $Path
    try {
        & docker compose @composeArgs
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   $Name demarre avec succes!" -ForegroundColor Green
        } else {
            Write-Host "   ERREUR: $Name n'a pas demarre" -ForegroundColor Red
        }
    }
    finally {
        Pop-Location
    }
}

# Toujours demarrer FORGE en premier
Write-Host "[1/4] FORGE (Infrastructure + Traefik)" -ForegroundColor Magenta
Start-Service -Name "FORGE" -Path "$BaseDir\forge" -ComposeFiles @("docker-compose.yml", "docker-compose.traefik.yml")

# Demarrer les apps selon le parametre
switch ($App) {
    "forge" {
        Write-Host "`nFORGE demarre. Acces: http://localhost:8888" -ForegroundColor Green
    }
    "synapse" {
        Write-Host "`n[2/4] SYNAPSE" -ForegroundColor Magenta
        Start-Service -Name "SYNAPSE" -Path "$BaseDir\apps\synapse" -ComposeFiles @("docker-compose.dev.yml", "docker-compose.traefik-labels.yml")
    }
    "nexus" {
        Write-Host "`n[2/4] NEXUS" -ForegroundColor Magenta
        Start-Service -Name "NEXUS" -Path "$BaseDir\apps\nexus" -ComposeFiles @("docker-compose.dev.yml", "docker-compose.traefik-labels.yml")
    }
    "all" {
        Write-Host "`n[2/4] SYNAPSE" -ForegroundColor Magenta
        Start-Service -Name "SYNAPSE" -Path "$BaseDir\apps\synapse" -ComposeFiles @("docker-compose.dev.yml", "docker-compose.traefik-labels.yml")

        Write-Host "`n[3/4] NEXUS" -ForegroundColor Magenta
        Start-Service -Name "NEXUS" -Path "$BaseDir\apps\nexus" -ComposeFiles @("docker-compose.dev.yml", "docker-compose.traefik-labels.yml")

        if (Test-Path "$BaseDir\apps\cortex\docker-compose.dev.yml") {
            Write-Host "`n[4/4] CORTEX" -ForegroundColor Magenta
            Start-Service -Name "CORTEX" -Path "$BaseDir\apps\cortex" -ComposeFiles @("docker-compose.dev.yml", "docker-compose.traefik-labels.yml")
        }
    }
    default {
        # Default: SYNAPSE + NEXUS
        Write-Host "`n[2/4] SYNAPSE" -ForegroundColor Magenta
        Start-Service -Name "SYNAPSE" -Path "$BaseDir\apps\synapse" -ComposeFiles @("docker-compose.dev.yml", "docker-compose.traefik-labels.yml")

        Write-Host "`n[3/4] NEXUS" -ForegroundColor Magenta
        Start-Service -Name "NEXUS" -Path "$BaseDir\apps\nexus" -ComposeFiles @("docker-compose.dev.yml", "docker-compose.traefik-labels.yml")
    }
}

# Afficher les URLs
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ACCES (via Traefik)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  SYNAPSE:    https://synapse.axoiq.com" -ForegroundColor White
Write-Host "  NEXUS:      https://nexus.axoiq.com" -ForegroundColor White
Write-Host "  Grafana:    https://grafana.axoiq.com" -ForegroundColor White
Write-Host "  Traefik:    http://localhost:8888" -ForegroundColor White
Write-Host ""
Write-Host "  NOTE: Accepter les certificats self-signed dans le navigateur" -ForegroundColor Yellow
Write-Host ""
