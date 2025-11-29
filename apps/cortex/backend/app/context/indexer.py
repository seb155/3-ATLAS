"""
Code Indexer

Indexes codebases for RAG retrieval.
"""

from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class CodeChunk:
    """A chunk of code for indexing."""
    id: str
    file_path: str
    chunk_type: str  # file, function, class, module
    name: str
    content: str
    start_line: int
    end_line: int
    symbols: List[str]
    dependencies: List[str]
    embedding: Optional[List[float]] = None


class CodeIndexer:
    """
    Indexes codebases for semantic search.

    Features:
    - File-level and function-level chunking
    - Symbol extraction
    - Dependency tracking
    - Embedding generation
    """

    # File extensions to index
    CODE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx',
        '.java', '.go', '.rs', '.rb', '.php',
        '.c', '.cpp', '.h', '.hpp', '.cs',
        '.swift', '.kt', '.scala', '.sql'
    }

    # Directories to skip
    SKIP_DIRS = {
        '.git', 'node_modules', '__pycache__', '.venv', 'venv',
        'dist', 'build', '.next', '.nuxt', 'target', 'vendor'
    }

    def __init__(
        self,
        repo_path: str,
        embedding_provider=None,
        chunk_size: int = 2000
    ):
        self.repo_path = Path(repo_path)
        self.embedding_provider = embedding_provider
        self.chunk_size = chunk_size
        self.chunks: Dict[str, CodeChunk] = {}

    async def index(self) -> Dict[str, Any]:
        """
        Index the entire repository.

        Returns:
            Summary of indexed content
        """
        logger.info(f"Indexing repository: {self.repo_path}")

        stats = {
            "files_indexed": 0,
            "chunks_created": 0,
            "total_lines": 0,
            "languages": set()
        }

        for file_path in self._walk_files():
            try:
                chunks = await self._index_file(file_path)
                for chunk in chunks:
                    self.chunks[chunk.id] = chunk
                    stats["chunks_created"] += 1

                stats["files_indexed"] += 1
                stats["total_lines"] += sum(c.end_line - c.start_line for c in chunks)
                stats["languages"].add(file_path.suffix)

            except Exception as e:
                logger.warning(f"Failed to index {file_path}: {e}")

        stats["languages"] = list(stats["languages"])
        logger.info(f"Indexing complete: {stats}")
        return stats

    async def _index_file(self, file_path: Path) -> List[CodeChunk]:
        """Index a single file."""
        relative_path = file_path.relative_to(self.repo_path)
        content = file_path.read_text(errors='ignore')

        # For MVP: one chunk per file
        # TODO: Use tree-sitter for function/class level chunking
        chunk_id = self._generate_chunk_id(str(relative_path), content)

        # Extract basic symbols (function/class names)
        symbols = self._extract_symbols(content, file_path.suffix)

        # Extract imports/dependencies
        dependencies = self._extract_dependencies(content, file_path.suffix)

        chunk = CodeChunk(
            id=chunk_id,
            file_path=str(relative_path),
            chunk_type="file",
            name=file_path.name,
            content=content[:self.chunk_size * 4],  # Limit content size
            start_line=1,
            end_line=len(content.split('\n')),
            symbols=symbols,
            dependencies=dependencies
        )

        # Generate embedding if provider available
        if self.embedding_provider:
            chunk.embedding = await self.embedding_provider.embed(content[:8000])

        return [chunk]

    def _walk_files(self):
        """Walk repository and yield code files."""
        for path in self.repo_path.rglob('*'):
            # Skip directories
            if path.is_dir():
                continue

            # Skip non-code files
            if path.suffix not in self.CODE_EXTENSIONS:
                continue

            # Skip excluded directories
            if any(skip in path.parts for skip in self.SKIP_DIRS):
                continue

            yield path

    def _generate_chunk_id(self, path: str, content: str) -> str:
        """Generate unique chunk ID."""
        hash_input = f"{path}:{content}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def _extract_symbols(self, content: str, extension: str) -> List[str]:
        """Extract symbol names from code."""
        symbols = []
        lines = content.split('\n')

        if extension == '.py':
            for line in lines:
                line = line.strip()
                if line.startswith('def '):
                    name = line[4:].split('(')[0].strip()
                    symbols.append(name)
                elif line.startswith('class '):
                    name = line[6:].split('(')[0].split(':')[0].strip()
                    symbols.append(name)

        elif extension in ('.js', '.ts', '.jsx', '.tsx'):
            import re
            # Function declarations
            for match in re.finditer(r'function\s+(\w+)', content):
                symbols.append(match.group(1))
            # Arrow functions assigned to variables
            for match in re.finditer(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(', content):
                symbols.append(match.group(1))
            # Class declarations
            for match in re.finditer(r'class\s+(\w+)', content):
                symbols.append(match.group(1))

        return symbols

    def _extract_dependencies(self, content: str, extension: str) -> List[str]:
        """Extract import/dependency names."""
        dependencies = []
        lines = content.split('\n')

        if extension == '.py':
            for line in lines:
                line = line.strip()
                if line.startswith('import '):
                    deps = line[7:].split(',')
                    for dep in deps:
                        dependencies.append(dep.split(' as ')[0].strip())
                elif line.startswith('from '):
                    module = line.split(' import ')[0][5:].strip()
                    dependencies.append(module)

        elif extension in ('.js', '.ts', '.jsx', '.tsx'):
            import re
            for match in re.finditer(r"(?:import|from)\s+['\"]([^'\"]+)['\"]", content):
                dependencies.append(match.group(1))
            for match in re.finditer(r"require\(['\"]([^'\"]+)['\"]\)", content):
                dependencies.append(match.group(1))

        return dependencies

    def generate_repo_map(self) -> str:
        """Generate a text map of the repository."""
        lines = [f"# Repository: {self.repo_path.name}", ""]

        # Group by directory
        by_dir: Dict[str, List[CodeChunk]] = {}
        for chunk in self.chunks.values():
            dir_path = str(Path(chunk.file_path).parent)
            if dir_path not in by_dir:
                by_dir[dir_path] = []
            by_dir[dir_path].append(chunk)

        for dir_path in sorted(by_dir.keys()):
            lines.append(f"## {dir_path}/")
            for chunk in sorted(by_dir[dir_path], key=lambda c: c.file_path):
                symbols_str = ", ".join(chunk.symbols[:5])
                if len(chunk.symbols) > 5:
                    symbols_str += f", ... (+{len(chunk.symbols) - 5})"
                lines.append(f"  - {chunk.name}: {symbols_str}")
            lines.append("")

        return "\n".join(lines)

    def search(self, query: str, limit: int = 5) -> List[CodeChunk]:
        """Simple keyword search (for MVP without vector store)."""
        query_lower = query.lower()
        scored = []

        for chunk in self.chunks.values():
            score = 0
            # Check symbols
            for symbol in chunk.symbols:
                if query_lower in symbol.lower():
                    score += 2
            # Check file path
            if query_lower in chunk.file_path.lower():
                score += 1
            # Check content
            if query_lower in chunk.content.lower():
                score += 0.5

            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored[:limit]]
