from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.metamodel import DisciplineType, MetamodelEdge, MetamodelNode, SemanticType
from app.schemas.metamodel import EdgeCreate, EdgeRead, GraphRead, NodeCreate, NodeRead
from app.services.metamodel import MetamodelService

router = APIRouter(
    prefix="/metamodel",
    tags=["metamodel"],
    responses={404: {"description": "Not found"}},
)

# --- Endpoints ---


@router.get("/graph", response_model=GraphRead)
def get_metamodel_graph(
    project_id: str | None = Header(None, alias="X-Project-ID"), db: Session = Depends(get_db)
):
    # Filter nodes by project_id OR where project_id is NULL (global/legacy)
    query = db.query(MetamodelNode)
    if project_id:
        query = query.filter(
            (MetamodelNode.project_id == project_id) | (MetamodelNode.project_id.is_(None))
        )
    else:
        query = query.filter(MetamodelNode.project_id.is_(None))

    nodes = query.all()
    node_ids = [n.id for n in nodes]

    # Filter edges where BOTH source and target are in the visible nodes
    edges = (
        db.query(MetamodelEdge)
        .filter(
            MetamodelEdge.source_node_id.in_(node_ids), MetamodelEdge.target_node_id.in_(node_ids)
        )
        .all()
    )

    return {"nodes": nodes, "edges": edges}


@router.post("/node", response_model=NodeRead)
def create_node(node: NodeCreate, db: Session = Depends(get_db)):
    return MetamodelService.create_node(db, node)


@router.post("/edge", response_model=EdgeRead)
def create_edge(edge: EdgeCreate, db: Session = Depends(get_db)):
    return MetamodelService.create_edge(db, edge)


@router.delete("/edge/{edge_id}")
def delete_edge(edge_id: str, db: Session = Depends(get_db)):
    edge = db.query(MetamodelEdge).filter(MetamodelEdge.id == edge_id).first()
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found")

    db.delete(edge)
    db.commit()
    return {"ok": True}


@router.post("/seed")
def seed_defaults(db: Session = Depends(get_db)):
    """Seed the Advanced Engineering Metamodel"""

    # Helper to create node
    def n(name, type, disc, sem, lod, isa95):
        return MetamodelService.create_node(
            db,
            NodeCreate(
                name=name, type=type, discipline=disc, semantic_type=sem, lod=lod, isa95_level=isa95
            ),
        )

    # 1. Hierarchy (LBS) - ISA95 Levels
    site = n("SITE", "LOCATION", DisciplineType.PROJECT, SemanticType.CONTAINER, 1, 4)
    area = n("AREA", "LOCATION", DisciplineType.PROJECT, SemanticType.CONTAINER, 1, 3)
    ehouse = n("EHOUSE", "LOCATION", DisciplineType.ELECTRICAL, SemanticType.CONTAINER, 1, 3)
    n("ROOM", "LOCATION", DisciplineType.PROJECT, SemanticType.CONTAINER, 1, 3)
    cabinet = n("CABINET", "LOCATION", DisciplineType.ELECTRICAL, SemanticType.CONTAINER, 2, 2)
    jb = n("JUNCTION_BOX", "LOCATION", DisciplineType.AUTOMATION, SemanticType.CONTAINER, 2, 2)

    # 2. Assets (Process)
    stream = n("STREAM", "ASSET", DisciplineType.PROCESS, SemanticType.LINK, 1, 1)
    valve = n("VALVE", "ASSET", DisciplineType.PROCESS, SemanticType.ASSET, 2, 1)
    tank = n("TANK", "ASSET", DisciplineType.PROCESS, SemanticType.ASSET, 2, 2)
    pump = n("PUMP", "ASSET", DisciplineType.MECHANICAL, SemanticType.ASSET, 2, 1)

    # 3. Assets (Electrical)
    mcc = n("MCC_600V", "ASSET", DisciplineType.ELECTRICAL, SemanticType.ASSET, 2, 2)
    transfo = n("TRANSFORMER", "ASSET", DisciplineType.ELECTRICAL, SemanticType.ASSET, 2, 2)
    panel = n("PANEL_120V", "ASSET", DisciplineType.ELECTRICAL, SemanticType.ASSET, 2, 2)
    motor = n("MOTOR", "ASSET", DisciplineType.ELECTRICAL, SemanticType.ASSET, 2, 1)

    # 4. Assets (Automation)
    inst = n("INSTRUMENT", "ASSET", DisciplineType.AUTOMATION, SemanticType.ASSET, 3, 0)
    control_sys = n("CONTROL_SYSTEM", "ASSET", DisciplineType.AUTOMATION, SemanticType.ASSET, 2, 2)
    io_card = n("IO_CARD", "ASSET", DisciplineType.AUTOMATION, SemanticType.ASSET, 3, 1)

    # Helper to create edge
    def e(src, tgt, rel, disc, props=None):
        if props is None:
            props = {}
        return MetamodelService.create_edge(
            db,
            EdgeCreate(
                source_node_id=src.id,
                target_node_id=tgt.id,
                relation_type=rel,
                discipline=disc,
                properties=props,
            ),
        )

    # --- Edges ---

    # Hierarchy
    e(site, area, "contains", DisciplineType.PROJECT)
    e(area, ehouse, "contains", DisciplineType.PROJECT)
    e(ehouse, cabinet, "contains", DisciplineType.ELECTRICAL)
    e(area, jb, "contains", DisciplineType.AUTOMATION)
    e(area, tank, "contains", DisciplineType.PROCESS)

    # Process Flow
    e(tank, pump, "feeds", DisciplineType.PROCESS, {"propagates": ["fluid"]})
    e(pump, valve, "feeds", DisciplineType.PROCESS, {"propagates": ["pressure", "flow"]})
    e(stream, valve, "flows_through", DisciplineType.PROCESS)
    e(stream, inst, "measured_by", DisciplineType.PROCESS)

    # Electrical Power
    e(mcc, motor, "powers", DisciplineType.ELECTRICAL, {"voltage": "600V"})
    e(mcc, transfo, "feeds", DisciplineType.ELECTRICAL, {"voltage": "600V"})
    e(transfo, panel, "feeds", DisciplineType.ELECTRICAL, {"voltage": "120V"})
    e(panel, inst, "powers", DisciplineType.ELECTRICAL, {"voltage": "24VDC"})

    # Automation / Control
    e(inst, jb, "connected_to", DisciplineType.AUTOMATION, {"signal": "4-20mA"})
    e(valve, jb, "controlled_by", DisciplineType.AUTOMATION)
    e(jb, cabinet, "homerun_to", DisciplineType.AUTOMATION, {"cable": "Multi-pair"})
    e(cabinet, control_sys, "contains", DisciplineType.AUTOMATION)
    e(control_sys, io_card, "has_card", DisciplineType.AUTOMATION)

    return {"status": "Seeded Advanced Metamodel"}
