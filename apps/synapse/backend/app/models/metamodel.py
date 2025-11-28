import enum
import uuid

from sqlalchemy import JSON, Column, Enum, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class DisciplineType(str, enum.Enum):
    PROCESS = "PROCESS"
    ELECTRICAL = "ELECTRICAL"
    AUTOMATION = "AUTOMATION"
    MECHANICAL = "MECHANICAL"
    PROJECT = "PROJECT"
    PROCUREMENT = "PROCUREMENT"
    GENERAL = "GENERAL"


class SemanticType(str, enum.Enum):
    CONTAINER = "CONTAINER"  # Area, Room, Cabinet
    ASSET = "ASSET"  # Motor, Valve
    LINK = "LINK"  # Cable, Stream


class AssetDataStatus(str, enum.Enum):
    """Status of the asset's data completeness"""

    FRESH_IMPORT = "FRESH_IMPORT"  # Raw data from CSV, potentially incomplete
    IN_REVIEW = "IN_REVIEW"  # Engineer is working on it
    VALIDATED = "VALIDATED"  # Data is complete and checked
    ERROR = "ERROR"  # Missing critical fields


class MetamodelNode(Base):
    __tablename__ = "metamodel_nodes"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)  # Removed unique=True to allow same name in diff projects
    project_id = Column(String, nullable=True)  # Nullable for now to support legacy/global nodes
    type = Column(String, nullable=False)  # "ASSET" or "LOCATION" (Legacy/High-level)

    # Advanced Attributes
    discipline = Column(Enum(DisciplineType), default=DisciplineType.GENERAL)
    semantic_type = Column(Enum(SemanticType), default=SemanticType.ASSET)
    lod = Column(Integer, default=2)  # 1=Macro, 2=Equip, 3=Detail
    isa95_level = Column(Integer, default=0)  # 0=Device, 1=Equip, 2=Unit, 3=Area, 4=Site

    description = Column(String)
    properties = Column(
        JSON, default={}
    )  # Custom properties for asset (e.g., {"area": "300-GRINDING", "system": "General"})

    # Data Quality
    data_status = Column(Enum(AssetDataStatus), default=AssetDataStatus.FRESH_IMPORT, index=True)

    # Phase 0: Ingestion & Quality Tracking
    confidence_score = Column(Float, default=1.0)  # 0.0 to 1.0
    data_source_id = Column(String, nullable=True)  # Link to source file, index=True)


class MetamodelEdge(Base):
    __tablename__ = "metamodel_edges"

    id = Column(String, primary_key=True, default=generate_uuid)
    source_node_id = Column(String, nullable=False)
    target_node_id = Column(String, nullable=False)
    relation_type = Column(String, nullable=False)
    cardinality = Column(String, default="1:N")

    # Advanced Attributes
    discipline = Column(Enum(DisciplineType), default=DisciplineType.GENERAL)
    properties = Column(JSON, default={})  # e.g. {"propagates": ["voltage"]}

    source = relationship(
        "MetamodelNode",
        primaryjoin="MetamodelEdge.source_node_id==MetamodelNode.id",
        foreign_keys=[source_node_id],
    )
    target = relationship(
        "MetamodelNode",
        primaryjoin="MetamodelEdge.target_node_id==MetamodelNode.id",
        foreign_keys=[target_node_id],
    )

    __table_args__ = (
        UniqueConstraint(
            "source_node_id", "target_node_id", "relation_type", name="uix_metamodel_edge"
        ),
    )
