#!/bin/bash
# setup-windows.sh - Configure ATLAS comme application Windows native
#
# Usage:
#   ./setup-windows.sh         # Configuration normale
#   ./setup-windows.sh -f      # Force la reconfiguration
#
# Ce script cree:
#   - Raccourci sur le Bureau Windows
#   - Entree dans le Menu Demarrer
#   - Icone personnalisee dans Windows Terminal

set -e

SCRIPT_DIR=""
PS_SCRIPT="/setup-windows-app.ps1"

echo ""
echo "  ATLAS Framework - Configuration Windows"
echo "  ========================================"
echo ""

# Verifier que le script PowerShell existe
if [[ ! -f "" ]]; then
    echo "  [!] Erreur: setup-windows-app.ps1 non trouve"
    echo "      Chemin attendu: "
    exit 1
fi

# Convertir le chemin WSL en chemin Windows
WIN_PATH="D:\"

# Executer le script PowerShell
echo "  [~] Execution du script PowerShell..."
echo ""

if [[ "" == "-f" ]] || [[ "" == "--force" ]]; then
    powershell.exe -ExecutionPolicy Bypass -File "" -Force
else
    powershell.exe -ExecutionPolicy Bypass -File ""
fi

echo "  Configuration terminee!"
echo ""
