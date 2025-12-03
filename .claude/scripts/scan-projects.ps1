# scan-projects.ps1
# Scans all projects from registry and returns status JSON
# Used by: projects-scanner agent, /0-projects-status, /0-new-session

param(
    [string]$RegistryPath,
    [switch]$Detailed,
    [string]$ProjectId
)

# Default registry path - resolve from script location or workspace root
if (-not $RegistryPath) {
    $workspaceRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
    $RegistryPath = Join-Path $workspaceRoot ".registry\projects.json"

    # Fallback: try D:\Projects directly
    if (-not (Test-Path $RegistryPath)) {
        $RegistryPath = "D:\Projects\.registry\projects.json"
    }
}

$ErrorActionPreference = "SilentlyContinue"

function Get-GitStatus {
    param([string]$Path)

    if (-not (Test-Path "$Path\.git")) {
        return @{ hasGit = $false }
    }

    Push-Location $Path
    try {
        $branch = git rev-parse --abbrev-ref HEAD 2>$null
        $status = git status --porcelain 2>$null
        $ahead = git rev-list --count "@{u}..HEAD" 2>$null
        $behind = git rev-list --count "HEAD..@{u}" 2>$null

        $modified = ($status | Where-Object { $_ -match "^ M|^MM" }).Count
        $untracked = ($status | Where-Object { $_ -match "^\?\?" }).Count
        $staged = ($status | Where-Object { $_ -match "^[MADRC]" }).Count

        return @{
            hasGit = $true
            branch = if ($branch) { $branch } else { "unknown" }
            ahead = if ($ahead) { [int]$ahead } else { 0 }
            behind = if ($behind) { [int]$behind } else { 0 }
            modified = $modified
            untracked = $untracked
            staged = $staged
            isDirty = ($status.Count -gt 0)
        }
    }
    finally {
        Pop-Location
    }
}

function Get-DockerStatus {
    param([string]$ProjectName, [string]$Path, [string]$ProjectId)

    # Check if docker is available
    $dockerAvailable = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $dockerAvailable) {
        return @{ available = $false }
    }

    # Build project-specific patterns
    $projectLower = $ProjectName.ToLower()
    $patterns = @($projectLower)

    # Add specific patterns based on project
    switch ($ProjectId) {
        "axiom" { $patterns += @("forge-", "synapse-", "nexus-", "prism-", "cortex-") }
        "findash" { $patterns += @("findash-") }
        "homelab-msh" { $patterns = @() }  # No Docker expected
        "homeassistant" { $patterns += @("homeassistant", "influxdb") }
        "note-synch" { $patterns += @("note", "trilium", "sync") }
        "atlas-framework" { $patterns = @() }  # No Docker expected
    }

    # Skip if no patterns
    if ($patterns.Count -eq 0) {
        return @{
            available = $true
            running = @()
            stopped = @()
            runningCount = 0
            totalCount = 0
        }
    }

    # Get all containers
    $allContainers = docker ps -a --format "{{.Names}},{{.Status}}" 2>$null

    $running = @()
    $stopped = @()

    foreach ($container in $allContainers) {
        if ($container) {
            $parts = $container -split ","
            $name = $parts[0]
            $status = $parts[1]

            # Check if container matches any pattern
            $matches = $false
            foreach ($pattern in $patterns) {
                if ($name -match $pattern) {
                    $matches = $true
                    break
                }
            }

            if ($matches) {
                if ($status -match "Up") {
                    $running += $name
                } else {
                    $stopped += $name
                }
            }
        }
    }

    return @{
        available = $true
        running = $running
        stopped = $stopped
        runningCount = $running.Count
        totalCount = $running.Count + $stopped.Count
    }
}

