#!/bin/bash
# ============================================================================
# ATLAS Framework - SessionStart Hook
# Displays banner and initializes agent state on session start
# ============================================================================

# Clear screen to remove Claude Code's default ASCII art
clear

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Display ATLAS banner
if [ -f "$SCRIPT_DIR/../scripts/banner.sh" ]; then
    bash "$SCRIPT_DIR/../scripts/banner.sh" 2>/dev/null
fi

# Initialize agent state file
STATE_FILE="$HOME/.claude/session-state.json"
mkdir -p "$(dirname "$STATE_FILE")"

# Reset agent stack to ATLAS on session start
if command -v jq &> /dev/null; then
    jq -n '{agent_stack: ["ATLAS"], current_agent: "ATLAS", last_updated: now | todate}' > "$STATE_FILE"
else
    # Fallback without jq
    echo '{"agent_stack":["ATLAS"],"current_agent":"ATLAS","last_updated":"'"$(date -Iseconds)"'"}' > "$STATE_FILE"
fi

# Log session start
SESSION_ID="session-$(date +%Y%m%d-%H%M)"
LOG_DIR="$HOME/.claude/logs"
mkdir -p "$LOG_DIR"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Session started: $SESSION_ID" >> "$LOG_DIR/sessions.log"

exit 0
