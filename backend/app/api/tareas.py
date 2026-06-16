from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid
from app.core.database import get_db
from app.core.permisos import puede_asignar
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
    asignado_por: Optional[str] = None
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
        estado="PENDING",
        fecha_vencimiento=data.fecha_vencimiento,
    )
    db.add(tarea)
    db.commit()
    db.refresh(tarea)
    return tarea

class TareaAsignar(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    nodo_id: Optional[uuid.UUID] = None
    nodo_titulo: Optional[str] = None
    nodo_tipo: Optional[str] = None
    responsable_ref: str  # a quién se le asigna (email o nombre)
    prioridad: str = "MEDIA"
    fecha_vencimiento: Optional[datetime] = None

@router.post("/asignar", response_model=TareaResponse)
def asignar_tarea(
    data: TareaAsignar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not puede_asignar(current_user):
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para asignar tareas a otros"
        )

    tarea = Tarea(
        titulo=data.titulo,
        descripcion=data.descripcion,
        nodo_id=data.nodo_id,
        nodo_titulo=data.nodo_titulo,
        nodo_tipo=data.nodo_tipo,
        responsable=data.responsable_ref,
        responsable_ref=data.responsable_ref,
        asignado_por=current_user.email,
        agente="humano",
        prioridad=data.prioridad,
        estado="PENDING",
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

class AsignarResponsable(BaseModel):
    responsable_ref: str

@router.get("/sin-asignar", response_model=list[TareaResponse])
def tareas_sin_asignar(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not puede_asignar(current_user):
        raise HTTPException(status_code=403, detail="No tienes permiso para ver la bandeja de asignación")
    return db.query(Tarea).filter(
        Tarea.responsable_ref.is_(None),
        Tarea.estado.notin_(["DONE", "CANCELLED"])
    ).order_by(Tarea.fecha_creacion.desc()).all()

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
    tarea.estado = "DONE"
    tarea.fecha_cierre = datetime.now(timezone.utc)
    db.commit()
    db.refresh(tarea)
    return tarea

ESTADOS_VALIDOS = {"PENDING", "IN_PROGRESS", "BLOCKED", "DONE", "CANCELLED"}

class CambiarEstado(BaseModel):
    estado: str

@router.patch("/{tarea_id}/estado", response_model=TareaResponse)
def cambiar_estado(
    tarea_id: int,
    data: CambiarEstado,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if data.estado not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Válidos: {ESTADOS_VALIDOS}")

    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    es_supervisor = puede_asignar(current_user)
    es_responsable = tarea.responsable_ref in (current_user.email, current_user.nombre)

    # Regla de Gil: CANCELLED solo supervisor
    if data.estado == "CANCELLED" and not es_supervisor:
        raise HTTPException(status_code=403, detail="Solo un supervisor puede cancelar una tarea")

    # El resto de estados: el responsable de la tarea o un supervisor
    if not es_responsable and not es_supervisor:
        raise HTTPException(status_code=403, detail="No tienes permiso para cambiar esta tarea")

    tarea.estado = data.estado
    if data.estado == "DONE":
        tarea.fecha_cierre = datetime.now(timezone.utc)
    db.commit()
    db.refresh(tarea)
    return tarea

@router.patch("/{tarea_id}/asignar-responsable", response_model=TareaResponse)
def asignar_responsable(
    tarea_id: int,
    data: AsignarResponsable,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not puede_asignar(current_user):
        raise HTTPException(status_code=403, detail="No tienes permiso para asignar tareas")
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    tarea.responsable = data.responsable_ref
    tarea.responsable_ref = data.responsable_ref
    if not tarea.asignado_por:
        tarea.asignado_por = current_user.email
    db.commit()
    db.refresh(tarea)
    return tarea
