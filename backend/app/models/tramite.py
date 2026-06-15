from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class TipoTramite(Base):
    __tablename__ = "tipos_tramite"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    clave = Column(String(50), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    plantilla = relationship("PlantillaTarea", back_populates="tipo_tramite", cascade="all, delete-orphan")

class PlantillaTarea(Base):
    __tablename__ = "plantilla_tareas"
    id = Column(Integer, primary_key=True, index=True)
    tipo_tramite_id = Column(Integer, ForeignKey("tipos_tramite.id", ondelete="CASCADE"), nullable=False)
    titulo = Column(String(255), nullable=False)
    rol_sugerido = Column(String(50), nullable=True)
    orden = Column(Integer, nullable=False, default=0)
    evento_disparador = Column(String(100), nullable=True)
    tipo_tramite = relationship("TipoTramite", back_populates="plantilla")
