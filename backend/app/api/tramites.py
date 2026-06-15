from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permisos import puede_asignar
from app.models.tramite import TipoTramite, PlantillaTarea
from app.models.usuario import Usuario

router = APIRouter(prefix="/tramites", tags=["Tipos de tramite"])

class TipoTramiteCreate(BaseModel):
    nombre: str
    clave: str

class PlantillaTareaCreate(BaseModel):
    tipo_tramite_id: int
    titulo: str
    rol_sugerido: Optional[str] = None
    orden: int = 0
    evento_disparador: Optional[str] = None

class PlantillaTareaResponse(BaseModel):
    id: int
    tipo_tramite_id: int
    titulo: str
    rol_sugerido: Optional[str]
    orden: int
    evento_disparador: Optional[str]
    class Config:
        from_attributes = True

class TipoTramiteResponse(BaseModel):
    id: int
    nombre: str
    clave: str
    activo: bool
    plantilla: list[PlantillaTareaResponse] = []
    class Config:
        from_attributes = True

@router.get("", response_model=list[TipoTramiteResponse])
def listar_tramites(db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return db.query(TipoTramite).filter(TipoTramite.activo == True).all()

@router.post("", response_model=TipoTramiteResponse)
def crear_tramite(data: TipoTramiteCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if not puede_asignar(current_user):
        raise HTTPException(status_code=403, detail="No tienes permiso para crear tipos de trámite")
    tramite = TipoTramite(nombre=data.nombre, clave=data.clave)
    db.add(tramite)
    db.commit()
    db.refresh(tramite)
    return tramite

@router.post("/plantilla", response_model=PlantillaTareaResponse)
def agregar_plantilla(data: PlantillaTareaCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    if not puede_asignar(current_user):
        raise HTTPException(status_code=403, detail="No tienes permiso para editar plantillas")
    tramite = db.query(TipoTramite).filter(TipoTramite.id == data.tipo_tramite_id).first()
    if not tramite:
        raise HTTPException(status_code=404, detail="Tipo de trámite no encontrado")
    paso = PlantillaTarea(
        tipo_tramite_id=data.tipo_tramite_id,
        titulo=data.titulo,
        rol_sugerido=data.rol_sugerido,
        orden=data.orden,
        evento_disparador=data.evento_disparador,
    )
    db.add(paso)
    db.commit()
    db.refresh(paso)
    return paso
