import random
import string
from sqlalchemy.orm import Session
from app.models.link import Link

CARACTERES = string.ascii_letters + string.digits
LONGITUD_CODIGO = 6


def generar_codigo() -> str:
    """Genera un código aleatorio alfanumérico de 6 caracteres."""
    return "".join(random.choices(CARACTERES, k=LONGITUD_CODIGO))


def generar_codigo_unico(db: Session) -> str:
    """
    Genera un código y verifica que no exista ya en la tabla urls.
    Si choca (colisión, muy improbable), genera otro hasta encontrar uno libre.
    """
    while True:
        codigo = generar_codigo()
        existe = db.query(Link).filter(Link.url_corta == codigo).first()
        if not existe:
            return codigo