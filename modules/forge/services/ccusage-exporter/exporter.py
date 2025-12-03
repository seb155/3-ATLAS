#!/usr/bin/env python3
"""
Claude Code Usage Exporter for Prometheus

Reads Claude Code JSONL files from ~/.claude/projects/ and exposes metrics
for Prometheus scraping. Zero token cost - all data from local files.

Metrics exposed:
- claude_code_tokens_total{model, type, project}
- claude_code_cost_usd{model, project}
- claude_code_sessions_total{project}
- claude_code_messages_total{role, project}
- claude_code_last_activity_timestamp{project}
"""

import json
import os
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pricing per 1M tokens (December 2025)
# Source: https://platform.claude.com/docs/en/about-claude/pricing
PRICING = {
    # Opus 4.5 - NEW PRICE (67% reduction!)
    "claude-opus-4-5-20251101": {
        "input": 5.00,        # Was $15
        "output": 25.00,      # Was $75
        "cache_read": 0.50,   # 0.1x input
        "cache_creation": 6.25  # 1.25x input
    },
    # Sonnet 4.5
    "claude-sonnet-4-5-20250514": {
        "input": 3.00,
        "output": 15.00,
        "cache_read": 0.30,
        "cache_creation": 3.75
    },
    # Sonnet 4 (alternate ID)
    "claude-sonnet-4-20250514": {
        "input": 3.00,
        "output": 15.00,
        "cache_read": 0.30,
        "cache_creation": 3.75
    },
    # Haiku 4.5 (new)
    "claude-haiku-4-5-20251001": {
        "input": 1.00,
        "output": 5.00,
        "cache_read": 0.10,
        "cache_creation": 1.25
    },
    # Haiku 3.5 (legacy)
    "claude-3-5-haiku-20241022": {
        "input": 0.80,
        "output": 4.00,
        "cache_read": 0.08,
        "cache_creation": 1.00
    },
    # Haiku 3 (legacy)
    "claude-3-haiku-20240307": {
        "input": 0.25,
        "output": 1.25,
        "cache_read": 0.03,
        "cache_creation": 0.30
    },
    # Default fallback (Sonnet pricing)
    "default": {
        "input": 3.00,
        "output": 15.00,
        "cache_read": 0.30,
        "cache_creation": 3.75
    }
}

# Monthly budget for Max plan (configurable via env)
MONTHLY_BUDGET = float(os.environ.get('CLAUDE_MONTHLY_BUDGET', '300'))

# Model name normalization
MODEL_ALIASES = {
    "opus": "claude-opus-4-5-20251101",
    "sonnet": "claude-sonnet-4-5-20250514",
    "haiku": "claude-haiku-4-5-20251001",  # Updated to Haiku 4.5
}


