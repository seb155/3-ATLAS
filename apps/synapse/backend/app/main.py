from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.api.endpoints import (
    actions,
    assets,
    auth,
    import_export,
    ingestion,
    locations,
    logs,
    owner_portal,
    packages,
    projects,
    rules,
    search,
    validation,
    workflow,
)
from app.core.exceptions import (
    BusinessLogicError,
    DatabaseError,
    DuplicateError,
    FileValidationError,
    ForeignKeyError,
    InactiveResourceError,
    NotFoundError,
    RuleExecutionError,
)
from app.core.exceptions import ValidationError as SynapseValidationError
from app.middleware.logging_middleware import LoggingMiddleware
from app.routers import ai, cables, mock
from app.routers import metamodel as metamodel_router

app = FastAPI(
    title="AXOIQ SYNAPSE API",
    description="Backend for the AXOIQ SYNAPSE MBSE Platform",
    version="0.2.2",
)


@app.on_event("startup")
def on_startup():
    # Base.metadata.create_all(bind=engine)
    pass


# CORS Configuration - Secure by default
# Configure via ALLOWED_ORIGINS environment variable
import os

# Read ALLOWED_ORIGINS from environment
# Default to localhost URLs for local development
_allowed_origins_env = os.getenv(
    "ALLOWED_ORIGINS",
    # Default origins for local development (override in .env for production)
    "http://localhost:4000,http://localhost:5173,http://localhost:8000,http://localhost:8001,http://127.0.0.1:4000,http://127.0.0.1:8000",
)

# Parse comma-separated origins
origins = [origin.strip() for origin in _allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Project-ID", "X-Request-ID"],
)

# Logging middleware for WebSocket broadcast
app.add_middleware(LoggingMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # Convert errors to ensure JSON serialization
    errors = []
    for error in exc.errors():
        error_dict = {
            "type": error.get("type"),
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "input": error.get("input"),
        }
        # Convert ctx error to string if present
        if "ctx" in error and "error" in error["ctx"]:
            error_dict["ctx"] = {"error": str(error["ctx"]["error"])}
        errors.append(error_dict)

    return JSONResponse(
        status_code=422,
        content={"detail": errors, "message": "Validation Error"},
    )


# ============================================================================
# Custom Exception Handlers
# ============================================================================


@app.exception_handler(NotFoundError)
async def not_found_handler(request, exc: NotFoundError):
    return JSONResponse(
        status_code=404, content={"detail": exc.message, "type": "not_found", **exc.details}
    )


@app.exception_handler(DuplicateError)
async def duplicate_handler(request, exc: DuplicateError):
    return JSONResponse(
        status_code=409, content={"detail": exc.message, "type": "duplicate", **exc.details}
    )


@app.exception_handler(SynapseValidationError)
async def synapse_validation_handler(request, exc: SynapseValidationError):
    return JSONResponse(
        status_code=400, content={"detail": exc.message, "type": "validation_error", **exc.details}
    )


@app.exception_handler(FileValidationError)
async def file_validation_handler(request, exc: FileValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message, "type": "file_validation_error", **exc.details},
    )


@app.exception_handler(BusinessLogicError)
async def business_logic_handler(request, exc: BusinessLogicError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message, "type": "business_logic_error", **exc.details},
    )


@app.exception_handler(RuleExecutionError)
async def rule_execution_handler(request, exc: RuleExecutionError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message, "type": "rule_execution_error", **exc.details},
    )


@app.exception_handler(InactiveResourceError)
async def inactive_resource_handler(request, exc: InactiveResourceError):
    return JSONResponse(
        status_code=403, content={"detail": exc.message, "type": "forbidden", **exc.details}
    )


@app.exception_handler(ForeignKeyError)
async def foreign_key_handler(request, exc: ForeignKeyError):
    return JSONResponse(
        status_code=400, content={"detail": exc.message, "type": "foreign_key_error", **exc.details}
    )


@app.exception_handler(DatabaseError)
async def database_error_handler(request, exc: DatabaseError):
    return JSONResponse(
        status_code=500, content={"detail": "Database error occurred", "type": "database_error"}
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc: IntegrityError):
    # Extract constraint details for better debugging
    detail = "Database constraint violation"
    if hasattr(exc, "orig") and exc.orig:
        detail = str(exc.orig)
    return JSONResponse(
        status_code=409,
        content={"detail": detail, "type": "integrity_error"},
    )


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])

app.include_router(import_export.router, prefix="/api/v1/import_export", tags=["import-export"])

app.include_router(ingestion.router, prefix="/api/v1/ingest", tags=["ingestion"])

app.include_router(assets.router, prefix="/api/v1/assets", tags=["assets"])
app.include_router(locations.router, prefix="/api/v1/locations", tags=["locations"])
app.include_router(packages.router, prefix="/api/v1/packages", tags=["packages"])

app.include_router(metamodel_router.router, prefix="/api/v1", tags=["metamodel"])
app.include_router(mock.router, prefix="/api/v1", tags=["mock"])
app.include_router(cables.router, prefix="/api/v1/cables", tags=["cables"])

app.include_router(rules.router, tags=["rules"])
app.include_router(actions.router, tags=["actions"])
app.include_router(validation.router, prefix="/api/v1", tags=["validation"])
app.include_router(logs.router, tags=["logs"])

app.include_router(owner_portal.router, prefix="/api/v1/owner", tags=["owner"])

app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(workflow.router, prefix="/api/v1/workflow", tags=["workflow"])


@app.get("/")
def read_root():
    return {"message": "Welcome to AXOIQ SYNAPSE API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
