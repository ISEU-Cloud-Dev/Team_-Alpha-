from fastapi import APIRouter
from app.api.endpoints import shorten, dashboard

api_router = APIRouter()

# Nota: el router de redirección (GET /{codigo}) YA NO se monta aquí.
# Iba con prefijo /api/v1 por error, cuando debe vivir en la raíz
# (localhost:8000/{codigo}). Se monta directo en app/main.py.

# Endpoint para el Desarrollador 1 (Generar URLs cortas)
api_router.include_router(shorten.router, prefix="/shorten", tags=["Shorten"])

# Endpoint para usted como Líder Alfa (Métricas globales)
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
