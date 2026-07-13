from pydantic import BaseModel, HttpUrl
from datetime import date


class LinkCreate(BaseModel):
    """Lo que el cliente envía al crear un link (POST /shorten)."""
    url_larga: HttpUrl


class LinkResponse(BaseModel):
    """Lo que la API devuelve tras crear o consultar un link."""
    id: int
    url_larga: str
    url_corta: str
    fecha_creacion: date
    clicks: int

    class Config:
        from_attributes = True  # permite crear este schema directo desde el modelo SQLAlchemy Link