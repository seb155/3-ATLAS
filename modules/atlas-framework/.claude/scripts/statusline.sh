#!/bin/bash
# ============================================================================
# ATLAS Framework - StatusLine Script (Bash version)
# Author: Atlas Team | Version: 2.0.0
# Modern format with emojis, monorepo support, and agent tracking
# ============================================================================

# ============================================================================
# Parse Claude Code JSON Input from stdin
# ============================================================================
MODEL_NAME="CLAUDE"
SESSION_COST="0.00"
SESSION_DURATION=0

# Read JSON from stdin (Claude Code passes this)
JSON_INPUT=$(cat 2>/dev/null)

if [ -n "$JSON_INPUT" ] && command -v jq &> /dev/null; then
    MODEL_NAME=$(echo "$JSON_INPUT" | jq -r '.model.display_name // "Claude"' 2>/dev/null)
    SESSION_COST=$(echo "$JSON_INPUT" | jq -r '.cost.total_cost_usd // 0' 2>/dev/null)
    SESSION_DURATION=$(echo "$JSON_INPUT" | jq -r '.cost.total_duration_ms // 0' 2>/dev/null)
fi

# ============================================================================
# Model Display with Emoji
# ============================================================================
MODEL_UPPER=$(echo "$MODEL_NAME" | tr '[:lower:]' '[:upper:]')
case "$MODEL_UPPER" in
    *OPUS*)   MODEL_DISPLAY="🧠 Opus" ;;
    *SONNET*) MODEL_DISPLAY="🎵 Sonnet" ;;
    *HAIKU*)  MODEL_DISPLAY="🍃 Haiku" ;;
    *)        MODEL_DISPLAY="🤖 Claude" ;;
esac

# ============================================================================
# Project Detection (Monorepo Support)
# ============================================================================
CWD=$(pwd)
CWD_LOWER=$(echo "$CWD" | tr '[:upper:]' '[:lower:]')
CURRENT_DIR=$(basename "$CWD")

# Default - use current directory name with folder emoji
PROJECT_EMOJI="📁"
PROJECT_NAME=$(echo "$CURRENT_DIR" | tr '[:lower:]' '[:upper:]')

# Known projects with emojis (check in order of specificity)
if [[ "$CWD_LOWER" == *"findash"* ]]; then
    PROJECT_EMOJI="💰"; PROJECT_NAME="FINDASH"
elif [[ "$CWD_LOWER" == *"axiom"* ]]; then
    PROJECT_EMOJI="🏗️"; PROJECT_NAME="AXIOM"
elif [[ "$CWD_LOWER" == *"nexus"* ]]; then
    PROJECT_EMOJI="🧠"; PROJECT_NAME="NEXUS"
elif [[ "$CWD_LOWER" == *"synapse"* ]]; then
    PROJECT_EMOJI="⚡"; PROJECT_NAME="SYNAPSE"
elif [[ "$CWD_LOWER" == *"cortex"* ]]; then
    PROJECT_EMOJI="🔮"; PROJECT_NAME="CORTEX"
elif [[ "$CWD_LOWER" == *"atlas"* ]]; then
    PROJECT_EMOJI="🏛️"; PROJECT_NAME="ATLAS"
elif [[ "$CWD_LOWER" == *"forge"* ]]; then
    PROJECT_EMOJI="🔥"; PROJECT_NAME="FORGE"
elif [[ "$CWD_LOWER" == *"prism"* ]]; then
    PROJECT_EMOJI="💎"; PROJECT_NAME="PRISM"
elif [[ "$CWD_LOWER" == *"perso"* ]]; then
    PROJECT_EMOJI="👤"; PROJECT_NAME="PERSO"
elif [[ "$CWD_LOWER" == *"homelab"* ]]; then
    PROJECT_EMOJI="🖥️"; PROJECT_NAME="HOMELAB"
elif [[ "$CWD_LOWER" == *"homeassistant"* ]]; then
    PROJECT_EMOJI="🏠"; PROJECT_NAME="HA"
fi

# Build project display (add subdirectory if in monorepo)
CURRENT_DIR_UPPER=$(echo "$CURRENT_DIR" | tr '[:lower:]' '[:upper:]')
if [[ "$PROJECT_NAME" != "$CURRENT_DIR_UPPER" ]]; then
    PROJECT_DISPLAY="$PROJECT_EMOJI $PROJECT_NAME/$CURRENT_DIR"
else
    PROJECT_DISPLAY="$PROJECT_EMOJI $PROJECT_NAME"
fi

# ============================================================================
# Git Info with Emoji
# ============================================================================
GIT_DISPLAY=""
if command -v git &> /dev/null; then
    BRANCH=$(git branch --show-current 2>/dev/null)
    if [ -n "$BRANCH" ]; then
        CHANGED_COUNT=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
        if [ "$CHANGED_COUNT" -gt 0 ]; then
            GIT_DISPLAY="🌿 ${BRANCH}*${CHANGED_COUNT}"
        else
            GIT_DISPLAY="🌿 ${BRANCH}"
        fi
    fi
