#!/bin/bash
# ============================================================================
# ATLAS Framework - Accurate Token Parser
# Parses JSONL transcripts for real token counts (not estimates!)
#
# Token pricing (Opus 4.5):
#   - Input:       $5.00/M
#   - Output:      $25.00/M
#   - Cache Write: $6.25/M (1.25x input)
#   - Cache Read:  $0.50/M (0.1x input - 90% savings!)
#
# Context % note: This shows cumulative session tokens, not current window.
# For accurate context %, use ccstatusline's context-percentage widget.
# ============================================================================

# Find project folder based on current working directory
PROJECT_PATH=$(pwd | sed 's|/|-|g; s|^-||')
TRANSCRIPT_DIR="$HOME/.claude/projects/-$PROJECT_PATH"

# Find most recently modified JSONL file (current session)
CURRENT_JSONL=$(ls -t "$TRANSCRIPT_DIR"/*.jsonl 2>/dev/null | head -1)

# Return empty JSON if no transcript found
if [ -z "$CURRENT_JSONL" ] || [ ! -f "$CURRENT_JSONL" ]; then
    echo '{"error":"no_transcript","input":0,"output":0,"cache_write":0,"cache_read":0,"total":0,"cost_total":0,"context_pct":0}'
    exit 0
fi

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo '{"error":"jq_not_found"}'
    exit 1
fi

# Parse and sum tokens from all assistant messages with usage data
jq -s '
  [.[] | select(.type == "assistant" and .message.usage != null)] |
  {
    input: (map(.message.usage.input_tokens // 0) | add // 0),
    output: (map(.message.usage.output_tokens // 0) | add // 0),
    cache_write: (map(.message.usage.cache_creation_input_tokens // 0) | add // 0),
    cache_read: (map(.message.usage.cache_read_input_tokens // 0) | add // 0)
  } |
  . + {
    total: (.input + .output + .cache_write + .cache_read),
    total_input: (.input + .cache_write + .cache_read),
    total_output: .output
  } |
  . + {
    cost_input: (.input * 5.00 / 1000000),
    cost_output: (.output * 25.00 / 1000000),
    cost_cache_write: (.cache_write * 6.25 / 1000000),
    cost_cache_read: (.cache_read * 0.50 / 1000000)
  } |
  . + {
    cost_total: (.cost_input + .cost_output + .cost_cache_write + .cost_cache_read),
    cache_savings: (.cache_read * 4.50 / 1000000),
    cache_efficiency: (if (.cache_read + .cache_write + .input) > 0
                       then (.cache_read / (.cache_read + .cache_write + .input) * 100)
                       else 0 end)
  } |
  . + {
    tokens_consumed: .total,
    context_estimate: (if .cache_read > 200000 then 100 else ((.cache_read + .input) / 200000 * 100) end)
  } |
  . + {
    cost_total: (.cost_total * 100 | round / 100),
    cache_savings: (.cache_savings * 100 | round / 100),
    cache_efficiency: (.cache_efficiency | round),
    context_pct: (if .context_estimate > 100 then 100 else (.context_estimate | round) end)
  }
' "$CURRENT_JSONL" 2>/dev/null || echo '{"error":"parse_failed"}'
