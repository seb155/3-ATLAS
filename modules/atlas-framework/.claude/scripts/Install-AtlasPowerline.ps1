<#
.SYNOPSIS
    Install Atlas Powerline status line for Claude Code CLI.

.DESCRIPTION
    Creates all necessary configuration files for the Atlas Framework
    Powerline status line in Claude Code.

.PARAMETER Validate
    Only validate the current installation, don't make changes.

.PARAMETER Force
    Overwrite existing files (default: skip if exists).

.EXAMPLE
    .\Install-AtlasPowerline.ps1
    Install with default settings (skip existing files).

.EXAMPLE
    .\Install-AtlasPowerline.ps1 -Force
    Reinstall, overwriting all files.

.EXAMPLE
    .\Install-AtlasPowerline.ps1 -Validate
    Check current installation status.
#>

param(
    [switch]$Validate,
    [switch]$Force
)

# ============================================================================
# Configuration
# ============================================================================

$ErrorActionPreference = "Stop"
$userProfile = [Environment]::GetFolderPath('UserProfile')
$claudeDir = Join-Path $userProfile ".claude"
$hooksDir = Join-Path $claudeDir "hooks"
$ccDir = Join-Path $userProfile ".config\ccstatusline"

# Script location (where templates are)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$templatesDir = Join-Path $scriptDir "templates"

# Files mapping: source template -> destination
$fileMappings = @{
    "atlas-agent.ps1" = @{
        Source = Join-Path $templatesDir "atlas-agent.ps1"
        Dest = Join-Path $claudeDir "atlas-agent.ps1"
    }
    "detect-project.ps1" = @{
        Source = Join-Path $templatesDir "detect-project.ps1"
        Dest = Join-Path $claudeDir "detect-project.ps1"
    }
    "track-agent.ps1" = @{
        Source = Join-Path $templatesDir "track-agent.ps1"
        Dest = Join-Path $hooksDir "track-agent.ps1"
    }
    "settings.json" = @{
        Source = Join-Path $templatesDir "settings.json"
        Dest = Join-Path $claudeDir "settings.json"
    }
    "ccstatusline.json" = @{
        Source = Join-Path $templatesDir "ccstatusline.json"
        Dest = Join-Path $ccDir "settings.json"
    }
}

# ============================================================================
# Helper Functions
# ============================================================================

function Write-Status {
    param([string]$Message, [string]$Type = "Info")

    switch ($Type) {
        "Success" { Write-Host "[OK] " -ForegroundColor Green -NoNewline; Write-Host $Message }
        "Error"   { Write-Host "[X] " -ForegroundColor Red -NoNewline; Write-Host $Message }
        "Warning" { Write-Host "[!] " -ForegroundColor Yellow -NoNewline; Write-Host $Message }
        "Info"    { Write-Host "[*] " -ForegroundColor Cyan -NoNewline; Write-Host $Message }
        "Skip"    { Write-Host "[-] " -ForegroundColor DarkGray -NoNewline; Write-Host $Message }
    }
}

function Test-Prerequisites {
    Write-Host "`n=== Prerequisites ===" -ForegroundColor Cyan

    $allGood = $true

    # Check Node.js
    try {
        $nodeVersion = node --version 2>$null
        Write-Status "Node.js: $nodeVersion" "Success"
    } catch {
        Write-Status "Node.js not found (required for ccstatusline)" "Error"
        $allGood = $false
    }

    # Check npm
    try {
        $npmVersion = npm --version 2>$null
        Write-Status "npm: $npmVersion" "Success"
    } catch {
        Write-Status "npm not found" "Error"
        $allGood = $false
    }

    # Check JetBrainsMono Nerd Font
    $fontInstalled = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" -ErrorAction SilentlyContinue |
        Get-Member -MemberType NoteProperty |
        Where-Object { $_.Name -match "JetBrainsMono.*Nerd" }

    if ($fontInstalled) {
        Write-Status "JetBrainsMono Nerd Font: Installed" "Success"
    } else {
        Write-Status "JetBrainsMono Nerd Font: Not found" "Warning"
        Write-Host "       Install with: winget install DEVCOM.JetBrainsMonoNerdFont" -ForegroundColor DarkGray
    }

    # Check templates directory
    if (Test-Path $templatesDir) {
        Write-Status "Templates directory: Found" "Success"
    } else {
        Write-Status "Templates directory: Not found at $templatesDir" "Error"
        $allGood = $false
    }

    return $allGood
}

function Test-Installation {
    Write-Host "`n=== Installation Status ===" -ForegroundColor Cyan

    $allGood = $true

    # Check directories
    if (Test-Path $claudeDir) {
        Write-Status "Directory: ~/.claude/" "Success"
    } else {
        Write-Status "Directory: ~/.claude/ (missing)" "Error"
        $allGood = $false
    }

    if (Test-Path $hooksDir) {
        Write-Status "Directory: ~/.claude/hooks/" "Success"
    } else {
        Write-Status "Directory: ~/.claude/hooks/ (missing)" "Error"
        $allGood = $false
    }

    if (Test-Path $ccDir) {
        Write-Status "Directory: ~/.config/ccstatusline/" "Success"
    } else {
        Write-Status "Directory: ~/.config/ccstatusline/ (missing)" "Error"
        $allGood = $false
    }

    # Check files
    foreach ($name in $fileMappings.Keys) {
        $dest = $fileMappings[$name].Dest
        if (Test-Path $dest) {
            Write-Status "File: $name" "Success"
        } else {
            Write-Status "File: $name (missing)" "Error"
            $allGood = $false
        }
    }

    return $allGood
}

