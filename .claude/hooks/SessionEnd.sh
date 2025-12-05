#!/bin/bash
# Atlas Agent Framework - SessionEnd Hook
# Runs when a Claude Code session ends

LOG_DIR="${HOME}/.claude/logs"

# Log session end
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Session ended" >> "$LOG_DIR/sessions.log"

exit 0
