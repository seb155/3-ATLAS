# ==============================================================================
# ADD LOCAL DOMAIN ENTRIES TO HOSTS FILE
# ==============================================================================
# Run as Administrator: Right-click > Run as Administrator
#
# This script adds local DNS entries for axoiq.com subdomains
# ==============================================================================

$hostsFile = "C:\Windows\System32\drivers\etc\hosts"
$domains = @(
    "# EPCB Workspace - Local Development",
    "127.0.0.1    nexus.axoiq.com",
    "127.0.0.1    api-nexus.axoiq.com",
    "127.0.0.1    synapse.axoiq.com",
    "127.0.0.1    api.axoiq.com",
    "127.0.0.1    portal.axoiq.com",
    "127.0.0.1    grafana.axoiq.com",
    "127.0.0.1    loki.axoiq.com",
    "127.0.0.1    pgadmin.axoiq.com",
    "127.0.0.1    prisma.axoiq.com"
)

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "Adding local domain entries to hosts file" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Right-click this file and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

# Backup hosts file
$backup = "$hostsFile.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Copy-Item $hostsFile $backup
Write-Host "✓ Backup created: $backup" -ForegroundColor Green

# Read current hosts file
$currentHosts = Get-Content $hostsFile

# Check if entries already exist
$alreadyExists = $false
foreach ($domain in $domains) {
    if ($currentHosts -contains $domain) {
        $alreadyExists = $true
        break
    }
}

if ($alreadyExists) {
    Write-Host ""
    Write-Host "⚠ Some entries already exist in hosts file" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite? (y/n)"

    if ($overwrite -ne "y") {
        Write-Host "Cancelled." -ForegroundColor Yellow
        exit 0
    }

    # Remove existing entries
    $newHosts = $currentHosts | Where-Object {
        $_ -notmatch "axoiq.com" -and $_ -notmatch "EPCB Workspace"
    }
    Set-Content $hostsFile $newHosts
}

# Add new entries
Add-Content $hostsFile ""
foreach ($domain in $domains) {
    Add-Content $hostsFile $domain
    Write-Host "✓ Added: $domain" -ForegroundColor Green
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "✓ Local domain entries added successfully!" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now access:" -ForegroundColor White
Write-Host "  - Nexus:    https://nexus.axoiq.com" -ForegroundColor Cyan
Write-Host "  - Synapse:  https://synapse.axoiq.com" -ForegroundColor Cyan
Write-Host "  - Portal:   https://portal.axoiq.com" -ForegroundColor Cyan
Write-Host "  - Grafana:  https://grafana.axoiq.com" -ForegroundColor Cyan
Write-Host "  - pgAdmin:  https://pgadmin.axoiq.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Generate SSL certificates with mkcert" -ForegroundColor White
Write-Host "  2. Restart Traefik" -ForegroundColor White
Write-Host ""
pause
