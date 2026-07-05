"""
Servicio de Geolocalización y detección de dispositivo - Desarrollador 3

Dos responsabilidades:
    1. get_country_from_ip(ip): dado un IP, devuelve el país (vía API pública).
    2. parse_user_agent(ua_string): dado el header User-Agent, devuelve
       una tupla (dispositivo, navegador).

Ambas funciones están pensadas para nunca lanzar una excepción hacia el
endpoint de redirección: si algo falla (sin internet, IP inválida, etc.)
devuelven valores por defecto ("Desconocido") en vez de tumbar la petición.
"""

import ipaddress
import logging

import httpx
from user_agents import parse as parse_ua

logger = logging.getLogger("geo_ip")

# API pública y gratuita para geolocalización por IP.
# No requiere API key para uso moderado (ver https://ip-api.com/docs).
IP_API_URL = "http://ip-api.com/json/{ip}"
REQUEST_TIMEOUT_SECONDS = 1.5


def _es_ip_privada_o_local(ip: str) -> bool:
    """
    Detecta IPs privadas/locales (127.0.0.1, 10.x.x.x, 192.168.x.x, ::1, etc.)
    En desarrollo local (docker-compose) el IP del cliente casi siempre
    cae en este caso, por lo que no tiene sentido consultar la API externa.
    """
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        # Si no es una IP válida (ej. "testclient" en pruebas), tratarla como local.
        return True


async def get_country_from_ip(ip: str) -> str:
    """
    Devuelve el país correspondiente a una IP pública.
    Para IPs privadas/locales o si la API externa falla, devuelve
    "Local/Desconocido" o "Desconocido" respectivamente, sin lanzar error.
    """
    if _es_ip_privada_o_local(ip):
        return "Local/Desconocido"

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(
                IP_API_URL.format(ip=ip),
                params={"fields": "status,country"},
            )
            data = response.json()
            if data.get("status") == "success":
                return data.get("country", "Desconocido")
            return "Desconocido"
    except Exception as exc:
        logger.warning("No se pudo geolocalizar el IP %s: %s", ip, exc)
        return "Desconocido"


def parse_user_agent(user_agent_string: str) -> tuple[str, str]:
    """
    Analiza el header User-Agent y devuelve (dispositivo, navegador).

    dispositivo: "Móvil", "Tablet", "PC" u "Otro/Bot"
    navegador: familia del navegador según user-agents (ej. "Chrome", "Firefox")
    """
    if not user_agent_string:
        return "Otro/Bot", "Desconocido"

    try:
        ua = parse_ua(user_agent_string)

        if ua.is_mobile:
            dispositivo = "Móvil"
        elif ua.is_tablet:
            dispositivo = "Tablet"
        elif ua.is_pc:
            dispositivo = "PC"
        else:
            dispositivo = "Otro/Bot"

        navegador = ua.browser.family or "Desconocido"
        return dispositivo, navegador
    except Exception as exc:
        logger.warning("No se pudo parsear el User-Agent '%s': %s", user_agent_string, exc)
        return "Otro/Bot", "Desconocido"