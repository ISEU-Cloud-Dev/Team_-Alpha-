from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import random, string
from datetime import datetime
from app.core.database import SessionLocal
from app.models.link import Link
from app.models.visit import Visit
router = APIRouter()
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
def generar_codigo(longitud=6): return "".join(random.choices(string.ascii_letters + string.digits, k=longitud))
@router.post("/shorten")
def acortar_url(url_larga: str, db: Session = Depends(get_db)):
    for _ in range(5):
        codigo = generar_codigo()
        if not db.query(Link).filter(Link.url_corta == codigo).first(): break
    nuevo_link = Link(url_larga=url_larga, url_corta=codigo, clicks=0, fecha_creacion=datetime.utcnow())
    db.add(nuevo_link); db.commit(); db.refresh(nuevo_link)
    return {"url_corta": codigo, "url_larga": url_larga}
@router.get("/{codigo}")
def redirigir_url(codigo: str, request: Request, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.url_corta == codigo).first()
    if not link: raise HTTPException(status_code=404, detail="Enlace no encontrado")
    nueva_visita = Visit(url_id=link.id, ip_usuario=request.client.host)
    link.clicks += 1; db.add(nueva_visita); db.commit()
    return RedirectResponse(url=link.url_larga, status_code=307)
