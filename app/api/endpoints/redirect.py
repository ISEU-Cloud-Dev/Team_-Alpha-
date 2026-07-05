"""
Endpoint de Redirección Inmediata - Desarrollador 3
Rama: feature/shorten-endpoint

GET /{codigo}

Flujo (Cache-Aside):
    1. Buscar el código en Redis (rápido, en memoria).
    2. Si existe (HIT) -> redirigir de inmediato.
       Si no existe (MISS) -> buscarlo en PostgreSQL.
         - Si existe en PostgreSQL -> guardarlo en Redis para la próxima vez
           y redirigir.
         - Si no existe en ninguno -> 404.
    3. En TODOS los casos de éxito, capturar la metadata de la visita
       (IP, país, dispositivo, navegador) y despacharla en un
       BackgroundTask, para NO bloquear la respuesta de redirección
       esperando escribir en la base de datos.

Nota para Dev 2 (persistencia de la tabla `visitas`):
    La función `despachar_metadata_visita()` de este archivo es donde se
    arma el diccionario con la metadata ya calculada (url_id, ip, país,
    dispositivo, navegador, fecha). Por ahora solo se deja registrado
    (log) para que tú conectes ahí el INSERT real a la tabla `visitas`
    con tu modelo de app/models/visit.py. Si necesitas columnas nuevas
    (pais, dispositivo, navegador) en el modelo/migración, aquí ya te
    dejo el dato listo para guardar. Cualquier duda, coordinar con el
    ing. Jorge para la parte de la migración de la DB.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import RedirectResponse
from fastapi import HTTPException, status

from app.core.database import SessionLocal
from app.core.redis_cache import get_cached_url, set_cached_url
from app.api.services.geo_ip import get_country_from_ip, parse_user_agent
from app.models.link import Link

logger = logging.getLogger("redirect_endpoint")

router = APIRouter()

# 302 = redirección TEMPORAL. Se usa a propósito en vez de 301 (permanente):
# los navegadores cachean agresivamente las redirecciones 301 y dejarían de
# volver a pedirle el código a esta API, lo que rompería el conteo de clics
# y las analíticas del dashboard.
REDIRECT_STATUS_CODE = status.HTTP_302_FOUND


def _obtener_ip_cliente(request: Request) -> str:
    """
    Obtiene el IP real del cliente. Si la app corre detrás de un proxy /
    load balancer (común en despliegues como Railway), el IP real viene
    en el header X-Forwarded-For y no en request.client.host.
    """
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # X-Forwarded-For puede traer una lista "ip1, ip2, ip3" -> el primero
        # es el cliente original.
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"


def _buscar_link_en_postgres(codigo: str) -> Link | None:
    """
    Consulta PostgreSQL solo cuando hubo un cache MISS en Redis.
    Abre y cierra su propia sesión para no depender de una dependencia
    global de DB que todavía no existe en app/core/database.py.
    """
    db = SessionLocal()
    try:
        return db.query(Link).filter(Link.url_corta == codigo).first()
    finally:
        db.close()


def despachar_metadata_visita(
    codigo: str,
    url_id: int,
    ip: str,
    pais: str,
    dispositivo: str,
    navegador: str,
) -> None:
    """
    Tarea que corre en segundo plano (no bloquea la redirección al usuario).

    Por ahora solo deja un log estructurado con toda la metadata calculada.
    Dev 2 debe reemplazar/ampliar el cuerpo de esta función con el INSERT
    real hacia la tabla `visitas` (app/models/visit.py), agregando las
    columnas que hagan falta (pais, dispositivo, navegador) vía migración.
    """
    metadata_visita = {
        "url_id": url_id,
        "codigo": codigo,
        "ip_usuario": ip,
        "pais": pais,
        "dispositivo": dispositivo,
        "navegador": navegador,
        "fecha": datetime.now(timezone.utc).isoformat(),
    }
    # TODO (Dev 2): Insertar `metadata_visita` en la tabla `visitas` aquí,
    # usando una sesión propia de SessionLocal (igual que en
    # _buscar_link_en_postgres) para no compartir sesión con el request.
    logger.info("Visita registrada (pendiente de persistir): %s", metadata_visita)


@router.get(
    "/{codigo}",
    summary="Redirigir a la URL original",
    description=(
        "Recibe un código corto, verifica primero en Redis (cache-aside), "
        "si no está lo busca en PostgreSQL, y redirige de inmediato al "
        "destino original. Registra la metadata de la visita de forma "
        "asíncrona sin bloquear la respuesta."
    ),
    response_class=RedirectResponse,
    status_code=REDIRECT_STATUS_CODE,
)
async def redirigir_codigo(codigo: str, request: Request, background_tasks: BackgroundTasks):
    # 1. Cache-Aside: primero Redis
    url_larga = await get_cached_url(codigo)
    link_id: int | None = None

    if url_larga is None:
        # 2. Cache MISS -> buscar en PostgreSQL
        link = _buscar_link_en_postgres(codigo)
        if link is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El código no existe o el enlace ya no está disponible.",
            )
        url_larga = link.url_larga
        link_id = link.id
        # Guardar en caché para que la próxima petición sea instantánea
        await set_cached_url(codigo, url_larga)
    else:
        # Cache HIT: igual necesitamos el id del link para registrar la
        # visita correctamente, así que lo buscamos (esto es rápido y no
        # bloquea la redirección porque ocurre en background).
        pass

    # 3. Capturar metadata de la visita (no bloquea la redirección)
    ip_cliente = _obtener_ip_cliente(request)
    user_agent = request.headers.get("user-agent", "")
    dispositivo, navegador = parse_user_agent(user_agent)
    pais = await get_country_from_ip(ip_cliente)

    def _tarea_background():
        # Si veníamos de un cache HIT y no tenemos el id todavía,
        # lo resolvemos aquí dentro del background task para no demorar
        # la redirección con una consulta extra a PostgreSQL.
        nonlocal link_id
        if link_id is None:
            link = _buscar_link_en_postgres(codigo)
            link_id = link.id if link else None
        despachar_metadata_visita(
            codigo=codigo,
            url_id=link_id,
            ip=ip_cliente,
            pais=pais,
            dispositivo=dispositivo,
            navegador=navegador,
        )

    background_tasks.add_task(_tarea_background)

    # 4. Redirección inmediata (lo primero que le llega al usuario)
    return RedirectResponse(url=url_larga, status_code=REDIRECT_STATUS_CODE)