#!/bin/bash
# ============================================================================
# ATLAS Framework - Tool Usage Analytics
# Analyzes which tools/commands consume the most tokens
#
# Helps identify optimization opportunities:
#   - Task agents are expensive (~2-5K tokens/call)
#   - WebFetch can consume 5-20K tokens
#   - Read without limits can be costly for large files
# ============================================================================

# Find project folder based on current working directory
PROJECT_PATH=$(pwd | sed 's|/|-|g; s|^-||')
TRANSCRIPT_DIR="$HOME/.claude/projects/-$PROJECT_PATH"

# Check if transcript directory exists
if [ ! -d "$TRANSCRIPT_DIR" ]; then
    echo '{"error":"no_transcripts","tools":[]}'
    exit 0
fi

# Check if any JSONL files exist
if ! ls "$TRANSCRIPT_DIR"/*.jsonl &>/dev/null; then
    echo '{"error":"no_jsonl_files","tools":[]}'
    exit 0
fi

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo '{"error":"jq_not_found"}'
    exit 1
fi

# Parse mode: "current" (latest session) or "all" (all sessions)
MODE="${1:-current}"

if [ "$MODE" = "current" ]; then
    # Analyze only the current session
    JSONL_FILES=$(ls -t "$TRANSCRIPT_DIR"/*.jsonl 2>/dev/null | head -1)
else
    # Analyze all sessions
    JSONL_FILES="$TRANSCRIPT_DIR"/*.jsonl
fi

# Parse all tool calls and aggregate statistics
jq -s '
  # Extract all tool_use blocks from assistant messages
  [
    .[].message.content[]? |
    select(.type == "tool_use") |
    {
      name: .name,
      input_size: (.input | tostring | length)
    }
  ] |

  # Group by tool name and calculate stats
  group_by(.name) |
  map({
    tool: .[0].name,
    count: length,
    total_input_chars: ([.[].input_size] | add),
    avg_input_size: (([.[].input_size] | add) / length | round),
    min_input_size: ([.[].input_size] | min),
    max_input_size: ([.[].input_size] | max)
  }) |

  # Sort by count (most used first)
  sort_by(-.count) |

  # Add status indicators
  map(. + {
    status: (
      if .avg_input_size > 2000 then "optimize"
      elif .avg_input_size > 500 then "watch"
      else "ok"
      end
    ),
    # Estimated token impact (rough: ~4 chars per token)
    est_tokens_per_call: ((.avg_input_size / 4) | round),
    est_total_tokens: (((.avg_input_size * .count) / 4) | round)
  }) |

  # Create summary
  {
    tools: .,
    summary: {
      total_tool_calls: (map(.count) | add // 0),
      unique_tools: length,
      top_consumer: (if length > 0 then .[0].tool else null end),
      tools_to_optimize: [.[] | select(.status == "optimize") | .tool]
    }
  }
' $JSONL_FILES 2>/dev/null || echo '{"error":"parse_failed","tools":[]}'
