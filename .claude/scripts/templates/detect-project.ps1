# Project Detector for Atlas Monorepo
# Returns project name WITHOUT emojis (emojis added by ccstatusline)
# Now reads from .registry/projects.json with fallback to hardcoded values

param(
    [Parameter(ValueFromPipeline=$true)]
    [string]$InputJson
)

# Lire le JSON depuis stdin si fourni
if (-not $InputJson) {
    $InputJson = [Console]::In.ReadToEnd()
}

try {
    $data = $InputJson | ConvertFrom-Json
    $cwd = $data.workspace.current_dir
} catch {
    $cwd = Get-Location
}

# Try to load from registry first
$registryPath = "D:\Projects\.registry\projects.json"
$useRegistry = Test-Path $registryPath

if ($useRegistry) {
    try {
        $registry = Get-Content $registryPath -Raw | ConvertFrom-Json

        # Build project maps from registry
        $axiomApps = @{}
        $projects = @{}

        foreach ($proj in $registry.projects) {
            if ($proj.status -ne "active") { continue }

            # Main projects mapping: name -> display_name
            $projects[$proj.name] = $proj.display_name

            # Sub-projects (for AXIOM-style monorepos)
            if ($proj.sub_projects) {
                foreach ($sub in $proj.sub_projects) {
                    $axiomApps[$sub.name.ToLower()] = $sub.name
                }
            }
        }
    } catch {
        # Fall back to hardcoded if registry parsing fails
        $useRegistry = $false
    }
}

# Fallback: hardcoded project maps (backwards compatibility)
if (-not $useRegistry) {
    $axiomApps = @{
        "synapse"       = "SYNAPSE"
        "nexus"         = "NEXUS"
        "prism"         = "PRISM"
        "atlas"         = "ATLAS-APP"
        "forge"         = "FORGE"
    }

    $projects = @{
        "AXIOM"         = "AXIOM"
        "FinDash"       = "FinDash"
        "Homelab_MSH"   = "Homelab"
        "HomeAssistant" = "HA-MCP"
        "Note_synch"    = "NoteSync"
        "atlas-agent"   = "Atlas-Fw"
    }
}

$detected = "ROOT"

# Check AXIOM sub-apps first (more specific)
if ($cwd -match "AXIOM[/\\]apps[/\\]") {
    foreach ($key in $axiomApps.Keys) {
        if ($cwd -match [regex]::Escape($key)) {
            $detected = $axiomApps[$key]
            break
        }
    }
} else {
    # Check main projects
    foreach ($key in $projects.Keys) {
        if ($cwd -match [regex]::Escape($key)) {
            $detected = $projects[$key]
            break
        }
    }
}

Write-Host $detected
