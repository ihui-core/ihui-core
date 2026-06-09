from typing import Optional

from pydantic import BaseModel, Field

ESTADOS_CASO = ["ABIERTO", "EN_PROCESO", "PENDIENTE", "RESUELTO", "CERRADO"]

TRANSICIONES_VALIDAS = {
    "ABIERTO": ["EN_PROCESO"],
    "EN_PROCESO": ["PENDIENTE", "RESUELTO"],
    "PENDIENTE": ["RESUELTO", "CERRADO"],
    "RESUELTO": ["CERRADO"],
    "CERRADO": [],
}


class CasoCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    estado: Optional[str] = Field(default="ABIERTO")
    usuario_id: Optional[int] = None
    usuario_nombre: Optional[str] = None


class CasoResponse(BaseModel):
    id: int
    titulo: str
    descripcion: Optional[str] = None
    estado: str

    class Config:
        from_attributes = True


class CasoCreateResponse(BaseModel):
    ok: bool
    caso: CasoResponse


class CasoUpdateEstado(BaseModel):
    estado: str = Field(..., min_length=1)
    usuario_id: Optional[int] = None
    usuario_nombre: Optional[str] = None
