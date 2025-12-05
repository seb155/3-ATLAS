#!/bin/bash
# trace-report.sh - Generate HTML reports from Claude Code sessions
# Uses claude-trace to create interactive visualizations

set -e

# Configuration
REPORTS_DIR="$HOME/.claude/reports"
CLAUDE_PROJECTS_DIR="$HOME/.claude/projects"
CLAUDE_TRACE_BIN="$HOME/.npm-global/bin/claude-trace"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Ensure reports directory exists
mkdir -p "$REPORTS_DIR"

# Function: List available sessions
list_sessions() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  📋 Available Claude Code Sessions                            ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Find all JSONL files, sorted by modification time (newest first)
    local count=0
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            count=$((count + 1))
            local size=$(du -h "$file" 2>/dev/null | cut -f1)
            local date=$(stat -c %y "$file" 2>/dev/null | cut -d' ' -f1)
            local basename=$(basename "$file")
            local dirname=$(dirname "$file" | sed "s|$CLAUDE_PROJECTS_DIR/||")

            echo -e "  ${GREEN}$count.${NC} ${YELLOW}$dirname${NC}"
            echo -e "     └─ $basename (${size}, ${date})"
            echo ""
        fi
    done < <(find "$CLAUDE_PROJECTS_DIR" -name "*.jsonl" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -20 | cut -d' ' -f2-)

    if [ $count -eq 0 ]; then
        echo -e "  ${RED}No sessions found in $CLAUDE_PROJECTS_DIR${NC}"
    fi
}

# Function: Get project JSONL directory from current path
get_project_jsonl_dir() {
    local current_path="$PWD"
    # Convert path to Claude's encoded format (replace / with -)
    local encoded_path=$(echo "$current_path" | sed 's|^/||' | sed 's|/|-|g')
    echo "$CLAUDE_PROJECTS_DIR/-$encoded_path"
}

# Function: Find most recent JSONL for current project
find_latest_jsonl() {
    local project_dir=$(get_project_jsonl_dir)

    if [ -d "$project_dir" ]; then
        find "$project_dir" -name "*.jsonl" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-
    else
        # Try parent directories
        local parent_path=$(dirname "$PWD")
        while [ "$parent_path" != "/" ]; do
            local encoded_path=$(echo "$parent_path" | sed 's|^/||' | sed 's|/|-|g')
            local try_dir="$CLAUDE_PROJECTS_DIR/-$encoded_path"
            if [ -d "$try_dir" ]; then
                find "$try_dir" -name "*.jsonl" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-
                return
            fi
            parent_path=$(dirname "$parent_path")
        done
    fi
}

# Function: Generate HTML report
generate_report() {
    local jsonl_file="$1"
    local output_file="$2"

    if [ ! -f "$jsonl_file" ]; then
        echo -e "${RED}Error: File not found: $jsonl_file${NC}"
        exit 1
    fi

    # Generate output filename if not provided
    if [ -z "$output_file" ]; then
        local date=$(date +%Y-%m-%d_%H%M%S)
        local basename=$(basename "$jsonl_file" .jsonl)
        output_file="$REPORTS_DIR/${date}_${basename}_trace.html"
    fi

    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  🔍 Generating claude-trace Report                           ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${YELLOW}Input:${NC}  $jsonl_file"
    echo -e "  ${YELLOW}Output:${NC} $output_file"
    echo ""

    # Generate the report
    if "$CLAUDE_TRACE_BIN" --generate-html "$jsonl_file" "$output_file"; then
        echo ""
        echo -e "${GREEN}✓ Report generated successfully!${NC}"
        echo ""
        echo -e "  ${BLUE}File:${NC} $output_file"

        # Try to open in browser (WSL-aware)
        if command -v wslview &> /dev/null; then
            echo -e "  ${BLUE}Opening in browser (WSL)...${NC}"
            wslview "$output_file" 2>/dev/null &
        elif command -v xdg-open &> /dev/null; then
            echo -e "  ${BLUE}Opening in browser...${NC}"
            xdg-open "$output_file" 2>/dev/null &
        elif command -v open &> /dev/null; then
            echo -e "  ${BLUE}Opening in browser (macOS)...${NC}"
            open "$output_file" 2>/dev/null &
        else
            echo -e "  ${YELLOW}Note: Could not auto-open. Please open manually.${NC}"
        fi
    else
        echo -e "${RED}Error generating report${NC}"
        exit 1
    fi
}

# Function: Generate index of all sessions
generate_index() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  📚 Generating Session Index                                 ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    cd "$HOME/.claude-trace" 2>/dev/null || mkdir -p "$HOME/.claude-trace"
    "$CLAUDE_TRACE_BIN" --index

    echo ""
    echo -e "${GREEN}✓ Index generated in ~/.claude-trace/${NC}"
}

# Main logic
case "${1:-}" in
    --list|-l)
        list_sessions
        ;;
    --latest|-L)
        latest=$(find_latest_jsonl)
        if [ -n "$latest" ]; then
            generate_report "$latest"
        else
            echo -e "${RED}No sessions found for current project${NC}"
            echo -e "${YELLOW}Try: /0-trace --list${NC}"
            exit 1
        fi
        ;;
    --file|-f)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: --file requires a path argument${NC}"
            exit 1
        fi
        generate_report "$2" "$3"
        ;;
    --all|-a)
        generate_index
        ;;
    --help|-h)
        echo "Usage: trace-report.sh [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --list, -l        List available sessions"
        echo "  --latest, -L      Generate report for most recent session"
        echo "  --file, -f FILE   Generate report for specific JSONL file"
        echo "  --all, -a         Generate index of all sessions"
        echo "  --help, -h        Show this help"
        echo ""
        echo "Without options: generates report for current project's latest session"
        ;;
    "")
        # Default: generate for current project
        latest=$(find_latest_jsonl)
        if [ -n "$latest" ]; then
            generate_report "$latest"
        else
            echo -e "${YELLOW}No sessions found for current project.${NC}"
            echo ""
            list_sessions
        fi
        ;;
    *)
        # Assume it's a file path
        if [ -f "$1" ]; then
            generate_report "$1" "$2"
        else
            echo -e "${RED}Error: Unknown option or file not found: $1${NC}"
            echo "Use --help for usage information"
            exit 1
        fi
        ;;
esac
