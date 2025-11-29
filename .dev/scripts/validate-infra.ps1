# ==============================================================================
# AXIOM Infrastructure Validator
# ==============================================================================
# Validates infrastructure configuration against registry rules
# Checks for: port conflicts, range violations, network requirements, dependencies
# ==============================================================================

param(
    [string]$RegistryPath = "D:\Projects\AXIOM\.dev\infra\registry.yml",
    [switch]$Fix,
    [switch]$Verbose,
    [switch]$Silent
)

# Color output helpers
function Write-Success { param($Message) Write-Host "  ✅ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "  ❌ $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "  ⚠️  $Message" -ForegroundColor Yellow }
function Write-Info { param($Message) Write-Host "  📋 $Message" -ForegroundColor Cyan }
function Write-Section { param($Message) Write-Host "`n$Message" -ForegroundColor Yellow }

if (-not $Silent) {
    Write-Host "==============================================================================" -ForegroundColor Cyan
    Write-Host "AXIOM Infrastructure Validator" -ForegroundColor Cyan
    Write-Host "==============================================================================" -ForegroundColor Cyan
    Write-Host ""
}

# ==============================================================================
# Load Registry
# ==============================================================================

if (-not (Test-Path $RegistryPath)) {
    Write-Error "Registry not found at $RegistryPath"
    exit 1
}

# Load PowerShell YAML module (install if needed)
if (-not (Get-Module -ListAvailable -Name powershell-yaml)) {
    Write-Warning "PowerShell YAML module not installed. Installing..."
    Install-Module -Name powershell-yaml -Force -Scope CurrentUser
}

Import-Module powershell-yaml -ErrorAction SilentlyContinue

# Read registry as hashtable
try {
    $registryContent = Get-Content $RegistryPath -Raw
    $registry = ConvertFrom-Yaml $registryContent
} catch {
    Write-Error "Failed to parse registry.yml: $_"
    exit 1
}

# Validation counters
$script:totalIssues = 0
$script:portConflicts = 0
$script:rangeViolations = 0
$script:networkIssues = 0
$script:depIssues = 0

# ==============================================================================
# Validation 1: Check for Port Conflicts
# ==============================================================================

Write-Section "Validating port allocations..."

$allocatedPorts = $registry.port_registry.allocated
$portMap = @{}
$conflicts = @()

foreach ($portKey in $allocatedPorts.Keys) {
    $port = [int]$portKey
    $service = $allocatedPorts[$portKey]

    # Check if port already allocated
    if ($portMap.ContainsKey($port)) {
        $conflicts += @{
            Port = $port
            Service1 = $portMap[$port].service
            Service2 = $service.service
        }
        $script:portConflicts++
        $script:totalIssues++
    } else {
        $portMap[$port] = $service
    }
}

if ($conflicts.Count -gt 0) {
    Write-Error "PORT CONFLICTS DETECTED:"
    foreach ($conflict in $conflicts) {
        Write-Host "     Port $($conflict.Port): $($conflict.Service1) vs $($conflict.Service2)" -ForegroundColor Red
    }
} else {
    Write-Success "No port conflicts detected"
}

# ==============================================================================
# Validation 2: Check Port Ranges
# ==============================================================================

Write-Section "Validating port ranges..."

$ranges = $registry.port_registry.ranges
$rangeViolations = @()

foreach ($portKey in $allocatedPorts.Keys) {
    $port = [int]$portKey
    $service = $allocatedPorts[$portKey]
    $app = $service.app

    # Skip system services (forge, traefik) - they have special rules
    if ($app -in @("forge", "traefik")) {
        if ($Verbose) {
            Write-Info "Skipping range check for system service: $($service.service) (port $port)"
        }
        continue
    }

    # Check if app has a defined range
    if (-not $ranges.ContainsKey($app)) {
        Write-Warning "App '$app' does not have a defined port range"
        continue
    }

    # Check if port is in correct range
    $range = $ranges[$app]
    $rangeStart = $range.start
    $rangeEnd = $range.end

    if ($port -lt $rangeStart -or $port -gt $rangeEnd) {
        $rangeViolations += @{
            Port = $port
            Service = $service.service
            App = $app
            ExpectedRange = "$rangeStart-$rangeEnd"
        }
        $script:rangeViolations++
        $script:totalIssues++
    }
}

if ($rangeViolations.Count -gt 0) {
    Write-Error "RANGE VIOLATIONS DETECTED:"
    foreach ($violation in $rangeViolations) {
        Write-Host "     $($violation.Service) on port $($violation.Port) should be in range $($violation.ExpectedRange)" -ForegroundColor Red
    }
} else {
    Write-Success "All ports in correct ranges"
}

# ==============================================================================
# Validation 3: Check Network Requirements
# ==============================================================================

Write-Section "Validating network requirements..."

# Get list of running containers
$containers = docker ps --format "{{.Names}}" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Warning "Docker is not running or not accessible. Skipping network validation."
} else {
    $networkIssues = @()

    # Get all services that should be on forge-network
    $forgeNetworkServices = $registry.networks.'forge-network'.services

    foreach ($serviceName in $forgeNetworkServices) {
        # Check if container is running
        if ($containers -contains $serviceName) {
            # Check if on forge-network
            $networks = docker inspect $serviceName --format '{{range $net, $config := .NetworkSettings.Networks}}{{$net}} {{end}}' 2>$null

            if ($networks -notmatch "forge-network") {
                $networkIssues += @{
                    Service = $serviceName
                    Issue = "Not on forge-network"
                    Networks = $networks
                }
                $script:networkIssues++
                $script:totalIssues++
            }
        } elseif ($Verbose) {
            Write-Info "$serviceName is not running (skipping network check)"
        }
    }

    if ($networkIssues.Count -gt 0) {
        Write-Error "NETWORK ISSUES DETECTED:"
        foreach ($issue in $networkIssues) {
            Write-Host "     $($issue.Service): $($issue.Issue)" -ForegroundColor Red
            if ($Verbose) {
                Write-Host "       Current networks: $($issue.Networks)" -ForegroundColor Gray
            }
        }
    } else {
        Write-Success "All running services on correct networks"
    }
}

