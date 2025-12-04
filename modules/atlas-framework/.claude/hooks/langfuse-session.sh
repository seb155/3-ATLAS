#!/bin/bash
# ============================================================================
# ATLAS Framework - Langfuse Session Hook
# Sends session events to Langfuse for LLM observability
# ============================================================================

# Configuration
LANGFUSE_ENABLED="${LANGFUSE_ENABLED:-false}"
LANGFUSE_HOST="${LANGFUSE_HOST:-http://localhost:3001}"
LANGFUSE_PUBLIC_KEY="${LANGFUSE_PUBLIC_KEY:-}"
LANGFUSE_SECRET_KEY="${LANGFUSE_SECRET_KEY:-}"

# Skip if Langfuse is not enabled
if [ "$LANGFUSE_ENABLED" != "true" ]; then
    exit 0
fi

# Skip if keys are not configured
if [ -z "$LANGFUSE_PUBLIC_KEY" ] || [ -z "$LANGFUSE_SECRET_KEY" ]; then
    exit 0
fi

# Get event type from first argument (start, stop)
EVENT_TYPE="${1:-unknown}"

# Get session info
SESSION_ID="${CLAUDE_SESSION_ID:-session-$(date +%Y%m%d-%H%M%S)}"
AGENT="${ATLAS_CURRENT_AGENT:-ATLAS}"
PROJECT=$(basename "$(pwd)")
TIMESTAMP=$(date -Iseconds)

# Build JSON payload
PAYLOAD=$(cat << EOF
{
  "batch": [{
    "type": "trace-create",
    "body": {
      "id": "$SESSION_ID",
      "name": "atlas-session",
      "metadata": {
        "event": "$EVENT_TYPE",
        "agent": "$AGENT",
        "project": "$PROJECT",
        "timestamp": "$TIMESTAMP"
      },
      "tags": ["atlas", "$EVENT_TYPE", "$AGENT"]
    }
  }]
}
EOF
)

# Send to Langfuse (async, don't block)
curl -s -X POST "$LANGFUSE_HOST/api/public/ingestion" \
    -H "Content-Type: application/json" \
    -H "Authorization: Basic $(echo -n "$LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY" | base64)" \
    -d "$PAYLOAD" \
    > /dev/null 2>&1 &

exit 0
