# Atlas Agent Detector for ccstatusline
# Detecte l'agent Atlas actif via fichier session ou variable d'environnement

$sessionFile = "$env:USERPROFILE\.claude\session-state.json"

if (Test-Path $sessionFile) {
    try {
        $session = Get-Content $sessionFile -Raw | ConvertFrom-Json
        $agent = if ($session.active_agent) { $session.active_agent } else { "ATLAS" }
    } catch {
        $agent = "ATLAS"
    }
} else {
    $agent = if ($env:ATLAS_AGENT) { $env:ATLAS_AGENT } else { "ATLAS" }
}

Write-Host $agent
