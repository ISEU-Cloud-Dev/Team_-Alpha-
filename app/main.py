from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.router import api_router
from app.api.endpoints.redirect import router as redirect_router
from app.core.database import engine
from app.models.link import Base as LinkBase
from app.models.visit import Base as VisitBase

# Inicialización de las tablas de la base de datos
LinkBase.metadata.create_all(bind=engine)
VisitBase.metadata.create_all(bind=engine)

app = FastAPI(title="Alpha URL Shortener API", version="1.0.0")

# 1. Montar archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar motor de plantillas HTML
templates = Jinja2Templates(directory="app/templates")

# 2. Ruta para ver la interfaz gráfica completa
@app.get("/dashboard")
def render_dashboard(request: Request):
    # Pasamos 'request' primero, seguido de la plantilla y el contexto
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )

# Rutas de la API
app.include_router(api_router, prefix="/api/v1")
app.include_router(redirect_router)

@app.get("/")
def read_root():
    return {"status": "ok", "project": "Team Alpha Shortener"}