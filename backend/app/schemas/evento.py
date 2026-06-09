from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


EVENTO_TIPOS_CATALOGO = [
    "CASO_CREADO",
    "ESTADO_CAMBIADO",
    "COMENTARIO",
    "TAREA_ASIGNADA",
    "TAREA_COMPLETADA",
    "DOCUMENTO_AGREGADO",
    "DECISION_REGISTRADA",
    "CASO_CERRADO",
]


def normalizar_tipo_evento(value: str) -> str:
    tipo = value.strip().upper()
    if tipo not in EVENTO_TIPOS_CATALOGO:
        raise ValueError(
            f"tipo_evento no permitido. Catálogo actual: {', '.join(EVENTO_TIPOS_CATALOGO)}"
        )
    return tipo


class EventoBase(BaseModel):
    caso_id: int
    tipo_evento: str = Field(..., min_length=1, max_length=50)
    descripcion: str = Field(..., min_length=1)
    usuario_id: Optional[int] = None
    usuario_nombre: Optional[str] = Field(default=None, max_length=255)


class EventoCreate(EventoBase):
    pass


class EventoResponse(EventoBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
