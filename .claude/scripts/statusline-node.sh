#!/bin/bash
# ============================================================================
# ATLAS Framework - StatusLine Wrapper (Node.js version)
# Calls the Node.js status line instead of bash version
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATUSLINE_JS="$SCRIPT_DIR/../lib/statusline/index.js"

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    # Fallback to bash version if Node.js not available
    exec bash "$SCRIPT_DIR/statusline.sh"
fi

# Check if statusline.js exists
if [ ! -f "$STATUSLINE_JS" ]; then
    # Fallback to bash version
    exec bash "$SCRIPT_DIR/statusline.sh"
fi

# Run Node.js status line
exec node "$STATUSLINE_JS" "$@"
