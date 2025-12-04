#!/bin/bash
# ============================================================================
# ATLAS Framework - Stop Hook
# Runs when Claude Code agent stops
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================================================
# Log session end
# ============================================================================
LOG_DIR="$HOME/.claude/logs"
if [ -d "$LOG_DIR" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Session stopped" >> "$LOG_DIR/sessions.log"
fi

# ============================================================================
# Langfuse Integration (if enabled)
# ============================================================================
if [ -f "$SCRIPT_DIR/langfuse-session.sh" ]; then
    bash "$SCRIPT_DIR/langfuse-session.sh" stop &
fi

exit 0
