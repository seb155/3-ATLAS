"""Tests for CORTEX tools."""

import pytest
from pathlib import Path
import tempfile

from app.tools.file_tools import ReadFileTool, WriteFileTool, EditFileTool


@pytest.fixture
def temp_repo():
    """Create a temporary repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some test files
        Path(tmpdir, "test.py").write_text("def hello():\n    return 'world'\n")
        Path(tmpdir, "subdir").mkdir()
        Path(tmpdir, "subdir", "nested.txt").write_text("nested content")
        yield tmpdir


class TestReadFileTool:
    @pytest.mark.asyncio
    async def test_read_existing_file(self, temp_repo):
        tool = ReadFileTool(temp_repo)
        result = await tool.execute(path="test.py")
        assert "def hello():" in result
        assert "return 'world'" in result

    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self, temp_repo):
        tool = ReadFileTool(temp_repo)
        result = await tool.execute(path="nonexistent.py")
        assert "ERROR" in result
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_read_with_line_range(self, temp_repo):
        tool = ReadFileTool(temp_repo)
        result = await tool.execute(path="test.py", start_line=1, end_line=1)
        assert "hello" in result
        assert "world" not in result

    @pytest.mark.asyncio
    async def test_path_traversal_blocked(self, temp_repo):
        tool = ReadFileTool(temp_repo)
        result = await tool.execute(path="../../../etc/passwd")
        assert "ERROR" in result


class TestWriteFileTool:
    @pytest.mark.asyncio
    async def test_write_new_file(self, temp_repo):
        tool = WriteFileTool(temp_repo)
        result = await tool.execute(path="new_file.py", content="# New file")
        assert "Successfully" in result
        assert Path(temp_repo, "new_file.py").read_text() == "# New file"

    @pytest.mark.asyncio
    async def test_write_creates_directories(self, temp_repo):
        tool = WriteFileTool(temp_repo)
        result = await tool.execute(path="new/nested/file.py", content="content")
        assert "Successfully" in result
        assert Path(temp_repo, "new/nested/file.py").exists()

    @pytest.mark.asyncio
    async def test_write_to_git_blocked(self, temp_repo):
        tool = WriteFileTool(temp_repo)
        result = await tool.execute(path=".git/config", content="malicious")
        assert "ERROR" in result


class TestEditFileTool:
    @pytest.mark.asyncio
    async def test_edit_existing_file(self, temp_repo):
        tool = EditFileTool(temp_repo)
        result = await tool.execute(
            path="test.py",
            old_content="return 'world'",
            new_content="return 'CORTEX'"
        )
        assert "Successfully" in result
        content = Path(temp_repo, "test.py").read_text()
        assert "CORTEX" in content
        assert "world" not in content

    @pytest.mark.asyncio
    async def test_edit_nonexistent_text(self, temp_repo):
        tool = EditFileTool(temp_repo)
        result = await tool.execute(
            path="test.py",
            old_content="this does not exist",
            new_content="replacement"
        )
        assert "ERROR" in result
        assert "not found" in result.lower()
