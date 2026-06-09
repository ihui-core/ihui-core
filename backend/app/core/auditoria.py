from typing import Optional, Tuple

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.evento import Evento
from app.models.usuario import Usuario


def resolver_contexto_usuario(
    db: Session,
    usuario_id: Optional[int] = None,
    usuario_nombre: Optional[str] = None,
) -> Tuple[Optional[int], Optional[str]]:
    if usuario_id is None and usuario_nombre is None:
        return None, None

    if usuario_id is not None:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        nombre = (usuario_nombre or usuario.nombre).strip() if usuario_nombre or usuario.nombre else None
        return usuario.id, nombre

    nombre = usuario_nombre.strip() if usuario_nombre else None
    return None, nombre


def crear_evento_auditoria(
    db: Session,
    caso_id: int,
    tipo_evento: str,
    descripcion: str,
    usuario_id: Optional[int] = None,
    usuario_nombre: Optional[str] = None,
) -> Evento:
    usuario_id_resuelto, usuario_nombre_resuelto = resolver_contexto_usuario(
        db,
        usuario_id=usuario_id,
        usuario_nombre=usuario_nombre,
    )
    evento = Evento(
        caso_id=caso_id,
        tipo_evento=tipo_evento,
        descripcion=descripcion,
        usuario_id=usuario_id_resuelto,
        usuario_nombre=usuario_nombre_resuelto,
    )
    db.add(evento)
    return evento
