# Smart Resume Enhanced - AI Context Loader
# Purpose: Load essential context for AI session (30 seconds)
# Usage: Run at start of dev session or when resuming work
# Version: 2.0 (MVP-focused)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  AI CONTEXT LOADER - SMART RESUME" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# === 1. PROJECT STATE ===
Write-Host "=== PROJECT STATE ===" -ForegroundColor Yellow
if (Test-Path ".dev/context/project-state.md") {
    $projectState = Get-Content ".dev/context/project-state.md" | Select-Object -Last 50
    Write-Host "Last 50 lines from project-state.md:" -ForegroundColor Green
    $projectState | ForEach-Object { Write-Host $_ }
} else {
    Write-Host "[!] project-state.md not found!" -ForegroundColor Red
}

Write-Host "`n----------------------------------------`n"

# === 2. TODAY'S JOURNAL ===
Write-Host "=== TODAY'S JOURNAL ===" -ForegroundColor Yellow
$today = Get-Date -Format "yyyy-MM-dd"
$monthDir = Get-Date -Format "yyyy-MM"
$journalPath = ".dev/journal/$monthDir/$today.md"

if (Test-Path $journalPath) {
    $todayJournal = Get-Content $journalPath
    Write-Host "Journal for $today found:" -ForegroundColor Green
    $todayJournal | ForEach-Object { Write-Host $_ }
} else {
    Write-Host "[i] No journal for today ($today)" -ForegroundColor Gray
    Write-Host "   Create one to track today's work!" -ForegroundColor Gray
}

Write-Host "`n----------------------------------------`n"

# === 3. CURRENT SPRINT ===
Write-Host "=== CURRENT SPRINT ===" -ForegroundColor Yellow
if (Test-Path ".dev/roadmap/current-sprint.md") {
    $currentSprint = Get-Content ".dev/roadmap/current-sprint.md" | Select-Object -First 30
    Write-Host "First 30 lines from current-sprint.md:" -ForegroundColor Green
    $currentSprint | ForEach-Object { Write-Host $_ }
} else {
    Write-Host "[!] current-sprint.md not found!" -ForegroundColor Red
}

Write-Host "`n----------------------------------------`n"

# === 4. TEST STATUS ===
Write-Host "=== TEST STATUS ===" -ForegroundColor Yellow
if (Test-Path ".dev/testing/test-status.md") {
    $testStatus = Get-Content ".dev/testing/test-status.md" | Select-Object -First 50
    Write-Host "First 50 lines from test-status.md:" -ForegroundColor Green
    $testStatus | ForEach-Object { Write-Host $_ }
} else {
    Write-Host "[i] test-status.md not found (will be created during MVP)" -ForegroundColor Gray
}

Write-Host "`n----------------------------------------`n"

# === 5. GIT STATUS ===
Write-Host "=== GIT STATUS ===" -ForegroundColor Yellow
try {
    $gitStatus = git status --short 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Modified files:" -ForegroundColor Green
        if ($gitStatus) {
            $gitStatus | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }
        } else {
            Write-Host "  (no changes)" -ForegroundColor Gray
        }

        Write-Host "`nLast 5 commits:" -ForegroundColor Green
        $gitLog = git log --oneline -5 2>&1
        $gitLog | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }
    } else {
        Write-Host "[!] Not a git repository or git not available" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[!] Error reading git status: $_" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  CONTEXT LOADED - READY FOR AI WORK" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# === 6. MVP CONTEXT REMINDER ===
Write-Host "=== MVP CONTEXT (4 Weeks Plan) ===" -ForegroundColor Magenta
Write-Host "Week 1 (Nov 25-29): UI Foundation + Import CSV" -ForegroundColor White
Write-Host "Week 2 (Dec 2-6):   Rule Engine + Workflow Logs" -ForegroundColor White
Write-Host "Week 3 (Dec 9-13):  Package Generation + UI Polish" -ForegroundColor White
Write-Host "Week 4 (Dec 16-20): Auto Tests + CI/CD + Demo Prep" -ForegroundColor White
Write-Host "`nFull Plan: ~/.claude/plans/encapsulated-shimmying-waterfall.md`n" -ForegroundColor Gray

# === 7. QUICK ACTIONS ===
Write-Host "=== QUICK ACTIONS ===" -ForegroundColor Yellow
Write-Host "Start dev:          .\dev.ps1" -ForegroundColor White
Write-Host "Start portal:       .\workspace\start-portal.ps1" -ForegroundColor White
Write-Host "View journal:       code .dev/journal/$monthDir/$today.md" -ForegroundColor White
Write-Host "View test status:   code .dev/testing/test-status.md" -ForegroundColor White
Write-Host "View plan:          code ~/.claude/plans/encapsulated-shimmying-waterfall.md" -ForegroundColor White
Write-Host ""

# === 8. SESSION START CHECKLIST ===
Write-Host "=== SESSION START CHECKLIST ===" -ForegroundColor Magenta
Write-Host "[ ] Docker services running (.\dev.ps1)" -ForegroundColor Yellow
Write-Host "[ ] Context loaded (this script)" -ForegroundColor Yellow
Write-Host "[ ] Git branch up-to-date" -ForegroundColor Yellow
Write-Host "[ ] AI ready with context" -ForegroundColor Yellow
Write-Host "[ ] Today's journal created/updated" -ForegroundColor Yellow
Write-Host ""

Write-Host "Ready to code! [GO]`n" -ForegroundColor Green
