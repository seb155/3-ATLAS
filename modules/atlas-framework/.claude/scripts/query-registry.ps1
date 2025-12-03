# Atlas Registry Query Tool
# Query project registry for information

param(
    [string]$ProjectId,
    [switch]$ListAll,
    [switch]$ListActive,
    [string]$TechFilter,
    [string]$TypeFilter,
    [switch]$Json,
    [switch]$Brief,
    [switch]$Interactive,
    [switch]$i  # Alias court pour -Interactive
)

$ErrorActionPreference = "Stop"
$registryPath = "D:\Projects\.registry\projects.json"

if (-not (Test-Path $registryPath)) {
    Write-Error "Registry not found: $registryPath"
    Write-Host "Run: .claude\scripts\sync-registry.ps1" -ForegroundColor Yellow
    exit 1
}

$registry = Get-Content $registryPath -Raw | ConvertFrom-Json

# Mode interactif avec numeros
if ($Interactive -or $i) {
    $projects = $registry.projects | Where-Object { $_.status -eq "active" }

    Write-Host ""
    Write-Host "  Projets disponibles" -ForegroundColor Cyan
    Write-Host "  -------------------" -ForegroundColor DarkGray
    Write-Host ""

    $index = 1
    $projectMap = @{}

    foreach ($project in $projects) {
        $projectMap[$index] = $project
        $techPreview = if ($project.tech_stack.Count -gt 0) {
            " [" + ($project.tech_stack[0..1] -join ", ") + "]"
        } else { "" }

        Write-Host "  $index. " -NoNewline -ForegroundColor Yellow
        Write-Host "$($project.display_name)" -NoNewline -ForegroundColor White
        Write-Host "$techPreview" -ForegroundColor DarkGray

        $index++
    }

    Write-Host ""
    Write-Host "  0. Quitter" -ForegroundColor DarkGray
    Write-Host ""

    $choice = Read-Host "  Choix"

    if ($choice -eq "0" -or $choice -eq "") {
        Write-Host "  Bye!" -ForegroundColor DarkGray
        return
    }

    $selected = $projectMap[[int]$choice]
    if ($selected) {
        Write-Host ""
        Write-Host "  > $($selected.display_name)" -ForegroundColor Green
        Write-Host "    Path: $($selected.path)" -ForegroundColor Gray
        Write-Host "    Tech: $($selected.tech_stack -join ', ')" -ForegroundColor Gray
        if ($selected.description) {
            Write-Host "    Desc: $($selected.description)" -ForegroundColor Gray
        }
        Write-Host ""

        # Proposer d'ouvrir le projet
        Write-Host "  Actions:" -ForegroundColor Cyan
        Write-Host "    1. cd vers le projet" -ForegroundColor Yellow
        Write-Host "    2. Afficher details complets" -ForegroundColor Yellow
        Write-Host "    0. Retour" -ForegroundColor DarkGray
        Write-Host ""

        $action = Read-Host "  Action"

        switch ($action) {
            "1" {
                Write-Host ""
                Write-Host "  Executez:" -ForegroundColor Cyan
                Write-Host "  cd `"$($selected.path)`"" -ForegroundColor White
            }
            "2" {
                & $PSCommandPath -ProjectId $selected.id
            }
        }
    } else {
        Write-Host "  Choix invalide" -ForegroundColor Red
    }

    return
}

# List all projects (also triggered by filters)
if ($ListAll -or $ListActive -or $TechFilter -or $TypeFilter) {
    $projects = $registry.projects

    if ($ListActive) {
        $projects = $projects | Where-Object { $_.status -eq "active" }
    }

    if ($TechFilter) {
        $projects = $projects | Where-Object { $_.tech_stack -contains $TechFilter }
    }

    if ($TypeFilter) {
        $projects = $projects | Where-Object { $_.type -eq $TypeFilter }
    }

    if ($Json) {
        $projects | ConvertTo-Json -Depth 5
        return
    }

    if ($Brief) {
        $projects | ForEach-Object {
            Write-Host "$($_.display_name)" -ForegroundColor Cyan -NoNewline
            Write-Host " - $($_.relative_path)" -ForegroundColor DarkGray
        }
        return
    }

    Write-Host ""
    Write-Host "  Atlas Project Registry" -ForegroundColor Cyan
    Write-Host "  ======================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Last updated: $($registry.last_updated)" -ForegroundColor DarkGray
    Write-Host ""

    $projects | ForEach-Object {
        $techStr = if ($_.tech_stack.Count -gt 0) { $_.tech_stack -join ", " } else { "n/a" }
        $statusIcon = switch ($_.status) {
            "active" { "[*]" }
            "archived" { "[-]" }
            default { "[ ]" }
        }

        Write-Host "  $statusIcon " -NoNewline -ForegroundColor $(if ($_.status -eq "active") { "Green" } else { "DarkGray" })
        Write-Host "$($_.display_name)" -NoNewline -ForegroundColor White
        Write-Host " ($($_.type))" -ForegroundColor DarkGray

        Write-Host "      Path: " -NoNewline -ForegroundColor DarkGray
        Write-Host "$($_.relative_path)" -ForegroundColor Gray

        Write-Host "      Tech: " -NoNewline -ForegroundColor DarkGray
        Write-Host "$techStr" -ForegroundColor Gray

        if ($_.description) {
            Write-Host "      Desc: " -NoNewline -ForegroundColor DarkGray
            Write-Host "$($_.description)" -ForegroundColor Gray
        }

        Write-Host ""
    }

    Write-Host "  Total: $($projects.Count) projects" -ForegroundColor Cyan
    Write-Host ""
    return
}

# Query specific project
if ($ProjectId) {
    $project = $registry.projects | Where-Object {
        $_.id -eq $ProjectId -or
        $_.name -eq $ProjectId -or
        $_.display_name -eq $ProjectId
    }

    if (-not $project) {
        Write-Error "Project not found: $ProjectId"
        Write-Host ""
        Write-Host "Available projects:" -ForegroundColor Yellow
        $registry.projects | ForEach-Object {
            Write-Host "  - $($_.id) ($($_.display_name))" -ForegroundColor Gray
        }
        exit 1
    }

    if ($Json) {
        $project | ConvertTo-Json -Depth 5
        return
    }

    Write-Host ""
    Write-Host "  Project: $($project.display_name)" -ForegroundColor Cyan
    Write-Host "  ========" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  ID:          $($project.id)" -ForegroundColor Gray
    Write-Host "  Name:        $($project.name)" -ForegroundColor Gray
    Write-Host "  Path:        $($project.path)" -ForegroundColor Gray
    Write-Host "  Type:        $($project.type)" -ForegroundColor Gray
    Write-Host "  Status:      $($project.status)" -ForegroundColor $(if ($project.status -eq "active") { "Green" } else { "Yellow" })
    Write-Host "  Tech Stack:  $($project.tech_stack -join ', ')" -ForegroundColor Gray

    if ($project.description) {
        Write-Host "  Description: $($project.description)" -ForegroundColor Gray
    }

    if ($project.quick_commands -and $project.quick_commands.Count -gt 0) {
        Write-Host ""
        Write-Host "  Quick Commands:" -ForegroundColor Cyan
        $project.quick_commands | ForEach-Object {
            Write-Host "    $($_.name): " -NoNewline -ForegroundColor Yellow
            Write-Host "$($_.command)" -ForegroundColor Gray
        }
    }

    if ($project.sub_projects -and $project.sub_projects.Count -gt 0) {
        Write-Host ""
        Write-Host "  Sub-projects:" -ForegroundColor Cyan
        $project.sub_projects | ForEach-Object {
            Write-Host "    - $($_.name) ($($_.path))" -ForegroundColor Gray
        }
    }

    Write-Host ""
    return
}

# Default: show help
Write-Host ""
Write-Host "  Atlas Registry Query Tool" -ForegroundColor Cyan
Write-Host "  =========================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Usage:" -ForegroundColor White
Write-Host "    query-registry.ps1 -i                    # Mode interactif (recommande)" -ForegroundColor Yellow
Write-Host "    query-registry.ps1 -Interactive          # Idem" -ForegroundColor Gray
Write-Host ""
Write-Host "    query-registry.ps1 -ListAll              # List all projects" -ForegroundColor Gray
Write-Host "    query-registry.ps1 -ListActive           # List active projects only" -ForegroundColor Gray
Write-Host "    query-registry.ps1 -ProjectId axiom      # Get project details" -ForegroundColor Gray
Write-Host "    query-registry.ps1 -TechFilter python    # Filter by tech stack" -ForegroundColor Gray
Write-Host "    query-registry.ps1 -TypeFilter monorepo  # Filter by type" -ForegroundColor Gray
Write-Host "    query-registry.ps1 -ListAll -Json        # Output as JSON" -ForegroundColor Gray
Write-Host "    query-registry.ps1 -ListAll -Brief       # Compact output" -ForegroundColor Gray
Write-Host ""
