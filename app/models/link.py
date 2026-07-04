from sqlalchemy import Column, Integer, String, Text, Date
from app.core.database import Base

class Link(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url_larga = Column(Text, nullable=False)
    url_corta = Column(String(10), unique=True, nullable=False, index=True)
    fecha_creacion = Column(Date, nullable=False)
    clicks = Column(Integer, default=0)