from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

ESTADOS_TAREA = ["PENDIENTE", "EN_PROCESO", "COMPLETADA", "CANCELADA"]
PRIORIDADES_TAREA = ["BAJA", "MEDIA", "ALTA", "CRITICA"]
AGENTES_TAREA = ["HUMANO", "CODEX", "CLAUDE_CODE", "SISTEMA"]


class TareaCreate(BaseModel):
    titulo: str = Field(..., min_length=1)
    descripcion: Optional[str] = None
    responsable: str = Field(..., min_length=1)
    agente: str = Field(..., min_length=1)
    prioridad: str = Field(default="MEDIA")
    estado: str = Field(default="PENDIENTE")
    fecha_vencimiento: Optional[datetime] = None
    usuario_id: Optional[int] = None
    usuario_nombre: Optional[str] = None


class TareaResponse(BaseModel):
    id: int
    caso_id: int
    titulo: str
    descripcion: Optional[str] = None
    responsable: str
    agente: str
    prioridad: str
    estado: str
    fecha_creacion: Optional[datetime] = None
    fecha_vencimiento: Optional[datetime] = None
    fecha_cierre: Optional[datetime] = None

    class Config:
        from_attributes = True


class TareaCompletar(BaseModel):
    estado: str = Field(default="COMPLETADA")
    usuario_id: Optional[int] = None
    usuario_nombre: Optional[str] = None
