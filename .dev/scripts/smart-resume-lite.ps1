# smart-resume-lite.ps1
# Purpose: Aggregate project context into a single JSON object for AI agents
# Usage: .\.dev\scripts\smart-resume-lite.ps1

$projectRoot = Resolve-Path "$PSScriptRoot\..\.."
$contextFile = "$projectRoot\.dev\context\project-state.md"
$sprintFile = "$projectRoot\.dev\roadmap\current-sprint.md"
$testFile = "$projectRoot\.dev\testing\test-status.md"

# Helper to get latest journal
$journalDir = "$projectRoot\.dev\journal"
$latestJournal = Get-ChildItem -Path $journalDir -Recurse -Filter "*.md" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# Data Container
$context = @{
    Timestamp        = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Project          = "SYNAPSE"
    Version          = "Unknown"
    Phase            = "Unknown"
    CurrentSprint    = "Unknown"
    ActiveGoals      = @()
    NextSessionTasks = @()
    TestStatus       = @{
        Pending = 0
        Failed  = 0
    }
    LatestJournal    = if ($latestJournal) { $latestJournal.Name } else { "None" }
}

# 1. Parse Project State
if (Test-Path $contextFile) {
    $content = Get-Content $contextFile -Raw
    if ($content -match "\*\*Version:\*\* (.*?)\r?\n") { $context.Version = $matches[1].Trim() }
    if ($content -match "\*\*Phase:\*\* (.*?)\r?\n") { $context.Phase = $matches[1].Trim() }
}

# 2. Parse Current Sprint
if (Test-Path $sprintFile) {
    $content = Get-Content $sprintFile -Raw
    if ($content -match "# (.*?)\r?\n") { $context.CurrentSprint = $matches[1].Trim() }
    
    # Extract goals and calculate progress
    $lines = $content -split "\r?\n"
    $goals = $lines | Select-String "^\s*- \[ \]" | Select-Object -First 5
    foreach ($goal in $goals) {
        $context.ActiveGoals += $goal.Line.Trim()
    }

    # Calculate Sprint Progress
    $totalTasks = ($content | Select-String "- \[(x| )\]").Count
    $completedTasks = ($content | Select-String "- \[x\]").Count
    if ($totalTasks -gt 0) {
        $context.SprintProgress = [math]::Round(($completedTasks / $totalTasks) * 100)
    }
    else {
        $context.SprintProgress = 0
    }
}

# 3. Parse Latest Journal (Next Session)
if ($latestJournal) {
    $content = Get-Content $latestJournal.FullName -Raw
    if ($content -match "### Next Session([\s\S]*?)---") {
        $nextSessionBlock = $matches[1]
        $tasks = $nextSessionBlock -split "\r?\n" | Where-Object { $_ -match "^- " }
        foreach ($task in $tasks) {
            $context.NextSessionTasks += $task.Trim("- ").Trim()
        }
    }
}

# 4. Parse Test Status
if (Test-Path $testFile) {
    $content = Get-Content $testFile -Raw
    $context.TestStatus.Pending = ($content | Select-String "⚠️").Count
    $context.TestStatus.Failed = ($content | Select-String "❌").Count
}

# Output JSON
$context | ConvertTo-Json -Depth 3
