#!/bin/bash
# ============================================================================
# ATLAS Framework - SubagentStop Hook
# Pops agent from stack when subagent completes
# ============================================================================

STATE_FILE="$HOME/.claude/session-state.json"

if [ -f "$STATE_FILE" ]; then
    # Read current stack
    STACK=$(jq -c '.agent_stack // ["ATLAS"]' "$STATE_FILE" 2>/dev/null)
    LEN=$(echo "$STACK" | jq 'length')

    if [ "$LEN" -gt 1 ]; then
        # Pop last agent from stack
        NEW_STACK=$(echo "$STACK" | jq '.[:-1]')
        CURRENT=$(echo "$NEW_STACK" | jq -r '.[-1]')
    else
        # Reset to ATLAS if stack is empty/single
        NEW_STACK='["ATLAS"]'
        CURRENT="ATLAS"
    fi

    # Write updated state
    jq -n --argjson stack "$NEW_STACK" --arg agent "$CURRENT" \
        '{agent_stack: $stack, current_agent: $agent, last_updated: now | todate}' > "$STATE_FILE"
fi

exit 0
