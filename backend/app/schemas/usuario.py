from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import uuid

class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    activo: Optional[bool] = True

class UsuarioResponse(BaseModel):
    id: uuid.UUID
    nombre: str
    email: str
    rol: str
    activo: bool
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True
