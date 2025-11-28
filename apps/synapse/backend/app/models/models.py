import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class AssetType(str, enum.Enum):
    INSTRUMENT = "INSTRUMENT"
    MOTOR = "MOTOR"
    VALVE = "VALVE"
    CONTROL_SYSTEM = "CONTROL_SYSTEM"
    PUMP = "PUMP"
    TANK = "TANK"
    # Added from metamodel
    AREA = "AREA"
    AGITATOR = "AGITATOR"
    BALL_MILL = "BALL_MILL"
    LEVEL_TRANSMITTER = "LEVEL_TRANSMITTER"
    CABLE = "CABLE"


class IOType(str, enum.Enum):
    AI = "AI"
    AO = "AO"
    DI = "DI"
    DO = "DO"
    PROFIBUS = "PROFIBUS"
    ETHERNET = "ETHERNET"
    HARDWIRED = "HARDWIRED"
    PROFINET = "PROFINET"
    ETHERNET_IP = "ETHERNET_IP"
    MODBUS_TCP = "MODBUS_TCP"


class LocationType(str, enum.Enum):
    SITE = "SITE"
    AREA = "AREA"
    EHOUSE = "EHOUSE"
    ROOM = "ROOM"
    CABINET = "CABINET"
    JUNCTION_BOX = "JUNCTION_BOX"


class AssetDataStatus(str, enum.Enum):
    """Status of the asset's data completeness"""

    FRESH_IMPORT = "FRESH_IMPORT"  # Raw data from CSV, potentially incomplete
    IN_REVIEW = "IN_REVIEW"  # Engineer is working on it
    VALIDATED = "VALIDATED"  # Data is complete and checked
    ERROR = "ERROR"  # Missing critical fields


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=generate_uuid)
    tag = Column(String, index=True, nullable=False)
    description = Column(String)
    type = Column(String, nullable=False)  # Changed from Enum to String for flexibility
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)

    # Soft delete support
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    __table_args__ = (
        UniqueConstraint("tag", "project_id", name="uix_project_tag"),
        Index("ix_asset_project_id", "project_id"),
        Index("ix_asset_type_project", "type", "project_id"),
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    # FBS
    area = Column(String)
    system = Column(String)

    # Domains
    io_type = Column(Enum(IOType))
    mechanical = Column(JSON)  # Weight, material, etc.
    electrical = Column(JSON)  # Voltage, power, etc.
    process = Column(JSON)  # Fluid, ranges, etc.
    purchasing = Column(JSON)  # PO, status, etc.

    manufacturer_part_id = Column(String)

    # Data Quality
    data_status = Column(Enum(AssetDataStatus), default=AssetDataStatus.FRESH_IMPORT, index=True)

    # Phase 0: Ingestion & Quality Tracking
    confidence_score = Column(Float, default=1.0)  # 0.0 to 1.0
    data_source_id = Column(String, nullable=True)  # Link to source file, index=True)

    # Metamodel Integration (NEW - from metamodel_nodes)
    discipline = Column(String, nullable=True, index=True)
    semantic_type = Column(String, nullable=True, index=True)
    lod = Column(Integer, nullable=True)  # Level of Detail
    isa95_level = Column(Integer, nullable=True)  # ISA-95 hierarchy level
    properties = Column(JSON, nullable=True)  # Generic properties dictionary

    # LBS Link
    location_id = Column(String, ForeignKey("lbs_nodes.id"), nullable=True)

    location = relationship("LBSNode", back_populates="assets")

    # Package Link
    package_id = Column(String, ForeignKey("packages.id"), nullable=True, index=True)
    package = relationship("Package", back_populates="assets")


class LBSNode(Base):
    __tablename__ = "lbs_nodes"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    type = Column(Enum(LocationType), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    parent_id = Column(String, ForeignKey("lbs_nodes.id"), nullable=True)

    capacity_slots = Column(Integer)
    design_heat_dissipation = Column(Float)
    ip_rating = Column(String)

    # Soft delete support
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    __table_args__ = (Index("ix_lbs_project_id", "project_id"),)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    children = relationship("LBSNode", backref="parent", remote_side=[id])
    assets = relationship("Asset", back_populates="location")


class Connection(Base):
    __tablename__ = "connections"

    id = Column(String, primary_key=True, default=generate_uuid)
    from_id = Column(String, nullable=False)  # Can be Asset ID or LBS ID
    to_id = Column(String, nullable=False)  # Can be Asset ID or LBS ID
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    type = Column(String)  # HOMERUN, SYSTEM, etc.
    cable_tag = Column(String)

    # Soft delete support
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    __table_args__ = (Index("ix_connection_project_id", "project_id"),)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
