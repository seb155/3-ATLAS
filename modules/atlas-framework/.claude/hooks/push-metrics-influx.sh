#!/bin/bash
# =============================================================================
# ATLAS Hook: Push Claude Code Metrics to InfluxDB
# =============================================================================
# Called by Stop.sh and SessionEnd hooks to push real-time metrics
#
# Usage: ./push-metrics-influx.sh [--async]
#   --async: Run in background (default for hooks)
# =============================================================================

# Configuration
export INFLUXDB_TOKEN="x1rguEPqrYg9P5wEU4ayYn8nkvq4SbvF50ny6u26OXHTVdJnrRqkHhHA-u_H1Z00MkFMbs9mgOn1dwZ-F7kRMw=="
export INFLUXDB_ORG="HomeLab"
export INFLUXDB_BUCKET="claude_metrics"

SCRIPT_PATH="$HOME/.claude/scripts/claude-influx-exporter.py"
LOG_FILE="$HOME/.claude/logs/influx-push.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Check if exporter script exists
if [[ ! -f "$SCRIPT_PATH" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: Exporter not found at $SCRIPT_PATH" >> "$LOG_FILE"
    exit 1
fi

# Run exporter
run_exporter() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pushing metrics to InfluxDB..." >> "$LOG_FILE"
    python3 "$SCRIPT_PATH" >> "$LOG_FILE" 2>&1
    local exit_code=$?
    if [[ $exit_code -eq 0 ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Metrics pushed successfully" >> "$LOG_FILE"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: Push failed with code $exit_code" >> "$LOG_FILE"
    fi
}

# Check for async flag
if [[ "$1" == "--async" ]] || [[ "$1" == "-a" ]]; then
    run_exporter &
    disown
else
    run_exporter
fi
