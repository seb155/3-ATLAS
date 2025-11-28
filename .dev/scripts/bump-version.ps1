<#
.SYNOPSIS
    Bump version number across all project files.
.DESCRIPTION
    Updates VERSION file, package.json, and backend __init__.py with new version.
.PARAMETER Type
    Version bump type: major, minor, patch, or explicit version (e.g., "0.3.0")
.EXAMPLE
    .\bump-version.ps1 -Type minor
    .\bump-version.ps1 -Type "0.3.0"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Type
)

$ErrorActionPreference = "Stop"

# Paths
$rootPath = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$versionFile = Join-Path $rootPath "VERSION"
$packageJson = Join-Path $rootPath "apps\synapse\frontend\package.json"
$backendInit = Join-Path $rootPath "apps\synapse\backend\app\__init__.py"

# Read current version
$currentVersion = (Get-Content $versionFile -Raw).Trim()
$currentVersion = $currentVersion -replace "-dev", ""
Write-Host "Current version: $currentVersion" -ForegroundColor Cyan

# Parse version
$versionParts = $currentVersion -split "\."
$major = [int]$versionParts[0]
$minor = [int]$versionParts[1]
$patch = [int]$versionParts[2]

# Calculate new version
if ($Type -match "^\d+\.\d+\.\d+") {
    $newVersion = $Type
} else {
    switch ($Type.ToLower()) {
        "major" { $major++; $minor = 0; $patch = 0 }
        "minor" { $minor++; $patch = 0 }
        "patch" { $patch++ }
        default {
            Write-Host "Invalid type: $Type. Use major, minor, patch, or explicit version." -ForegroundColor Red
            exit 1
        }
    }
    $newVersion = "$major.$minor.$patch"
}

Write-Host "New version: $newVersion" -ForegroundColor Green

# Update VERSION file
Set-Content -Path $versionFile -Value $newVersion -NoNewline
Write-Host "Updated: VERSION" -ForegroundColor Gray

# Update package.json
if (Test-Path $packageJson) {
    $json = Get-Content $packageJson -Raw | ConvertFrom-Json
    $json.version = $newVersion
    $json | ConvertTo-Json -Depth 10 | Set-Content $packageJson
    Write-Host "Updated: apps/synapse/frontend/package.json" -ForegroundColor Gray
}

# Update backend __init__.py
if (Test-Path $backendInit) {
    $content = Get-Content $backendInit -Raw
    if ($content -match '__version__\s*=\s*[''"]([^''"]+)[''"]') {
        $content = $content -replace '__version__\s*=\s*[''"][^''"]+[''"]', "__version__ = `"$newVersion`""
        Set-Content -Path $backendInit -Value $content -NoNewline
        Write-Host "Updated: apps/synapse/backend/app/__init__.py" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Version bumped to $newVersion" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Update CHANGELOG.md"
Write-Host "  2. Create release notes: .dev/releases/v$newVersion.md"
Write-Host "  3. Commit: git commit -am 'chore: release v$newVersion'"
Write-Host "  4. Tag: git tag -a v$newVersion -m 'Release v$newVersion'"
