"""
Search Tools

Tools for searching the codebase.
"""

from typing import Dict, Any, Optional

from .base import Tool


class SearchCodebaseTool(Tool):
    """Tool for semantic search in the codebase."""

    def __init__(self, indexer=None):
        self.indexer = indexer

    @property
    def name(self) -> str:
        return "search_codebase"

    @property
    def description(self) -> str:
        return "Search the codebase for relevant code. Use natural language to describe what you're looking for."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What you're looking for (natural language)"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Optional: Filter by file pattern (e.g., '*.py', 'src/**/*.ts')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 5)"
                }
            },
            "required": ["query"]
        }

    async def execute(
        self,
        query: str,
        file_pattern: Optional[str] = None,
        limit: int = 5
    ) -> str:
        """Search the codebase."""
        if not self.indexer:
            return "ERROR: Code indexer not configured"

        try:
            results = self.indexer.search(query, limit=limit)

            if not results:
                return f"No results found for: {query}"

            output = [f"Found {len(results)} results for: {query}\n"]

            for i, chunk in enumerate(results, 1):
                output.append(f"--- [{i}] {chunk.file_path} ---")
                output.append(f"Symbols: {', '.join(chunk.symbols[:5])}")
                output.append(f"Lines: {chunk.start_line}-{chunk.end_line}")
                output.append("")
                # Show preview of content
                preview = chunk.content[:500]
                if len(chunk.content) > 500:
                    preview += "\n... (truncated)"
                output.append(preview)
                output.append("")

            return '\n'.join(output)

        except Exception as e:
            return f"ERROR: Search failed: {e}"


class GrepTool(Tool):
    """Tool for regex search in files."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    @property
    def name(self) -> str:
        return "grep"

    @property
    def description(self) -> str:
        return "Search for a pattern in files using regex."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Regex pattern to search for"
                },
                "path": {
                    "type": "string",
                    "description": "Path to search in (file or directory)"
                },
                "case_insensitive": {
                    "type": "boolean",
                    "description": "Ignore case (default: false)"
                }
            },
            "required": ["pattern"]
        }

    async def execute(
        self,
        pattern: str,
        path: str = ".",
        case_insensitive: bool = False
    ) -> str:
        """Execute grep search."""
        import re
        from pathlib import Path

        repo = Path(self.repo_path)
        search_path = repo / path

        flags = re.IGNORECASE if case_insensitive else 0

        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            return f"ERROR: Invalid regex: {e}"

        results = []

        if search_path.is_file():
            files = [search_path]
        else:
            files = list(search_path.rglob('*'))

        for file_path in files:
            if not file_path.is_file():
                continue
            if any(skip in str(file_path) for skip in ['.git', 'node_modules', '__pycache__']):
                continue

            try:
                content = file_path.read_text(errors='ignore')
                for i, line in enumerate(content.split('\n'), 1):
                    if regex.search(line):
                        rel_path = file_path.relative_to(repo)
                        results.append(f"{rel_path}:{i}: {line.strip()}")
                        if len(results) >= 50:
                            break
            except Exception:
                continue

            if len(results) >= 50:
                break

        if not results:
            return f"No matches found for pattern: {pattern}"

        return f"Found {len(results)} matches:\n" + '\n'.join(results[:50])
