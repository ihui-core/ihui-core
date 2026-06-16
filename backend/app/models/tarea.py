import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id"), nullable=True)

    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)

    # Vínculo flexible al grafo
    nodo_id = Column(UUID(as_uuid=True), nullable=True)
    nodo_titulo = Column(String(255), nullable=True)
    nodo_tipo = Column(String(50), nullable=True)

    responsable = Column(String(255), nullable=False)
    responsable_ref = Column(String(255), nullable=True)
    asignado_por = Column(String(255), nullable=True)
    tarea_padre_id = Column(Integer, ForeignKey("tareas.id", ondelete="SET NULL"), nullable=True)
    dueno_ref = Column(String(255), nullable=True)
    cerrado_por = Column(String(255), nullable=True)
    agente = Column(String(50), nullable=False)
    prioridad = Column(String(20), nullable=False, default="MEDIA")
    estado = Column(String(20), nullable=False, default="PENDIENTE")

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_vencimiento = Column(DateTime(timezone=True), nullable=True)
    fecha_cierre = Column(DateTime(timezone=True), nullable=True)

    caso = relationship("Caso", back_populates="tareas")
    hijas = relationship("Tarea", backref="padre", remote_side=[id])
