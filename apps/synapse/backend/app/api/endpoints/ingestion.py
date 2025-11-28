from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api import deps
from app.models.ingestion import DataSource, StagedRow
from app.schemas.ingestion import DataSourceResponse, StagedRowResponse
from app.services.ingestion_service import IngestionService

router = APIRouter()


class FileScanResponse(BaseModel):
    files: list[str]


class IngestRequest(BaseModel):
    filename: str
    project_id: str


@router.post("/scan", response_model=FileScanResponse)
def scan_data_folder() -> Any:
    """
    Scan the server's Data_raw folder for Excel/CSV files.
    """
    files = IngestionService.scan_folder()
    return {"files": files}


@router.post("/process", response_model=DataSourceResponse)
async def process_file(request: IngestRequest, db: Session = Depends(deps.get_db)) -> Any:
    """
    Ingest a file from Data_raw into the staging area.
    """
    file_path = f"/app/Data_raw/{request.filename}"
    source = IngestionService.ingest_file(db, request.project_id, file_path)
    if not source:
        raise HTTPException(status_code=400, detail="Failed to ingest file")
    return source


@router.get("/sources", response_model=list[DataSourceResponse])
def list_sources(db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100) -> Any:
    """
    List all ingested data sources.
    """
    return db.query(DataSource).offset(skip).limit(limit).all()


@router.get("/sources/{source_id}/rows", response_model=list[StagedRowResponse])
def get_staged_rows(
    source_id: str, db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Get raw staged rows for a data source.
    """
    return (
        db.query(StagedRow)
        .filter(StagedRow.data_source_id == source_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
