from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.email == data.email).first()
    if usuario_existente:
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    usuario = Usuario(
        nombre=data.nombre,
        email=data.email,
        activo=data.activo if data.activo is not None else True,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.get("", response_model=list[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).order_by(Usuario.fecha_creacion.desc()).all()
