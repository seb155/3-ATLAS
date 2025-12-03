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
# Token Estimation from Cost (Claude Code doesn't expose token counts)
# Opus 4.5: $5/M input, $25/M output → avg ~$9/M with 80/20 ratio
# Formula: tokens ≈ cost × 111111 (1M / 9)
# ============================================================================
TOKEN_DISPLAY=""
if command -v awk &> /dev/null && [ -n "$SESSION_COST" ]; then
    ESTIMATED_TOKENS=$(awk "BEGIN {printf \"%.0f\", $SESSION_COST * 111111}")
    if [ "$ESTIMATED_TOKENS" -gt 0 ] 2>/dev/null; then
        if [ "$ESTIMATED_TOKENS" -ge 1000000 ]; then
            # Millions: ~1.2M
            TOKEN_DISPLAY=$(awk "BEGIN {printf \"~%.1fM\", $ESTIMATED_TOKENS/1000000}")
        elif [ "$ESTIMATED_TOKENS" -ge 1000 ]; then
            # Thousands: ~57K
            TOKEN_DISPLAY=$(awk "BEGIN {printf \"~%.0fK\", $ESTIMATED_TOKENS/1000}")
        else
            # Under 1K: ~500
            TOKEN_DISPLAY="~${ESTIMATED_TOKENS}"
        fi
    fi
fi

# ============================================================================
# Build Final Status Line
# Format: 🏛️ ATLAS │ 🧠 Opus │ 🏗️ AXIOM/backend │ 🌿 main*3 │ 🔧 BACKEND │ 💰 $1.2 │ 📝 75.6K │ ⏱️ 0:12
# ============================================================================

OUTPUT="🏛️ ATLAS │ $MODEL_DISPLAY │ $PROJECT_DISPLAY"

if [ -n "$GIT_DISPLAY" ]; then
    OUTPUT="$OUTPUT │ $GIT_DISPLAY"
fi

OUTPUT="$OUTPUT │ $AGENT_DISPLAY │ 💰 \$${COST_DISPLAY}"

if [ -n "$TOKEN_DISPLAY" ]; then
    OUTPUT="$OUTPUT │ 📝 ${TOKEN_DISPLAY}"
fi

if [ -n "$DURATION_STR" ]; then
    OUTPUT="$OUTPUT │ $DURATION_STR"
fi

echo -n "$OUTPUT"
