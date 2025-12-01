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

# Pricing per 1M tokens (as of December 2024)
PRICING = {
    # Opus 4.5
    "claude-opus-4-5-20251101": {
        "input": 15.00,
        "output": 75.00,
        "cache_read": 1.50,
        "cache_creation": 18.75
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
    # Haiku 3.5
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
    # Default fallback
    "default": {
        "input": 3.00,
        "output": 15.00,
        "cache_read": 0.30,
        "cache_creation": 3.75
    }
}

# Model name normalization
MODEL_ALIASES = {
    "opus": "claude-opus-4-5-20251101",
    "sonnet": "claude-sonnet-4-5-20250514",
    "haiku": "claude-3-5-haiku-20241022",
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

    def extract_project_name(self, filepath: Path) -> str:
        """Extract project name from file path."""
        # Path structure: ~/.claude/projects/<project-hash>/conversations/<file>.jsonl
        parts = filepath.parts
        try:
            projects_idx = parts.index('projects')
            if projects_idx + 1 < len(parts):
                project_hash = parts[projects_idx + 1]
                # Try to find a readable name from the path
                return project_hash[:12]  # Truncate hash for readability
        except (ValueError, IndexError):
            pass
        return "unknown"

    def scan_all_projects(self) -> dict:
        """Scan all JSONL files and collect metrics."""
        metrics = {
            'tokens': defaultdict(lambda: defaultdict(int)),  # {project: {model_type: count}}
            'cost': defaultdict(lambda: defaultdict(float)),  # {project: {model: cost}}
            'sessions': defaultdict(int),  # {project: count}
            'messages': defaultdict(lambda: defaultdict(int)),  # {project: {role: count}}
            'last_activity': defaultdict(float),  # {project: timestamp}
        }

        if not self.projects_dir.exists():
            logger.warning(f"Projects directory not found: {self.projects_dir}")
            return metrics

        # Find all JSONL files
        jsonl_files = list(self.projects_dir.rglob("*.jsonl"))
        logger.info(f"Found {len(jsonl_files)} JSONL files")

        for filepath in jsonl_files:
            project = self.extract_project_name(filepath)
            entries = self.parse_jsonl_file(filepath)

            session_ids = set()

            for entry in entries:
                # Track sessions
                session_id = entry.get('sessionId') or entry.get('session_id')
                if session_id:
                    session_ids.add(session_id)

                # Track messages
                role = entry.get('role', 'unknown')
                metrics['messages'][project][role] += 1

                # Track timestamp
                timestamp = entry.get('timestamp') or entry.get('created_at')
                if timestamp:
                    try:
                        if isinstance(timestamp, str):
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            ts = dt.timestamp()
                        else:
                            ts = float(timestamp)
                        metrics['last_activity'][project] = max(
                            metrics['last_activity'][project], ts
                        )
                    except (ValueError, TypeError):
                        pass

                # Track tokens and cost from usage data
                usage = entry.get('usage', {})
                model = entry.get('model', 'unknown')
                model_normalized = self.normalize_model_name(model)
                pricing = self.get_pricing(model)

                # Input tokens
                input_tokens = usage.get('input_tokens', 0)
                if input_tokens:
                    metrics['tokens'][project][f"{model_normalized}_input"] += input_tokens
                    cost = (input_tokens / 1_000_000) * pricing['input']
                    metrics['cost'][project][model_normalized] += cost

                # Output tokens
                output_tokens = usage.get('output_tokens', 0)
                if output_tokens:
                    metrics['tokens'][project][f"{model_normalized}_output"] += output_tokens
                    cost = (output_tokens / 1_000_000) * pricing['output']
                    metrics['cost'][project][model_normalized] += cost

                # Cache read tokens
                cache_read = usage.get('cache_read_input_tokens', 0)
                if cache_read:
                    metrics['tokens'][project][f"{model_normalized}_cache_read"] += cache_read
                    cost = (cache_read / 1_000_000) * pricing['cache_read']
                    metrics['cost'][project][model_normalized] += cost

                # Cache creation tokens
                cache_creation = usage.get('cache_creation_input_tokens', 0)
                if cache_creation:
                    metrics['tokens'][project][f"{model_normalized}_cache_creation"] += cache_creation
                    cost = (cache_creation / 1_000_000) * pricing['cache_creation']
                    metrics['cost'][project][model_normalized] += cost

            metrics['sessions'][project] += len(session_ids)

        self.metrics = metrics
        self.last_scan = time.time()
        return metrics

    def format_prometheus_metrics(self) -> str:
        """Format metrics in Prometheus exposition format."""
        lines = []

        # Help and type declarations
        lines.append("# HELP claude_code_tokens_total Total tokens used by Claude Code")
        lines.append("# TYPE claude_code_tokens_total counter")

        lines.append("# HELP claude_code_cost_usd Total cost in USD")
        lines.append("# TYPE claude_code_cost_usd counter")

        lines.append("# HELP claude_code_sessions_total Total number of sessions")
        lines.append("# TYPE claude_code_sessions_total counter")

        lines.append("# HELP claude_code_messages_total Total messages by role")
        lines.append("# TYPE claude_code_messages_total counter")

        lines.append("# HELP claude_code_last_activity_timestamp Last activity timestamp")
        lines.append("# TYPE claude_code_last_activity_timestamp gauge")

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
