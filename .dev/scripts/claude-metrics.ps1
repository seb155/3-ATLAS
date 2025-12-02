# Claude Code Metrics PRO - Quick Summary
# Usage: .\.dev\scripts\claude-metrics.ps1 [summary|insights|dashboard]

param(
    [Parameter(Position=0)]
    [ValidateSet("summary", "insights", "dashboard", "health")]
    [string]$Command = "summary"
)

$ExporterUrl = "http://localhost:3202"
$GrafanaUrl = "https://grafana.axoiq.com/d/claude-code-pro"

function Show-Summary {
    Write-Host "`n=== Claude Code Usage Summary ===" -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "$ExporterUrl/summary" -Method Get -TimeoutSec 5

        Write-Host "`nToken Flow:" -ForegroundColor Yellow
        Write-Host "  Sent to Claude:     $($response.token_flow.sent_to_claude.ToString('N0'))" -ForegroundColor Blue
        Write-Host "  Received from Claude: $($response.token_flow.received_from_claude.ToString('N0'))" -ForegroundColor Green
        Write-Host "  From Cache:         $($response.token_flow.from_cache.ToString('N0'))" -ForegroundColor DarkYellow
        Write-Host "  Cache Efficiency:   $($response.token_flow.cache_efficiency)" -ForegroundColor Magenta

        Write-Host "`nCosts:" -ForegroundColor Yellow
        Write-Host "  This Month:    $($response.costs.this_month)" -ForegroundColor White
        Write-Host "  Saved (Cache): $($response.costs.saved_via_cache)" -ForegroundColor Green
        Write-Host "  Remaining:     $($response.costs.budget_remaining)" -ForegroundColor Cyan

        if ($response.top_commands.Count -gt 0) {
            Write-Host "`nTop ATLAS Commands:" -ForegroundColor Yellow
            $response.top_commands.PSObject.Properties | Sort-Object Value -Descending | ForEach-Object {
                Write-Host "  $($_.Name): $($_.Value)" -ForegroundColor Gray
            }
        }

        if ($response.top_workflows.Count -gt 0) {
            Write-Host "`nTop Workflows:" -ForegroundColor Yellow
            $response.top_workflows.PSObject.Properties | Sort-Object Value -Descending | ForEach-Object {
                Write-Host "  $($_.Name): $($_.Value)" -ForegroundColor Gray
            }
        }

        Write-Host "`n" -NoNewline
    }
    catch {
        Write-Host "Error: Could not connect to exporter at $ExporterUrl" -ForegroundColor Red
        Write-Host "Make sure the observability stack is running:" -ForegroundColor Yellow
        Write-Host "  cd forge && docker compose -f docker-compose.yml -f docker-compose.observability.yml up -d" -ForegroundColor Gray
    }
}

function Show-Insights {
    Write-Host "`n=== Optimization Insights ===" -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "$ExporterUrl/insights" -Method Get -TimeoutSec 5

        if ($response.insights.Count -eq 0) {
            Write-Host "`nNo optimization issues found!" -ForegroundColor Green
            Write-Host "Your Claude Code usage is efficient." -ForegroundColor Gray
        }
        else {
            Write-Host "`nFound $($response.insights.Count) optimization opportunities:`n" -ForegroundColor Yellow

            foreach ($insight in $response.insights) {
                $color = switch ($insight.severity) {
                    "high" { "Red" }
                    "medium" { "Yellow" }
                    default { "Gray" }
                }

                Write-Host "[$($insight.severity.ToUpper())] $($insight.type)" -ForegroundColor $color
                Write-Host "  Project: $($insight.project)" -ForegroundColor Gray
                Write-Host "  $($insight.message)" -ForegroundColor White
                if ($insight.potential_savings) {
                    Write-Host "  Potential: $($insight.potential_savings)" -ForegroundColor Green
                }
                if ($insight.recommendation) {
                    Write-Host "  Tip: $($insight.recommendation)" -ForegroundColor Cyan
                }
                Write-Host ""
            }
        }
    }
    catch {
        Write-Host "Error: Could not connect to exporter" -ForegroundColor Red
    }
}

function Show-Health {
    Write-Host "`n=== Exporter Health ===" -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "$ExporterUrl/health" -Method Get -TimeoutSec 5
        Write-Host "Status: $($response.status)" -ForegroundColor Green
        Write-Host "Version: $($response.version)" -ForegroundColor Gray
        Write-Host "Projects Dir: $($response.projects_dir)" -ForegroundColor Gray
        Write-Host "Last Scan: $(if($response.last_scan) { [DateTimeOffset]::FromUnixTimeSeconds($response.last_scan).LocalDateTime } else { 'Never' })" -ForegroundColor Gray
        Write-Host "Insights Count: $($response.insights_count)" -ForegroundColor Gray
    }
    catch {
        Write-Host "Exporter is not running or not reachable" -ForegroundColor Red
    }
}

function Open-Dashboard {
    Write-Host "Opening Grafana Dashboard..." -ForegroundColor Cyan
    Start-Process $GrafanaUrl
}

# Main
switch ($Command) {
    "summary" { Show-Summary }
    "insights" { Show-Insights }
    "dashboard" { Open-Dashboard }
    "health" { Show-Health }
}
