"""
Temporal Awareness

Time-based context tracking, versioning, and change detection.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class ChangeType(str, Enum):
    """Types of changes tracked."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


@dataclass
class TemporalEvent:
    """A tracked change event."""
    id: str
    timestamp: datetime
    entity_type: str  # file, context_block, session, etc.
    entity_id: str
    change_type: ChangeType

    # Change details
    before: Optional[Dict[str, Any]] = None
    after: Optional[Dict[str, Any]] = None
    diff_summary: Optional[str] = None

    # Context
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    user_id: Optional[str] = None

    # For snapshots
    snapshot_id: Optional[str] = None


@dataclass
class ContextSnapshot:
    """Point-in-time snapshot of context state."""
    id: str
    timestamp: datetime
    description: str

    # State capture
    file_hashes: Dict[str, str] = field(default_factory=dict)  # path -> hash
    context_block_versions: Dict[str, int] = field(default_factory=dict)  # block_id -> version

    # Metadata
    session_id: Optional[str] = None
    trigger: str = "manual"  # manual, auto, milestone


class TemporalTracker:
    """
    Tracks changes over time for temporal awareness.

    Features:
    - Change detection between sessions
    - Version history for context
    - Snapshots for time-travel
    - Evolution analysis
    """

    def __init__(self):
        self.events: List[TemporalEvent] = []
        self.snapshots: Dict[str, ContextSnapshot] = {}
        self.current_session: Optional[str] = None

    def record_change(
        self,
        entity_type: str,
        entity_id: str,
        change_type: ChangeType,
        before: Dict[str, Any] = None,
        after: Dict[str, Any] = None,
        **kwargs
    ) -> TemporalEvent:
        """Record a change event."""
        import uuid

        # Generate diff summary
        diff_summary = None
        if before and after:
            diff_summary = self._generate_diff_summary(before, after)

        event = TemporalEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            entity_type=entity_type,
            entity_id=entity_id,
            change_type=change_type,
            before=before,
            after=after,
            diff_summary=diff_summary,
            session_id=self.current_session,
            **kwargs
        )

        self.events.append(event)
        logger.debug(f"Recorded {change_type.value} for {entity_type}:{entity_id}")
        return event

    def create_snapshot(
        self,
        description: str,
        file_hashes: Dict[str, str] = None,
        context_versions: Dict[str, int] = None
    ) -> ContextSnapshot:
        """Create a point-in-time snapshot."""
        import uuid

        snapshot = ContextSnapshot(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            description=description,
            file_hashes=file_hashes or {},
            context_block_versions=context_versions or {},
            session_id=self.current_session
        )

        self.snapshots[snapshot.id] = snapshot
        logger.info(f"Created snapshot: {snapshot.id} - {description}")
        return snapshot

    def get_changes_since(
        self,
        since: datetime,
        entity_type: Optional[str] = None
    ) -> List[TemporalEvent]:
        """Get all changes since a timestamp."""
        events = [e for e in self.events if e.timestamp > since]
        if entity_type:
            events = [e for e in events if e.entity_type == entity_type]
        return events

    def get_entity_history(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 10
    ) -> List[TemporalEvent]:
        """Get change history for a specific entity."""
        events = [
            e for e in self.events
            if e.entity_type == entity_type and e.entity_id == entity_id
        ]
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]

    def detect_changes(
        self,
        current_state: Dict[str, str],
        snapshot_id: str
    ) -> Dict[str, Any]:
        """
        Detect changes between current state and a snapshot.

        Returns summary of what changed.
        """
        if snapshot_id not in self.snapshots:
            return {"error": "Snapshot not found"}

        snapshot = self.snapshots[snapshot_id]
        old_state = snapshot.file_hashes

        changes = {
            "created": [],
            "modified": [],
            "deleted": [],
            "unchanged": 0
        }

        # Check for new and modified
        for path, hash_val in current_state.items():
            if path not in old_state:
                changes["created"].append(path)
            elif old_state[path] != hash_val:
                changes["modified"].append(path)
            else:
                changes["unchanged"] += 1

        # Check for deleted
        for path in old_state:
            if path not in current_state:
                changes["deleted"].append(path)

        return changes

    def generate_change_summary(
        self,
        since: datetime,
        entity_type: Optional[str] = None
    ) -> str:
        """Generate human-readable summary of changes."""
        events = self.get_changes_since(since, entity_type)

        if not events:
            return "No changes since the specified time."

        lines = [f"Changes since {since.isoformat()}:", ""]

        # Group by entity type
        by_type: Dict[str, List[TemporalEvent]] = {}
        for event in events:
            if event.entity_type not in by_type:
                by_type[event.entity_type] = []
            by_type[event.entity_type].append(event)

        for etype, type_events in by_type.items():
            lines.append(f"## {etype.title()} ({len(type_events)} changes)")
            for event in type_events[:5]:  # Limit to 5 per type
                lines.append(f"  - {event.change_type.value}: {event.entity_id}")
                if event.diff_summary:
                    lines.append(f"    {event.diff_summary}")
            if len(type_events) > 5:
                lines.append(f"  ... and {len(type_events) - 5} more")
            lines.append("")

        return "\n".join(lines)

    def _generate_diff_summary(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any]
    ) -> str:
        """Generate a brief summary of differences."""
        added = set(after.keys()) - set(before.keys())
        removed = set(before.keys()) - set(after.keys())
        changed = {
            k for k in set(before.keys()) & set(after.keys())
            if before[k] != after[k]
        }

        parts = []
        if added:
            parts.append(f"+{len(added)} keys")
        if removed:
            parts.append(f"-{len(removed)} keys")
        if changed:
            parts.append(f"~{len(changed)} modified")

        return ", ".join(parts) if parts else "no structural changes"
