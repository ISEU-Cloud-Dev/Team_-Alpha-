from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models.link import Link
from app.models.visit import Visit


class AnalyticsService:
    @staticmethod
    def get_global_dashboard_data(db: Session) -> dict:
        """
        Calcula y consolida las métricas globales para las gráficas del Dashboard.
        """
        # 1. Totales globales
        total_links_creados = db.query(Link).count()
        total_links_activos = db.query(Link).filter(Link.clicks >= 0).count()
        total_clicks = db.query(func.sum(Link.clicks)).scalar() or 0

        # 2. Clicks por día (últimos 7 días), basado en la tabla visitas
        clicks_por_dia = []
        hoy = datetime.utcnow().date()
        for i in range(6, -1, -1):
            dia = hoy - timedelta(days=i)
            conteo = (
                db.query(func.count(Visit.id))
                .filter(func.date(Visit.fecha) == dia)
                .scalar()
                or 0
            )
            clicks_por_dia.append({
                "fecha": dia.strftime("%Y-%m-%d"),
                "clicks": conteo,
            })

        # 3. Top países
        paises_query = (
            db.query(Visit.pais, func.count(Visit.id).label("clicks"))
            .filter(Visit.pais.isnot(None))
            .group_by(Visit.pais)
            .order_by(func.count(Visit.id).desc())
            .limit(5)
            .all()
        )
        top_paises = [
            {
                "pais": pais,
                "clicks": clicks,
                "porcentaje": round((clicks / total_clicks) * 100, 2) if total_clicks else 0,
            }
            for pais, clicks in paises_query
        ]

        # 4. Top dispositivos
        dispositivos_query = (
            db.query(Visit.dispositivo, func.count(Visit.id).label("clicks"))
            .filter(Visit.dispositivo.isnot(None))
            .group_by(Visit.dispositivo)
            .order_by(func.count(Visit.id).desc())
            .all()
        )
        top_dispositivos = [
            {"dispositivo": dispositivo, "clicks": clicks}
            for dispositivo, clicks in dispositivos_query
        ]

        return {
            "total_links_creados": total_links_creados,
            "total_links_activos": total_links_activos,
            "total_clicks_globales": total_clicks,
            "clicks_por_dia": clicks_por_dia,
            "top_paises": top_paises,
            "top_dispositivos": top_dispositivos,
        }