class MetricsCollector:
    """Collects metrics from Claude Code JSONL files."""

    def __init__(self, projects_dir: str):
        self.projects_dir = Path(projects_dir)
        self.metrics = {}
        self.last_scan = None

    def get_pricing(self, model: str) -> dict:
        """Get pricing for a model, with fallback to default."""
        # Try exact match
        if model in PRICING:
            return PRICING[model]

        # Try alias
        model_lower = model.lower()
        for alias, full_name in MODEL_ALIASES.items():
            if alias in model_lower:
                return PRICING.get(full_name, PRICING["default"])

        # Fallback
        return PRICING["default"]

    def normalize_model_name(self, model: str) -> str:
        """Normalize model name for consistent labeling."""
        model_lower = model.lower()
        if "opus" in model_lower:
            return "opus"
        elif "sonnet" in model_lower:
            return "sonnet"
        elif "haiku" in model_lower:
            return "haiku"
        return model

    def parse_jsonl_file(self, filepath: Path) -> list:
        """Parse a JSONL file and extract usage data."""
        entries = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        entries.append(data)
                    except json.JSONDecodeError as e:
                        logger.debug(f"Skipping invalid JSON at {filepath}:{line_num}: {e}")
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
        return entries

    def extract_project_name(self, entry: dict, filepath: Path) -> str:
        """Extract project name from cwd field (last folder) or filepath."""
        # Try cwd field first (best source)
        cwd = entry.get('cwd', '')
        if cwd:
            # /home/seb/projects/AXIOM/apps/synapse -> synapse
            # /home/seb/projects/AXIOM -> AXIOM
            parts = cwd.rstrip('/').split('/')
            if parts:
                return parts[-1]

        # Fallback: decode folder name from filepath
        # Folder name format: -home-seb-projects-AXIOM
        folder_name = filepath.parent.name
        if folder_name.startswith('-'):
            parts = folder_name.split('-')
            if parts:
                return parts[-1]

        return "unknown"

    def scan_all_projects(self) -> dict:
        """Scan all JSONL files and collect metrics."""
        metrics = {
            'tokens': defaultdict(lambda: defaultdict(int)),  # {project: {model_type: count}}
            'cost': defaultdict(lambda: defaultdict(float)),  # {project: {model: cost}}
            'cost_monthly': defaultdict(lambda: defaultdict(float)),  # {project: {model: cost}} current month only
            'sessions': defaultdict(int),  # {project: count}
            'messages': defaultdict(lambda: defaultdict(int)),  # {project: {role: count}}
            'tools': defaultdict(lambda: defaultdict(int)),  # {project: {tool: count}}
            'responses': defaultdict(lambda: defaultdict(int)),  # {project: {status: count}}
            'last_activity': defaultdict(float),  # {project: timestamp}
        }

        # Calculate current month start for budget tracking
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_start_ts = month_start.timestamp()

        if not self.projects_dir.exists():
            logger.warning(f"Projects directory not found: {self.projects_dir}")
            return metrics

        # Find all JSONL files
        jsonl_files = list(self.projects_dir.rglob("*.jsonl"))
        logger.info(f"Found {len(jsonl_files)} JSONL files")

        for filepath in jsonl_files:
            entries = self.parse_jsonl_file(filepath)

            session_ids = set()
            project_cache = {}  # Cache project names per session

            for entry in entries:
                # Extract project name from cwd (cached per session for efficiency)
                session_id = entry.get('sessionId') or entry.get('session_id')
                if session_id:
                    session_ids.add(session_id)
                    if session_id not in project_cache:
                        project_cache[session_id] = self.extract_project_name(entry, filepath)
                    project = project_cache[session_id]
                else:
                    project = self.extract_project_name(entry, filepath)

                # Get message object (Claude Code structure)
                message = entry.get('message', {})

                # Track messages by role (from message object or entry type)
                role = message.get('role') or entry.get('type', 'unknown')
                metrics['messages'][project][role] += 1

                # Track timestamp
                timestamp = entry.get('timestamp') or entry.get('created_at')
                entry_ts = None
                if timestamp:
                    try:
                        if isinstance(timestamp, str):
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            entry_ts = dt.timestamp()
                        else:
                            entry_ts = float(timestamp)
                        metrics['last_activity'][project] = max(
                            metrics['last_activity'][project], entry_ts
                        )
                    except (ValueError, TypeError):
                        pass

                # Track stop_reason for success/error rate
                stop_reason = message.get('stop_reason')
                if stop_reason:  # Ignore null (streaming in progress)
                    if stop_reason in ['end_turn', 'tool_use']:
                        metrics['responses'][project]['success'] += 1
                    elif stop_reason == 'max_tokens':
                        metrics['responses'][project]['truncated'] += 1
                    else:
                        metrics['responses'][project]['error'] += 1

                # Extract usage from message object (correct structure)
                usage = message.get('usage', {})
                model = message.get('model', 'unknown')

                # Skip if no usage data
                if not usage:
                    continue

                model_normalized = self.normalize_model_name(model)
                pricing = self.get_pricing(model)

                # Track if this entry is in current month (for budget)
                is_current_month = entry_ts and entry_ts >= month_start_ts

                # Input tokens
                input_tokens = usage.get('input_tokens', 0)
                if input_tokens:
                    metrics['tokens'][project][f"{model_normalized}_input"] += input_tokens
                    cost = (input_tokens / 1_000_000) * pricing['input']
                    metrics['cost'][project][model_normalized] += cost
                    if is_current_month:
                        metrics['cost_monthly'][project][model_normalized] += cost

                # Output tokens
                output_tokens = usage.get('output_tokens', 0)
                if output_tokens:
                    metrics['tokens'][project][f"{model_normalized}_output"] += output_tokens
                    cost = (output_tokens / 1_000_000) * pricing['output']
                    metrics['cost'][project][model_normalized] += cost
                    if is_current_month:
                        metrics['cost_monthly'][project][model_normalized] += cost

                # Cache read tokens
                cache_read = usage.get('cache_read_input_tokens', 0)
                if cache_read:
                    metrics['tokens'][project][f"{model_normalized}_cache_read"] += cache_read
                    cost = (cache_read / 1_000_000) * pricing['cache_read']
                    metrics['cost'][project][model_normalized] += cost
                    if is_current_month:
                        metrics['cost_monthly'][project][model_normalized] += cost

                # Cache creation tokens
                cache_creation = usage.get('cache_creation_input_tokens', 0)
                if cache_creation:
                    metrics['tokens'][project][f"{model_normalized}_cache_creation"] += cache_creation
                    cost = (cache_creation / 1_000_000) * pricing['cache_creation']
                    metrics['cost'][project][model_normalized] += cost
                    if is_current_month:
                        metrics['cost_monthly'][project][model_normalized] += cost

                # Track tool usage from message content
                content = message.get('content', [])
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'tool_use':
                            tool_name = item.get('name', 'unknown')
                            metrics['tools'][project][tool_name] += 1

            # Add session count for all projects found in this file
            for proj in set(project_cache.values()):
                metrics['sessions'][proj] += len([sid for sid, p in project_cache.items() if p == proj])

        self.metrics = metrics
        self.last_scan = time.time()
        return metrics

    def format_prometheus_metrics(self) -> str:
        """Format metrics in Prometheus exposition format."""
        lines = []

        # Help and type declarations
        lines.append("# HELP claude_code_tokens_total Total tokens used by Claude Code")
        lines.append("# TYPE claude_code_tokens_total counter")

        lines.append("# HELP claude_code_cost_usd Total cost in USD (all time)")
        lines.append("# TYPE claude_code_cost_usd counter")

        lines.append("# HELP claude_code_cost_monthly_usd Cost in USD for current month")
        lines.append("# TYPE claude_code_cost_monthly_usd gauge")

        lines.append("# HELP claude_code_sessions_total Total number of sessions")
        lines.append("# TYPE claude_code_sessions_total counter")

        lines.append("# HELP claude_code_messages_total Total messages by role")
        lines.append("# TYPE claude_code_messages_total counter")

        lines.append("# HELP claude_code_responses_total Total responses by status (success/truncated/error)")
        lines.append("# TYPE claude_code_responses_total counter")

        lines.append("# HELP claude_code_last_activity_timestamp Last activity timestamp")
        lines.append("# TYPE claude_code_last_activity_timestamp gauge")

        lines.append("# HELP claude_code_tools_total Total tool calls by tool name")
        lines.append("# TYPE claude_code_tools_total counter")

        lines.append("# HELP claude_code_budget_monthly_usd Monthly budget for Max plan")
        lines.append("# TYPE claude_code_budget_monthly_usd gauge")

        lines.append("# HELP claude_code_budget_used_usd Amount used from monthly budget")
        lines.append("# TYPE claude_code_budget_used_usd gauge")

        lines.append("# HELP claude_code_budget_remaining_usd Remaining monthly budget")
        lines.append("# TYPE claude_code_budget_remaining_usd gauge")

        lines.append("# HELP claude_code_budget_used_percent Percentage of monthly budget used")
        lines.append("# TYPE claude_code_budget_used_percent gauge")

        lines.append("# HELP claude_code_exporter_last_scan_timestamp Last successful scan")
        lines.append("# TYPE claude_code_exporter_last_scan_timestamp gauge")

        # Token metrics
        for project, token_data in self.metrics.get('tokens', {}).items():
            for model_type, count in token_data.items():
                # Parse model and type from key like "opus_input"
                parts = model_type.rsplit('_', 1)
                if len(parts) == 2:
                    model, token_type = parts
                else:
                    model, token_type = model_type, "unknown"
                lines.append(
                    f'claude_code_tokens_total{{model="{model}",type="{token_type}",project="{project}"}} {count}'
                )

        # Cost metrics
        for project, cost_data in self.metrics.get('cost', {}).items():
            for model, cost in cost_data.items():
                lines.append(
                    f'claude_code_cost_usd{{model="{model}",project="{project}"}} {cost:.6f}'
                )

        # Session metrics
        for project, count in self.metrics.get('sessions', {}).items():
            lines.append(
                f'claude_code_sessions_total{{project="{project}"}} {count}'
            )

        # Message metrics
        for project, role_data in self.metrics.get('messages', {}).items():
            for role, count in role_data.items():
                lines.append(
                    f'claude_code_messages_total{{role="{role}",project="{project}"}} {count}'
                )

        # Last activity
        for project, timestamp in self.metrics.get('last_activity', {}).items():
            lines.append(
                f'claude_code_last_activity_timestamp{{project="{project}"}} {timestamp}'
            )

        # Tool usage metrics
        for project, tool_data in self.metrics.get('tools', {}).items():
            for tool, count in tool_data.items():
                lines.append(
                    f'claude_code_tools_total{{tool="{tool}",project="{project}"}} {count}'
                )

        # Response status metrics (success/truncated/error)
        for project, response_data in self.metrics.get('responses', {}).items():
            for status, count in response_data.items():
                lines.append(
                    f'claude_code_responses_total{{status="{status}",project="{project}"}} {count}'
                )

        # Monthly cost metrics
        for project, cost_data in self.metrics.get('cost_monthly', {}).items():
            for model, cost in cost_data.items():
                lines.append(
                    f'claude_code_cost_monthly_usd{{model="{model}",project="{project}"}} {cost:.6f}'
                )

        # Budget metrics (aggregate)
        total_monthly_cost = sum(
            cost for project_costs in self.metrics.get('cost_monthly', {}).values()
            for cost in project_costs.values()
        )
        budget_remaining = max(0, MONTHLY_BUDGET - total_monthly_cost)
        budget_percent = min(100, (total_monthly_cost / MONTHLY_BUDGET) * 100) if MONTHLY_BUDGET > 0 else 0

        lines.append(f'claude_code_budget_monthly_usd {MONTHLY_BUDGET:.2f}')
        lines.append(f'claude_code_budget_used_usd {total_monthly_cost:.6f}')
        lines.append(f'claude_code_budget_remaining_usd {budget_remaining:.6f}')
        lines.append(f'claude_code_budget_used_percent {budget_percent:.2f}')

        # Exporter metadata
        if self.last_scan:
            lines.append(f'claude_code_exporter_last_scan_timestamp {self.last_scan}')

        return '\n'.join(lines) + '\n'


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for Prometheus metrics endpoint."""

    collector = None

    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.debug(f"HTTP: {args[0]}")

    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()

            # Refresh metrics
            self.collector.scan_all_projects()
            metrics = self.collector.format_prometheus_metrics()
            self.wfile.write(metrics.encode('utf-8'))

        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            health = {
                "status": "healthy",
                "last_scan": self.collector.last_scan,
                "projects_dir": str(self.collector.projects_dir)
            }
            self.wfile.write(json.dumps(health).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()


def main():
    """Main entry point."""
    projects_dir = os.environ.get('CLAUDE_PROJECTS_DIR', os.path.expanduser('~/.claude/projects'))
    port = int(os.environ.get('METRICS_PORT', '9091'))
    scrape_interval = int(os.environ.get('SCRAPE_INTERVAL', '60'))

    logger.info(f"Starting Claude Code Usage Exporter")
    logger.info(f"  Projects directory: {projects_dir}")
    logger.info(f"  Metrics port: {port}")
    logger.info(f"  Scrape interval: {scrape_interval}s")
    logger.info(f"  Monthly budget: ${MONTHLY_BUDGET:.2f}")

    # Initialize collector
    collector = MetricsCollector(projects_dir)
    MetricsHandler.collector = collector

    # Initial scan
    collector.scan_all_projects()
    logger.info(f"Initial scan complete. Found {len(collector.metrics.get('sessions', {}))} projects")

    # Start HTTP server
    server = HTTPServer(('0.0.0.0', port), MetricsHandler)
    logger.info(f"Serving metrics on http://0.0.0.0:{port}/metrics")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.shutdown()


if __name__ == '__main__':
    main()
