# ==============================================================================
# CONFIGURE DNS WINDOWS POUR DNSMASQ
# ==============================================================================
# Exécuter en tant qu'administrateur
# ==============================================================================

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "Configuration DNS Windows pour dnsmasq (*.axoiq.com)" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check for admin rights
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: Ce script doit être exécuté en tant qu'Administrateur!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Clic droit > Exécuter en tant qu'administrateur" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

# Find active network adapters
Write-Host "Recherche des adaptateurs réseau actifs..." -ForegroundColor Cyan
$adapters = Get-NetAdapter | Where-Object Status -eq 'Up' | Where-Object {$_.Name -notlike '*WSL*' -and $_.Name -notlike '*Loopback*'}

if ($adapters.Count -eq 0) {
    Write-Host "Aucun adaptateur réseau actif trouvé!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "Adaptateurs réseau trouvés:" -ForegroundColor White
$i = 1
foreach ($adapter in $adapters) {
    Write-Host "  [$i] $($adapter.Name) - $($adapter.InterfaceDescription)" -ForegroundColor Green
    $i++
}
Write-Host ""

# Select adapter
if ($adapters.Count -eq 1) {
    $selectedAdapter = $adapters[0]
    Write-Host "Sélection automatique: $($selectedAdapter.Name)" -ForegroundColor Yellow
} else {
    $selection = Read-Host "Sélectionnez l'adaptateur (1-$($adapters.Count))"
    $selectedAdapter = $adapters[[int]$selection - 1]
}

Write-Host ""
Write-Host "Configuration de '$($selectedAdapter.Name)'..." -ForegroundColor Cyan

# Get current DNS settings
$currentDNS = Get-DnsClientServerAddress -InterfaceAlias $selectedAdapter.Name -AddressFamily IPv4

if ($currentDNS.ServerAddresses) {
    Write-Host ""
    Write-Host "DNS actuel:" -ForegroundColor Yellow
    foreach ($dns in $currentDNS.ServerAddresses) {
        Write-Host "  - $dns" -ForegroundColor White
    }
}

Write-Host ""
$confirm = Read-Host "Voulez-vous configurer le DNS local? (y/n)"

if ($confirm -ne 'y') {
    Write-Host "Annulé." -ForegroundColor Yellow
    pause
    exit 0
}

# Configure DNS
Write-Host ""
Write-Host "Configuration du DNS..." -ForegroundColor Cyan

try {
    Set-DnsClientServerAddress -InterfaceAlias $selectedAdapter.Name -ServerAddresses ('127.0.0.1','8.8.8.8')
    Write-Host "✓ DNS configuré avec succès!" -ForegroundColor Green
} catch {
    Write-Host "Erreur lors de la configuration DNS:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    pause
    exit 1
}

# Flush DNS cache
Write-Host ""
Write-Host "Vidage du cache DNS..." -ForegroundColor Cyan
ipconfig /flushdns | Out-Null
Write-Host "✓ Cache DNS vidé" -ForegroundColor Green

# Test DNS resolution
Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "Test de résolution DNS:" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

$testDomains = @('nexus.axoiq.com', 'synapse.axoiq.com', 'portal.axoiq.com')

foreach ($domain in $testDomains) {
    Write-Host "Test: $domain" -ForegroundColor White
    try {
        $result = Resolve-DnsName $domain -Type A -ErrorAction Stop
        if ($result.IPAddress -eq '127.0.0.1') {
            Write-Host "  ✓ $domain → $($result.IPAddress)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ $domain → $($result.IPAddress) (devrait être 127.0.0.1)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ✗ Échec de résolution" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "Configuration terminée!" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "TOUS les *.axoiq.com pointent maintenant vers 127.0.0.1" -ForegroundColor White
Write-Host ""
Write-Host "Vous pouvez maintenant accéder (avec SSL valide):" -ForegroundColor White
Write-Host "  - https://nexus.axoiq.com" -ForegroundColor Cyan
Write-Host "  - https://synapse.axoiq.com" -ForegroundColor Cyan
Write-Host "  - https://portal.axoiq.com" -ForegroundColor Cyan
Write-Host "  - https://grafana.axoiq.com" -ForegroundColor Cyan
Write-Host "  - https://reportportal.axoiq.com" -ForegroundColor Cyan
Write-Host "  - Et TOUT nouveau service automatiquement!" -ForegroundColor Green
Write-Host ""
Write-Host "Note: Pour revenir au DNS précédent, utilisez:" -ForegroundColor Yellow
Write-Host "  Set-DnsClientServerAddress -InterfaceAlias '$($selectedAdapter.Name)' -ResetServerAddresses" -ForegroundColor White
Write-Host ""
pause