fi

# ============================================================================
# Agent Display from State File
# ============================================================================
AGENT_DISPLAY="🥇 ATLAS"
STATE_FILE="$HOME/.claude/session-state.json"

if [ -f "$STATE_FILE" ] && command -v jq &> /dev/null; then
    AGENT=$(jq -r '.current_agent // "ATLAS"' "$STATE_FILE" 2>/dev/null)
    case "$AGENT" in
        "ATLAS")            AGENT_DISPLAY="🥇 ATLAS" ;;
        "GENESIS")          AGENT_DISPLAY="🧬 GENESIS" ;;
        "BRAINSTORM")       AGENT_DISPLAY="💡 BRAIN" ;;
        "SYSTEM-ARCHITECT") AGENT_DISPLAY="🏛️ ARCH" ;;
        "BACKEND-BUILDER")  AGENT_DISPLAY="🔧 BACKEND" ;;
        "FRONTEND-BUILDER") AGENT_DISPLAY="🎨 FRONTEND" ;;
        "DEVOPS-BUILDER")   AGENT_DISPLAY="🐳 DEVOPS" ;;
        "DEVOPS-MANAGER")   AGENT_DISPLAY="🚀 DEVOPS-MGR" ;;
        "DEBUGGER")         AGENT_DISPLAY="🐛 DEBUG" ;;
        "PLANNER")          AGENT_DISPLAY="📋 PLANNER" ;;
        "DOC-WRITER")       AGENT_DISPLAY="📝 DOCS" ;;
        "UX-DESIGNER")      AGENT_DISPLAY="🎯 UX" ;;
        "OPUS-DIRECT")      AGENT_DISPLAY="⭐ OPUS" ;;
        "SONNET-DIRECT")    AGENT_DISPLAY="🔵 SONNET" ;;
        "EXPLORE")          AGENT_DISPLAY="🔍 EXPLORE" ;;
        "PLAN")             AGENT_DISPLAY="📐 PLAN" ;;
        *)                  AGENT_DISPLAY="🤖 $AGENT" ;;
    esac
fi

# ============================================================================
# Duration Formatting (H:MM format)
# ============================================================================
DURATION_STR=""
if [ "$SESSION_DURATION" -gt 0 ] 2>/dev/null; then
    TOTAL_SECONDS=$((SESSION_DURATION / 1000))
    HOURS=$((TOTAL_SECONDS / 3600))
    MINUTES=$(( (TOTAL_SECONDS % 3600) / 60 ))
    # Format as H:MM (e.g., 0:05, 1:30, 2:45)
    DURATION_STR=$(printf "⏱️ %d:%02d" $HOURS $MINUTES)
fi

# ============================================================================
# Cost Formatting (1 decimal max)
# ============================================================================
# Format cost: show 1 decimal if needed, no decimals if whole number
if command -v awk &> /dev/null; then
    COST_DISPLAY=$(echo "$SESSION_COST" | awk '{
        if ($1 == int($1)) printf "%.0f", $1
        else printf "%.1f", $1
    }')
else
    COST_DISPLAY=$(printf "%.1f" "$SESSION_COST")
fi

# ============================================================================
# ACCURATE Token Counting from Transcript JSONL
# Replaces inaccurate cost-based estimation with real token counts!
#
# Pricing (Opus 4.5):
#   - Input:       $5.00/M
#   - Output:      $25.00/M
#   - Cache Write: $6.25/M
#   - Cache Read:  $0.50/M (90% cheaper!)
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INPUT_TOKENS=0
OUTPUT_TOKENS=0
CACHE_TOKENS=0
TOTAL_TOKENS=0
CONTEXT_PCT=0
CALCULATED_COST="0"

# Parse real token data from transcript
if [ -f "$SCRIPT_DIR/parse-tokens.sh" ] && command -v jq &> /dev/null; then
    TOKEN_DATA=$(bash "$SCRIPT_DIR/parse-tokens.sh" 2>/dev/null)

    if [ -n "$TOKEN_DATA" ] && [ "$(echo "$TOKEN_DATA" | jq -r '.error // empty')" = "" ]; then
        INPUT_TOKENS=$(echo "$TOKEN_DATA" | jq -r '.input // 0')
        OUTPUT_TOKENS=$(echo "$TOKEN_DATA" | jq -r '.output // 0')
        CACHE_WRITE=$(echo "$TOKEN_DATA" | jq -r '.cache_write // 0')
        CACHE_READ=$(echo "$TOKEN_DATA" | jq -r '.cache_read // 0')
        CACHE_TOKENS=$((CACHE_WRITE + CACHE_READ))
        TOTAL_TOKENS=$(echo "$TOKEN_DATA" | jq -r '.total // 0')
        CONTEXT_PCT=$(echo "$TOKEN_DATA" | jq -r '.context_pct // 0')
        CALCULATED_COST=$(echo "$TOKEN_DATA" | jq -r '.cost_total // 0')

        # Use calculated cost if available (more accurate than API cost)
        if [ "$CALCULATED_COST" != "0" ] && [ "$CALCULATED_COST" != "null" ]; then
            COST_DISPLAY=$(echo "$CALCULATED_COST" | awk '{
                if ($1 < 0.01) printf "%.3f", $1
                else if ($1 < 0.1) printf "%.2f", $1
                else if ($1 == int($1)) printf "%.0f", $1
                else printf "%.1f", $1
            }')
        fi
    fi
