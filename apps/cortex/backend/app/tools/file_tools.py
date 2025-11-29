"""
File Tools

Tools for reading, writing, and editing files.
"""

from pathlib import Path
from typing import Optional, Dict, Any

from .base import Tool


class ReadFileTool(Tool):
    """Tool for reading file contents."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file. Use this to understand existing code before modifying it."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to the file from repository root"
                },
                "start_line": {
                    "type": "integer",
                    "description": "Optional: Start reading from this line (1-indexed)"
                },
                "end_line": {
                    "type": "integer",
                    "description": "Optional: Stop reading at this line (1-indexed)"
                }
            },
            "required": ["path"]
        }

    async def execute(
        self,
        path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None
    ) -> str:
        """Read file contents."""
        full_path = self.repo_path / path

        # Security check
        try:
            full_path = full_path.resolve()
            if not str(full_path).startswith(str(self.repo_path.resolve())):
                return f"ERROR: Access denied - path outside repository: {path}"
        except Exception:
            return f"ERROR: Invalid path: {path}"

        if not full_path.exists():
            return f"ERROR: File not found: {path}"

        if full_path.is_dir():
            return f"ERROR: Path is a directory: {path}"

        try:
            content = full_path.read_text(errors='replace')
            lines = content.split('\n')

            # Apply line filtering
            if start_line is not None:
                start_idx = max(0, start_line - 1)
                end_idx = end_line if end_line else len(lines)
                lines = lines[start_idx:end_idx]

                # Add line numbers
                result_lines = []
                for i, line in enumerate(lines, start=start_line or 1):
                    result_lines.append(f"{i:4d} | {line}")
                return '\n'.join(result_lines)

            return content

        except Exception as e:
            return f"ERROR: Failed to read file: {e}"


class WriteFileTool(Tool):
    """Tool for writing/creating files."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write or replace the entire contents of a file. Creates parent directories if needed."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to the file"
                },
                "content": {
                    "type": "string",
                    "description": "Complete new content for the file"
                }
            },
            "required": ["path", "content"]
        }

    async def execute(self, path: str, content: str) -> str:
        """Write file contents."""
        full_path = self.repo_path / path

        # Security check
        try:
            full_path = full_path.resolve()
            if not str(full_path).startswith(str(self.repo_path.resolve())):
                return f"ERROR: Access denied - path outside repository: {path}"
        except Exception:
            return f"ERROR: Invalid path: {path}"

        # Check for protected paths
        protected = ['.git', '__pycache__', 'node_modules']
        if any(p in path for p in protected):
            return f"ERROR: Cannot write to protected path: {path}"

        try:
            # Create parent directories
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            full_path.write_text(content)

            return f"Successfully wrote {len(content)} characters to {path}"

        except Exception as e:
            return f"ERROR: Failed to write file: {e}"


class EditFileTool(Tool):
    """Tool for editing specific parts of files."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    @property
    def name(self) -> str:
        return "edit_file"

    @property
    def description(self) -> str:
        return "Edit a specific part of a file by replacing exact text. More precise than write_file for modifications."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to the file"
                },
                "old_content": {
                    "type": "string",
                    "description": "Exact text to replace (must be unique in the file)"
                },
                "new_content": {
                    "type": "string",
                    "description": "New text to replace it with"
                }
            },
            "required": ["path", "old_content", "new_content"]
        }

    async def execute(self, path: str, old_content: str, new_content: str) -> str:
        """Edit file by replacing text."""
        full_path = self.repo_path / path

        # Security check
        try:
            full_path = full_path.resolve()
            if not str(full_path).startswith(str(self.repo_path.resolve())):
                return f"ERROR: Access denied - path outside repository: {path}"
        except Exception:
            return f"ERROR: Invalid path: {path}"

        if not full_path.exists():
            return f"ERROR: File not found: {path}"

        try:
            content = full_path.read_text()

            # Check that old_content exists
            if old_content not in content:
                return f"ERROR: Text to replace not found in {path}"

            # Check uniqueness
            count = content.count(old_content)
            if count > 1:
                return f"ERROR: Text appears {count} times in file. Be more specific."

            # Replace
            new_file_content = content.replace(old_content, new_content)
            full_path.write_text(new_file_content)

            return f"Successfully edited {path}"

        except Exception as e:
            return f"ERROR: Failed to edit file: {e}"
