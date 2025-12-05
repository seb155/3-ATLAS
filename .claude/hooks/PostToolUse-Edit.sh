#!/bin/bash
# ============================================================================
# ATLAS Framework - PostToolUse Hook for Edit/Write
# Tracks project context based on edited/written files
# ============================================================================

# Read tool input from stdin
INPUT=$(cat)

# Extract file path from tool input
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)

# If we have a file path, run project detection in background (non-blocking)
if [ -n "$FILE_PATH" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")/../scripts" 2>/dev/null && pwd)"
    if [ -f "$SCRIPT_DIR/detect-project.sh" ]; then
        bash "$SCRIPT_DIR/detect-project.sh" "$FILE_PATH" &
    fi
fi

exit 0
