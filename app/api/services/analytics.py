from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
# Nota: Estas importaciones se activarán cuando Jorge (Dev 2) suba sus modelos
# from app.models.link import Link
# from app.models.visit import Visit

class AnalyticsService:
    @staticmethod
    def get_global_dashboard_data(db: Session) -> dict:
        """
        Calcula y consolida las métricas globales para las gráficas del Dashboard.
        """
        # 1. Obtener totales globales (Simulado mientras Jorge termina las tablas)
        # total_links = db.query(Link).count()
        # total_clicks = db.query(Link).with_entities(func.sum(Link.clicks)).scalar() or 0
        total_links = 124  # Datos base de prueba (Mock)
        total_clicks = 4850

        # 2. Clicks por día (Últimos 7 días)
        clicks_por_dia = []
        hoy = datetime.utcnow()
        for i in range(6, -1, -1):
            dia = hoy - timedelta(days=i)
            clicks_por_dia.append({
                "fecha": dia.strftime("%Y-%m-%d"),
                "clicks": 500 + (i * 75)  # Mock de comportamiento
            })

        # 3. Top Países con cálculo de porcentaje
        top_paises = [
            {"pais": "México", "clicks": 2500, "porcentaje": round((2500 / total_clicks) * 100, 2)},
            {"pais": "Estados Unidos", "clicks": 1350, "porcentaje": round((1350 / total_clicks) * 100, 2)},
            {"pais": "Colombia", "clicks": 1000, "porcentaje": round((1000 / total_clicks) * 100, 2)}
        ]

        # 4. Distribución por Dispositivo
        top_dispositivos = [
            {"dispositivo": "Mobile", "clicks": 3100},
            {"dispositivo": "Desktop", "clicks": 1500},
            {"dispositivo": "Tablet", "clicks": 250}
        ]

        return {
            "total_links_activos": total_links,
            "total_clicks_globales": total_clicks,
            "clicks_por_dia": clicks_por_dia,
            "top_paises": top_paises,
            "top_dispositivos": top_dispositivos
        }