# ============================================================================
# Installation Functions
# ============================================================================

function Install-Directories {
    Write-Host "`n=== Creating Directories ===" -ForegroundColor Cyan

    # Create ~/.claude/hooks
    if (-not (Test-Path $hooksDir)) {
        New-Item -ItemType Directory -Force -Path $hooksDir | Out-Null
        Write-Status "Created: ~/.claude/hooks/" "Success"
    } else {
        Write-Status "Exists: ~/.claude/hooks/" "Skip"
    }

    # Create ~/.config/ccstatusline
    if (-not (Test-Path $ccDir)) {
        New-Item -ItemType Directory -Force -Path $ccDir | Out-Null
        Write-Status "Created: ~/.config/ccstatusline/" "Success"
    } else {
        Write-Status "Exists: ~/.config/ccstatusline/" "Skip"
    }
}

function Install-File {
    param(
        [string]$Source,
        [string]$Dest,
        [string]$Name
    )

    $exists = Test-Path $Dest

    if ($exists -and -not $Force) {
        Write-Status "$Name (exists, use -Force to overwrite)" "Skip"
        return
    }

    if (-not (Test-Path $Source)) {
        Write-Status "$Name (template not found: $Source)" "Error"
        return
    }

    # Copy with proper encoding preservation
    Copy-Item -Path $Source -Destination $Dest -Force

    if ($exists) {
        Write-Status "$Name (overwritten)" "Success"
    } else {
        Write-Status "$Name (created)" "Success"
    }
}

function Install-SettingsJson {
    $mapping = $fileMappings["settings.json"]
    $source = $mapping.Source
    $dest = $mapping.Dest
    $exists = Test-Path $dest

    if ($exists -and -not $Force) {
        # Merge with existing
        try {
            $existing = Get-Content $dest -Raw -Encoding UTF8 | ConvertFrom-Json
            $new = Get-Content $source -Raw -Encoding UTF8 | ConvertFrom-Json

            # Add/update statusLine
            $existing | Add-Member -NotePropertyName "statusLine" -NotePropertyValue $new.statusLine -Force

            # Add/update hooks
            $existing | Add-Member -NotePropertyName "hooks" -NotePropertyValue $new.hooks -Force

            $existing | ConvertTo-Json -Depth 10 | Set-Content $dest -Encoding UTF8
            Write-Status "settings.json (merged)" "Success"
        } catch {
            Write-Status "settings.json (merge failed: $($_.Exception.Message))" "Error"
        }
    } else {
        Install-File -Source $source -Dest $dest -Name "settings.json"
    }
}

function Install-CcStatuslineJson {
    $mapping = $fileMappings["ccstatusline.json"]
    $source = $mapping.Source
    $dest = $mapping.Dest
    $exists = Test-Path $dest

    if ($exists -and -not $Force) {
        Write-Status "ccstatusline.json (exists, use -Force to overwrite)" "Skip"
        return
    }

    if (-not (Test-Path $source)) {
        Write-Status "ccstatusline.json (template not found: $source)" "Error"
        return
    }

    # Read template and replace {{USERPROFILE}} with actual path
    try {
        $templateContent = Get-Content $source -Raw -Encoding UTF8

        # Replace placeholder with actual path (double backslash for JSON escaping)
        $userProfileEscaped = $userProfile -replace '\\', '\\\\'
        $templateContent = $templateContent -replace '\{\{USERPROFILE\}\}', $userProfileEscaped

        # Save with UTF8 encoding
        $templateContent | Set-Content $dest -Encoding UTF8 -NoNewline

        if ($exists) {
            Write-Status "ccstatusline.json (overwritten with path substitution)" "Success"
        } else {
            Write-Status "ccstatusline.json (created with path substitution)" "Success"
        }
    } catch {
        Write-Status "ccstatusline.json (error: $($_.Exception.Message))" "Error"
    }
}

function Install-AllFiles {
    Write-Host "`n=== Installing Files ===" -ForegroundColor Cyan

    foreach ($name in $fileMappings.Keys) {
        if ($name -eq "settings.json") {
            Install-SettingsJson
        } elseif ($name -eq "ccstatusline.json") {
            Install-CcStatuslineJson
        } else {
            $mapping = $fileMappings[$name]
            Install-File -Source $mapping.Source -Dest $mapping.Dest -Name $name
        }
    }
}

# ============================================================================
# Main
# ============================================================================

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Atlas Powerline Installer" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

if ($Validate) {
    Test-Prerequisites | Out-Null
    $result = Test-Installation

    Write-Host ""
    if ($result) {
        Write-Host "Installation is complete!" -ForegroundColor Green
    } else {
        Write-Host "Installation has issues. Run without -Validate to fix." -ForegroundColor Yellow
    }
} else {
    $prereqOk = Test-Prerequisites

    if (-not $prereqOk) {
        Write-Host "`nPrerequisites check failed. Fix issues above and retry." -ForegroundColor Red
        exit 1
    }

    Install-Directories
    Install-AllFiles

    Write-Host ""
    Test-Installation | Out-Null

    Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
    Write-Host "1. Restart Claude Code to apply changes"
    Write-Host "2. Ensure Windows Terminal uses JetBrainsMono Nerd Font"
    Write-Host ""
    Write-Host "Your Powerline will display:" -ForegroundColor Cyan
    Write-Host "  ATLAS | Model | Project | git | Agent | Context | Cost | Tokens"
    Write-Host ""
}
