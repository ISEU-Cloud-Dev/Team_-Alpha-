from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Visit(Base):
    __tablename__ = "visitas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    ip_usuario = Column(String(45), nullable=False)
    pais = Column(String(100), nullable=True)
    dispositivo = Column(String(50), nullable=True)
    navegador = Column(String(50), nullable=True)