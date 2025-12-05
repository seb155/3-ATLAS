# Atlas Project Discovery Scanner
# Scans configured paths and generates/updates projects.json registry

param(
    [string]$WorkspaceRoot = "D:\Projects",
    [switch]$DryRun,
    [switch]$Verbose,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$registryPath = Join-Path $WorkspaceRoot ".registry"
$configPath = Join-Path $registryPath "discovery-config.json"
$projectsPath = Join-Path $registryPath "projects.json"

# Load configuration
if (-not (Test-Path $configPath)) {
    Write-Error "Configuration file not found: $configPath"
    Write-Host "Run: /1-init-system to initialize the registry" -ForegroundColor Yellow
    exit 1
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json

# Check if auto-sync needed (unless Force)
if (-not $Force -and (Test-Path $projectsPath)) {
    $registryAge = (Get-Date) - (Get-Item $projectsPath).LastWriteTime
    $intervalDays = $config.auto_sync.interval_days

    if ($registryAge.TotalDays -lt $intervalDays) {
        if ($Verbose) {
            Write-Host "Registry is fresh ($([int]$registryAge.TotalHours) hours old). Use -Force to rescan." -ForegroundColor Cyan
        }
        # Return existing registry
        Get-Content $projectsPath -Raw
        exit 0
    }
}

Write-Host "=== Atlas Project Discovery ===" -ForegroundColor Cyan
Write-Host ""

$discoveredProjects = @()

foreach ($scanPath in $config.scan_paths) {
    if (-not (Test-Path $scanPath)) {
        if ($Verbose) {
            Write-Host "  [SKIP] Path not found: $scanPath" -ForegroundColor Yellow
        }
        continue
    }

    $projectName = Split-Path $scanPath -Leaf
    if ($Verbose) {
        Write-Host "  [SCAN] $projectName" -ForegroundColor White
    }

    # Detect signals
    $signals = @{
        hasClaude = Test-Path (Join-Path $scanPath "CLAUDE.md")
        hasGit = Test-Path (Join-Path $scanPath ".git")
        hasDev = Test-Path (Join-Path $scanPath ".dev")
        hasPackageJson = Test-Path (Join-Path $scanPath "package.json")
        hasRequirements = Test-Path (Join-Path $scanPath "requirements.txt")
        hasPyproject = Test-Path (Join-Path $scanPath "pyproject.toml")
        hasDockerCompose = (Get-ChildItem $scanPath -Filter "docker-compose*.yml" -ErrorAction SilentlyContinue).Count -gt 0
        hasAppsFolder = Test-Path (Join-Path $scanPath "apps")
        hasServerPy = Test-Path (Join-Path $scanPath "server.py")
        hasStartServer = Test-Path (Join-Path $scanPath "start_server.sh")
    }

    # Skip if no detection signals
    $hasAnySignal = $signals.Values -contains $true
    if (-not $hasAnySignal) {
        if ($Verbose) {
            Write-Host "    No signals found, skipping" -ForegroundColor DarkGray
        }
        continue
    }

    # Infer project type
    $type = "application"
    if ($signals.hasAppsFolder) {
        $type = "monorepo"
    } elseif ($signals.hasServerPy -or $signals.hasStartServer) {
        $type = "mcp-server"
    } elseif ($signals.hasDockerCompose -and (Test-Path (Join-Path $scanPath "scripts"))) {
        $type = "infrastructure"
    } elseif ($projectName -match "framework|template") {
        $type = "framework"
    }

    # Extract tech stack
    $techStack = @()

    if ($signals.hasPackageJson) {
        $techStack += "nodejs"
        try {
            $pkg = Get-Content (Join-Path $scanPath "package.json") -Raw | ConvertFrom-Json
            if ($pkg.dependencies.PSObject.Properties["react"] -or $pkg.devDependencies.PSObject.Properties["react"]) {
                $techStack += "react"
            }
            if ($pkg.dependencies.PSObject.Properties["typescript"] -or $pkg.devDependencies.PSObject.Properties["typescript"]) {
                $techStack += "typescript"
            }
            if ($pkg.dependencies.PSObject.Properties["vite"] -or $pkg.devDependencies.PSObject.Properties["vite"]) {
                $techStack += "vite"
            }
        } catch {
            # Ignore JSON parse errors
        }
    }

    if ($signals.hasRequirements -or $signals.hasPyproject) {
        $techStack += "python"
        if ($signals.hasRequirements) {
            $requirements = Get-Content (Join-Path $scanPath "requirements.txt") -Raw -ErrorAction SilentlyContinue
            if ($requirements -match "fastapi") { $techStack += "fastapi" }
            if ($requirements -match "flask") { $techStack += "flask" }
            if ($requirements -match "django") { $techStack += "django" }
        }
    }

    if ($signals.hasDockerCompose) {
        $techStack += "docker"
    }

    # Remove duplicates
    $techStack = $techStack | Select-Object -Unique

    # Parse CLAUDE.md for description
    $description = ""
    if ($signals.hasClaude) {
        $claudeContent = Get-Content (Join-Path $scanPath "CLAUDE.md") -Raw -ErrorAction SilentlyContinue
        if ($claudeContent) {
            # Try to extract description from various patterns
            if ($claudeContent -match '## Project Overview\s*\n+([^\n#]+)') {
                $description = $matches[1].Trim()
            } elseif ($claudeContent -match '(?:This|It) is (?:a |an )?([^.]+)\.') {
                $description = $matches[1].Trim()
            }
        }
    }

    # Generate display name
    $displayName = switch ($projectName) {
        "AXIOM" { "AXIOM" }
        "FinDash" { "FinDash" }
        "Homelab_MSH" { "Homelab" }
        "HomeAssistant" { "HA-MCP" }
        "Note_synch" { "NoteSync" }
        "atlas-agent-framework" { "Atlas-Fw" }
        default { $projectName }
    }

    # Calculate relative path
    $relativePath = $scanPath.Replace("$WorkspaceRoot\", "").Replace("$WorkspaceRoot/", "")

    # Infer status
    $status = "active"
    if ($projectName -match "Archive|OLD|deprecated") {
        $status = "archived"
    }

    # Build project object
    $project = [PSCustomObject]@{
        id = ($projectName.ToLower() -replace '[^a-z0-9-]', '-')
        name = $projectName
        display_name = $displayName
        path = $scanPath
        relative_path = $relativePath
        type = $type
        status = $status
        description = $description
        tech_stack = @($techStack)
        quick_commands = @()
        metadata = [PSCustomObject]@{
            has_claude_md = $signals.hasClaude
            has_git = $signals.hasGit
            has_dev_folder = $signals.hasDev
            primary_languages = @($techStack | Where-Object { $_ -in @("python", "typescript", "javascript") })
        }
    }

    # Discover sub-projects for monorepos
    if ($type -eq "monorepo" -and $signals.hasAppsFolder) {
        $subProjects = @()
        Get-ChildItem (Join-Path $scanPath "apps") -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $subProjects += [PSCustomObject]@{
                id = $_.Name.ToLower()
                name = $_.Name.ToUpper()
                path = "apps/$($_.Name)"
                type = "application"
            }
        }
        $project | Add-Member -NotePropertyName "sub_projects" -NotePropertyValue $subProjects -Force
    }

    $discoveredProjects += $project

    if ($Verbose) {
        Write-Host "    Type: $type | Tech: $($techStack -join ', ')" -ForegroundColor Green
    }
}

# Build registry object
$registry = [PSCustomObject]@{
    version = "1.0.0"
    last_updated = (Get-Date -Format "o")
    workspace_root = $WorkspaceRoot
    projects = $discoveredProjects
}

# Output summary
Write-Host ""
Write-Host "Discovered $($discoveredProjects.Count) projects:" -ForegroundColor Cyan
$discoveredProjects | ForEach-Object {
    $techStr = if ($_.tech_stack.Count -gt 0) { " ($($_.tech_stack -join ', '))" } else { "" }
    Write-Host "  - $($_.display_name) [$($_.type)]$techStr" -ForegroundColor White
}

# Write registry
if (-not $DryRun) {
    $registry | ConvertTo-Json -Depth 10 | Set-Content $projectsPath -Encoding UTF8
    Write-Host ""
    Write-Host "Registry updated: $projectsPath" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[DRY RUN] Registry not written" -ForegroundColor Yellow
}

# Return registry as JSON for programmatic use
$registry | ConvertTo-Json -Depth 10
