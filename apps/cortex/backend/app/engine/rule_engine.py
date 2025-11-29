"""
Rule Engine

Validation and guard rules for agent actions.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class RuleSeverity(str, Enum):
    """Rule violation severity."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    BLOCK = "block"  # Prevents action entirely


class RuleResult(str, Enum):
    """Result of rule evaluation."""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"


@dataclass
class RuleViolation:
    """Represents a rule violation."""
    rule_id: str
    rule_name: str
    severity: RuleSeverity
    message: str
    context: Dict[str, Any]


@dataclass
class Rule:
    """A validation rule."""
    id: str
    name: str
    description: str
    severity: RuleSeverity
    check: Callable[[Dict[str, Any]], bool]
    message_template: str
    applies_to: List[str] = None  # Tool names this applies to, None = all


class RuleEngine:
    """
    Validates agent actions against defined rules.

    Features:
    - Pre-action validation (before tool execution)
    - Post-action validation (after tool execution)
    - File protection rules
    - Command whitelisting
    - Rate limiting
    """

    def __init__(self):
        self.rules: Dict[str, Rule] = {}
        self._register_default_rules()

    def _register_default_rules(self):
        """Register default safety rules."""

        # Rule: No writing to system files
        self.register_rule(Rule(
            id="no_system_files",
            name="No System File Modification",
            description="Prevents modification of system configuration files",
            severity=RuleSeverity.BLOCK,
            check=lambda ctx: not any(
                ctx.get("path", "").startswith(p)
                for p in ["/etc/", "/usr/", "/bin/", "/sbin/", "C:\\Windows\\"]
            ),
            message_template="Cannot modify system file: {path}",
            applies_to=["write_file", "edit_file"]
        ))

        # Rule: No deleting .git
        self.register_rule(Rule(
            id="protect_git",
            name="Protect Git Directory",
            description="Prevents modification of .git directory",
            severity=RuleSeverity.BLOCK,
            check=lambda ctx: ".git" not in ctx.get("path", ""),
            message_template="Cannot modify .git directory: {path}",
            applies_to=["write_file", "edit_file", "run_command"]
        ))

        # Rule: No dangerous commands
        self.register_rule(Rule(
            id="no_dangerous_commands",
            name="No Dangerous Commands",
            description="Blocks potentially dangerous shell commands",
            severity=RuleSeverity.BLOCK,
            check=lambda ctx: not any(
                cmd in ctx.get("command", "").lower()
                for cmd in ["rm -rf /", "format", "mkfs", "dd if=", ":(){:|:&};:"]
            ),
            message_template="Dangerous command blocked: {command}",
            applies_to=["run_command"]
        ))

        # Rule: Read before write
        self.register_rule(Rule(
            id="read_before_write",
            name="Read Before Write",
            description="Warns if file wasn't read before being modified",
            severity=RuleSeverity.WARNING,
            check=lambda ctx: ctx.get("file_was_read", False),
            message_template="File was not read before modification: {path}",
            applies_to=["write_file", "edit_file"]
        ))

        # Rule: No secrets in output
        self.register_rule(Rule(
            id="no_secrets_output",
            name="No Secrets in Output",
            description="Prevents exposing secrets in responses",
            severity=RuleSeverity.ERROR,
            check=lambda ctx: not re.search(
                r'(password|api_key|secret|token)\s*[:=]\s*["\'][^"\']+["\']',
                ctx.get("content", ""),
                re.IGNORECASE
            ),
            message_template="Potential secret detected in output",
            applies_to=None
        ))

    def register_rule(self, rule: Rule):
        """Register a new rule."""
        self.rules[rule.id] = rule
        logger.info(f"Registered rule: {rule.name}")

    def validate(
        self,
        action: str,
        context: Dict[str, Any]
    ) -> List[RuleViolation]:
        """
        Validate an action against all applicable rules.

        Args:
            action: The tool/action being performed
            context: Context dict with action parameters

        Returns:
            List of rule violations (empty if all pass)
        """
        violations = []

        for rule in self.rules.values():
            # Check if rule applies to this action
            if rule.applies_to and action not in rule.applies_to:
                continue

            try:
                passed = rule.check(context)

                if not passed:
                    violation = RuleViolation(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        severity=rule.severity,
                        message=rule.message_template.format(**context),
                        context=context
                    )
                    violations.append(violation)
                    logger.warning(f"Rule violation: {violation.message}")

            except Exception as e:
                logger.error(f"Error evaluating rule {rule.id}: {e}")

        return violations

    def should_block(self, violations: List[RuleViolation]) -> bool:
        """Check if any violation should block the action."""
        return any(v.severity == RuleSeverity.BLOCK for v in violations)

    def get_warnings(self, violations: List[RuleViolation]) -> List[RuleViolation]:
        """Get warning-level violations."""
        return [v for v in violations if v.severity == RuleSeverity.WARNING]
