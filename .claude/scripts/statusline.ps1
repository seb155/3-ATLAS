# AXIOM StatusLine - Clean ASCII
# Author: AXIOM Team | Version: 3.0

param()

# ============================================================================
# Parse Claude Code JSON Input
# ============================================================================
$modelName = "CLAUDE"
$sessionCost = 0.0
$sessionDuration = 0

try {
    $jsonInput = $input | Out-String
    if ($jsonInput -and $jsonInput.Trim()) {
        $data = $jsonInput | ConvertFrom-Json -ErrorAction SilentlyContinue

        if ($data.model.display_name) {
            $modelName = $data.model.display_name.ToUpper()
        }
        if ($data.cost.total_cost_usd) {
            $sessionCost = [math]::Round($data.cost.total_cost_usd, 2)
        }
        if ($data.cost.total_duration_ms) {
            $sessionDuration = $data.cost.total_duration_ms
        }
    }
} catch { }

# ============================================================================
# Build Duration String
# ============================================================================
$durationStr = ""
if ($sessionDuration -gt 0) {
    $totalSeconds = [math]::Floor($sessionDuration / 1000)
    $minutes = [math]::Floor($totalSeconds / 60)
    $seconds = $totalSeconds % 60
    if ($minutes -ge 60) {
        $hours = [math]::Floor($minutes / 60)
        $minutes = $minutes % 60
        $durationStr = "${hours}h${minutes}m"
    } else {
        $durationStr = "${minutes}m${seconds}s"
    }
}

# ============================================================================
# Git Info
# ============================================================================
$gitInfo = ""
try {
    $branch = git branch --show-current 2>$null
    if ($branch) {
        $status = git status --porcelain 2>$null
        $changedCount = 0
        if ($status) {
            $changedCount = ($status -split "`n" | Where-Object { $_ }).Count
        }
        if ($changedCount -gt 0) {
            $gitInfo = "${branch}*${changedCount}"
        } else {
            $gitInfo = "${branch}"
        }
    }
} catch { }

# ============================================================================
# App Context
# ============================================================================
$cwd = (Get-Location).Path.ToLower()
$appName = "AXIOM"

if ($cwd -match "synapse") { $appName = "SYNAPSE" }
elseif ($cwd -match "nexus") { $appName = "NEXUS" }
elseif ($cwd -match "atlas") { $appName = "ATLAS" }
elseif ($cwd -match "prism") { $appName = "PRISM" }
elseif ($cwd -match "forge") { $appName = "FORGE" }

# ============================================================================
# Get Current Directory (short name)
# ============================================================================
$currentDir = Split-Path -Leaf (Get-Location)

# ============================================================================
# Agent Status
# ============================================================================
$agentInfo = ""
try {
    $agentFile = Join-Path $PSScriptRoot "..\context\agent-status.json"
    if (Test-Path $agentFile) {
        $agentData = Get-Content $agentFile -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($agentData -and $agentData.summary) {
            $running = $agentData.summary.running
            $total = $agentData.summary.total
            if ($total -gt 0) {
                $agentInfo = "A:${running}/${total}"
            }
        }
    }
} catch { }

# ============================================================================
# Build Final Status Line - ASCII Art Style
# ============================================================================
# Format: << MODEL >> --- [ project/dir ] --- < git > --- { agents } --- $cost --- time
#
# Example: << OPUS >> --- [ AXIOM/backend ] --- < master*3 > --- { A:1/2 } --- $0.42 --- 5m32s

$output = "<< ${modelName} >> --- [ ${appName}/${currentDir} ]"

if ($gitInfo) {
    $output += " --- < ${gitInfo} >"
}

if ($agentInfo) {
    $output += " --- { ${agentInfo} }"
}

$output += " --- `$${sessionCost}"

if ($durationStr) {
    $output += " --- ${durationStr}"
}

Write-Host $output -NoNewline
