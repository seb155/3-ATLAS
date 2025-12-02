#!/usr/bin/env python3
"""
Claude Code Usage Exporter PRO - Advanced Metrics for AXIOM

Enhanced version with:
- ATLAS command tracking (slash commands, workflows)
- Token flow analysis (sent vs received vs cached)
- Optimization insights and recommendations
- Cost efficiency metrics
- Session patterns analysis

Zero token cost - all data from local files.
"""

import json
import os
import time
import logging
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from typing import Dict, List, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# PRICING (December 2025)
# =============================================================================
PRICING = {
    "claude-opus-4-5-20251101": {
        "input": 5.00, "output": 25.00,
        "cache_read": 0.50, "cache_creation": 6.25
    },
    "claude-sonnet-4-5-20250514": {
        "input": 3.00, "output": 15.00,
        "cache_read": 0.30, "cache_creation": 3.75
    },
    "claude-sonnet-4-20250514": {
        "input": 3.00, "output": 15.00,
        "cache_read": 0.30, "cache_creation": 3.75
    },
    "claude-haiku-4-5-20251001": {
        "input": 1.00, "output": 5.00,
        "cache_read": 0.10, "cache_creation": 1.25
    },
    "claude-3-5-haiku-20241022": {
        "input": 0.80, "output": 4.00,
        "cache_read": 0.08, "cache_creation": 1.00
    },
    "default": {
        "input": 3.00, "output": 15.00,
        "cache_read": 0.30, "cache_creation": 3.75
    }
}

MONTHLY_BUDGET = float(os.environ.get('CLAUDE_MONTHLY_BUDGET', '300'))

# =============================================================================
# ATLAS COMMAND PATTERNS
# =============================================================================
ATLAS_COMMANDS = {
    # Session commands
    '/0-new-session': 'session_start',
    '/0-next': 'session_continue',
    '/0-resume': 'session_resume',
    '/0-ship': 'git_workflow',
    '/0-progress': 'progress_check',
    '/0-dashboard': 'dashboard',
    # Common slash commands
    '/compact': 'context_compact',
    '/clear': 'context_clear',
    '/help': 'help',
    '/doctor': 'diagnostics',
    '/config': 'configuration',
    '/cost': 'cost_check',
    '/memory': 'memory_check',
    # Tools
    'Task': 'agent_spawn',
    'Bash': 'shell_command',
    'Read': 'file_read',
    'Write': 'file_write',
    'Edit': 'file_edit',
    'Glob': 'file_search',
    'Grep': 'content_search',
    'WebFetch': 'web_fetch',
    'WebSearch': 'web_search',
    'TodoWrite': 'todo_management',
}

# Workflow patterns (detected from user messages)
WORKFLOW_PATTERNS = {
    r'test|pytest|jest|vitest': 'testing',
    r'commit|push|pull|merge|branch': 'git_operations',
    r'debug|fix|error|bug': 'debugging',
    r'refactor|clean|optimize': 'refactoring',
    r'create|add|implement|build': 'development',
    r'document|readme|comment': 'documentation',
    r'review|check|validate': 'code_review',
    r'deploy|docker|container': 'deployment',
    r'database|migration|alembic': 'database',
    r'api|endpoint|route': 'api_development',
}


