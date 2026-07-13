from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.dashboard import DashboardAnalyticsResponse
from app.api.services.analytics import AnalyticsService
from app.core.database import get_db

router = APIRouter()


@router.get(
    "/",
    response_model=DashboardAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener analíticas globales",
    description="Retorna las métricas consolidadas (clics, países, dispositivos) para renderizar el Dashboard.",
)
def get_global_analytics(db: Session = Depends(get_db)):
    try:
        analytics_data = AnalyticsService.get_global_dashboard_data(db)
        return analytics_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar las analíticas del sistema: {str(e)}",
        )