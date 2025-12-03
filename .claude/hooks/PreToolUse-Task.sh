#!/bin/bash
# ============================================================================
# ATLAS Framework - PreToolUse Hook for Task Tool
# Tracks agent when Task tool is invoked (push to agent stack)
# ============================================================================

STATE_FILE="$HOME/.claude/session-state.json"
INPUT=$(cat)

# Extract subagent_type from tool_input
SUBAGENT=$(echo "$INPUT" | jq -r '.tool_input.subagent_type // empty' 2>/dev/null)

if [ -n "$SUBAGENT" ]; then
    # Normalize agent name (uppercase, underscores to hyphens)
    AGENT_NAME=$(echo "$SUBAGENT" | tr '[:lower:]' '[:upper:]' | tr '_' '-')

    # Read existing stack or initialize
    if [ -f "$STATE_FILE" ]; then
        STACK=$(jq -c '.agent_stack // ["ATLAS"]' "$STATE_FILE" 2>/dev/null)
    else
        STACK='["ATLAS"]'
    fi

    # Push new agent onto stack
    NEW_STACK=$(echo "$STACK" | jq --arg a "$AGENT_NAME" '. + [$a]')

    # Ensure directory exists
    mkdir -p "$(dirname "$STATE_FILE")"

    # Write updated state
    jq -n --argjson stack "$NEW_STACK" --arg agent "$AGENT_NAME" \
        '{agent_stack: $stack, current_agent: $agent, last_updated: now | todate}' > "$STATE_FILE"
fi

exit 0
