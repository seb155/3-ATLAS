"""
Context Blocks

Definitions and management of context blocks.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ContextType(str, Enum):
    """Types of context blocks."""
    PROFILE = "PROFILE"         # Personal/user preferences
    PROJECT = "PROJECT"         # Project structure and conventions
    CLIENT = "CLIENT"           # Client-specific context
    PRODUCT = "PRODUCT"         # Product documentation
    CODEBASE = "CODEBASE"       # Indexed code
    DOCS = "DOCS"               # Documentation
    RULES = "RULES"             # Business rules
    SESSION = "SESSION"         # Current session context
    CUSTOM = "CUSTOM"           # Custom context


class SensitivityLevel(str, Enum):
    """Data sensitivity levels for routing."""
    PUBLIC = "PUBLIC"           # Can be sent to any AI
    INTERNAL = "INTERNAL"       # Trusted cloud AI only
    CONFIDENTIAL = "CONFIDENTIAL"  # Local AI only or anonymized
    SECRET = "SECRET"           # Never sent to AI


@dataclass
class ContextBlock:
    """
    A modular block of context that can be assembled for tasks.

    Context blocks are the fundamental unit of context management in CORTEX.
    They can represent various types of information (code, docs, profiles, etc.)
    and are assembled dynamically based on task requirements.
    """
    id: str
    type: ContextType
    name: str
    version: int = 1

    # Content
    content: Dict[str, Any] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)

    # Metadata
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL
    owner: Optional[str] = None
    shared_with: List[str] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Relations
    parent_id: Optional[str] = None
    linked_blocks: List[str] = field(default_factory=list)

    # Computed
    token_count: int = 0
    embedding: Optional[List[float]] = None

    def __post_init__(self):
        """Calculate token count after initialization."""
        if self.token_count == 0:
            # Rough estimate: 1 token ≈ 4 characters
            content_str = str(self.content)
            self.token_count = len(content_str) // 4

    def to_text(self) -> str:
        """Convert block to text for LLM context."""
        lines = [
            f"## {self.type.value}: {self.name}",
            ""
        ]

        for key, value in self.content.items():
            if isinstance(value, dict):
                lines.append(f"### {key}")
                for k, v in value.items():
                    lines.append(f"- {k}: {v}")
            elif isinstance(value, list):
                lines.append(f"### {key}")
                for item in value:
                    lines.append(f"- {item}")
            else:
                lines.append(f"**{key}**: {value}")
            lines.append("")

        return "\n".join(lines)

    def update(self, content: Dict[str, Any], keywords: List[str] = None):
        """Update block content and increment version."""
        self.content = content
        if keywords:
            self.keywords = keywords
        self.version += 1
        self.updated_at = datetime.utcnow()
        # Recalculate token count
        content_str = str(self.content)
        self.token_count = len(content_str) // 4


def create_profile_block(
    id: str,
    name: str,
    preferences: Dict[str, Any],
    expertise: List[str],
    sensitivity: SensitivityLevel = SensitivityLevel.CONFIDENTIAL
) -> ContextBlock:
    """Factory function to create a profile block."""
    return ContextBlock(
        id=id,
        type=ContextType.PROFILE,
        name=name,
        content={
            "preferences": preferences,
            "expertise": expertise
        },
        keywords=expertise + list(preferences.keys()),
        sensitivity=sensitivity
    )


def create_project_block(
    id: str,
    name: str,
    structure: Dict[str, Any],
    conventions: Dict[str, str],
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL
) -> ContextBlock:
    """Factory function to create a project block."""
    return ContextBlock(
        id=id,
        type=ContextType.PROJECT,
        name=name,
        content={
            "structure": structure,
            "conventions": conventions
        },
        keywords=list(structure.keys()) + list(conventions.keys()),
        sensitivity=sensitivity
    )


def create_codebase_block(
    id: str,
    name: str,
    file_path: str,
    content: str,
    symbols: List[str],
    dependencies: List[str]
) -> ContextBlock:
    """Factory function to create a codebase block."""
    return ContextBlock(
        id=id,
        type=ContextType.CODEBASE,
        name=name,
        content={
            "file_path": file_path,
            "code": content,
            "symbols": symbols,
            "dependencies": dependencies
        },
        keywords=symbols + [file_path.split("/")[-1]]
    )
