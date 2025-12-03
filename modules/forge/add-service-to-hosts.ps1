# ==============================================================================
# ADD NEW SERVICE TO HOSTS FILE
# ==============================================================================
# Quick script to add a new axoiq.com subdomain to hosts file
# Run as Administrator
# ==============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$ServiceName
)

$hostsFile = "C:\Windows\System32\drivers\etc\hosts"

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    exit 1
}

# Add entry
$entry = "127.0.0.1    $ServiceName.axoiq.com"

# Check if already exists
$currentHosts = Get-Content $hostsFile
if ($currentHosts -contains $entry) {
    Write-Host "Entry already exists: $entry" -ForegroundColor Yellow
    exit 0
}

# Add entry
Add-Content $hostsFile $entry
Write-Host "✓ Added: $entry" -ForegroundColor Green

Write-Host ""
Write-Host "Access your service at: https://$ServiceName.axoiq.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "Don't forget to add the route in Traefik dynamic.yml!" -ForegroundColor Yellow
