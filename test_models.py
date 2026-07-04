from app.core.database import SessionLocal
from app.models.link import Link
from app.models.visit import Visit
from datetime import date

db = SessionLocal()

nuevo_link = Link(
    url_larga="https://www.ejemplo.com/pagina-muy-larga",
    url_corta="abc123",
    fecha_creacion=date.today(),
    clicks=0
)
db.add(nuevo_link)
db.commit()
db.refresh(nuevo_link)

nueva_visita = Visit(
    url_id=nuevo_link.id,
    ip_usuario="192.168.1.1"
)
db.add(nueva_visita)
db.commit()

print("Link creado:", nuevo_link.id, nuevo_link.url_corta)
print("Visita creada:", nueva_visita.id, "asociada a url_id:", nueva_visita.url_id)

db.close()