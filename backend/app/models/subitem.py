from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class TareaSubitem(Base):
    __tablename__ = "tarea_subitems"

    id = Column(Integer, primary_key=True, index=True)
    tarea_id = Column(Integer, ForeignKey("tareas.id", ondelete="CASCADE"), nullable=False)
    texto = Column(String(500), nullable=False)
    completado = Column(Boolean, nullable=False, default=False)
    orden = Column(Integer, nullable=False, default=0)
    evento_disparador = Column(String(100), nullable=True)
    completado_por = Column(String(255), nullable=True)
    fecha_completado = Column(DateTime(timezone=True), nullable=True)
