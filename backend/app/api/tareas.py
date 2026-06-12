from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.tarea import Tarea
from app.models.usuario import Usuario

router = APIRouter(prefix="/tareas", tags=["Tareas"])

class TareaCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    nodo_id: Optional[uuid.UUID] = None
    nodo_titulo: Optional[str] = None
    nodo_tipo: Optional[str] = None
    responsable_ref: str
    prioridad: str = "MEDIA"
    fecha_vencimiento: Optional[datetime] = None

class TareaResponse(BaseModel):
    id: int
    titulo: str
    descripcion: Optional[str]
    nodo_titulo: Optional[str]
    nodo_tipo: Optional[str]
    responsable: str
    responsable_ref: Optional[str]
    prioridad: str
    estado: str
    fecha_creacion: Optional[datetime]
    fecha_vencimiento: Optional[datetime]

    class Config:
        from_attributes = True

@router.post("", response_model=TareaResponse)
def crear_tarea(
    data: TareaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    tarea = Tarea(
        titulo=data.titulo,
        descripcion=data.descripcion,
        nodo_id=data.nodo_id,
        nodo_titulo=data.nodo_titulo,
        nodo_tipo=data.nodo_tipo,
        responsable=data.responsable_ref,
        responsable_ref=data.responsable_ref,
        agente="humano",
        prioridad=data.prioridad,
        estado="PENDIENTE",
        fecha_vencimiento=data.fecha_vencimiento,
    )
    db.add(tarea)
    db.commit()
    db.refresh(tarea)
    return tarea

@router.get("/mis-tareas", response_model=list[TareaResponse])
def mis_tareas(
    incluir_completadas: bool = False,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(Tarea).filter(
        or_(
            Tarea.responsable_ref == current_user.email,
            Tarea.responsable_ref == current_user.nombre,
        )
    )
    if not incluir_completadas:
        query = query.filter(Tarea.estado != "COMPLETADA")
    return query.order_by(Tarea.fecha_creacion.desc()).all()

@router.get("", response_model=list[TareaResponse])
def listar_tareas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return db.query(Tarea).order_by(Tarea.fecha_creacion.desc()).all()

@router.patch("/{tarea_id}/completar", response_model=TareaResponse)
def completar_tarea(
    tarea_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    tarea.estado = "COMPLETADA"
    tarea.fecha_cierre = datetime.now(timezone.utc)
    db.commit()
    db.refresh(tarea)
    return tarea
