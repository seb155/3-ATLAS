# Generate .env from .env.template
# Automatically detects Docker vs local environment
# Usage: .\generate-env.ps1 [-Force]

param(
    [switch]$Force = $false
)

$ErrorActionProvider = "Stop"

# Configuration
$TemplateFile = ".env.template"
$OutputFile = ".env"
$BackupSuffix = ".backup"

# ANSI Colors
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = $Reset
    )
    Write-Host "${Color}${Message}${Reset}"
}

function Test-DockerEnvironment {
    <#
    .SYNOPSIS
    Detects if running inside Docker container
    #>

    # Check if /.dockerenv exists (standard Docker marker)
    if (Test-Path "/.dockerenv") {
        return $true
    }

    # Check if running in Docker via environment variable
    if ($env:DOCKER_CONTAINER -eq "true") {
        return $true
    }

    # Check if docker-compose is running (by checking for forge-network)
    try {
        $networks = docker network ls --format "{{.Name}}" 2>$null
        if ($networks -contains "forge-network") {
            return $true
        }
    } catch {
        # Docker command not available or failed
    }

    return $false
}

function Get-EnvironmentVariables {
    <#
    .SYNOPSIS
    Returns hashtable of variables based on environment (Docker vs Local)
    #>
    param(
        [bool]$IsDocker
    )

    if ($IsDocker) {
        Write-ColorOutput "🐳 Detected Docker environment" $Blue
        return @{
            "ENV_MODE" = "docker"
            "DATABASE_HOST" = "forge-postgres"
            "DATABASE_PORT" = "5432"
            "REDIS_HOST" = "forge-redis"
            "REDIS_PORT" = "6379"
            "LOKI_HOST" = "forge-loki"
            "LOKI_PORT" = "3100"
            "MEILISEARCH_HOST" = "forge-meilisearch"
            "MEILISEARCH_PORT" = "7700"
        }
    } else {
        Write-ColorOutput "💻 Detected local development environment" $Blue
        return @{
            "ENV_MODE" = "local"
            "DATABASE_HOST" = "localhost"
            "DATABASE_PORT" = "5433"
            "REDIS_HOST" = "localhost"
            "REDIS_PORT" = "6379"
            "LOKI_HOST" = "localhost"
            "LOKI_PORT" = "3100"
            "MEILISEARCH_HOST" = "localhost"
            "MEILISEARCH_PORT" = "7700"
        }
    }
}

function Expand-Template {
    <#
    .SYNOPSIS
    Replaces {{VARIABLE}} placeholders in template with actual values
    #>
    param(
        [string]$TemplateContent,
        [hashtable]$Variables
    )

    $result = $TemplateContent

    foreach ($key in $Variables.Keys) {
        $placeholder = "{{$key}}"
        $value = $Variables[$key]
        $result = $result -replace [regex]::Escape($placeholder), $value
    }

    return $result
}

# Main execution
try {
    Write-ColorOutput "`n=== Environment File Generator ===" $Green
    Write-ColorOutput "Template: $TemplateFile" $Blue
    Write-ColorOutput "Output: $OutputFile`n" $Blue

    # Check if template exists
    if (-not (Test-Path $TemplateFile)) {
        Write-ColorOutput "❌ Error: Template file '$TemplateFile' not found" $Red
        Write-ColorOutput "Please create a .env.template file first" $Yellow
        exit 1
    }

    # Check if .env already exists
    if ((Test-Path $OutputFile) -and -not $Force) {
        Write-ColorOutput "⚠️  .env file already exists" $Yellow
        $response = Read-Host "Overwrite? This will backup the current file. (y/N)"
        if ($response -ne 'y' -and $response -ne 'Y') {
            Write-ColorOutput "Aborted." $Yellow
            exit 0
        }
    }

    # Backup existing .env
    if (Test-Path $OutputFile) {
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $backupFile = "${OutputFile}${BackupSuffix}-${timestamp}"
        Copy-Item $OutputFile $backupFile
        Write-ColorOutput "✓ Backed up existing .env to: $backupFile" $Green
    }

    # Detect environment
    $isDocker = Test-DockerEnvironment
    $variables = Get-EnvironmentVariables -IsDocker $isDocker

    # Read template
    $templateContent = Get-Content $TemplateFile -Raw

    # Expand template
    $expandedContent = Expand-Template -TemplateContent $templateContent -Variables $variables

    # Write output
    Set-Content -Path $OutputFile -Value $expandedContent -NoNewline

    Write-ColorOutput "`n✓ Successfully generated $OutputFile" $Green
    Write-ColorOutput "  Mode: $($variables['ENV_MODE'])" $Blue
    Write-ColorOutput "  Database: $($variables['DATABASE_HOST']):$($variables['DATABASE_PORT'])" $Blue

    # Show warning for unresolved placeholders
    $unresolvedMatches = [regex]::Matches($expandedContent, '{{[^}]+}}')
    if ($unresolvedMatches.Count -gt 0) {
        Write-ColorOutput "`n⚠️  Warning: Found unresolved placeholders:" $Yellow
        foreach ($match in $unresolvedMatches) {
            Write-ColorOutput "  - $($match.Value)" $Yellow
        }
        Write-ColorOutput "`nPlease manually replace these values in $OutputFile" $Yellow
    }

    Write-ColorOutput "`n✓ Done!`n" $Green

} catch {
    Write-ColorOutput "`n❌ Error: $($_.Exception.Message)" $Red
    exit 1
}
