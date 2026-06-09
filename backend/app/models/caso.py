from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Caso(Base):
    __tablename__ = "casos"

    id = Column(Integer, primary_key=True, index=True)

    titulo = Column(String(255), nullable=False)

    descripcion = Column(Text)

    estado = Column(String(50), default="abierto")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    eventos = relationship("Evento", back_populates="caso", cascade="all, delete-orphan")
    tareas = relationship("Tarea", back_populates="caso", cascade="all, delete-orphan")