fi

# Format token values for display (K or M suffix)
format_tokens() {
    local tokens=$1
    if [ "$tokens" -ge 1000000 ] 2>/dev/null; then
        awk "BEGIN {printf \"%.1fM\", $tokens/1000000}"
    elif [ "$tokens" -ge 1000 ] 2>/dev/null; then
        awk "BEGIN {printf \"%.0fK\", $tokens/1000}"
    else
        echo "$tokens"
    fi
}

INPUT_K=$(format_tokens $INPUT_TOKENS)
OUTPUT_K=$(format_tokens $OUTPUT_TOKENS)
CACHE_K=$(format_tokens $CACHE_TOKENS)
TOTAL_K=$(format_tokens $TOTAL_TOKENS)

# Context status indicator based on percentage
if [ "$CONTEXT_PCT" -ge 85 ]; then
    CONTEXT_DISPLAY="🔴 ${CONTEXT_PCT}%"
elif [ "$CONTEXT_PCT" -ge 70 ]; then
    CONTEXT_DISPLAY="🟠 ${CONTEXT_PCT}%"
elif [ "$CONTEXT_PCT" -ge 50 ]; then
    CONTEXT_DISPLAY="🟡 ${CONTEXT_PCT}%"
else
    CONTEXT_DISPLAY="🟢 ${CONTEXT_PCT}%"
fi

# ============================================================================
# Build Final Status Line - RESPONSIVE MODE
# Adapts to terminal width for split terminal support
#
# Modes:
#   < 60:   Ultra Compact - 💰 $0.45 │ 🟢 37%
#   60-89:  Compact       - 🏛️ ATLAS │ 🧠 Opus │ 💰 $0.45 │ 🟢 37%
#   90-119: Standard      - + 📝 75K (total tokens)
#   >= 120: Full          - + 📥 5K │ 📤 2K │ 💾 68K (breakdown)
# ============================================================================

# Detect terminal width
# When piped (like from Claude Code), tput returns 80 by default which is wrong
# Try multiple methods, default to 150 (FULL mode) if detection fails
if [ -n "$COLUMNS" ]; then
    TERM_WIDTH=$COLUMNS
elif [ -t 1 ]; then
    # stdout is a terminal, tput should work
    TERM_WIDTH=$(tput cols 2>/dev/null || echo 150)
else
    # Piped context (Claude Code) - default to FULL mode
    # Override with ATLAS_TERM_WIDTH env var if needed
    TERM_WIDTH=${ATLAS_TERM_WIDTH:-150}
fi

if [ "$TERM_WIDTH" -lt 60 ]; then
    # ULTRA COMPACT: Cost + Context only (for very narrow splits)
    OUTPUT="💰 \$${COST_DISPLAY} │ ${CONTEXT_DISPLAY}"

elif [ "$TERM_WIDTH" -lt 90 ]; then
    # COMPACT: Essential info without token details
    OUTPUT="🏛️ ATLAS │ $MODEL_DISPLAY │ 💰 \$${COST_DISPLAY} │ ${CONTEXT_DISPLAY}"

elif [ "$TERM_WIDTH" -lt 120 ]; then
    # STANDARD: With total tokens grouped
    OUTPUT="🏛️ ATLAS │ $MODEL_DISPLAY │ $PROJECT_DISPLAY"

    if [ -n "$GIT_DISPLAY" ]; then
        OUTPUT="$OUTPUT │ $GIT_DISPLAY"
    fi

    OUTPUT="$OUTPUT │ 📝 ${TOTAL_K} │ 💰 \$${COST_DISPLAY} │ ${CONTEXT_DISPLAY}"

else
    # FULL: Complete breakdown with Input/Output/Cache
    OUTPUT="🏛️ ATLAS │ $MODEL_DISPLAY │ $PROJECT_DISPLAY"

    if [ -n "$GIT_DISPLAY" ]; then
        OUTPUT="$OUTPUT │ $GIT_DISPLAY"
    fi

    OUTPUT="$OUTPUT │ $AGENT_DISPLAY"

    # Token breakdown: Input | Output | Cache
    if [ "$TOTAL_TOKENS" -gt 0 ] 2>/dev/null; then
        OUTPUT="$OUTPUT │ 📥 ${INPUT_K} │ 📤 ${OUTPUT_K} │ 💾 ${CACHE_K}"
    fi

    OUTPUT="$OUTPUT │ 💰 \$${COST_DISPLAY} │ ${CONTEXT_DISPLAY}"

    if [ -n "$DURATION_STR" ]; then
        OUTPUT="$OUTPUT │ $DURATION_STR"
    fi
fi

echo -n "$OUTPUT"
