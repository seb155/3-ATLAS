#!/bin/bash
# ============================================================================
# ATLAS Framework - PreToolUse Hook for Write Tool
# Rule 50 Enforcement: Warn/block Write on existing files (use Edit instead)
# ============================================================================
#
# This hook enforces Rule 50 (Tool Optimization):
# - If file exists → BLOCK with message to use Edit instead
# - If new file → ALLOW
#
# Mode: Set ATLAS_WRITE_MODE environment variable
# - "block" : Block Write on existing files (default)
# - "warn"  : Show warning but allow
# - "off"   : Disable this hook
# ============================================================================

# Read tool input from stdin
INPUT=$(cat)

# Get the file path from tool input
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)

# Check mode (default: block)
MODE="${ATLAS_WRITE_MODE:-block}"

# If mode is off, allow everything
if [ "$MODE" = "off" ]; then
    exit 0
fi

# If no file path, allow (shouldn't happen)
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Check if file exists
if [ -f "$FILE_PATH" ]; then
    # File exists - this should be an Edit, not Write!

    # Get file size for context
    FILE_SIZE=$(wc -l < "$FILE_PATH" 2>/dev/null || echo "unknown")

    if [ "$MODE" = "block" ]; then
        # Block mode: Reject the Write using exit code 2 (Claude Code blocking)
        # Note: exit 2 = block, exit 1 = ignored, exit 0 = allow
        # Output must go to stderr for exit 2

        echo "⚠️  RULE 50 VIOLATION: Write on existing file!" >&2
        echo "" >&2
        echo "📁 File: $FILE_PATH" >&2
        echo "📏 Size: $FILE_SIZE lines" >&2
        echo "" >&2
        echo "❌ BLOCKED: Use 'Edit' tool instead of 'Write' for existing files." >&2
        echo "   This saves ~95% tokens. See: .claude/agents/rules/50-tool-optimization.md" >&2
        echo "" >&2
        echo "💡 To override: export ATLAS_WRITE_MODE=warn" >&2
        exit 2
    else
        # Warn mode: Allow but show warning
        echo "⚠️  Rule 50 Reminder: Consider using 'Edit' instead of 'Write'"
        echo "   File exists: $FILE_PATH ($FILE_SIZE lines)"
        echo "   Edit saves ~95% tokens for partial modifications."
        exit 0
    fi
fi

# New file - allow Write
exit 0