class MetricsCollectorPro:
    """Advanced metrics collector with optimization insights."""

    def __init__(self, projects_dir: str, atlas_logs_dir: str = None):
        self.projects_dir = Path(projects_dir)
        self.atlas_logs_dir = Path(atlas_logs_dir) if atlas_logs_dir else None
        self.metrics = {}
        self.last_scan = None
        self.optimization_insights = []

    def get_pricing(self, model: str) -> dict:
        if model in PRICING:
            return PRICING[model]
        model_lower = model.lower()
        for key in PRICING:
            if key != "default" and any(part in model_lower for part in key.split('-')[1:3]):
                return PRICING[key]
        return PRICING["default"]

    def normalize_model_name(self, model: str) -> str:
        model_lower = model.lower()
        if "opus" in model_lower:
            return "opus"
        elif "sonnet" in model_lower:
            return "sonnet"
        elif "haiku" in model_lower:
            return "haiku"
        return model

    def extract_project_name(self, entry: dict, filepath: Path) -> str:
        cwd = entry.get('cwd', '')
        if cwd:
            parts = cwd.rstrip('/').split('/')
            if parts:
                return parts[-1]
        folder_name = filepath.parent.name
        if folder_name.startswith('-'):
            parts = folder_name.split('-')
            if parts:
                return parts[-1]
        return "unknown"

    def detect_atlas_command(self, content: str) -> Optional[str]:
        """Detect ATLAS slash commands in user messages."""
        for cmd, cmd_type in ATLAS_COMMANDS.items():
            if cmd.startswith('/') and cmd in content:
                return cmd_type
        return None

    def detect_workflow(self, content: str) -> Optional[str]:
        """Detect workflow type from message content."""
        content_lower = content.lower()
        for pattern, workflow_type in WORKFLOW_PATTERNS.items():
            if re.search(pattern, content_lower):
                return workflow_type
        return None

    def parse_jsonl_file(self, filepath: Path) -> list:
        entries = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
        return entries

    def scan_all_projects(self) -> dict:
        """Scan all JSONL files and collect comprehensive metrics."""
        metrics = {
            # Token metrics
            'tokens_sent': defaultdict(lambda: defaultdict(int)),      # Input to Claude
            'tokens_received': defaultdict(lambda: defaultdict(int)),  # Output from Claude
            'tokens_cached': defaultdict(lambda: defaultdict(int)),    # Cache read (savings!)
            'tokens_cache_created': defaultdict(lambda: defaultdict(int)),  # Cache creation

            # Cost metrics
            'cost': defaultdict(lambda: defaultdict(float)),
            'cost_monthly': defaultdict(lambda: defaultdict(float)),
            'cost_saved_cache': defaultdict(float),  # Money saved via cache

            # Session & message metrics
            'sessions': defaultdict(int),
            'messages': defaultdict(lambda: defaultdict(int)),
            'responses': defaultdict(lambda: defaultdict(int)),
            'last_activity': defaultdict(float),

            # Tool usage (detailed)
            'tools': defaultdict(lambda: defaultdict(int)),
            'tools_by_session': defaultdict(lambda: defaultdict(int)),

            # ATLAS specific
            'atlas_commands': defaultdict(int),           # Slash command usage
            'workflows': defaultdict(int),                # Detected workflow types
            'session_modes': defaultdict(int),            # FULL/QUICK/RECOVERY

            # Optimization metrics
            'avg_tokens_per_message': defaultdict(list),  # For calculating efficiency
            'cache_hit_rate': defaultdict(list),          # Cache effectiveness
            'model_switches': defaultdict(int),           # Model changes in session

            # Time-based metrics
            'hourly_usage': defaultdict(lambda: defaultdict(int)),  # Hour -> tokens
            'daily_cost': defaultdict(float),             # Date -> cost
        }

        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_start_ts = month_start.timestamp()

        if not self.projects_dir.exists():
            logger.warning(f"Projects directory not found: {self.projects_dir}")
            return metrics

        jsonl_files = list(self.projects_dir.rglob("*.jsonl"))
        logger.info(f"Found {len(jsonl_files)} JSONL files")

        for filepath in jsonl_files:
            entries = self.parse_jsonl_file(filepath)
            session_ids = set()
            project_cache = {}
            session_models = defaultdict(set)  # Track models per session

            for entry in entries:
                session_id = entry.get('sessionId') or entry.get('session_id')
                if session_id:
                    session_ids.add(session_id)
                    if session_id not in project_cache:
                        project_cache[session_id] = self.extract_project_name(entry, filepath)
                    project = project_cache[session_id]
                else:
                    project = self.extract_project_name(entry, filepath)

                message = entry.get('message', {})
                role = message.get('role') or entry.get('type', 'unknown')
                metrics['messages'][project][role] += 1

                # Extract user message content for command/workflow detection
                if role == 'user':
                    content = message.get('content', '')
                    if isinstance(content, list):
                        content = ' '.join(
                            item.get('text', '') for item in content
                            if isinstance(item, dict) and item.get('type') == 'text'
                        )

                    # Detect ATLAS commands
                    atlas_cmd = self.detect_atlas_command(str(content))
                    if atlas_cmd:
                        metrics['atlas_commands'][atlas_cmd] += 1

                    # Detect workflow type
                    workflow = self.detect_workflow(str(content))
                    if workflow:
                        metrics['workflows'][workflow] += 1

                # Timestamp processing
                timestamp = entry.get('timestamp') or entry.get('created_at')
                entry_ts = None
                if timestamp:
                    try:
                        if isinstance(timestamp, str):
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            entry_ts = dt.timestamp()
                            # Track hourly usage
                            hour = dt.hour
                            day_str = dt.strftime('%Y-%m-%d')
                        else:
                            entry_ts = float(timestamp)
                            dt = datetime.fromtimestamp(entry_ts)
                            hour = dt.hour
                            day_str = dt.strftime('%Y-%m-%d')
                        metrics['last_activity'][project] = max(
                            metrics['last_activity'][project], entry_ts
                        )
                    except (ValueError, TypeError):
                        hour = None
                        day_str = None

                # Response tracking
                stop_reason = message.get('stop_reason')
                if stop_reason:
                    if stop_reason in ['end_turn', 'tool_use']:
                        metrics['responses'][project]['success'] += 1
                    elif stop_reason == 'max_tokens':
                        metrics['responses'][project]['truncated'] += 1
                    else:
                        metrics['responses'][project]['error'] += 1

                # Usage extraction
                usage = message.get('usage', {})
                model = message.get('model', 'unknown')

                if not usage:
                    continue

                model_normalized = self.normalize_model_name(model)
                pricing = self.get_pricing(model)
                is_current_month = entry_ts and entry_ts >= month_start_ts

                # Track model per session (for model switch detection)
                if session_id:
                    session_models[session_id].add(model_normalized)

                # =====================================================
                # TOKEN FLOW ANALYSIS
                # =====================================================

                # Input tokens (SENT to Claude - your context)
                input_tokens = usage.get('input_tokens', 0)
                if input_tokens:
                    metrics['tokens_sent'][project][model_normalized] += input_tokens
                    cost = (input_tokens / 1_000_000) * pricing['input']
                    metrics['cost'][project][model_normalized] += cost
                    if is_current_month:
                        metrics['cost_monthly'][project][model_normalized] += cost
                    if hour is not None:
                        metrics['hourly_usage'][hour]['input'] += input_tokens
                    if day_str:
                        metrics['daily_cost'][day_str] += cost

                # Output tokens (RECEIVED from Claude - its response)
                output_tokens = usage.get('output_tokens', 0)
                if output_tokens:
                    metrics['tokens_received'][project][model_normalized] += output_tokens
                    cost = (output_tokens / 1_000_000) * pricing['output']
                    metrics['cost'][project][model_normalized] += cost
                    if is_current_month:
                        metrics['cost_monthly'][project][model_normalized] += cost
                    if hour is not None:
                        metrics['hourly_usage'][hour]['output'] += output_tokens
                    if day_str:
                        metrics['daily_cost'][day_str] += cost

                    # Track tokens per message for efficiency calculation
                    metrics['avg_tokens_per_message'][project].append(output_tokens)

                # Cache READ tokens (SAVINGS! - context already cached)
                cache_read = usage.get('cache_read_input_tokens', 0)
                if cache_read:
                    metrics['tokens_cached'][project][model_normalized] += cache_read
                    cost = (cache_read / 1_000_000) * pricing['cache_read']
                    metrics['cost'][project][model_normalized] += cost
                    if is_current_month:
                        metrics['cost_monthly'][project][model_normalized] += cost

                    # Calculate savings (what we would have paid without cache)
                    full_cost = (cache_read / 1_000_000) * pricing['input']
                    savings = full_cost - cost
                    metrics['cost_saved_cache'][project] += savings

                # Cache CREATION tokens (one-time cost to cache context)
                cache_creation = usage.get('cache_creation_input_tokens', 0)
                if cache_creation:
                    metrics['tokens_cache_created'][project][model_normalized] += cache_creation
                    cost = (cache_creation / 1_000_000) * pricing['cache_creation']
                    metrics['cost'][project][model_normalized] += cost
                    if is_current_month:
                        metrics['cost_monthly'][project][model_normalized] += cost

                # Calculate cache hit rate for this entry
                total_input = input_tokens + cache_read + cache_creation
                if total_input > 0:
                    cache_hit = cache_read / total_input
                    metrics['cache_hit_rate'][project].append(cache_hit)

                # Tool usage tracking
                content = message.get('content', [])
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'tool_use':
                            tool_name = item.get('name', 'unknown')
                            metrics['tools'][project][tool_name] += 1
                            if session_id:
                                metrics['tools_by_session'][session_id][tool_name] += 1

            # Count sessions per project
            for proj in set(project_cache.values()):
                proj_sessions = [sid for sid, p in project_cache.items() if p == proj]
                metrics['sessions'][proj] += len(proj_sessions)

            # Count model switches
            for session_id, models in session_models.items():
                if len(models) > 1:
                    proj = project_cache.get(session_id, 'unknown')
                    metrics['model_switches'][proj] += 1

        # Generate optimization insights
        self.optimization_insights = self._generate_insights(metrics)

        self.metrics = metrics
        self.last_scan = time.time()
        return metrics

    def _generate_insights(self, metrics: dict) -> List[dict]:
        """Generate optimization insights from metrics."""
        insights = []

        # Insight 1: Low cache hit rate
        for project, rates in metrics['cache_hit_rate'].items():
            if rates:
                avg_rate = sum(rates) / len(rates)
                if avg_rate < 0.3:
                    insights.append({
                        'type': 'cache_optimization',
                        'severity': 'high',
                        'project': project,
                        'message': f'Cache hit rate is {avg_rate:.1%}. Consider structuring prompts to maximize cache reuse.',
                        'potential_savings': 'up to 90% on repeated context'
                    })

        # Insight 2: High output vs input ratio (might indicate verbose prompts)
        for project in metrics['tokens_sent']:
            total_sent = sum(metrics['tokens_sent'][project].values())
            total_received = sum(metrics['tokens_received'][project].values())
            if total_sent > 0:
                ratio = total_received / total_sent
                if ratio < 0.5:
                    insights.append({
                        'type': 'prompt_efficiency',
                        'severity': 'medium',
                        'project': project,
                        'message': f'Output/Input ratio is {ratio:.2f}. Large context with small responses may indicate over-contexting.',
                        'recommendation': 'Consider using /compact more frequently'
                    })

        # Insight 3: Opus usage for simple tasks
        for project in metrics['tools']:
            tools = metrics['tools'][project]
            if 'Read' in tools or 'Glob' in tools:
                opus_tokens = metrics['tokens_sent'][project].get('opus', 0)
                total_tokens = sum(metrics['tokens_sent'][project].values())
                if opus_tokens > 0 and total_tokens > 0:
                    opus_ratio = opus_tokens / total_tokens
                    if opus_ratio > 0.7:
                        insights.append({
                            'type': 'model_optimization',
                            'severity': 'medium',
                            'project': project,
                            'message': f'{opus_ratio:.0%} of tokens use Opus. Consider Haiku for file reading tasks.',
                            'potential_savings': f'${(opus_tokens/1_000_000) * 4:.2f} by switching to Haiku'
                        })

        return insights

    def format_prometheus_metrics(self) -> str:
        """Format all metrics in Prometheus exposition format."""
        lines = []

        # =================================================================
        # TOKEN FLOW METRICS (The key insight: what's sent vs received)
        # =================================================================
        lines.append("# HELP claude_code_tokens_sent_total Tokens sent TO Claude (your input)")
        lines.append("# TYPE claude_code_tokens_sent_total counter")
        for project, model_data in self.metrics.get('tokens_sent', {}).items():
            for model, count in model_data.items():
                lines.append(f'claude_code_tokens_sent_total{{model="{model}",project="{project}"}} {count}')

        lines.append("# HELP claude_code_tokens_received_total Tokens received FROM Claude (its output)")
        lines.append("# TYPE claude_code_tokens_received_total counter")
        for project, model_data in self.metrics.get('tokens_received', {}).items():
            for model, count in model_data.items():
                lines.append(f'claude_code_tokens_received_total{{model="{model}",project="{project}"}} {count}')

        lines.append("# HELP claude_code_tokens_cached_total Tokens from cache (SAVINGS)")
        lines.append("# TYPE claude_code_tokens_cached_total counter")
        for project, model_data in self.metrics.get('tokens_cached', {}).items():
            for model, count in model_data.items():
                lines.append(f'claude_code_tokens_cached_total{{model="{model}",project="{project}"}} {count}')

        lines.append("# HELP claude_code_tokens_cache_created_total Tokens used to create cache")
        lines.append("# TYPE claude_code_tokens_cache_created_total counter")
        for project, model_data in self.metrics.get('tokens_cache_created', {}).items():
            for model, count in model_data.items():
                lines.append(f'claude_code_tokens_cache_created_total{{model="{model}",project="{project}"}} {count}')

        # Legacy total (for backwards compatibility)
        lines.append("# HELP claude_code_tokens_total Total tokens (all types)")
        lines.append("# TYPE claude_code_tokens_total counter")
        for project in set(list(self.metrics.get('tokens_sent', {}).keys()) +
                          list(self.metrics.get('tokens_received', {}).keys())):
            for model in set(list(self.metrics.get('tokens_sent', {}).get(project, {}).keys()) +
                            list(self.metrics.get('tokens_received', {}).get(project, {}).keys())):
                sent = self.metrics.get('tokens_sent', {}).get(project, {}).get(model, 0)
                received = self.metrics.get('tokens_received', {}).get(project, {}).get(model, 0)
                cached = self.metrics.get('tokens_cached', {}).get(project, {}).get(model, 0)
                lines.append(f'claude_code_tokens_total{{model="{model}",type="input",project="{project}"}} {sent}')
                lines.append(f'claude_code_tokens_total{{model="{model}",type="output",project="{project}"}} {received}')
                lines.append(f'claude_code_tokens_total{{model="{model}",type="cache_read",project="{project}"}} {cached}')

        # =================================================================
        # COST METRICS
        # =================================================================
        lines.append("# HELP claude_code_cost_usd Total cost in USD")
        lines.append("# TYPE claude_code_cost_usd counter")
        for project, cost_data in self.metrics.get('cost', {}).items():
            for model, cost in cost_data.items():
                lines.append(f'claude_code_cost_usd{{model="{model}",project="{project}"}} {cost:.6f}')

        lines.append("# HELP claude_code_cost_monthly_usd Cost for current month")
        lines.append("# TYPE claude_code_cost_monthly_usd gauge")
        for project, cost_data in self.metrics.get('cost_monthly', {}).items():
            for model, cost in cost_data.items():
                lines.append(f'claude_code_cost_monthly_usd{{model="{model}",project="{project}"}} {cost:.6f}')

        lines.append("# HELP claude_code_cost_saved_cache_usd Money saved via prompt caching")
        lines.append("# TYPE claude_code_cost_saved_cache_usd counter")
        for project, savings in self.metrics.get('cost_saved_cache', {}).items():
            lines.append(f'claude_code_cost_saved_cache_usd{{project="{project}"}} {savings:.6f}')

        # Budget metrics
        total_monthly = sum(
            cost for project_costs in self.metrics.get('cost_monthly', {}).values()
            for cost in project_costs.values()
        )
        total_savings = sum(self.metrics.get('cost_saved_cache', {}).values())

        lines.append("# HELP claude_code_budget_monthly_usd Monthly budget")
        lines.append("# TYPE claude_code_budget_monthly_usd gauge")
        lines.append(f'claude_code_budget_monthly_usd {MONTHLY_BUDGET:.2f}')

        lines.append("# HELP claude_code_budget_used_usd Budget used this month")
        lines.append("# TYPE claude_code_budget_used_usd gauge")
        lines.append(f'claude_code_budget_used_usd {total_monthly:.6f}')

        lines.append("# HELP claude_code_budget_remaining_usd Budget remaining")
        lines.append("# TYPE claude_code_budget_remaining_usd gauge")
        lines.append(f'claude_code_budget_remaining_usd {max(0, MONTHLY_BUDGET - total_monthly):.6f}')

        lines.append("# HELP claude_code_budget_used_percent Budget usage percentage")
        lines.append("# TYPE claude_code_budget_used_percent gauge")
        lines.append(f'claude_code_budget_used_percent {min(100, (total_monthly / MONTHLY_BUDGET) * 100):.2f}')

        lines.append("# HELP claude_code_total_savings_usd Total savings from caching")
        lines.append("# TYPE claude_code_total_savings_usd counter")
        lines.append(f'claude_code_total_savings_usd {total_savings:.6f}')

        # =================================================================
        # ATLAS COMMAND METRICS
        # =================================================================
        lines.append("# HELP claude_code_atlas_commands_total ATLAS slash command usage")
        lines.append("# TYPE claude_code_atlas_commands_total counter")
        for cmd_type, count in self.metrics.get('atlas_commands', {}).items():
            lines.append(f'claude_code_atlas_commands_total{{command="{cmd_type}"}} {count}')

        lines.append("# HELP claude_code_workflows_total Detected workflow types")
        lines.append("# TYPE claude_code_workflows_total counter")
        for workflow, count in self.metrics.get('workflows', {}).items():
            lines.append(f'claude_code_workflows_total{{workflow="{workflow}"}} {count}')

        # =================================================================
        # SESSION & MESSAGE METRICS
        # =================================================================
        lines.append("# HELP claude_code_sessions_total Total sessions")
        lines.append("# TYPE claude_code_sessions_total counter")
        for project, count in self.metrics.get('sessions', {}).items():
            lines.append(f'claude_code_sessions_total{{project="{project}"}} {count}')

        lines.append("# HELP claude_code_messages_total Messages by role")
        lines.append("# TYPE claude_code_messages_total counter")
        for project, role_data in self.metrics.get('messages', {}).items():
            for role, count in role_data.items():
                lines.append(f'claude_code_messages_total{{role="{role}",project="{project}"}} {count}')

        lines.append("# HELP claude_code_responses_total Responses by status")
        lines.append("# TYPE claude_code_responses_total counter")
        for project, status_data in self.metrics.get('responses', {}).items():
            for status, count in status_data.items():
                lines.append(f'claude_code_responses_total{{status="{status}",project="{project}"}} {count}')

        lines.append("# HELP claude_code_last_activity_timestamp Last activity time")
        lines.append("# TYPE claude_code_last_activity_timestamp gauge")
        for project, ts in self.metrics.get('last_activity', {}).items():
            lines.append(f'claude_code_last_activity_timestamp{{project="{project}"}} {ts}')

        # =================================================================
        # TOOL USAGE METRICS
        # =================================================================
        lines.append("# HELP claude_code_tools_total Tool usage count")
        lines.append("# TYPE claude_code_tools_total counter")
        for project, tool_data in self.metrics.get('tools', {}).items():
            for tool, count in tool_data.items():
                lines.append(f'claude_code_tools_total{{tool="{tool}",project="{project}"}} {count}')

        # =================================================================
        # OPTIMIZATION METRICS
        # =================================================================
        lines.append("# HELP claude_code_cache_hit_rate Average cache hit rate (0-1)")
        lines.append("# TYPE claude_code_cache_hit_rate gauge")
        for project, rates in self.metrics.get('cache_hit_rate', {}).items():
            if rates:
                avg_rate = sum(rates) / len(rates)
                lines.append(f'claude_code_cache_hit_rate{{project="{project}"}} {avg_rate:.4f}')

        lines.append("# HELP claude_code_model_switches_total Sessions with model switches")
        lines.append("# TYPE claude_code_model_switches_total counter")
        for project, count in self.metrics.get('model_switches', {}).items():
            lines.append(f'claude_code_model_switches_total{{project="{project}"}} {count}')

        lines.append("# HELP claude_code_avg_output_tokens Average output tokens per response")
        lines.append("# TYPE claude_code_avg_output_tokens gauge")
        for project, token_list in self.metrics.get('avg_tokens_per_message', {}).items():
            if token_list:
                avg = sum(token_list) / len(token_list)
                lines.append(f'claude_code_avg_output_tokens{{project="{project}"}} {avg:.2f}')

        # =================================================================
        # HOURLY DISTRIBUTION
        # =================================================================
        lines.append("# HELP claude_code_hourly_tokens Token usage by hour of day")
        lines.append("# TYPE claude_code_hourly_tokens gauge")
        for hour, type_data in self.metrics.get('hourly_usage', {}).items():
            for token_type, count in type_data.items():
                lines.append(f'claude_code_hourly_tokens{{hour="{hour}",type="{token_type}"}} {count}')

        # =================================================================
        # INSIGHTS COUNT
        # =================================================================
        lines.append("# HELP claude_code_optimization_insights_total Number of optimization insights")
        lines.append("# TYPE claude_code_optimization_insights_total gauge")
        severity_counts = defaultdict(int)
        for insight in self.optimization_insights:
            severity_counts[insight['severity']] += 1
        for severity, count in severity_counts.items():
            lines.append(f'claude_code_optimization_insights_total{{severity="{severity}"}} {count}')

        # Exporter metadata
        lines.append("# HELP claude_code_exporter_last_scan_timestamp Last scan time")
        lines.append("# TYPE claude_code_exporter_last_scan_timestamp gauge")
        if self.last_scan:
            lines.append(f'claude_code_exporter_last_scan_timestamp {self.last_scan}')

        return '\n'.join(lines) + '\n'

    def get_insights_json(self) -> str:
        """Return optimization insights as JSON."""
        return json.dumps({
            'insights': self.optimization_insights,
            'generated_at': datetime.now().isoformat(),
            'total_insights': len(self.optimization_insights)
        }, indent=2)


