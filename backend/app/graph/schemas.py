from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel
import uuid

class NodeCreate(BaseModel):
    type: str  # PERSONA, EMPRESA, DOCUMENTO, EVENTO, TAREA, INCIDENTE, BAJA
    title: str
    status: str = "ACTIVO"
    metadata: dict[str, Any] = {}
    app_source: Optional[str] = None
    valid_from: Optional[datetime] = None

class EdgeCreate(BaseModel):
    source_id: uuid.UUID
    target_id: uuid.UUID
    relation_type: str  # TRABAJA_EN, FIRMÓ_DOCUMENTO, REPORTÓ_BUG, BAJA_DE, ACCESO_A
    metadata: dict[str, Any] = {}
    app_source: Optional[str] = None

class FactIngest(BaseModel):
    node: NodeCreate
    relations: list[EdgeCreate] = []

class NodeResponse(BaseModel):
    id: uuid.UUID
    type: str
    title: str
    status: str
    metadata: dict[str, Any]
    app_source: Optional[str]
    system_created_at: datetime
    valid_from: datetime
    valid_to: Optional[datetime]

    class Config:
        from_attributes = True
