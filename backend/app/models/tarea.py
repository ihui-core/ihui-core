from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id"), nullable=False)

    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    responsable = Column(String(255), nullable=False)
    agente = Column(String(50), nullable=False)
    prioridad = Column(String(20), nullable=False, default="MEDIA")
    estado = Column(String(20), nullable=False, default="PENDIENTE")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_vencimiento = Column(DateTime(timezone=True), nullable=True)
    fecha_cierre = Column(DateTime(timezone=True), nullable=True)

    caso = relationship("Caso", back_populates="tareas")
