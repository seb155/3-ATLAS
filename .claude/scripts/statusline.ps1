# AXIOM StatusLine Pro for Claude Code
# Dashboard-style status bar with model, cost, git, app context, and docker status
# Author: AXIOM Team | Version: 2.0

param()

# ============================================================================
# ANSI Color Codes
# ============================================================================
$reset = "`e[0m"
$bold = "`e[1m"
$dim = "`e[2m"

# Foreground colors
$black = "`e[30m"
$red = "`e[31m"
$green = "`e[32m"
$yellow = "`e[33m"
$blue = "`e[34m"
$magenta = "`e[35m"
$cyan = "`e[36m"
$white = "`e[37m"

# ============================================================================
# Parse Claude Code JSON Input
# ============================================================================
$modelName = "CLAUDE"
$modelColor = $blue
$sessionCost = 0.0
$sessionDuration = 0

try {
    $jsonInput = $input | Out-String
    if ($jsonInput -and $jsonInput.Trim()) {
        $data = $jsonInput | ConvertFrom-Json -ErrorAction SilentlyContinue

        # Model info
        if ($data.model.display_name) {
            $modelName = $data.model.display_name.ToUpper()
            switch -Regex ($modelName) {
                "OPUS"   { $modelColor = "${bold}${blue}" }
                "SONNET" { $modelColor = "${magenta}" }
                "HAIKU"  { $modelColor = "${green}" }
                default  { $modelColor = "${cyan}" }
            }
        }

        # Cost info
        if ($data.cost.total_cost_usd) {
            $sessionCost = [math]::Round($data.cost.total_cost_usd, 2)
        }

        # Duration info
        if ($data.cost.total_duration_ms) {
            $sessionDuration = $data.cost.total_duration_ms
        }
    }
} catch {
    # Silent fail - use defaults
}

# ============================================================================
# Build Model Badge
# ============================================================================
$modelBadge = "${modelColor}[${modelName}]${reset}"

# ============================================================================
# Build Cost Badge with dynamic color
# ============================================================================
$costColor = $green
if ($sessionCost -ge 5) {
    $costColor = $red
} elseif ($sessionCost -ge 1) {
    $costColor = $yellow
}
$costBadge = "${costColor}[`$${sessionCost}]${reset}"

# ============================================================================
# Build Duration Badge
# ============================================================================
$durationBadge = ""
if ($sessionDuration -gt 0) {
    $totalSeconds = [math]::Floor($sessionDuration / 1000)
    $minutes = [math]::Floor($totalSeconds / 60)
    $seconds = $totalSeconds % 60
    if ($minutes -ge 60) {
        $hours = [math]::Floor($minutes / 60)
        $minutes = $minutes % 60
        $durationBadge = "${dim}[${hours}h${minutes}m]${reset}"
    } else {
        $durationBadge = "${dim}[${minutes}m${seconds}s]${reset}"
    }
}

# ============================================================================
# Git Status Badge
# ============================================================================
$gitBadge = ""
try {
    $branch = git branch --show-current 2>$null
    if ($branch) {
        # Count modified files
        $status = git status --porcelain 2>$null
        $changedCount = 0
        if ($status) {
            $changedCount = ($status -split "`n" | Where-Object { $_ }).Count
        }

        if ($changedCount -gt 0) {
            $gitBadge = "${yellow}[${branch} +${changedCount}]${reset}"
        } else {
            $gitBadge = "${green}[${branch}]${reset}"
        }
    }
} catch {
    # Silent fail
}

# ============================================================================
# App Context Badge
# ============================================================================
$cwd = (Get-Location).Path.ToLower()
$appName = "AXIOM"
$appColor = $magenta

if ($cwd -match "synapse") {
    $appName = "SYNAPSE"
    $appColor = $cyan
} elseif ($cwd -match "nexus") {
    $appName = "NEXUS"
    $appColor = $green
} elseif ($cwd -match "atlas") {
    $appName = "ATLAS"
    $appColor = $blue
} elseif ($cwd -match "prism") {
    $appName = "PRISM"
    $appColor = $magenta
} elseif ($cwd -match "forge") {
    $appName = "FORGE"
    $appColor = $red
}

$appBadge = "${appColor}[${appName}]${reset}"

# ============================================================================
# Docker Status Badge
# ============================================================================
$dockerBadge = ""
try {
    # Check if docker is available
    $dockerCheck = docker version --format '{{.Server.Version}}' 2>$null
    if ($dockerCheck) {
        # FORGE containers
        $forgeContainers = @(
            "forge-postgres",
            "forge-redis",
            "forge-loki",
            "forge-promtail",
            "forge-grafana",
            "forge-meilisearch",
            "forge-wiki"
        )

        # Get running containers
        $runningContainers = docker ps --format '{{.Names}}' 2>$null
        if ($runningContainers) {
            $runningList = $runningContainers -split "`n" | Where-Object { $_ }

            # Count FORGE containers
            $forgeUp = 0
            $forgeTotal = $forgeContainers.Count
            foreach ($container in $forgeContainers) {
                if ($runningList -contains $container) {
                    $forgeUp++
                }
            }

            # Determine color
            $forgeColor = $red
            if ($forgeUp -eq $forgeTotal) {
                $forgeColor = $green
            } elseif ($forgeUp -gt 0) {
                $forgeColor = $yellow
            }

            # Check app-specific containers
            $appStatus = ""

            # SYNAPSE
            if ($runningList -contains "synapse-backend") {
                $appStatus += "${green}S${reset}"
            } else {
                $appStatus += "${dim}s${reset}"
            }

            # NEXUS
            $nexusUp = ($runningList -contains "nexus-backend") -or ($runningList -contains "nexus-frontend")
            if ($nexusUp) {
                $appStatus += "${green}N${reset}"
            } else {
                $appStatus += "${dim}n${reset}"
            }

            $dockerBadge = "${forgeColor}[FORGE ${forgeUp}/${forgeTotal}]${reset} [${appStatus}]"
        } else {
            $dockerBadge = "${red}[DOCKER OFF]${reset}"
        }
    }
} catch {
    # Docker not available or error
    $dockerBadge = "${dim}[no docker]${reset}"
}

# ============================================================================
# Build Final Status Line
# ============================================================================
$segments = @()
$segments += $modelBadge
$segments += $gitBadge
$segments += $costBadge
$segments += $appBadge
$segments += $dockerBadge
if ($durationBadge) { $segments += $durationBadge }

# Filter out empty segments and join
$output = ($segments | Where-Object { $_ }) -join " "

Write-Host $output -NoNewline
