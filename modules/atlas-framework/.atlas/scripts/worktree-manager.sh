#!/bin/bash
#
# ATLAS 2.0 - Git Worktree Manager
# Manages isolated worktrees for parallel agent execution
#
# Usage:
#   ./worktree-manager.sh create <agent-name>   # Create worktree for agent
#   ./worktree-manager.sh list                  # List all worktrees
#   ./worktree-manager.sh status <agent-name>   # Check worktree status
#   ./worktree-manager.sh merge <agent-name>    # Merge and cleanup worktree
#   ./worktree-manager.sh cleanup <agent-name>  # Remove worktree without merge
#   ./worktree-manager.sh cleanup-all           # Remove all agent worktrees
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AXIOM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WORKTREE_BASE="${AXIOM_ROOT}-worktrees"
RUNTIME_DIR="${AXIOM_ROOT}/.atlas/runtime"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Ensure runtime directory exists
ensure_runtime_dir() {
    mkdir -p "$RUNTIME_DIR/worktrees"
}

# Generate unique branch name for agent
generate_branch_name() {
    local agent_name=$1
    local timestamp=$(date +%Y%m%d-%H%M%S)
    echo "atlas-agent/${agent_name}/${timestamp}"
}

# Get worktree path for agent
get_worktree_path() {
    local agent_name=$1
    echo "${WORKTREE_BASE}/agent-${agent_name}"
}

# Create worktree for agent
cmd_create() {
    local agent_name=$1

    if [ -z "$agent_name" ]; then
        log_error "Usage: $0 create <agent-name>"
        exit 1
    fi

    local worktree_path=$(get_worktree_path "$agent_name")
    local branch_name=$(generate_branch_name "$agent_name")

    # Check if worktree already exists
    if [ -d "$worktree_path" ]; then
        log_warn "Worktree already exists for agent: $agent_name"
        log_info "Path: $worktree_path"
        log_info "Use 'cleanup' first if you want to recreate it"
        exit 1
    fi

    log_info "Creating worktree for agent: $agent_name"
    log_info "Branch: $branch_name"
    log_info "Path: $worktree_path"

    # Create base directory if needed
    mkdir -p "$WORKTREE_BASE"

    # Create new branch from current HEAD
    git -C "$AXIOM_ROOT" branch "$branch_name" HEAD

    # Create worktree
    git -C "$AXIOM_ROOT" worktree add "$worktree_path" "$branch_name"

    # Record worktree info
    ensure_runtime_dir
    cat > "$RUNTIME_DIR/worktrees/${agent_name}.json" << EOF
{
    "agent": "$agent_name",
    "branch": "$branch_name",
    "path": "$worktree_path",
    "created_at": "$(date -Iseconds)",
    "status": "active"
}
EOF

    log_success "Worktree created successfully"
    log_info "Agent can now work in: $worktree_path"

    # Return the path for scripting
    echo "$worktree_path"
}

