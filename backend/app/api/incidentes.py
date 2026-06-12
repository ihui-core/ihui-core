from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
import httpx

router = APIRouter(prefix="/incidentes", tags=["Incidentes"])

class IncidenteCreate(BaseModel):
    titulo: str
    descripcion: str
    app_source: str
    tipo: str = "BUG"  # BUG, SUGERENCIA, FALLO, MEJORA
    prioridad: str = "MEDIA"  # BAJA, MEDIA, ALTA, CRITICA
    usuario_email: Optional[str] = None
    metadata: dict = {}

@router.post("")
def reportar_incidente(data: IncidenteCreate, db: Session = Depends(get_db)):
    import json
    import uuid

    node_id = str(uuid.uuid4())
    metadata = {
        "descripcion": data.descripcion,
        "tipo": data.tipo,
        "prioridad": data.prioridad,
        "usuario_email": data.usuario_email,
        **data.metadata
    }

    db.execute(text("""
        INSERT INTO core_graph.nodes
            (id, type, title, status, metadata, app_source)
        VALUES
            (:id, 'INCIDENTE', :title, :status, CAST(:metadata AS jsonb), :app_source)
    """), {
        "id": node_id,
        "title": f"[{data.tipo}] {data.titulo}",
        "status": data.prioridad,
        "metadata": json.dumps(metadata),
        "app_source": data.app_source,
    })
    db.commit()

    return {
        "status": "ok",
        "incidente_id": node_id,
        "mensaje": "Incidente registrado en la memoria institucional"
    }

@router.get("")
def listar_incidentes(
    app_source: Optional[str] = None,
    prioridad: Optional[str] = None,
    db: Session = Depends(get_db)
):
    filters = ["type = 'INCIDENTE'", "valid_to IS NULL"]
    params = {}

    if app_source:
        filters.append("app_source = :app_source")
        params["app_source"] = app_source
    if prioridad:
        filters.append("status = :prioridad")
        params["prioridad"] = prioridad

    where = " AND ".join(filters)
    result = db.execute(
        text(f"SELECT id, title, status, metadata, app_source, valid_from FROM core_graph.nodes WHERE {where} ORDER BY valid_from DESC"),
        params
    ).fetchall()

    return [dict(r._mapping) for r in result]

@router.patch("/{incidente_id}/resolver")
def resolver_incidente(incidente_id: str, db: Session = Depends(get_db)):
    from datetime import datetime, timezone
    db.execute(text("""
        UPDATE core_graph.nodes
        SET valid_to = :now
        WHERE id = :id AND type = 'INCIDENTE'
    """), {"id": incidente_id, "now": datetime.now(timezone.utc)})
    db.commit()
    return {"status": "ok", "mensaje": "Incidente resuelto"}
