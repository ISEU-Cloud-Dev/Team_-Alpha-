from fastapi import APIRouter
from app.api.endpoints import shorten, redirect, dashboard

api_router = APIRouter()

# Endpoint para el Desarrollador 3 (Redirección inmediata en la raíz)
# Nota: Como GET /{codigo} va en la raíz, se monta directo o en su router respectivo
api_router.include_router(redirect.router, tags=["Redirection"])

# Endpoint para el Desarrollador 1 (Generar URLs cortas)
api_router.include_router(shorten.router, prefix="/shorten", tags=["Shorten"])

# Endpoint para usted como Líder Alfa (Métricas globales)
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])