# List all worktrees
cmd_list() {
    log_info "Git worktrees for AXIOM:"
    echo ""
    git -C "$AXIOM_ROOT" worktree list
    echo ""

    # Also show runtime info if available
    if [ -d "$RUNTIME_DIR/worktrees" ] && [ "$(ls -A $RUNTIME_DIR/worktrees 2>/dev/null)" ]; then
        log_info "Agent worktree details:"
        for f in "$RUNTIME_DIR/worktrees"/*.json; do
            if [ -f "$f" ]; then
                echo "  - $(basename "$f" .json):"
                cat "$f" | sed 's/^/      /'
            fi
        done
    fi
}

# Check worktree status
cmd_status() {
    local agent_name=$1

    if [ -z "$agent_name" ]; then
        log_error "Usage: $0 status <agent-name>"
        exit 1
    fi

    local worktree_path=$(get_worktree_path "$agent_name")

    if [ ! -d "$worktree_path" ]; then
        log_error "No worktree found for agent: $agent_name"
        exit 1
    fi

    log_info "Worktree status for agent: $agent_name"
    echo ""

    # Git status
    echo "Git status:"
    git -C "$worktree_path" status --short
    echo ""

    # Changed files count
    local changed=$(git -C "$worktree_path" status --porcelain | wc -l)
    log_info "Changed files: $changed"

    # Commits ahead of main
    local main_branch=$(git -C "$AXIOM_ROOT" symbolic-ref --short HEAD 2>/dev/null || echo "main")
    local ahead=$(git -C "$worktree_path" rev-list --count "${main_branch}..HEAD" 2>/dev/null || echo "0")
    log_info "Commits ahead: $ahead"

    # Runtime info
    if [ -f "$RUNTIME_DIR/worktrees/${agent_name}.json" ]; then
        echo ""
        log_info "Runtime info:"
        cat "$RUNTIME_DIR/worktrees/${agent_name}.json"
    fi
}

# Merge worktree changes back to main
cmd_merge() {
    local agent_name=$1

    if [ -z "$agent_name" ]; then
        log_error "Usage: $0 merge <agent-name>"
        exit 1
    fi

    local worktree_path=$(get_worktree_path "$agent_name")

    if [ ! -d "$worktree_path" ]; then
        log_error "No worktree found for agent: $agent_name"
        exit 1
    fi

    log_info "Merging worktree for agent: $agent_name"

    # Get branch name
    local branch_name=$(git -C "$worktree_path" branch --show-current)

    # Check for uncommitted changes
    if [ -n "$(git -C "$worktree_path" status --porcelain)" ]; then
        log_info "Committing uncommitted changes..."
        git -C "$worktree_path" add -A
        git -C "$worktree_path" commit -m "Agent $agent_name: auto-commit before merge" || true
    fi

    # Get current branch in main repo
    local current_branch=$(git -C "$AXIOM_ROOT" branch --show-current)

    # Merge the agent branch
    log_info "Merging branch $branch_name into $current_branch..."
    git -C "$AXIOM_ROOT" merge "$branch_name" --no-edit -m "Merge agent $agent_name work"

    if [ $? -eq 0 ]; then
        log_success "Merge successful"

        # Cleanup
        log_info "Cleaning up worktree..."
        cmd_cleanup "$agent_name"
    else
        log_error "Merge failed - resolve conflicts manually"
        log_info "Worktree preserved at: $worktree_path"
        exit 1
    fi
}

# Cleanup worktree without merge
cmd_cleanup() {
    local agent_name=$1

    if [ -z "$agent_name" ]; then
        log_error "Usage: $0 cleanup <agent-name>"
        exit 1
    fi

    local worktree_path=$(get_worktree_path "$agent_name")

    if [ ! -d "$worktree_path" ]; then
        log_warn "No worktree found for agent: $agent_name"
        # Still try to cleanup runtime info
        rm -f "$RUNTIME_DIR/worktrees/${agent_name}.json"
        return 0
    fi

    # Get branch name before removing worktree
    local branch_name=$(git -C "$worktree_path" branch --show-current 2>/dev/null || echo "")

    log_info "Removing worktree for agent: $agent_name"

    # Remove worktree
    git -C "$AXIOM_ROOT" worktree remove "$worktree_path" --force 2>/dev/null || rm -rf "$worktree_path"

    # Prune worktrees
    git -C "$AXIOM_ROOT" worktree prune

    # Delete branch if it exists
    if [ -n "$branch_name" ]; then
        git -C "$AXIOM_ROOT" branch -D "$branch_name" 2>/dev/null || true
    fi

    # Remove runtime info
    rm -f "$RUNTIME_DIR/worktrees/${agent_name}.json"

    log_success "Worktree cleaned up for agent: $agent_name"
}

# Cleanup all agent worktrees
cmd_cleanup_all() {
    log_warn "This will remove ALL agent worktrees!"

    # Find all agent worktrees
    if [ -d "$WORKTREE_BASE" ]; then
        for dir in "$WORKTREE_BASE"/agent-*; do
            if [ -d "$dir" ]; then
                local agent_name=$(basename "$dir" | sed 's/^agent-//')
                log_info "Cleaning up: $agent_name"
                cmd_cleanup "$agent_name"
            fi
        done
    fi

    # Cleanup base directory if empty
    rmdir "$WORKTREE_BASE" 2>/dev/null || true

    # Cleanup runtime directory
    rm -rf "$RUNTIME_DIR/worktrees"

    log_success "All agent worktrees cleaned up"
}

# Show help
cmd_help() {
    echo "ATLAS 2.0 - Git Worktree Manager"
    echo ""
    echo "Usage: $0 <command> [args]"
    echo ""
    echo "Commands:"
    echo "  create <agent-name>    Create isolated worktree for agent"
    echo "  list                   List all worktrees"
    echo "  status <agent-name>    Check worktree status and changes"
    echo "  merge <agent-name>     Merge changes and cleanup worktree"
    echo "  cleanup <agent-name>   Remove worktree without merging"
    echo "  cleanup-all            Remove all agent worktrees"
    echo "  help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 create backend-builder"
    echo "  $0 status backend-builder"
    echo "  $0 merge backend-builder"
    echo ""
    echo "Worktree location: $WORKTREE_BASE"
}

# Main command dispatcher
case "${1:-help}" in
    create)     cmd_create "$2" ;;
    list)       cmd_list ;;
    status)     cmd_status "$2" ;;
    merge)      cmd_merge "$2" ;;
    cleanup)    cmd_cleanup "$2" ;;
    cleanup-all) cmd_cleanup_all ;;
    help|--help|-h) cmd_help ;;
    *)
        log_error "Unknown command: $1"
        cmd_help
        exit 1
        ;;
esac
