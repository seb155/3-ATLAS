# Atlas Registry Sync Wrapper
# User-friendly wrapper for discover-projects.ps1

param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$Quiet
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$discoverScript = Join-Path $scriptDir "discover-projects.ps1"

if (-not (Test-Path $discoverScript)) {
    Write-Error "Discovery script not found: $discoverScript"
    exit 1
}

if (-not $Quiet) {
    Write-Host ""
    Write-Host "  Atlas Project Registry Sync" -ForegroundColor Cyan
    Write-Host "  ===========================" -ForegroundColor Cyan
    Write-Host ""
}

$params = @{
    Verbose = (-not $Quiet)
}

if ($DryRun) { $params.DryRun = $true }
if ($Force) { $params.Force = $true }

# Run discovery
$result = & $discoverScript @params

if (-not $Quiet) {
    Write-Host ""
    if ($DryRun) {
        Write-Host "  [DRY RUN] No changes made" -ForegroundColor Yellow
    } else {
        Write-Host "  Registry synced successfully!" -ForegroundColor Green
    }
    Write-Host ""
}