class MetricsHandlerPro(BaseHTTPRequestHandler):
    """HTTP handler with additional endpoints."""

    collector = None

    def log_message(self, format, *args):
        logger.debug(f"HTTP: {args[0]}")

    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.collector.scan_all_projects()
            metrics = self.collector.format_prometheus_metrics()
            self.wfile.write(metrics.encode('utf-8'))

        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            health = {
                "status": "healthy",
                "version": "pro",
                "last_scan": self.collector.last_scan,
                "projects_dir": str(self.collector.projects_dir),
                "insights_count": len(self.collector.optimization_insights)
            }
            self.wfile.write(json.dumps(health).encode('utf-8'))

        elif self.path == '/insights':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(self.collector.get_insights_json().encode('utf-8'))

        elif self.path == '/summary':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            metrics = self.collector.metrics

            # Calculate totals
            total_sent = sum(
                sum(model_data.values())
                for model_data in metrics.get('tokens_sent', {}).values()
            )
            total_received = sum(
                sum(model_data.values())
                for model_data in metrics.get('tokens_received', {}).values()
            )
            total_cached = sum(
                sum(model_data.values())
                for model_data in metrics.get('tokens_cached', {}).values()
            )
            total_cost = sum(
                sum(model_data.values())
                for model_data in metrics.get('cost_monthly', {}).values()
            )
            total_savings = sum(metrics.get('cost_saved_cache', {}).values())

            summary = {
                "token_flow": {
                    "sent_to_claude": total_sent,
                    "received_from_claude": total_received,
                    "from_cache": total_cached,
                    "cache_efficiency": f"{(total_cached / (total_sent + total_cached) * 100):.1f}%" if (total_sent + total_cached) > 0 else "0%"
                },
                "costs": {
                    "this_month": f"${total_cost:.2f}",
                    "saved_via_cache": f"${total_savings:.2f}",
                    "budget_remaining": f"${max(0, MONTHLY_BUDGET - total_cost):.2f}"
                },
                "top_commands": dict(sorted(
                    metrics.get('atlas_commands', {}).items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]),
                "top_workflows": dict(sorted(
                    metrics.get('workflows', {}).items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]),
                "insights_count": len(self.collector.optimization_insights)
            }
            self.wfile.write(json.dumps(summary, indent=2).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()


def main():
    projects_dir = os.environ.get('CLAUDE_PROJECTS_DIR', os.path.expanduser('~/.claude/projects'))
    atlas_logs = os.environ.get('ATLAS_LOGS_DIR', None)
    port = int(os.environ.get('METRICS_PORT', '9091'))

    logger.info("Starting Claude Code Usage Exporter PRO")
    logger.info(f"  Projects directory: {projects_dir}")
    logger.info(f"  ATLAS logs: {atlas_logs or 'Not configured'}")
    logger.info(f"  Metrics port: {port}")
    logger.info(f"  Monthly budget: ${MONTHLY_BUDGET:.2f}")

    collector = MetricsCollectorPro(projects_dir, atlas_logs)
    MetricsHandlerPro.collector = collector

    collector.scan_all_projects()
    logger.info(f"Initial scan complete. Found {len(collector.metrics.get('sessions', {}))} projects")
    logger.info(f"Generated {len(collector.optimization_insights)} optimization insights")

    server = HTTPServer(('0.0.0.0', port), MetricsHandlerPro)
    logger.info(f"Serving metrics on http://0.0.0.0:{port}")
    logger.info(f"  /metrics  - Prometheus metrics")
    logger.info(f"  /health   - Health check")
    logger.info(f"  /insights - Optimization insights (JSON)")
    logger.info(f"  /summary  - Quick summary (JSON)")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.shutdown()


if __name__ == '__main__':
    main()
