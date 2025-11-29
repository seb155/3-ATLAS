"""
Shell Tools

Tools for executing shell commands.
"""

from typing import Dict, Any, Optional
import asyncio
import logging

from .base import Tool

logger = logging.getLogger(__name__)

# Whitelisted commands that are generally safe
SAFE_COMMANDS = {
    'ls', 'dir', 'pwd', 'cd', 'cat', 'head', 'tail', 'wc',
    'grep', 'find', 'which', 'whereis', 'file', 'stat',
    'git', 'npm', 'yarn', 'pnpm', 'pip', 'python', 'node',
    'pytest', 'jest', 'ruff', 'black', 'mypy', 'eslint',
    'docker', 'docker-compose', 'make', 'cargo', 'go'
}

# Blocked patterns (security)
BLOCKED_PATTERNS = [
    'rm -rf /',
    'rm -rf ~',
    'rm -rf *',
    ':(){:|:&};:',  # Fork bomb
    'mkfs',
    'dd if=',
    '> /dev/',
    'chmod 777',
    'curl | sh',
    'wget | sh',
    'eval',
    '`',  # Backtick execution
    '$(',  # Command substitution (be careful)
]


class RunCommandTool(Tool):
    """Tool for running shell commands."""

    def __init__(self, repo_path: str, timeout: int = 60):
        self.repo_path = repo_path
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "run_command"

    @property
    def description(self) -> str:
        return "Execute a shell command. Use for running tests, linters, git commands, etc."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": f"Timeout in seconds (default: {self.timeout})"
                }
            },
            "required": ["command"]
        }

    async def execute(
        self,
        command: str,
        timeout: Optional[int] = None
    ) -> str:
        """Execute shell command."""
        timeout = timeout or self.timeout

        # Security checks
        security_result = self._security_check(command)
        if security_result:
            return security_result

        logger.info(f"Executing command: {command}")

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.repo_path
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return f"ERROR: Command timed out after {timeout}s"

            output = ""
            if stdout:
                output += stdout.decode('utf-8', errors='replace')
            if stderr:
                if output:
                    output += "\n--- STDERR ---\n"
                output += stderr.decode('utf-8', errors='replace')

            if not output:
                output = "(no output)"

            # Truncate if too long
            if len(output) > 10000:
                output = output[:10000] + "\n... (output truncated)"

            # Add exit code
            if process.returncode != 0:
                output = f"Exit code: {process.returncode}\n\n{output}"

            return output

        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return f"ERROR: {e}"

    def _security_check(self, command: str) -> Optional[str]:
        """Check command for security issues."""
        command_lower = command.lower()

        # Check blocked patterns
        for pattern in BLOCKED_PATTERNS:
            if pattern.lower() in command_lower:
                return f"ERROR: Blocked command pattern: {pattern}"

        # Check if base command is whitelisted
        base_cmd = command.split()[0] if command.split() else ""
        base_cmd = base_cmd.split('/')[-1]  # Handle paths like /usr/bin/git

        # Allow piped commands if first command is safe
        if '|' in command:
            first_cmd = command.split('|')[0].strip().split()[0]
            first_cmd = first_cmd.split('/')[-1]
            if first_cmd not in SAFE_COMMANDS:
                logger.warning(f"Non-whitelisted command: {first_cmd}")
                # Just warn, don't block - allow with caution

        return None


class GitTool(Tool):
    """Specialized tool for git operations."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    @property
    def name(self) -> str:
        return "git"

    @property
    def description(self) -> str:
        return "Execute git commands. Supports status, diff, log, add, commit, etc."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "subcommand": {
                    "type": "string",
                    "description": "Git subcommand (status, diff, log, add, commit, etc.)"
                },
                "args": {
                    "type": "string",
                    "description": "Additional arguments for the git command"
                }
            },
            "required": ["subcommand"]
        }

    async def execute(self, subcommand: str, args: str = "") -> str:
        """Execute git command."""
        # Blocked git operations
        blocked = ['push --force', 'reset --hard', 'clean -fd']
        full_cmd = f"{subcommand} {args}".strip()

        for b in blocked:
            if b in full_cmd:
                return f"ERROR: Blocked git operation: {b}"

        command = f"git {subcommand} {args}".strip()

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.repo_path
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=30
            )

            output = ""
            if stdout:
                output += stdout.decode('utf-8', errors='replace')
            if stderr:
                output += stderr.decode('utf-8', errors='replace')

            return output or "(no output)"

        except asyncio.TimeoutError:
            return "ERROR: Git command timed out"
        except Exception as e:
            return f"ERROR: {e}"
