from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class IngestStatus(str, Enum):
    PENDING = "PENDING"
    STAGED = "STAGED"
    MAPPED = "MAPPED"
    IMPORTED = "IMPORTED"
    ERROR = "ERROR"


class DetectedType(str, Enum):
    BBA_INSTRUMENT_LIST = "BBA_INSTRUMENT_LIST"
    CABLE_SCHEDULE = "CABLE_SCHEDULE"
    GENERIC_LIST = "GENERIC_LIST"
    UNKNOWN = "UNKNOWN"


class DataSourceResponse(BaseModel):
    id: str
    filename: str
    file_hash: str
    ingest_status: IngestStatus
    detected_type: DetectedType
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StagedRowResponse(BaseModel):
    id: str
    data_source_id: str
    row_index: int
    raw_data: dict[str, Any]
    import_status: str
    asset_id: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
