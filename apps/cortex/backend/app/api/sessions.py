"""
Session Management API

Endpoints for creating and managing CORTEX sessions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

router = APIRouter()


class SessionCreate(BaseModel):
    """Request model for creating a session."""
    name: Optional[str] = None
    repo_path: str
    context_blocks: List[str] = []


class SessionResponse(BaseModel):
    """Response model for session data."""
    id: str
    name: str
    repo_path: str
    status: str
    created_at: datetime
    context_blocks: List[str]


# In-memory storage for MVP (replace with DB later)
sessions_store: dict = {}


@router.post("/", response_model=SessionResponse)
async def create_session(session: SessionCreate):
    """Create a new CORTEX session."""
    session_id = str(uuid.uuid4())
    now = datetime.utcnow()

    session_data = {
        "id": session_id,
        "name": session.name or f"Session {session_id[:8]}",
        "repo_path": session.repo_path,
        "status": "active",
        "created_at": now,
        "context_blocks": session.context_blocks,
    }

    sessions_store[session_id] = session_data
    return SessionResponse(**session_data)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session details."""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(**sessions_store[session_id])


@router.get("/", response_model=List[SessionResponse])
async def list_sessions():
    """List all sessions."""
    return [SessionResponse(**s) for s in sessions_store.values()]


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="Session not found")
    del sessions_store[session_id]
    return {"status": "deleted", "session_id": session_id}
