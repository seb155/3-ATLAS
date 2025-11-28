import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class IngestStatus(str, enum.Enum):
    PENDING = "PENDING"
    STAGED = "STAGED"
    MAPPED = "MAPPED"
    IMPORTED = "IMPORTED"
    ERROR = "ERROR"


class DetectedType(str, enum.Enum):
    BBA_INSTRUMENT_LIST = "BBA_INSTRUMENT_LIST"
    CABLE_SCHEDULE = "CABLE_SCHEDULE"
    GENERIC_LIST = "GENERIC_LIST"
    UNKNOWN = "UNKNOWN"


class ImportStatus(str, enum.Enum):
    PENDING = "PENDING"
    SKIPPED = "SKIPPED"
    IMPORTED = "IMPORTED"
    ERROR = "ERROR"


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, nullable=False)  # Link to project
    filename = Column(String, nullable=False)
    file_hash = Column(String, nullable=True)  # MD5/SHA256 to detect duplicates

    ingest_status = Column(Enum(IngestStatus), default=IngestStatus.PENDING)
    detected_type = Column(Enum(DetectedType), default=DetectedType.UNKNOWN)

    metadata_json = Column(JSONB, default={})  # Sheet names, row counts, header mapping

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    staged_rows = relationship(
        "StagedRow", back_populates="data_source", cascade="all, delete-orphan"
    )


class StagedRow(Base):
    __tablename__ = "staged_rows"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    data_source_id = Column(String, ForeignKey("data_sources.id"), nullable=False)

    row_index = Column(Integer, nullable=False)  # Excel row number
    raw_data = Column(JSONB, nullable=False)  # {"Col A": "Val", "Col B": "Val"}

    import_status = Column(Enum(ImportStatus), default=ImportStatus.PENDING)

    # Link to created asset (if imported)
    asset_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    data_source = relationship("DataSource", back_populates="staged_rows")
