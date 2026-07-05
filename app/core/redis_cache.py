"""
Módulo de Caché (Redis) - Desarrollador 3

Implementa la estrategia Cache-Aside para las redirecciones:
    1. Al pedir un código, primero se busca en Redis.
    2. Si no está (cache miss), quien llama debe buscarlo en PostgreSQL
       y luego guardarlo aquí con set_cached_url() para la próxima vez.

Se usa el cliente asíncrono de redis-py (redis.asyncio) para no bloquear
el event loop de FastAPI mientras se espera la respuesta de Redis.
"""

import os
import logging
from typing import Optional

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger("redis_cache")

# TTL (tiempo de vida) por defecto de cada código en caché, en segundos.
# 3600 = 1 hora. Se puede sobreescribir con la variable de entorno
# REDIS_CACHE_TTL sin necesidad de tocar core/config.py.
DEFAULT_TTL_SECONDS = int(os.getenv("REDIS_CACHE_TTL", "3600"))

# Prefijo para namespacing de las llaves en Redis (buena práctica para
# evitar colisiones si en el futuro se guardan otro tipo de datos).
KEY_PREFIX = "shortlink:"

# Cliente único (singleton) reutilizado en toda la app.
# decode_responses=True para trabajar directamente con str en vez de bytes.
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """
    Devuelve el cliente de Redis (lo crea una sola vez - patrón singleton).
    Se conecta usando REDIS_URL definido en app/core/config.py (Settings),
    que a su vez se llena desde la variable de entorno REDIS_URL / .env.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
    return _redis_client


def _build_key(codigo: str) -> str:
    return f"{KEY_PREFIX}{codigo}"


async def get_cached_url(codigo: str) -> Optional[str]:
    """
    Busca la URL larga asociada a `codigo` en Redis.

    Retorna la URL si existe (cache HIT) o None si no existe (cache MISS).
    Si Redis está caído, no debe tumbar la API: se hace log del error
    y se retorna None para que el flujo caiga a PostgreSQL.
    """
    client = get_redis_client()
    try:
        return await client.get(_build_key(codigo))
    except Exception as exc:
        logger.warning("No se pudo leer de Redis (código=%s): %s", codigo, exc)
        return None


async def set_cached_url(codigo: str, url_larga: str, ttl: int = DEFAULT_TTL_SECONDS) -> None:
    """
    Guarda en Redis la relación codigo -> url_larga con un TTL definido.

    Se llama después de un cache MISS, justo después de haber consultado
    PostgreSQL, para que la próxima petición al mismo código sea servida
    directamente desde memoria (respuesta en milisegundos).
    """
    client = get_redis_client()
    try:
        await client.set(_build_key(codigo), url_larga, ex=ttl)
    except Exception as exc:
        # Si Redis falla al escribir no debe romper la redirección:
        # simplemente la próxima petición volverá a consultar PostgreSQL.
        logger.warning("No se pudo escribir en Redis (código=%s): %s", codigo, exc)


async def delete_cached_url(codigo: str) -> None:
    """
    Elimina un código de la caché. Útil para cuando el endpoint
    DELETE /link/{id} borre un enlace y haya que invalidar su caché.
    """
    client = get_redis_client()
    try:
        await client.delete(_build_key(codigo))
    except Exception as exc:
        logger.warning("No se pudo eliminar de Redis (código=%s): %s", codigo, exc)