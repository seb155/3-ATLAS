#!/bin/bash
# ============================================================================
# ECHO Backend Control from WSL
# ============================================================================
# Controls Windows-native backend with NPU support via PowerShell interop.
#
# Usage:
#   ./echo-backend.sh start    # Start backend with NPU environment
#   ./echo-backend.sh stop     # Stop backend
#   ./echo-backend.sh restart  # Restart backend
#   ./echo-backend.sh status   # Show status (JSON)
#   ./echo-backend.sh logs     # Show recent logs
#   ./echo-backend.sh tail     # Tail logs in real-time
#   ./echo-backend.sh health   # Quick health check
# ============================================================================

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ECHO_ROOT="/home/seb/projects/AXIOM/apps/echo"
WIN_SCRIPT="D:\\Projects\\AXIOM\\apps\\echo\\.dev\\scripts\\echo-backend-manager.ps1"
WIN_LOG_DIR="/mnt/d/Projects/AXIOM/apps/echo/.dev/logs"

# Find PowerShell (prefer pwsh 7+)
if command -v pwsh.exe &> /dev/null; then
    PWSH="pwsh.exe"
elif [ -f "/mnt/c/Program Files/PowerShell/7/pwsh.exe" ]; then
    PWSH="/mnt/c/Program Files/PowerShell/7/pwsh.exe"
else
    PWSH="powershell.exe"
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Banner
show_banner() {
    echo -e "${CYAN}"
    echo "  ╔═══════════════════════════════════════════════════╗"
    echo "  ║     ECHO Backend Control (WSL → Windows NPU)      ║"
    echo "  ╚═══════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

usage() {
    show_banner
    echo -e "${BOLD}Usage:${NC} $0 <command>"
    echo ""
    echo -e "${BOLD}Commands:${NC}"
    echo -e "  ${GREEN}start${NC}     Start backend with NPU environment activated"
    echo -e "  ${RED}stop${NC}      Stop the backend"
    echo -e "  ${YELLOW}restart${NC}   Restart the backend"
    echo -e "  ${CYAN}status${NC}    Show backend status (JSON format)"
    echo -e "  ${GRAY}logs${NC}      Show recent log entries"
    echo -e "  ${GRAY}tail${NC}      Tail logs in real-time (Ctrl+C to stop)"
    echo -e "  ${CYAN}health${NC}    Quick health check via API"
    echo ""
    echo -e "${BOLD}Architecture:${NC}"
    echo -e "  ${GRAY}WSL (this script) → PowerShell.exe → uvicorn + NPU${NC}"
    echo ""
}

run_ps() {
    "$PWSH" -NoProfile -ExecutionPolicy Bypass -File "$WIN_SCRIPT" "$@"
}

check_forge() {
    # Check if FORGE PostgreSQL is accessible
    if ! nc -z localhost 5433 2>/dev/null; then
        echo -e "${YELLOW}[WARNING]${NC} FORGE PostgreSQL (port 5433) not accessible"
        echo -e "          Run: ${GRAY}cd /home/seb/projects/AXIOM/forge && docker-compose up -d${NC}"
        return 1
    fi
    return 0
}

case "$1" in
    start)
        show_banner
        echo -e "${CYAN}[INFO]${NC} Checking prerequisites..."

        # Check FORGE
        if ! check_forge; then
            echo ""
            read -p "Continue anyway? [y/N] " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        else
            echo -e "${GREEN}[OK]${NC} FORGE PostgreSQL accessible"
        fi

        echo ""
        echo -e "${CYAN}[INFO]${NC} Starting ECHO backend on Windows with NPU..."
        echo -e "${GRAY}       PowerShell: $PWSH${NC}"
        echo ""
        run_ps -Action start
        ;;

    stop)
        show_banner
        echo -e "${CYAN}[INFO]${NC} Stopping ECHO backend..."
        run_ps -Action stop
        ;;

    restart)
        show_banner
        echo -e "${CYAN}[INFO]${NC} Restarting ECHO backend..."
        run_ps -Action restart
        ;;

    status)
        run_ps -Action status
        ;;

    logs)
        run_ps -Action logs
        ;;

    tail)
        show_banner
        echo -e "${CYAN}[INFO]${NC} Tailing backend logs (Ctrl+C to stop)..."
        echo ""

        # Find log file
        LOG_FILE="$WIN_LOG_DIR/backend.log"
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            echo -e "${YELLOW}[WARNING]${NC} Log file not found: $LOG_FILE"
            echo -e "          Backend may not have started yet."
        fi
        ;;

    health)
        show_banner
        echo -e "${CYAN}[INFO]${NC} Checking backend health..."
        echo ""

        if command -v jq &> /dev/null; then
            curl -s http://localhost:7201/api/v1/health 2>/dev/null | jq . || {
                echo -e "${RED}[ERROR]${NC} Backend unreachable at http://localhost:7201"
                exit 1
            }
        else
            curl -s http://localhost:7201/api/v1/health 2>/dev/null || {
                echo -e "${RED}[ERROR]${NC} Backend unreachable at http://localhost:7201"
                exit 1
            }
        fi
        ;;

    *)
        usage
        exit 1
        ;;
esac
