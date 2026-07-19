from pydantic import BaseModel
from typing import List, Dict

class ClickChronology(BaseModel):
    fecha: str
    clicks: int

class CountryMetric(BaseModel):
    pais: str
    clicks: int
    porcentaje: float

class DeviceMetric(BaseModel):
    dispositivo: str
    clicks: int

class DashboardAnalyticsResponse(BaseModel):
    total_links_creados: int
    total_links_activos: int
    total_clicks_globales: int
    clicks_por_dia: List[ClickChronology]
    top_paises: List[CountryMetric]
    top_dispositivos: List[DeviceMetric]