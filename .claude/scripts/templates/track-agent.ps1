# Hook: Track Active Atlas Agent
# Triggered by PreToolUse on Task tool to track which agent is active

# Lire le JSON depuis stdin
$inputJson = [Console]::In.ReadToEnd()

try {
    $data = $inputJson | ConvertFrom-Json
    $agent = $data.tool_input.subagent_type

    if ($agent) {
        # Sauvegarder l'agent actif dans le fichier session
        $sessionState = @{
            active_agent = $agent
            timestamp = (Get-Date).ToString("o")
            tool_name = $data.tool_name
        }

        $sessionFile = "$env:USERPROFILE\.claude\session-state.json"
        $sessionState | ConvertTo-Json | Set-Content $sessionFile -Encoding UTF8
    }
} catch {
    # Silently ignore errors to not block Claude Code
    exit 0
}
