from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auditoria import crear_evento_auditoria
from app.core.database import get_db
from app.models.caso import Caso
from app.models.tarea import Tarea
from app.schemas.caso import (
    CasoCreate,
    CasoCreateResponse,
    CasoResponse,
    CasoUpdateEstado,
    ESTADOS_CASO,
    TRANSICIONES_VALIDAS,
)
from app.schemas.tarea import (
    AGENTES_TAREA,
    ESTADOS_TAREA,
    PRIORIDADES_TAREA,
    TareaCompletar,
    TareaCreate,
    TareaResponse,
)

router = APIRouter(prefix="/casos", tags=["Casos"])


@router.get("/", response_model=list[CasoResponse])
def listar_casos(db: Session = Depends(get_db)):
    return db.query(Caso).order_by(Caso.created_at.desc()).all()


@router.post("/", response_model=CasoCreateResponse, status_code=status.HTTP_201_CREATED)
def crear_caso(data: CasoCreate, db: Session = Depends(get_db)):
    estado = (data.estado or "ABIERTO").upper()
    if estado not in ESTADOS_CASO:
        raise HTTPException(status_code=422, detail="Estado inválido")

    caso = Caso(
        titulo=data.titulo,
        descripcion=data.descripcion,
        estado=estado,
    )
    db.add(caso)
    db.flush()

    crear_evento_auditoria(
        db,
        caso.id,
        "CASO_CREADO",
        "Caso creado",
        usuario_id=data.usuario_id,
        usuario_nombre=data.usuario_nombre,
    )
    db.commit()
    db.refresh(caso)

    return {
        "ok": True,
        "caso": caso,
    }


@router.patch("/{caso_id}/estado", response_model=CasoResponse)
def actualizar_estado_caso(caso_id: int, data: CasoUpdateEstado, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    estado_nuevo = data.estado.upper()
    estado_actual = caso.estado.upper()

    if estado_nuevo not in ESTADOS_CASO:
        raise HTTPException(status_code=422, detail="Estado inválido")

    if estado_nuevo not in TRANSICIONES_VALIDAS.get(estado_actual, []):
        raise HTTPException(
            status_code=422,
            detail=f"Transición inválida de {estado_actual} a {estado_nuevo}",
        )

    caso.estado = estado_nuevo
    db.add(caso)
    db.flush()

    crear_evento_auditoria(
        db,
        caso.id,
        "ESTADO_CAMBIADO",
        f"Estado cambiado de {estado_actual} a {estado_nuevo}",
        usuario_id=data.usuario_id,
        usuario_nombre=data.usuario_nombre,
    )
    db.commit()
    db.refresh(caso)

    return caso


@router.post("/{caso_id}/tareas", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
def crear_tarea(caso_id: int, data: TareaCreate, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    agente = data.agente.upper()
    prioridad = data.prioridad.upper()
    estado = data.estado.upper()

    if agente not in AGENTES_TAREA:
        raise HTTPException(status_code=422, detail="Agente inválido")
    if prioridad not in PRIORIDADES_TAREA:
        raise HTTPException(status_code=422, detail="Prioridad inválida")
    if estado not in ESTADOS_TAREA:
        raise HTTPException(status_code=422, detail="Estado inválido")

    tarea = Tarea(
        caso_id=caso.id,
        titulo=data.titulo,
        descripcion=data.descripcion,
        responsable=data.responsable,
        agente=agente,
        prioridad=prioridad,
        estado=estado,
        fecha_vencimiento=data.fecha_vencimiento,
    )
    db.add(tarea)
    db.flush()

    crear_evento_auditoria(
        db,
        caso.id,
        "TAREA_ASIGNADA",
        f"Tarea asignada: {tarea.titulo}",
        usuario_id=data.usuario_id,
        usuario_nombre=data.usuario_nombre,
    )
    db.commit()
    db.refresh(tarea)

    return tarea


@router.get("/{caso_id}/tareas", response_model=list[TareaResponse])
def listar_tareas_por_caso(caso_id: int, db: Session = Depends(get_db)):
    caso = db.query(Caso).filter(Caso.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return db.query(Tarea).filter(Tarea.caso_id == caso_id).order_by(Tarea.fecha_creacion.desc()).all()


@router.patch("/tareas/{tarea_id}/completar", response_model=TareaResponse)
def completar_tarea(tarea_id: int, data: TareaCompletar, db: Session = Depends(get_db)):
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    estado_nuevo = data.estado.upper()
    if estado_nuevo not in {"COMPLETADA", "CANCELADA"}:
        raise HTTPException(status_code=422, detail="Estado inválido para finalización")

    tarea.estado = estado_nuevo
    tarea.fecha_cierre = datetime.now(timezone.utc)
    db.add(tarea)
    db.flush()

    crear_evento_auditoria(
        db,
        tarea.caso_id,
        "TAREA_COMPLETADA",
        f"Tarea completada: {tarea.titulo}",
        usuario_id=data.usuario_id,
        usuario_nombre=data.usuario_nombre,
    )
    db.commit()
    db.refresh(tarea)

    return tarea