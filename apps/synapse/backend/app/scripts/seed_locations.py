import logging

from app.core.database import SessionLocal
from app.models.auth import Project
from app.models.metamodel import DisciplineType, SemanticType
from app.schemas.metamodel import EdgeCreate, NodeCreate
from app.services.metamodel import MetamodelService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_locations():
    db = SessionLocal()
    try:
        # 1. Get Project
        project_name = "Gold Mine"
        project = db.query(Project).filter(Project.name.ilike(f"%{project_name}%")).first()

        if not project:
            # Fallback to Default Project if Gold Mine not found
            project = db.query(Project).filter(Project.name == "Default Project").first()

        if not project:
            logger.error("No project found. Please run seed_initial_data.py first.")
            return

        logger.info(f"Seeding locations for project: {project.name} ({project.id})")

        # 2. Define Location Hierarchy
        locations = [
            # Level 4: Site
            {
                "name": "Gold Mine Site",
                "type": "SITE",
                "discipline": DisciplineType.GENERAL,
                "semantic_type": SemanticType.CONTAINER,
                "isa95_level": 4,
                "description": "Main mine site location",
                "properties": {"address": "123 Mine Road"},
            },
            # Level 3: Areas
            {
                "name": "100 - Feed System",
                "type": "AREA",
                "discipline": DisciplineType.PROCESS,
                "semantic_type": SemanticType.CONTAINER,
                "isa95_level": 3,
                "description": "Crushing and conveying area",
                "properties": {"area_code": "100"},
            },
            {
                "name": "310 - Grinding",
                "type": "AREA",
                "discipline": DisciplineType.PROCESS,
                "semantic_type": SemanticType.CONTAINER,
                "isa95_level": 3,
                "description": "Grinding and milling area",
                "properties": {"area_code": "310"},
            },
            # Level 2: Rooms (in 310)
            {
                "name": "310-ER-01",
                "type": "ROOM",
                "discipline": DisciplineType.ELECTRICAL,
                "semantic_type": SemanticType.CONTAINER,
                "isa95_level": 2,
                "description": "Electrical Room 01 in Area 310",
                "properties": {"room_type": "Electrical"},
            },
            {
                "name": "310-CR-01",
                "type": "ROOM",
                "discipline": DisciplineType.AUTOMATION,
                "semantic_type": SemanticType.CONTAINER,
                "isa95_level": 2,
                "description": "Control Room 01 in Area 310",
                "properties": {"room_type": "Control"},
            },
            # Level 1: Cabinets (in 310-ER-01)
            {
                "name": "310-MCC-01",
                "type": "CABINET",
                "discipline": DisciplineType.ELECTRICAL,
                "semantic_type": SemanticType.CONTAINER,
                "isa95_level": 1,
                "description": "Motor Control Center 01",
                "properties": {"voltage": "600V", "manufacturer": "Eaton"},
            },
            {
                "name": "310-PLC-01",
                "type": "CABINET",
                "discipline": DisciplineType.AUTOMATION,
                "semantic_type": SemanticType.CONTAINER,
                "isa95_level": 1,
                "description": "Main PLC Cabinet",
                "properties": {"manufacturer": "Rockwell"},
            },
        ]

        # 3. Create Nodes
        created_nodes = {}
        for loc_data in locations:
            node_in = NodeCreate(
                name=loc_data["name"],
                type=loc_data["type"],
                discipline=loc_data["discipline"],
                semantic_type=loc_data["semantic_type"],
                isa95_level=loc_data["isa95_level"],
                description=loc_data["description"],
                properties=loc_data["properties"],
                project_id=project.id,
                lod=1,  # Macro level
            )
            node = MetamodelService.create_node(db, node_in)
            created_nodes[loc_data["name"]] = node
            logger.info(f"Created/Updated node: {node.name} ({node.id})")

        # 4. Create Edges (Hierarchy)
        edges = [
            # Site -> Areas
            ("Gold Mine Site", "100 - Feed System", "contains"),
            ("Gold Mine Site", "310 - Grinding", "contains"),
            # Area 310 -> Rooms
            ("310 - Grinding", "310-ER-01", "contains"),
            ("310 - Grinding", "310-CR-01", "contains"),
            # Room 310-ER-01 -> Cabinets
            ("310-ER-01", "310-MCC-01", "contains"),
            ("310-ER-01", "310-PLC-01", "contains"),
        ]

        for source_name, target_name, relation in edges:
            source = created_nodes.get(source_name)
            target = created_nodes.get(target_name)

            if source and target:
                edge_in = EdgeCreate(
                    source_node_id=source.id,
                    target_node_id=target.id,
                    relation_type=relation,
                    discipline=DisciplineType.PROJECT,
                )
                MetamodelService.create_edge(db, edge_in)
                logger.info(f"Created edge: {source.name} --[{relation}]--> {target.name}")
            else:
                logger.warning(
                    f"Could not create edge {source_name} -> {target_name}: Node not found"
                )

        logger.info("Location seeding completed successfully!")

    except Exception as e:
        logger.error(f"Error seeding locations: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_locations()
