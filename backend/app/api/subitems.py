from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.subitem import TareaSubitem
from app.models.tarea import Tarea
from app.models.usuario import Usuario

router = APIRouter(prefix="/subitems", tags=["Checklist"])

class SubitemCreate(BaseModel):
    tarea_id: int
    texto: str
    orden: int = 0
    evento_disparador: Optional[str] = None

class SubitemResponse(BaseModel):
    id: int
    tarea_id: int
    texto: str
    completado: bool
    orden: int
    evento_disparador: Optional[str]
    completado_por: Optional[str]
    fecha_completado: Optional[datetime]

    class Config:
        from_attributes = True

@router.get("/tarea/{tarea_id}", response_model=list[SubitemResponse])
def listar_subitems(
    tarea_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return db.query(TareaSubitem).filter(
        TareaSubitem.tarea_id == tarea_id
    ).order_by(TareaSubitem.orden).all()

@router.post("", response_model=SubitemResponse)
def crear_subitem(
    data: SubitemCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    tarea = db.query(Tarea).filter(Tarea.id == data.tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    sub = TareaSubitem(
        tarea_id=data.tarea_id,
        texto=data.texto,
        orden=data.orden,
        evento_disparador=data.evento_disparador,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

@router.patch("/{subitem_id}/toggle", response_model=SubitemResponse)
def toggle_subitem(
    subitem_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    sub = db.query(TareaSubitem).filter(TareaSubitem.id == subitem_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subitem no encontrado")
    sub.completado = not sub.completado
    if sub.completado:
        sub.completado_por = current_user.email
        sub.fecha_completado = datetime.now(timezone.utc)
    else:
        sub.completado_por = None
        sub.fecha_completado = None
    db.commit()
    db.refresh(sub)
    # NOTA FUTURA: si sub.evento_disparador y sub.completado -> emitir evento al grafo aquí
    return sub

@router.delete("/{subitem_id}")
def eliminar_subitem(
    subitem_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    sub = db.query(TareaSubitem).filter(TareaSubitem.id == subitem_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subitem no encontrado")
    db.delete(sub)
    db.commit()
    return {"status": "ok", "deleted": subitem_id}
