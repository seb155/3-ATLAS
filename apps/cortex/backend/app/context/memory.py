"""
Memory System

HOT/WARM/COLD memory layers for context management.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """An entry in the memory system."""
    id: str
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    access_count: int = 0
    relevance_score: float = 0.0


class HotCache:
    """
    HOT Cache (CAG - Cache-Augmented Generation)

    Ultra-fast, always-available context:
    - Current session context
    - Recently accessed files
    - Current task context
    - Error history

    Access: O(1) instant lookup
    """

    def __init__(self, max_size: int = 50000):
        self.max_size = max_size  # Max tokens
        self.entries: OrderedDict[str, MemoryEntry] = OrderedDict()
        self.current_tokens = 0

    def put(self, key: str, content: str, metadata: Dict[str, Any] = None):
        """Add entry to hot cache."""
        token_count = len(content) // 4

        # Evict if needed
        while self.current_tokens + token_count > self.max_size and self.entries:
            _, evicted = self.entries.popitem(last=False)
            self.current_tokens -= len(evicted.content) // 4

        entry = MemoryEntry(
            id=key,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.utcnow()
        )
        self.entries[key] = entry
        self.current_tokens += token_count

        # Move to end (most recent)
        self.entries.move_to_end(key)

    def get(self, key: str) -> Optional[str]:
        """Get entry from hot cache."""
        if key in self.entries:
            entry = self.entries[key]
            entry.access_count += 1
            self.entries.move_to_end(key)
            return entry.content
        return None

    def get_all(self) -> List[MemoryEntry]:
        """Get all entries."""
        return list(self.entries.values())

    def clear(self):
        """Clear the cache."""
        self.entries.clear()
        self.current_tokens = 0


class WarmCache:
    """
    WARM Cache (Fast RAG)

    Pre-filtered context based on project scope:
    - Files in same module
    - Direct dependencies
    - Related tests
    - Associated documentation

    Access: Milliseconds (pre-indexed)
    """

    def __init__(self, max_size: int = 100000):
        self.max_size = max_size
        self.index: Dict[str, List[str]] = {}  # keyword -> entry IDs
        self.entries: Dict[str, MemoryEntry] = {}

    def add(self, entry_id: str, content: str, keywords: List[str], metadata: Dict[str, Any] = None):
        """Add entry with keyword indexing."""
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.utcnow()
        )
        self.entries[entry_id] = entry

        # Index by keywords
        for keyword in keywords:
            if keyword not in self.index:
                self.index[keyword] = []
            self.index[keyword].append(entry_id)

    def search(self, keywords: List[str], limit: int = 10) -> List[MemoryEntry]:
        """Search by keywords."""
        matching_ids = set()
        for keyword in keywords:
            if keyword.lower() in self.index:
                matching_ids.update(self.index[keyword.lower()])

        results = [self.entries[eid] for eid in matching_ids if eid in self.entries]
        results.sort(key=lambda x: x.access_count, reverse=True)
        return results[:limit]


class ColdStorage:
    """
    COLD Storage (Full RAG)

    Complete codebase index:
    - All indexed files
    - Git history
    - Full documentation
    - External references

    Access: Seconds (semantic search)
    """

    def __init__(self, vector_store=None):
        self.vector_store = vector_store
        self.entries: Dict[str, MemoryEntry] = {}

    async def search(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Semantic search using vector store."""
        if not self.vector_store:
            logger.warning("No vector store configured for cold storage")
            return []

        # TODO: Implement actual vector search
        # results = await self.vector_store.search(query, limit)
        # return [self.entries[r.id] for r in results if r.id in self.entries]
        return []

    def add(self, entry_id: str, content: str, embedding: List[float], metadata: Dict[str, Any] = None):
        """Add entry to cold storage with embedding."""
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.utcnow()
        )
        self.entries[entry_id] = entry

        if self.vector_store:
            # TODO: Store embedding
            pass


class MemorySystem:
    """
    Unified memory system managing all cache layers.

    Flow:
    1. Check HOT first (instant)
    2. If not found → WARM (milliseconds)
    3. If still not found → COLD (seconds)
    """

    def __init__(
        self,
        hot_size: int = 50000,
        warm_size: int = 100000,
        vector_store=None
    ):
        self.hot = HotCache(max_size=hot_size)
        self.warm = WarmCache(max_size=warm_size)
        self.cold = ColdStorage(vector_store=vector_store)

    async def get_hot(self) -> List[MemoryEntry]:
        """Get all hot cache entries."""
        return self.hot.get_all()

    async def search_warm(self, query: str) -> List[MemoryEntry]:
        """Search warm cache."""
        # Extract keywords from query
        keywords = query.lower().split()
        return self.warm.search(keywords)

    async def search_cold(self, query: str) -> List[MemoryEntry]:
        """Search cold storage."""
        return await self.cold.search(query)

    def add_to_hot(self, key: str, content: str, metadata: Dict[str, Any] = None):
        """Add to hot cache (most recent context)."""
        self.hot.put(key, content, metadata)

    def add_to_warm(self, entry_id: str, content: str, keywords: List[str], metadata: Dict[str, Any] = None):
        """Add to warm cache (project-scoped context)."""
        self.warm.add(entry_id, content, keywords, metadata)

    def add_to_cold(self, entry_id: str, content: str, embedding: List[float], metadata: Dict[str, Any] = None):
        """Add to cold storage (full codebase)."""
        self.cold.add(entry_id, content, embedding, metadata)

    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return {
            "hot": {
                "entries": len(self.hot.entries),
                "tokens": self.hot.current_tokens,
                "max_tokens": self.hot.max_size
            },
            "warm": {
                "entries": len(self.warm.entries),
                "keywords_indexed": len(self.warm.index)
            },
            "cold": {
                "entries": len(self.cold.entries)
            }
        }
