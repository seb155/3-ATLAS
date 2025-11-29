"""
Trace Engine

Audit logging, replay, and time-travel for agent actions.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import uuid
import logging

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Types of trace events."""
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    TASK_START = "task_start"
    TASK_END = "task_end"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    CONTEXT_LOAD = "context_load"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_EDIT = "file_edit"
    ERROR = "error"
    USER_CONFIRMATION = "user_confirmation"


@dataclass
class TraceEvent:
    """A single event in the trace."""
    id: str
    timestamp: datetime
    event_type: EventType
    session_id: str
    task_id: Optional[str]

    # Event data
    data: Dict[str, Any]

    # For file changes
    before_state: Optional[str] = None
    after_state: Optional[str] = None
    diff: Optional[str] = None

    # Metadata
    duration_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None


@dataclass
class Snapshot:
    """A point-in-time snapshot of system state."""
    id: str
    timestamp: datetime
    session_id: str
    description: str
    file_states: Dict[str, str]  # path -> content hash
    context_blocks: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class TraceEngine:
    """
    Records and manages execution traces.

    Features:
    - Complete audit log of all actions
    - Replay capability
    - Time-travel (snapshot/restore)
    - Change detection
    - Cost tracking
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self.events: List[TraceEvent] = []
        self.snapshots: Dict[str, Snapshot] = {}
        self.current_session: Optional[str] = None
        self.current_task: Optional[str] = None

    def start_session(self, session_id: str) -> TraceEvent:
        """Record session start."""
        self.current_session = session_id
        return self._record(EventType.SESSION_START, {"session_id": session_id})

    def end_session(self) -> TraceEvent:
        """Record session end."""
        event = self._record(EventType.SESSION_END, {"session_id": self.current_session})
        self.current_session = None
        return event

    def start_task(self, task_id: str, description: str) -> TraceEvent:
        """Record task start."""
        self.current_task = task_id
        return self._record(EventType.TASK_START, {
            "task_id": task_id,
            "description": description
        })

    def end_task(self, result: str, status: str) -> TraceEvent:
        """Record task end."""
        event = self._record(EventType.TASK_END, {
            "task_id": self.current_task,
            "result": result,
            "status": status
        })
        self.current_task = None
        return event

    def record_tool_call(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        output: str,
        duration_ms: int
    ) -> TraceEvent:
        """Record a tool call."""
        return self._record(EventType.TOOL_CALL, {
            "tool": tool_name,
            "input": input_data,
            "output": output[:1000]  # Truncate long outputs
        }, duration_ms=duration_ms)

    def record_file_change(
        self,
        event_type: EventType,
        path: str,
        before: Optional[str],
        after: Optional[str]
    ) -> TraceEvent:
        """Record a file change with before/after states."""
        # Generate diff if both states available
        diff = None
        if before and after:
            # Simple line diff - could use difflib for more sophisticated
            diff = f"-{len(before)} chars, +{len(after)} chars"

        return self._record(
            event_type,
            {"path": path},
            before_state=before,
            after_state=after,
            diff=diff
        )

    def record_llm_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        duration_ms: int,
        cost_usd: float
    ) -> TraceEvent:
        """Record an LLM API call."""
        return self._record(
            EventType.LLM_REQUEST,
            {
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            },
            duration_ms=duration_ms,
            tokens_used=input_tokens + output_tokens,
            cost_usd=cost_usd
        )

    def create_snapshot(self, description: str, file_states: Dict[str, str]) -> Snapshot:
        """Create a point-in-time snapshot."""
        snapshot = Snapshot(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            session_id=self.current_session,
            description=description,
            file_states=file_states,
            context_blocks=[]  # TODO: Get current context blocks
        )
        self.snapshots[snapshot.id] = snapshot
        logger.info(f"Created snapshot: {snapshot.id} - {description}")
        return snapshot

    def get_events_since(self, since: datetime) -> List[TraceEvent]:
        """Get all events since a timestamp."""
        return [e for e in self.events if e.timestamp > since]

    def get_session_events(self, session_id: str) -> List[TraceEvent]:
        """Get all events for a session."""
        return [e for e in self.events if e.session_id == session_id]

    def get_task_events(self, task_id: str) -> List[TraceEvent]:
        """Get all events for a task."""
        return [e for e in self.events if e.task_id == task_id]

    def calculate_session_cost(self, session_id: str) -> float:
        """Calculate total cost for a session."""
        return sum(
            e.cost_usd or 0
            for e in self.get_session_events(session_id)
        )

    def calculate_session_tokens(self, session_id: str) -> int:
        """Calculate total tokens used in a session."""
        return sum(
            e.tokens_used or 0
            for e in self.get_session_events(session_id)
        )

    def export_trace(self, session_id: str) -> str:
        """Export trace as JSON for analysis."""
        events = self.get_session_events(session_id)
        return json.dumps([
            {
                "id": e.id,
                "timestamp": e.timestamp.isoformat(),
                "type": e.event_type.value,
                "data": e.data,
                "duration_ms": e.duration_ms,
                "tokens": e.tokens_used,
                "cost_usd": e.cost_usd
            }
            for e in events
        ], indent=2)

    def _record(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        **kwargs
    ) -> TraceEvent:
        """Internal method to record an event."""
        event = TraceEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event_type=event_type,
            session_id=self.current_session,
            task_id=self.current_task,
            data=data,
            **kwargs
        )
        self.events.append(event)
        logger.debug(f"Trace event: {event_type.value}")
        return event
