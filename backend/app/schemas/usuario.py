from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    activo: Optional[bool] = True


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    activo: bool
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True
