"""
CORTEX Sandbox Manager

Manages isolated Docker containers for safe code execution.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
import asyncio
import uuid

app = FastAPI(title="CORTEX Sandbox Manager", version="0.5.0")


class SandboxRequest(BaseModel):
    """Request to create a sandbox."""
    image: str = "python:3.11-slim"
    timeout: int = 60
    memory_limit: str = "512m"
    cpu_limit: float = 1.0


class CommandRequest(BaseModel):
    """Request to execute a command in sandbox."""
    sandbox_id: str
    command: str
    timeout: int = 30


class SandboxInfo(BaseModel):
    """Sandbox information."""
    id: str
    image: str
    status: str
    created_at: datetime
    expires_at: datetime


# In-memory sandbox tracking
sandboxes: Dict[str, dict] = {}


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "service": "cortex-sandbox"}


@app.post("/sandboxes", response_model=SandboxInfo)
async def create_sandbox(request: SandboxRequest):
    """
    Create a new isolated sandbox container.

    The sandbox is a Docker container with limited resources
    and network isolation for safe code execution.
    """
    sandbox_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow()

    # TODO: Actually create Docker container
    # For MVP, just track the request

    sandbox = {
        "id": sandbox_id,
        "image": request.image,
        "status": "ready",
        "created_at": now,
        "expires_at": datetime.fromtimestamp(now.timestamp() + request.timeout),
        "container_id": None,
        "config": {
            "memory_limit": request.memory_limit,
            "cpu_limit": request.cpu_limit,
            "timeout": request.timeout
        }
    }

    sandboxes[sandbox_id] = sandbox

    return SandboxInfo(**sandbox)


@app.get("/sandboxes/{sandbox_id}", response_model=SandboxInfo)
async def get_sandbox(sandbox_id: str):
    """Get sandbox information."""
    if sandbox_id not in sandboxes:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    return SandboxInfo(**sandboxes[sandbox_id])


@app.get("/sandboxes", response_model=List[SandboxInfo])
async def list_sandboxes():
    """List all active sandboxes."""
    return [SandboxInfo(**s) for s in sandboxes.values()]


@app.post("/sandboxes/{sandbox_id}/exec")
async def execute_in_sandbox(sandbox_id: str, request: CommandRequest):
    """
    Execute a command inside a sandbox.

    Returns the command output (stdout/stderr).
    """
    if sandbox_id not in sandboxes:
        raise HTTPException(status_code=404, detail="Sandbox not found")

    sandbox = sandboxes[sandbox_id]

    # TODO: Actually execute in Docker container
    # For MVP, just return a placeholder

    return {
        "sandbox_id": sandbox_id,
        "command": request.command,
        "exit_code": 0,
        "stdout": f"[SANDBOX {sandbox_id}] Command would execute: {request.command}",
        "stderr": "",
        "duration_ms": 0
    }


@app.delete("/sandboxes/{sandbox_id}")
async def destroy_sandbox(sandbox_id: str):
    """Destroy a sandbox and clean up resources."""
    if sandbox_id not in sandboxes:
        raise HTTPException(status_code=404, detail="Sandbox not found")

    # TODO: Actually destroy Docker container

    del sandboxes[sandbox_id]
    return {"status": "destroyed", "sandbox_id": sandbox_id}


@app.post("/sandboxes/cleanup")
async def cleanup_expired():
    """Clean up expired sandboxes."""
    now = datetime.utcnow()
    expired = [
        sid for sid, s in sandboxes.items()
        if s["expires_at"] < now
    ]

    for sid in expired:
        del sandboxes[sid]

    return {"cleaned_up": len(expired)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
