# AXIOM StatusLine for Claude Code
# Detects current app context and displays a nice status bar

$cwd = Get-Location
$path = $cwd.Path.ToLower()

# Detect current app/module
$app = "AXIOM"
$icon = "🏛️"

if ($path -match "synapse") {
    $app = "SYNAPSE"
    $icon = "🧠"
} elseif ($path -match "nexus") {
    $app = "NEXUS"
    $icon = "🔗"
} elseif ($path -match "atlas") {
    $app = "ATLAS"
    $icon = "🤖"
} elseif ($path -match "prism") {
    $app = "PRISM"
    $icon = "💎"
} elseif ($path -match "forge") {
    $app = "FORGE"
    $icon = "🔥"
}

# Get git branch
$branch = ""
try {
    $branch = git branch --show-current 2>$null
    if ($branch) {
        $branch = "🌿 $branch"
    }
} catch {}

# Build status line
Write-Host "$icon $app | $branch" -NoNewline
