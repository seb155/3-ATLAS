#!/bin/bash
# ============================================================================
# ATLAS Framework - Hybrid StatusLine Script
# Author: Atlas Team | Version: 3.1.0
# Custom emojis everywhere + ccstatusline for tokens/cost/context
# ============================================================================

# ============================================================================
# Read JSON input and pass to ccstatusline
# ============================================================================
JSON_INPUT=$(cat)
CCSTATUS=$(echo "$JSON_INPUT" | ~/.npm-global/bin/ccstatusline 2>/dev/null)

# ============================================================================
# Model Detection with Emoji
# ============================================================================
MODEL_NAME=$(echo "$JSON_INPUT" | jq -r '.model.display_name // "Claude"' 2>/dev/null)
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
# Parse ccstatusline output and add emojis
# ccstatusline returns something like: "75.6K | $1.23 | 45%"
# ============================================================================
TOKENS=$(echo "$CCSTATUS" | grep -oE '[0-9.]+[KM]' | head -1)
COST=$(echo "$CCSTATUS" | grep -oE '\$[0-9.]+' | head -1 | tr -d '$')
CONTEXT=$(echo "$CCSTATUS" | grep -oE '[0-9]+%' | head -1)

# Build metrics string with emojis
METRICS=""
[ -n "$TOKENS" ] && METRICS="🪙 $TOKENS"
[ -n "$COST" ] && [ -n "$METRICS" ] && METRICS="$METRICS │ 💰 $COST"
[ -n "$COST" ] && [ -z "$METRICS" ] && METRICS="💰 $COST"
[ -n "$CONTEXT" ] && [ -n "$METRICS" ] && METRICS="$METRICS │ $CONTEXT"
[ -n "$CONTEXT" ] && [ -z "$METRICS" ] && METRICS="$CONTEXT"

# ============================================================================
# Build Final Status Line
# Format: 🏛️ ATLAS │ 🏗️ AXIOM │ 🥇 ATLAS │ 🧠 Opus │ 🪙 75.6K │ 💰 1.23 │ 45%
# ============================================================================
OUTPUT="🏛️ ATLAS │ $PROJECT_DISPLAY │ $AGENT_DISPLAY │ $MODEL_DISPLAY"

if [ -n "$METRICS" ]; then
    OUTPUT="$OUTPUT │ $METRICS"
fi

echo -n "$OUTPUT"
