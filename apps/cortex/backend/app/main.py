"""
CORTEX FastAPI Application

Main entry point for the CORTEX Engine API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import sessions, tasks, context, websocket

app = FastAPI(
    title="CORTEX",
    description="The Contextual Intelligence Engine - An autonomous AI agent",
    version="0.5.0-dev",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(context.router, prefix="/api/v1/context", tags=["context"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "cortex-engine"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "CORTEX",
        "version": "0.5.0-dev",
        "description": "The Contextual Intelligence Engine",
        "docs": "/docs",
    }
