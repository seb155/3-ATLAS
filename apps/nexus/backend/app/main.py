from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, notes
from .config import get_settings

settings = get_settings()

app = FastAPI(
    title="Nexus API",
    description="Knowledge Graph Portal API",
    version="0.2.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(notes.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Nexus API v0.2.0", "status": "operational"}


@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "version": "0.2.0"}
