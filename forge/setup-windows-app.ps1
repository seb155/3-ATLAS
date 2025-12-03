# setup-windows-app.ps1
# Configure ATLAS comme application Windows native
# Usage: powershell -ExecutionPolicy Bypass -File setup-windows-app.ps1

param(
    [string] = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Classical%20building/3D/classical_building_3d.png",
    [switch]
)

Write-Host ""
Write-Host "  Configuration ATLAS pour Windows" -ForegroundColor Cyan
Write-Host "  ================================" -ForegroundColor Cyan
Write-Host ""

# 1. Creer le dossier Icons
 = ":USERPROFILE\Pictures\Icons"
if (-not (Test-Path )) {
    New-Item -ItemType Directory -Path  -Force | Out-Null
    Write-Host "  [+] Dossier Icons cree" -ForegroundColor Green
}

# 2. Telecharger et convertir l icone si necessaire
 = "\atlas.ico"
 = "\atlas.png"

if (-not (Test-Path ) -or ) {
    Write-Host "  [~] Telechargement de l icone..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri  -OutFile  -ErrorAction Stop
        
        # Convertir PNG en ICO
        Add-Type -AssemblyName System.Drawing
         = [System.Drawing.Image]::FromFile()
         = New-Object System.Drawing.Bitmap(, 256, 256)
         = [System.Drawing.Icon]::FromHandle(.GetHicon())
         = [System.IO.File]::Create()
        .Save()
        .Close()
        .Dispose()
        .Dispose()
        
        Write-Host "  [+] Icone creee: " -ForegroundColor Green
    }
    catch {
        Write-Host "  [!] Erreur telechargement icone: " -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  [=] Icone existe deja" -ForegroundColor Gray
}

# 3. Creer les raccourcis
 = New-Object -ComObject WScript.Shell

# Bureau
 = ":USERPROFILE\Desktop\ATLAS.lnk"
 = .CreateShortcut()
.TargetPath = "wt.exe"
.Arguments = '-p "ATLAS"'
.IconLocation = 
.Description = "ATLAS Framework - Environnement de developpement WSL"
.Save()
Write-Host "  [+] Raccourci Bureau cree" -ForegroundColor Green

# Menu Demarrer
 = "PPDATA\Microsoft\Windows\Start Menu\Programs\ATLAS.lnk"
 = .CreateShortcut()
.TargetPath = "wt.exe"
.Arguments = '-p "ATLAS"'
.IconLocation = 
.Description = "ATLAS Framework - Environnement de developpement WSL"
.Save()
Write-Host "  [+] Raccourci Menu Demarrer cree" -ForegroundColor Green

# 4. Mettre a jour Windows Terminal (si le profil n a pas deja l icone)
 = ":LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"
if (Test-Path ) {
    try {
         = Get-Content  -Raw | ConvertFrom-Json
         = .profiles.list | Where-Object { .name -match "ATLAS" }
        if () {
            if (-not .icon -or ) {
                 | Add-Member -NotePropertyName "icon" -NotePropertyValue  -Force
                 | ConvertTo-Json -Depth 10 | Set-Content  -Encoding UTF8
                Write-Host "  [+] Windows Terminal mis a jour" -ForegroundColor Green
            } else {
                Write-Host "  [=] Windows Terminal deja configure" -ForegroundColor Gray
            }
        } else {
            Write-Host "  [!] Profil ATLAS non trouve dans Windows Terminal" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "  [!] Erreur mise a jour Windows Terminal: " -ForegroundColor Yellow
    }
} else {
    Write-Host "  [!] Windows Terminal settings.json non trouve" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  ATLAS configure avec succes!" -ForegroundColor Green
Write-Host ""
Write-Host "  Tu peux maintenant:" -ForegroundColor Cyan
Write-Host "    - Double-cliquer sur l icone ATLAS sur le Bureau"
Write-Host "    - Rechercher 'ATLAS' dans le Menu Demarrer"
Write-Host "    - Epingler a la barre des taches (clic droit)"
Write-Host ""