function Get-SessionStatus {
    param([string]$Path)

    $sessionPath = "$Path\.dev\1-sessions\active\current-session.md"
    $backlogPath = "$Path\.dev\0-backlog"

    $result = @{
        hasDevFolder = (Test-Path "$Path\.dev")
        activeSession = $null
        backlogCount = 0
        lastSession = $null
    }

    if (Test-Path $sessionPath) {
        $content = Get-Content $sessionPath -Raw -ErrorAction SilentlyContinue
        if ($content -match "type:\s*(\w+)") {
            $result.activeSession = @{
                type = $Matches[1]
                file = $sessionPath
            }
            if ($content -match "started:\s*([\d-]+\s*[\d:]+)") {
                $result.activeSession.started = $Matches[1]
            }
            if ($content -match "current_task:\s*(.+)") {
                $result.activeSession.task = $Matches[1].Trim()
            }
        }
    }

    if (Test-Path $backlogPath) {
        $backlogFiles = Get-ChildItem -Path $backlogPath -Filter "*.md" -ErrorAction SilentlyContinue
        $result.backlogCount = $backlogFiles.Count
    }

    # Get last session info (did/next)
    $result.lastSession = Get-LastSessionInfo -Path $Path

    return $result
}

function Get-LastSessionInfo {
    param([string]$Path)

    $result = @{
        lastDate = $null
        did = $null
        next = $null
    }

    # Try hot-context.md first (most reliable for "next")
    $hotContext = "$Path\.dev\context\hot-context.md"
    if (Test-Path $hotContext) {
        $content = Get-Content $hotContext -Raw -ErrorAction SilentlyContinue
        $fileDate = (Get-Item $hotContext).LastWriteTime.ToString("yy-MM-dd HH:mm")
        $result.lastDate = $fileDate

        # Extract "Next Session" or "What's Next" section
        if ($content -match "(?:Next Session|What's Next|TODO)[:\s]*\n[-*\s]*(.+?)(?:\n\n|\n#|$)") {
            $result.next = $Matches[1].Trim() -replace "^[-*]\s*", ""
        }
        # Extract last completed work
        if ($content -match "(?:Completed|Done|Did)[:\s]*\n[-*\s]*(.+?)(?:\n\n|\n#|$)") {
            $result.did = $Matches[1].Trim() -replace "^[-*]\s*", ""
        }
    }

    # Try journal entries
    $journalPath = "$Path\.dev\journal"
    if (Test-Path $journalPath) {
        $latestJournal = Get-ChildItem -Path $journalPath -Filter "*.md" -Recurse -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1

        if ($latestJournal) {
            $fileDate = $latestJournal.LastWriteTime.ToString("yy-MM-dd HH:mm")
            if (-not $result.lastDate -or $fileDate -gt $result.lastDate) {
                $result.lastDate = $fileDate
            }

            $content = Get-Content $latestJournal.FullName -Raw -ErrorAction SilentlyContinue

            # Extract summary/accomplished
            if (-not $result.did -and $content -match "(?:Summary|Accomplished|Done|Completed)[:\s]*\n[-*\s]*(.+?)(?:\n\n|\n#|$)") {
                $result.did = $Matches[1].Trim() -replace "^[-*]\s*", ""
            }
            # Extract next steps
            if (-not $result.next -and $content -match "(?:Next|TODO|Priorities)[:\s]*\n[-*\s]*(.+?)(?:\n\n|\n#|$)") {
                $result.next = $Matches[1].Trim() -replace "^[-*]\s*", ""
            }
        }
    }

    # Try archived sessions
    $archivePath = "$Path\.dev\1-sessions\archive"
    if (Test-Path $archivePath) {
        $latestArchive = Get-ChildItem -Path $archivePath -Filter "*.md" -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1

        if ($latestArchive) {
            $fileDate = $latestArchive.LastWriteTime.ToString("yy-MM-dd HH:mm")
            if (-not $result.lastDate -or $fileDate -gt $result.lastDate) {
                $result.lastDate = $fileDate
            }

            $content = Get-Content $latestArchive.FullName -Raw -ErrorAction SilentlyContinue

            if (-not $result.did -and $content -match "(?:Summary|Completed|Done)[:\s]*\n[-*\s]*(.+?)(?:\n\n|\n#|$)") {
                $result.did = $Matches[1].Trim() -replace "^[-*]\s*", ""
            }
            if (-not $result.next -and $content -match "(?:Next Session|TODO)[:\s]*\n[-*\s]*(.+?)(?:\n\n|\n#|$)") {
                $result.next = $Matches[1].Trim() -replace "^[-*]\s*", ""
            }
        }
    }

    # Truncate long strings
    if ($result.did -and $result.did.Length -gt 50) {
        $result.did = $result.did.Substring(0, 47) + "..."
    }
    if ($result.next -and $result.next.Length -gt 50) {
        $result.next = $result.next.Substring(0, 47) + "..."
    }

    return $result
}

