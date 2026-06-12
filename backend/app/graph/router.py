from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.graph.schemas import FactIngest, NodeCreate, EdgeCreate
from app.graph.services import GraphService

router = APIRouter(prefix="/graph", tags=["IHUI Graph"])

@router.post("/ingest-fact")
async def ingerir_hecho(
    payload: FactIngest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    node = GraphService.create_node(db, payload.node)

    if payload.relations:
        for edge_data in payload.relations:
            if not edge_data.source_id:
                edge_data.source_id = node["id"]
            background_tasks.add_task(GraphService.create_edge, db, edge_data)

    return {"status": "ok", "node_id": node["id"], "type": node["type"]}

@router.get("/node/{node_id}")
def obtener_contexto(node_id: str, db: Session = Depends(get_db)):
    return GraphService.get_node_context(db, node_id)

@router.get("/search")
def buscar_nodos(
    type: str = None,
    title: str = None,
    app_source: str = None,
    db: Session = Depends(get_db)
):
    from sqlalchemy import text
    filters = ["valid_to IS NULL"]
    params = {}

    if type:
        filters.append("type = :type")
        params["type"] = type
    if title:
        filters.append("title ILIKE :title")
        params["title"] = f"%{title}%"
    if app_source:
        filters.append("app_source = :app_source")
        params["app_source"] = app_source

    where = " AND ".join(filters)
    result = db.execute(
        text(f"SELECT id, type, title, status, app_source, valid_from FROM core_graph.nodes WHERE {where} ORDER BY valid_from DESC LIMIT 50"),
        params
    ).fetchall()

    return [dict(r._mapping) for r in result]
