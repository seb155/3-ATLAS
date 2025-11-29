"""
Base Tool Class

Abstract interface for agent tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Result of tool execution."""
    success: bool
    output: str
    error: str = None
    metadata: Dict[str, Any] = None


class Tool(ABC):
    """
    Abstract base class for agent tools.

    Tools are the "hands" of the agent - they allow it to interact
    with the filesystem, execute commands, search code, etc.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name used in function calls."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description for the LLM."""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON Schema for tool input."""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """
        Execute the tool.

        Args:
            **kwargs: Tool-specific arguments

        Returns:
            String result for the LLM
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dict for API."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }
