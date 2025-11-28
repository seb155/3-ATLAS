<#
.SYNOPSIS
    Generate changelog entry from git commits.
.DESCRIPTION
    Creates a changelog section based on commits since last tag.
.PARAMETER Version
    Version number for the release (e.g., "0.3.0")
.PARAMETER Since
    Git reference to start from (default: last tag)
.EXAMPLE
    .\generate-changelog.ps1 -Version "0.3.0"
    .\generate-changelog.ps1 -Version "0.3.0" -Since "v0.2.0"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,

    [string]$Since = ""
)

$ErrorActionPreference = "Stop"

$rootPath = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $rootPath

# Get last tag if not specified
if ([string]::IsNullOrEmpty($Since)) {
    $Since = git describe --tags --abbrev=0 2>$null
    if ([string]::IsNullOrEmpty($Since)) {
        $Since = "HEAD~50"  # Fallback to last 50 commits
        Write-Host "No tags found, using last 50 commits" -ForegroundColor Yellow
    }
}

Write-Host "Generating changelog from $Since to HEAD" -ForegroundColor Cyan
Write-Host ""

# Get commits grouped by type
$commits = git log "$Since..HEAD" --pretty=format:"%s" 2>$null

$added = @()
$changed = @()
$fixed = @()
$other = @()

foreach ($commit in $commits) {
    if ($commit -match "^feat[:\(]") {
        $added += "- $($commit -replace '^feat[:\(][^\)]*\)?\s*:?\s*', '')"
    }
    elseif ($commit -match "^fix[:\(]") {
        $fixed += "- $($commit -replace '^fix[:\(][^\)]*\)?\s*:?\s*', '')"
    }
    elseif ($commit -match "^(refactor|perf|style)[:\(]") {
        $changed += "- $($commit -replace '^(refactor|perf|style)[:\(][^\)]*\)?\s*:?\s*', '')"
    }
    elseif ($commit -match "^(docs|chore|test|ci)[:\(]") {
        # Skip non-user-facing changes
    }
    else {
        $other += "- $commit"
    }
}

# Generate output
$date = Get-Date -Format "yyyy-MM-dd"
$output = @"
## [$Version] - $date

"@

if ($added.Count -gt 0) {
    $output += @"

### Added
$($added -join "`n")
"@
}

if ($changed.Count -gt 0) {
    $output += @"

### Changed
$($changed -join "`n")
"@
}

if ($fixed.Count -gt 0) {
    $output += @"

### Fixed
$($fixed -join "`n")
"@
}

if ($other.Count -gt 0 -and ($added.Count + $changed.Count + $fixed.Count) -eq 0) {
    $output += @"

### Changes
$($other -join "`n")
"@
}

$output += @"

---
"@

Write-Host "Generated changelog entry:" -ForegroundColor Green
Write-Host ""
Write-Host $output
Write-Host ""

# Ask to append to CHANGELOG.md
$changelogPath = Join-Path $rootPath "CHANGELOG.md"
Write-Host "Copy the above content to CHANGELOG.md" -ForegroundColor Yellow
Write-Host "Location: $changelogPath" -ForegroundColor Gray