# ==============================================================================
# Validation 4: Check Service Dependencies
# ==============================================================================

Write-Section "Validating service dependencies..."

$depIssues = @()

# Check SYNAPSE dev dependencies
if ($registry.services.synapse.dev) {
    foreach ($service in $registry.services.synapse.dev) {
        $serviceName = $service.name

        # Check if container is running
        if ($containers -contains $serviceName) {
            # Check if dependencies are running
            foreach ($dep in $service.dependencies) {
                if ($containers -notcontains $dep) {
                    $depIssues += @{
                        Service = $serviceName
                        MissingDep = $dep
                    }
                    $script:depIssues++
                    $script:totalIssues++
                }
            }
        } elseif ($Verbose) {
            Write-Info "$serviceName is not running (skipping dependency check)"
        }
    }
}

# Check NEXUS dev dependencies
if ($registry.services.nexus.dev) {
    foreach ($service in $registry.services.nexus.dev) {
        $serviceName = $service.name

        if ($containers -contains $serviceName) {
            foreach ($dep in $service.dependencies) {
                if ($containers -notcontains $dep) {
                    $depIssues += @{
                        Service = $serviceName
                        MissingDep = $dep
                    }
                    $script:depIssues++
                    $script:totalIssues++
                }
            }
        }
    }
}

if ($depIssues.Count -gt 0) {
    Write-Error "DEPENDENCY ISSUES DETECTED:"
    foreach ($issue in $depIssues) {
        Write-Host "     $($issue.Service) requires $($issue.MissingDep) which is not running" -ForegroundColor Red
    }
} else {
    Write-Success "All dependencies satisfied for running services"
}

# ==============================================================================
# Validation 5: Check for forge-network Existence
# ==============================================================================

Write-Section "Validating Docker networks..."

$networks = docker network ls --format "{{.Name}}" 2>$null

if ($networks -contains "forge-network") {
    Write-Success "forge-network exists"
} else {
    Write-Error "forge-network does not exist!"
    Write-Host "       Create it with: docker network create forge-network" -ForegroundColor Yellow
    $script:totalIssues++
}

# ==============================================================================
# Validation 6: Check Health Checks for Critical Services
# ==============================================================================

Write-Section "Validating health checks..."

$criticalServiceTypes = @("database", "cache", "api")
$missingHealthChecks = @()

foreach ($portKey in $allocatedPorts.Keys) {
    $service = $allocatedPorts[$portKey]

    # Check if service type is critical
    if ($service.type -in $criticalServiceTypes) {
        # Find service definition in registry
        $serviceFound = $false

        # Check FORGE services
        foreach ($forgeService in $registry.services.forge) {
            if ($forgeService.name -eq $service.service) {
                $serviceFound = $true
                if (-not $forgeService.health_check) {
                    $missingHealthChecks += $service.service
                }
                break
            }
        }

        # Check SYNAPSE services
        if (-not $serviceFound -and $registry.services.synapse.dev) {
            foreach ($synapseService in $registry.services.synapse.dev) {
                if ($synapseService.name -eq $service.service) {
                    $serviceFound = $true
                    # SYNAPSE services don't have health_check in registry (acceptable)
                    break
                }
            }
        }
    }
}

if ($missingHealthChecks.Count -gt 0) {
    Write-Warning "Critical services without health checks:"
    foreach ($svc in $missingHealthChecks) {
        Write-Host "     $svc" -ForegroundColor Yellow
    }
} else {
    Write-Success "All critical services have health checks (or are application services)"
}

# ==============================================================================
# Summary
# ==============================================================================

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan

if ($script:totalIssues -eq 0) {
    Write-Host "✅ VALIDATION PASSED - No issues detected" -ForegroundColor Green
} else {
    Write-Host "❌ VALIDATION FAILED - $script:totalIssues issues detected" -ForegroundColor Red
    Write-Host ""
    Write-Host "Issue Breakdown:" -ForegroundColor Yellow
    if ($script:portConflicts -gt 0) {
        Write-Host "  - Port conflicts: $script:portConflicts" -ForegroundColor Red
    }
    if ($script:rangeViolations -gt 0) {
        Write-Host "  - Range violations: $script:rangeViolations" -ForegroundColor Red
    }
    if ($script:networkIssues -gt 0) {
        Write-Host "  - Network issues: $script:networkIssues" -ForegroundColor Red
    }
    if ($script:depIssues -gt 0) {
        Write-Host "  - Dependency issues: $script:depIssues" -ForegroundColor Red
    }

    if ($Fix) {
        Write-Host ""
        Write-Host "⚠️  Automatic fixes are not yet implemented." -ForegroundColor Yellow
        Write-Host "    Please consult DevOps Manager agent for guidance." -ForegroundColor Yellow
    }
}

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

# Exit with appropriate code
exit $(if ($script:totalIssues -eq 0) { 0 } else { 1 })
