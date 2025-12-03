#!/bin/bash
# ============================================================================
# ATLAS Framework - Banner Display
# Author: Atlas Team | Version: 1.2.0
# Modern Box Style with dynamic project detection
# ============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# Project Detection (mirrors statusline.sh logic)
# ─────────────────────────────────────────────────────────────────────────────

CWD_LOWER=$(pwd | tr '[:upper:]' '[:lower:]')
CURRENT_DIR=$(basename "$(pwd)")
CURRENT_DIR_UPPER=$(echo "$CURRENT_DIR" | tr '[:lower:]' '[:upper:]')

# Default values
PROJECT_EMOJI="📁"
PROJECT_NAME="$CURRENT_DIR_UPPER"

# Project detection by path pattern
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
elif [[ "$CWD_LOWER" == *"/ha/"* ]] || [[ "$CWD_LOWER" == *"/ha" ]]; then
    PROJECT_EMOJI="🏠"; PROJECT_NAME="HA"
fi

# Add subdirectory if we're in a known project but deeper
if [[ "$PROJECT_NAME" != "$CURRENT_DIR_UPPER" ]]; then
    PROJECT_DISPLAY="$PROJECT_NAME/$CURRENT_DIR"
else
    PROJECT_DISPLAY="$PROJECT_NAME"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Display Banner
# ─────────────────────────────────────────────────────────────────────────────

# Colors (if terminal supports them)
CYAN='\033[0;36m'
GOLD='\033[0;33m'
WHITE='\033[1;37m'
DIM='\033[2m'
RESET='\033[0m'

echo -e "${CYAN}"
cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║       █████╗ ████████╗██╗      █████╗ ███████╗                       ║
║      ██╔══██╗╚══██╔══╝██║     ██╔══██╗██╔════╝                       ║
║      ███████║   ██║   ██║     ███████║███████╗                       ║
║      ██╔══██║   ██║   ██║     ██╔══██║╚════██║                       ║
║      ██║  ██║   ██║   ███████╗██║  ██║███████║                       ║
║      ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝                       ║
║                                                                      ║
EOF
echo -e "${RESET}"

# Dynamic info line with proper padding
printf "${CYAN}║${RESET}    ${WHITE}🏛️  Framework v1.2${RESET}  ${DIM}•${RESET}  ${GOLD}AI Agent Orchestration${RESET}                     ${CYAN}║${RESET}\n"
printf "${CYAN}║${RESET}    ${PROJECT_EMOJI}  Projet: ${WHITE}%-50s${RESET}   ${CYAN}║${RESET}\n" "$PROJECT_DISPLAY"
printf "${CYAN}║${RESET}                                                                      ${CYAN}║${RESET}\n"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════╝${RESET}"
echo ""
