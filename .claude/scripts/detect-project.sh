#!/bin/bash
# ============================================================================
# ATLAS Framework - Project Detection Script
# Detects project from file path and updates session-state.json
# Called by PostToolUse hooks to track logical project context
# ============================================================================

FILE_PATH="$1"
STATE_FILE="$HOME/.claude/session-state.json"

# Skip if no path provided
[ -z "$FILE_PATH" ] && exit 0

# Convert to lowercase for matching
PATH_LOWER=$(echo "$FILE_PATH" | tr '[:upper:]' '[:lower:]')

# Known projects (order matters - check more specific patterns first)
# Pattern uses directory boundaries to avoid false matches
if [[ "$PATH_LOWER" == *"/synapse/"* ]] || [[ "$PATH_LOWER" == *"/synapse-"* ]]; then
    PROJECT="SYNAPSE"; EMOJI="⚡"
elif [[ "$PATH_LOWER" == *"/nexus/"* ]] || [[ "$PATH_LOWER" == *"/nexus-"* ]]; then
    PROJECT="NEXUS"; EMOJI="🧠"
elif [[ "$PATH_LOWER" == *"/axiom/"* ]] || [[ "$PATH_LOWER" == *"/axiom-"* ]]; then
    PROJECT="AXIOM"; EMOJI="🏗️"
elif [[ "$PATH_LOWER" == *"/forge/"* ]] || [[ "$PATH_LOWER" == *"/forge-"* ]]; then
    PROJECT="FORGE"; EMOJI="🔥"
elif [[ "$PATH_LOWER" == *"/cortex/"* ]] || [[ "$PATH_LOWER" == *"/cortex-"* ]]; then
    PROJECT="CORTEX"; EMOJI="🔮"
elif [[ "$PATH_LOWER" == *"/findash/"* ]] || [[ "$PATH_LOWER" == *"/findash-"* ]]; then
    PROJECT="FINDASH"; EMOJI="💰"
elif [[ "$PATH_LOWER" == *"/prism/"* ]] || [[ "$PATH_LOWER" == *"/prism-"* ]]; then
    PROJECT="PRISM"; EMOJI="💎"
elif [[ "$PATH_LOWER" == *"/homelab/"* ]] || [[ "$PATH_LOWER" == *"/homelab-"* ]]; then
    PROJECT="HOMELAB"; EMOJI="🖥️"
elif [[ "$PATH_LOWER" == *"/homeassistant/"* ]]; then
    PROJECT="HA"; EMOJI="🏠"
elif [[ "$PATH_LOWER" == *"/perso/"* ]]; then
    PROJECT="PERSO"; EMOJI="👤"
elif [[ "$PATH_LOWER" == *"/atlas/"* ]] || [[ "$PATH_LOWER" == *"/atlas-"* ]] || [[ "$PATH_LOWER" == *"/.claude/"* ]]; then
    PROJECT="ATLAS"; EMOJI="🏛️"
else
    # Unknown project - don't update state
    exit 0
fi

# Update state file if it exists and jq is available
if [ -f "$STATE_FILE" ] && command -v jq &> /dev/null; then
    # Atomic update using temp file
    jq --arg p "$PROJECT" --arg e "$EMOJI" \
       '.current_project = $p | .project_emoji = $e | .last_updated = (now | todate)' \
       "$STATE_FILE" > "${STATE_FILE}.tmp" 2>/dev/null && \
    mv "${STATE_FILE}.tmp" "$STATE_FILE" 2>/dev/null
elif [ ! -f "$STATE_FILE" ] && command -v jq &> /dev/null; then
    # Create state file if it doesn't exist
    echo "{\"current_agent\":\"ATLAS\",\"current_project\":\"$PROJECT\",\"project_emoji\":\"$EMOJI\",\"last_updated\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > "$STATE_FILE"
fi

exit 0
