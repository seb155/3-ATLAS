# ==============================================================================
# GENERATE LOCAL SSL CERTIFICATES WITH MKCERT
# ==============================================================================
# This script generates trusted SSL certificates for local development
# ==============================================================================

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "Generating local SSL certificates for axoiq.com" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if mkcert is installed
$mkcertPath = Get-Command mkcert -ErrorAction SilentlyContinue

if (-not $mkcertPath) {
    Write-Host "ERROR: mkcert is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install mkcert with one of these commands:" -ForegroundColor Yellow
    Write-Host "  choco install mkcert" -ForegroundColor White
    Write-Host "  scoop install mkcert" -ForegroundColor White
    Write-Host ""
    Write-Host "Then run this script again." -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

Write-Host "✓ mkcert is installed" -ForegroundColor Green
Write-Host ""

# Install local CA (if not already done)
Write-Host "Installing local Certificate Authority..." -ForegroundColor Cyan
mkcert -install
Write-Host ""

# Navigate to traefik config directory
$certDir = "D:\Projects\EPCB-Tools\workspace\config\traefik"
Set-Location $certDir

Write-Host "Generating wildcard certificate for *.axoiq.com..." -ForegroundColor Cyan
Write-Host ""

# Generate wildcard certificate
mkcert -cert-file axoiq.com.crt -key-file axoiq.com.key "*.axoiq.com" "axoiq.com"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==============================================================================" -ForegroundColor Cyan
    Write-Host "✓ SSL Certificates generated successfully!" -ForegroundColor Green
    Write-Host "==============================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Certificate files created:" -ForegroundColor White
    Write-Host "  - $certDir\axoiq.com.crt" -ForegroundColor Cyan
    Write-Host "  - $certDir\axoiq.com.key" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "These certificates are valid for:" -ForegroundColor White
    Write-Host "  - *.axoiq.com (all subdomains)" -ForegroundColor Cyan
    Write-Host "  - axoiq.com (root domain)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Restart Traefik: docker restart forge-traefik" -ForegroundColor White
    Write-Host "  2. Access https://nexus.axoiq.com (no SSL warning!)" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR: Failed to generate certificates" -ForegroundColor Red
    Write-Host ""
}

pause
