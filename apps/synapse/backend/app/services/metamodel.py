from sqlalchemy.orm import Session

from app.models.metamodel import (
    AssetDataStatus,
    DisciplineType,
    MetamodelEdge,
    MetamodelNode,
    SemanticType,
)
from app.models.models import Asset
from app.schemas.metamodel import EdgeCreate, NodeCreate


class MetamodelService:
    @staticmethod
    def map_asset_type_to_discipline(asset_type: str) -> DisciplineType:
        if not asset_type:
            return DisciplineType.GENERAL

        asset_type = asset_type.upper()

        process_types = ["TANK", "VALVE", "STREAM", "PIPE"]
        mechanical_types = ["PUMP", "AGITATOR", "COMPRESSOR", "CONVEYOR"]
        electrical_types = ["MOTOR", "MCC", "TRANSFORMER", "PANEL", "VFD", "GENERATOR"]
        automation_types = [
            "INSTRUMENT",
            "PLC",
            "IO_CARD",
            "CONTROL_SYSTEM",
            "CABINET",
            "JUNCTION_BOX",
            "RIO",
        ]

        if asset_type in process_types:
            return DisciplineType.PROCESS
        if asset_type in mechanical_types:
            return DisciplineType.MECHANICAL
        if asset_type in electrical_types:
            return DisciplineType.ELECTRICAL
        if asset_type in automation_types:
            return DisciplineType.AUTOMATION

        return DisciplineType.GENERAL

    @staticmethod
    def create_node(db: Session, node: NodeCreate) -> MetamodelNode:
        # Check for existing node by name AND project_id
        query = db.query(MetamodelNode).filter(MetamodelNode.name == node.name)

        if node.project_id:
            query = query.filter(MetamodelNode.project_id == node.project_id)
        else:
            query = query.filter(MetamodelNode.project_id.is_(None))

        db_node = query.first()

        if db_node:
            # Update existing node
            db_node.discipline = node.discipline
            db_node.semantic_type = node.semantic_type
            db_node.lod = node.lod
            db_node.isa95_level = node.isa95_level
            if node.properties:
                db_node.properties = node.properties
            if node.description:
                db_node.description = node.description

            db.commit()
            db.refresh(db_node)
            return db_node

        new_node = MetamodelNode(
            name=node.name,
            type=node.type,
            discipline=node.discipline,
            semantic_type=node.semantic_type,
            lod=node.lod,
            isa95_level=node.isa95_level,
            description=node.description,
            properties=node.properties,
            project_id=node.project_id,
            data_status=AssetDataStatus.FRESH_IMPORT,
        )
        db.add(new_node)
        db.commit()
        db.refresh(new_node)
        return new_node

    @staticmethod
    def create_edge(db: Session, edge: EdgeCreate) -> MetamodelEdge:
        existing = (
            db.query(MetamodelEdge)
            .filter(
                MetamodelEdge.source_node_id == edge.source_node_id,
                MetamodelEdge.target_node_id == edge.target_node_id,
                MetamodelEdge.relation_type == edge.relation_type,
            )
            .first()
        )

        if existing:
            return existing

        new_edge = MetamodelEdge(
            source_node_id=edge.source_node_id,
            target_node_id=edge.target_node_id,
            relation_type=edge.relation_type,
            cardinality=edge.cardinality,
            discipline=edge.discipline,
            properties=edge.properties,
        )
        db.add(new_edge)
        db.commit()
        db.refresh(new_edge)
        return new_edge

    @staticmethod
    def create_node_from_asset(db: Session, asset: Asset) -> MetamodelNode:
        """
        Creates or updates a MetamodelNode based on an Asset.
        """
        discipline = MetamodelService.map_asset_type_to_discipline(asset.type)

        # Determine Semantic Type (Most assets are ASSET, but some might be CONTAINER like Cabinets)
        semantic_type = SemanticType.ASSET
        if asset.type and asset.type.upper() in ["CABINET", "MCC", "PANEL", "JUNCTION_BOX"]:
            semantic_type = SemanticType.CONTAINER

        node_create = NodeCreate(
            name=asset.tag,
            type=asset.type or "UNKNOWN",
            discipline=discipline,
            semantic_type=semantic_type,
            lod=2,  # Default to Equipment level
            isa95_level=1,  # Default to Equipment
            description=asset.description,
            properties={
                "area": asset.area,
                "system": asset.system,
                "manufacturer_part_id": asset.manufacturer_part_id,
            },
            project_id=asset.project_id,
        )

        return MetamodelService.create_node(db, node_create)
