from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.core.database import get_db
from app.models.link import Link
from app.schemas.link import LinkCreate, LinkResponse
from app.api.services.shorten_service import generar_codigo_unico
from app.core.redis_cache import set_cached_url

router = APIRouter()


@router.post("/", response_model=LinkResponse)
async def crear_link_corto(payload: LinkCreate, db: Session = Depends(get_db)):
    codigo = generar_codigo_unico(db)

    nuevo_link = Link(
        url_larga=str(payload.url_larga),
        url_corta=codigo,
        fecha_creacion=date.today(),
        clicks=0,
    )
    db.add(nuevo_link)
    db.commit()
    db.refresh(nuevo_link)

    # Se guarda de inmediato en Redis para que la primera redirección
    # ya sea un cache HIT, sin esperar al primer cache miss.
    await set_cached_url(codigo, nuevo_link.url_larga)

    return nuevo_link

from typing import List


@router.get("/", response_model=List[LinkResponse])
def listar_links(db: Session = Depends(get_db)):
    return db.query(Link).order_by(Link.id.desc()).all()
from app.core.redis_cache import delete_cached_url


@router.delete("/{link_id}", status_code=204)
async def eliminar_link(link_id: int, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Enlace no encontrado")

    codigo = link.url_corta
    db.delete(link)
    db.commit()

    await delete_cached_url(codigo)