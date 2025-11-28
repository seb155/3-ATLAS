import json
import os

import sqlalchemy
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.metamodel import DisciplineType, MetamodelEdge, MetamodelNode, SemanticType
from app.services.logger import SystemLog
from app.services.rule_engine import RuleEngine

router = APIRouter(
    prefix="/mock",
    tags=["mock"],
    responses={404: {"description": "Not found"}},
)


@router.post("/import-gold-mine")
def import_gold_mine(
    project_id: str = Header(None, alias="X-Project-ID"), db: Session = Depends(get_db)
):
    """
    Imports the Gold Mine Mock Data and runs the Engineering Rule Engine.
    """
    SystemLog.clear()
    SystemLog.log("INFO", f"Starting Gold Mine Import for Project: {project_id or 'Global'}")

    # 1. Load JSON
    file_path = os.path.join(os.path.dirname(__file__), "../mock_data/gold_mine.json")
    try:
        with open(file_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Mock data file not found") from None

    # 1.5 Ensure Project Exists
    if project_id:
        from app.models.auth import Client, Project

        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            SystemLog.log("INFO", f"Creating missing project: {project_id}")

            # Ensure a default client exists
            client = db.query(Client).filter(Client.name == "Default Client").first()
            if not client:
                client = Client(name="Default Client", contact_email="admin@example.com")
                db.add(client)
                db.flush()

            new_project = Project(
                id=project_id, name=project_id, description="Imported Project", client_id=client.id
            )
            db.add(new_project)
            db.commit()

    # 2. Create Areas and Assets in UNIFIED ASSETS TABLE
    from app.models.models import Asset

    for area in data.get("areas", []):
        SystemLog.log("INFO", f"Importing Area: {area['name']}")

        # Create Area in assets table (unified!)
        existing_area = (
            db.query(Asset)
            .filter(Asset.tag == area["name"], Asset.project_id == project_id)
            .first()
        )

        if not existing_area:
            area_asset = Asset(
                tag=area["name"],
                type="AREA",
                project_id=project_id,
                description=area["description"],
                discipline=DisciplineType.PROJECT.value,
                semantic_type=SemanticType.CONTAINER.value,
                lod=1,
                isa95_level=3,
                properties={"system": "General"},
            )
            db.add(area_asset)
            db.flush()
        else:
            area_asset = existing_area

        for asset in area.get("assets", []):
            # Check if asset already exists
            existing_asset = (
                db.query(Asset)
                .filter(Asset.tag == asset["tag"], Asset.project_id == project_id)
                .first()
            )

            if not existing_asset:
                # Create Asset in unified table
                new_asset = Asset(
                    tag=asset["tag"],
                    type=asset["type"],
                    project_id=project_id,
                    description=asset["description"],
                    discipline=(
                        DisciplineType.PROCESS.value
                        if asset["type"] in ["TANK", "PUMP"]
                        else DisciplineType.MECHANICAL.value
                    ),
                    semantic_type=SemanticType.ASSET.value,
                    lod=2,
                    isa95_level=1,
                    properties={
                        "area": area["name"],
                        "system": asset.get("system", "General"),
                        "work_package": asset.get("tag")
                        if asset["type"] in ["TANK", "PUMP", "AGITATOR", "MILL"]
                        else "Unassigned",
                    },
                )
                db.add(new_asset)
                db.flush()
                asset_id = new_asset.id
            else:
                asset_id = existing_asset.id

            # Link to Area via edge
            existing_edge = (
                db.query(MetamodelEdge)
                .filter(
                    MetamodelEdge.source_node_id == asset_id,
                    MetamodelEdge.target_node_id == area_asset.id,
                    MetamodelEdge.relation_type == "located_in",
                )
                .first()
            )

            if not existing_edge:
                edge = MetamodelEdge(
                    source_node_id=asset_id,
                    target_node_id=area_asset.id,
                    relation_type="located_in",
                    discipline=DisciplineType.PROJECT,
                )
                db.add(edge)

    db.commit()

    # 3. Run Rule Engine
    RuleEngine.apply_rules(db, project_id)

    return {"status": "Import Completed", "logs": SystemLog.get_logs()}


@router.get("/logs")
def get_system_logs():
    return SystemLog.get_logs()


@router.delete("/logs")
def clear_system_logs():
    SystemLog.clear()
    return {"status": "Logs Cleared"}


@router.delete("/project-data")
def clear_project_data(
    project_id: str = Header(None, alias="X-Project-ID"),
    include_global: bool = False,
    db: Session = Depends(get_db),
):
    if not project_id:
        raise HTTPException(status_code=400, detail="Project ID required")

    # Delete Assets
    from app.models.models import Asset

    deleted_assets = (
        db.query(Asset).filter(Asset.project_id == project_id).delete(synchronize_session=False)
    )

    # Delete Action Logs
    from app.models.action_log import ActionLog

    deleted_logs = (
        db.query(ActionLog)
        .filter(ActionLog.project_id == project_id)
        .delete(synchronize_session=False)
    )

    # Delete Metamodel Nodes (existing logic)
    filters = [MetamodelNode.project_id == project_id]
    if include_global:
        filters.append(MetamodelNode.project_id.is_(None))

    nodes_to_delete = (
        db.query(MetamodelNode)
        .filter(sqlalchemy.or_(*filters) if len(filters) > 1 else filters[0])
        .all()
    )

    node_ids = [n.id for n in nodes_to_delete]
    deleted_nodes = len(node_ids)
    deleted_edges = 0

    if node_ids:
        deleted_edges = (
            db.query(MetamodelEdge)
            .filter(
                (MetamodelEdge.source_node_id.in_(node_ids))
                | (MetamodelEdge.target_node_id.in_(node_ids))
            )
            .delete(synchronize_session=False)
        )

        db.query(MetamodelNode).filter(MetamodelNode.id.in_(node_ids)).delete(
            synchronize_session=False
        )

    db.commit()

    SystemLog.log(
        "INFO",
        f"Cleared data for Project: {project_id}. Assets: {deleted_assets}, "
        f"Logs: {deleted_logs}, Nodes: {deleted_nodes}, Edges: {deleted_edges}",
    )
    return {
        "status": "Project Data Cleared",
        "deleted": {
            "assets": deleted_assets,
            "logs": deleted_logs,
            "nodes": deleted_nodes,
            "edges": deleted_edges,
        },
    }
