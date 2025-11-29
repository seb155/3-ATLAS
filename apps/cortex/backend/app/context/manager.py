"""
Context Manager

Assembles context from blocks, keywords, and memory layers.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import logging

from .blocks import ContextBlock, ContextType
from .memory import MemorySystem

logger = logging.getLogger(__name__)


@dataclass
class AssembledContext:
    """Result of context assembly."""
    blocks: List[ContextBlock]
    keywords: Set[str]
    concepts: Set[str]
    repo_map: str
    blocks_summary: str
    total_tokens: int
    hot_tokens: int
    warm_tokens: int
    cold_tokens: int
    estimated_cost: float


class ContextManager:
    """
    Manages context assembly from multiple sources.

    Responsibilities:
    - Extract keywords from task descriptions
    - Expand keywords to related concepts
    - Find relevant context blocks
    - Assemble context within token budget
    - Track context usage for optimization
    """

    def __init__(
        self,
        memory: MemorySystem,
        max_tokens: int = 100000
    ):
        self.memory = memory
        self.max_tokens = max_tokens
        self.blocks: Dict[str, ContextBlock] = {}

    def register_block(self, block: ContextBlock):
        """Register a context block."""
        self.blocks[block.id] = block
        logger.info(f"Registered context block: {block.name} ({block.type.value})")

    async def assemble(
        self,
        task: str,
        block_ids: List[str] = None,
        explicit_keywords: List[str] = None
    ) -> AssembledContext:
        """
        Assemble context for a task.

        Args:
            task: Task description
            block_ids: Optional explicit block IDs to include
            explicit_keywords: Optional explicit keywords

        Returns:
            AssembledContext with all relevant context
        """
        # 1. Extract keywords from task
        task_keywords = self._extract_keywords(task)
        all_keywords = set(task_keywords + (explicit_keywords or []))

        # 2. Expand to related concepts
        concepts = self._expand_to_concepts(all_keywords)

        # 3. Get explicitly requested blocks
        explicit_blocks = [
            self.blocks[bid] for bid in (block_ids or [])
            if bid in self.blocks
        ]

        # 4. Find relevant blocks by keywords
        keyword_blocks = self._find_blocks_by_keywords(all_keywords | concepts)

        # 5. Get from memory layers
        hot_context = await self.memory.get_hot()
        warm_context = await self.memory.search_warm(task)
        cold_context = await self.memory.search_cold(task) if len(hot_context) + len(warm_context) < 5 else []

        # 6. Score and combine
        all_blocks = explicit_blocks + keyword_blocks
        scored_blocks = self._score_relevance(all_blocks, task, all_keywords)

        # 7. Fit to token budget
        final_blocks, token_counts = self._fit_to_budget(scored_blocks)

        # 8. Generate summaries
        repo_map = self._generate_repo_map()
        blocks_summary = self._generate_blocks_summary(final_blocks)

        return AssembledContext(
            blocks=final_blocks,
            keywords=all_keywords,
            concepts=concepts,
            repo_map=repo_map,
            blocks_summary=blocks_summary,
            total_tokens=sum(token_counts.values()),
            hot_tokens=token_counts.get("hot", 0),
            warm_tokens=token_counts.get("warm", 0),
            cold_tokens=token_counts.get("cold", 0),
            estimated_cost=self._estimate_cost(sum(token_counts.values()))
        )

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction - could use NLP for better results
        import re

        # Remove common words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                      "being", "have", "has", "had", "do", "does", "did", "will",
                      "would", "could", "should", "may", "might", "must", "shall",
                      "can", "need", "dare", "ought", "used", "to", "of", "in",
                      "for", "on", "with", "at", "by", "from", "as", "into",
                      "through", "during", "before", "after", "above", "below",
                      "between", "under", "again", "further", "then", "once",
                      "and", "but", "or", "nor", "so", "yet", "both", "either",
                      "neither", "not", "only", "own", "same", "than", "too",
                      "very", "just", "also", "now", "here", "there", "when",
                      "where", "why", "how", "all", "each", "every", "any",
                      "some", "no", "this", "that", "these", "those", "i", "you",
                      "he", "she", "it", "we", "they", "me", "him", "her", "us",
                      "them", "my", "your", "his", "its", "our", "their"}

        # Extract words
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', text.lower())

        # Filter and return unique keywords
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return list(set(keywords))

    def _expand_to_concepts(self, keywords: Set[str]) -> Set[str]:
        """Expand keywords to related concepts."""
        # Simple concept mapping - could use embeddings or ontology
        concept_map = {
            "api": {"endpoint", "rest", "http", "request", "response"},
            "user": {"authentication", "auth", "login", "account"},
            "database": {"sql", "query", "table", "model", "orm"},
            "test": {"pytest", "unittest", "mock", "assert"},
            "error": {"exception", "try", "catch", "handle"},
            "file": {"read", "write", "path", "io"},
            "function": {"def", "method", "call", "return"},
            "class": {"object", "instance", "init", "self"},
        }

        concepts = set()
        for keyword in keywords:
            if keyword in concept_map:
                concepts.update(concept_map[keyword])

        return concepts

    def _find_blocks_by_keywords(self, keywords: Set[str]) -> List[ContextBlock]:
        """Find context blocks matching keywords."""
        matching = []
        for block in self.blocks.values():
            block_keywords = set(k.lower() for k in block.keywords)
            if block_keywords & keywords:
                matching.append(block)
        return matching

    def _score_relevance(
        self,
        blocks: List[ContextBlock],
        task: str,
        keywords: Set[str]
    ) -> List[tuple]:
        """Score blocks by relevance to task."""
        scored = []
        for block in blocks:
            # Simple scoring based on keyword overlap
            block_keywords = set(k.lower() for k in block.keywords)
            overlap = len(block_keywords & keywords)
            score = overlap / max(len(keywords), 1)
            scored.append((score, block))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored

    def _fit_to_budget(
        self,
        scored_blocks: List[tuple]
    ) -> tuple:
        """Fit blocks to token budget."""
        final_blocks = []
        token_counts = {"hot": 0, "warm": 0, "cold": 0}
        total = 0

        for score, block in scored_blocks:
            if total + block.token_count <= self.max_tokens:
                final_blocks.append(block)
                total += block.token_count
                # Categorize by score
                if score > 0.7:
                    token_counts["hot"] += block.token_count
                elif score > 0.3:
                    token_counts["warm"] += block.token_count
                else:
                    token_counts["cold"] += block.token_count

        return final_blocks, token_counts

    def _generate_repo_map(self) -> str:
        """Generate repository map."""
        # TODO: Implement actual repo map generation
        return "Repository map not yet implemented"

    def _generate_blocks_summary(self, blocks: List[ContextBlock]) -> str:
        """Generate summary of included blocks."""
        if not blocks:
            return "No context blocks loaded"

        lines = ["Loaded context blocks:"]
        for block in blocks:
            lines.append(f"- [{block.type.value}] {block.name} ({block.token_count} tokens)")
        return "\n".join(lines)

    def _estimate_cost(self, tokens: int) -> float:
        """Estimate cost based on token count."""
        # Rough estimate: $0.01 per 1K tokens
        return tokens * 0.00001
