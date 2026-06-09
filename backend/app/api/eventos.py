from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auditoria import crear_evento_auditoria
from app.core.database import get_db
from app.models.caso import Caso
from app.models.evento import Evento
from app.schemas.evento import (
    EventoCreate,
    EventoResponse,
    normalizar_tipo_evento,
)

router = APIRouter(tags=["Eventos"])


@router.get("/eventos", response_model=list[EventoResponse])
def listar_eventos(db: Session = Depends(get_db)):
    return db.query(Evento).order_by(Evento.created_at.asc()).all()


@router.post(
    "/eventos",
    response_model=EventoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_evento(data: EventoCreate, db: Session = Depends(get_db)):
    try:
        tipo_evento = normalizar_tipo_evento(data.tipo_evento)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    caso = db.query(Caso).filter(Caso.id == data.caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado")

    evento = crear_evento_auditoria(
        db,
        data.caso_id,
        tipo_evento,
        data.descripcion,
        usuario_id=data.usuario_id,
        usuario_nombre=data.usuario_nombre,
    )
    db.commit()
    db.refresh(evento)
    return evento


@router.get("/casos/{caso_id}/eventos", response_model=list[EventoResponse])
def listar_eventos_por_caso(caso_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Evento)
        .filter(Evento.caso_id == caso_id)
        .order_by(Evento.created_at.asc())
        .all()
    )