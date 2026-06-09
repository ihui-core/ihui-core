import uuid
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    caso_id = Column(Integer, ForeignKey("casos.id"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    tipo_evento = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=False)
    usuario_nombre = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    caso = relationship("Caso", back_populates="eventos")
    usuario = relationship("Usuario", back_populates="eventos")