function Get-TestStatus {
    param([string]$Path)

    $result = @{
        hasTests = $false
        coverage = $null
        lastRun = $null
    }

    # Check for pytest coverage
    $coverageXml = "$Path\coverage.xml"
    $pytestCache = "$Path\.pytest_cache"
    $htmlcov = "$Path\htmlcov"

    if (Test-Path $coverageXml) {
        $result.hasTests = $true
        $result.lastRun = (Get-Item $coverageXml).LastWriteTime.ToString("yyyy-MM-dd HH:mm")

        # Parse coverage from XML
        try {
            [xml]$xml = Get-Content $coverageXml
            $lineRate = $xml.coverage.'line-rate'
            if ($lineRate) {
                $result.coverage = [math]::Round([double]$lineRate * 100, 1)
            }
        } catch {}
    }
    elseif (Test-Path $htmlcov) {
        $result.hasTests = $true
        $result.lastRun = (Get-Item $htmlcov).LastWriteTime.ToString("yyyy-MM-dd HH:mm")
    }
    elseif (Test-Path $pytestCache) {
        $result.hasTests = $true
        $result.lastRun = (Get-Item $pytestCache).LastWriteTime.ToString("yyyy-MM-dd HH:mm")
    }

    # Check for jest/vitest
    $nodeModules = "$Path\node_modules"
    $packageJson = "$Path\package.json"
    if (Test-Path $packageJson) {
        $pkg = Get-Content $packageJson -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($pkg.scripts.test) {
            $result.hasTests = $true
        }
    }

    # Check coverage folder for frontend
    $coverageFolder = "$Path\coverage"
    if (Test-Path "$coverageFolder\coverage-summary.json") {
        $result.hasTests = $true
        try {
            $summary = Get-Content "$coverageFolder\coverage-summary.json" -Raw | ConvertFrom-Json
            if ($summary.total.lines.pct) {
                $result.coverage = $summary.total.lines.pct
            }
        } catch {}
        $result.lastRun = (Get-Item "$coverageFolder\coverage-summary.json").LastWriteTime.ToString("yyyy-MM-dd HH:mm")
    }

    return $result
}

function Get-ProjectStatus {
    param($Project, [switch]$Detailed)

    $path = $Project.path

    $status = @{
        id = $Project.id
        name = $Project.name
        display_name = $Project.display_name
        path = $path
        relative_path = $Project.relative_path
        type = $Project.type
        tech_stack = $Project.tech_stack
        git = Get-GitStatus -Path $path
        docker = Get-DockerStatus -ProjectName $Project.name -Path $path -ProjectId $Project.id
        session = Get-SessionStatus -Path $path
        tests = Get-TestStatus -Path $path
    }

    # Add sub-projects scan for monorepos if detailed
    if ($Detailed -and $Project.sub_projects) {
        $status.sub_projects = @()
        foreach ($sub in $Project.sub_projects) {
            $subPath = Join-Path $path $sub.path
            if (Test-Path $subPath) {
                $status.sub_projects += @{
                    id = $sub.id
                    name = $sub.name
                    tests = Get-TestStatus -Path $subPath
                }
            }
        }
    }

    return $status
}

# Main execution
if (-not (Test-Path $RegistryPath)) {
    Write-Error "Registry not found: $RegistryPath"
    exit 1
}

$registry = Get-Content $RegistryPath -Raw | ConvertFrom-Json

$results = @{
    scan_time = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    workspace_root = $registry.workspace_root
    projects = @()
}

foreach ($project in $registry.projects) {
    if ($ProjectId -and $project.id -ne $ProjectId) {
        continue
    }

    if ($project.status -eq "active") {
        $projectStatus = Get-ProjectStatus -Project $project -Detailed:$Detailed
        $results.projects += $projectStatus
    }
}

# Output as JSON
$results | ConvertTo-Json -Depth 10
