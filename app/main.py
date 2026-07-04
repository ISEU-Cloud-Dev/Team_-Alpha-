from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
)

# Configurar el motor de plantillas para renderizar la UI
templates = Jinja2Templates(directory="app/templates")

# Incluir el enrutador central de la API
app.include_router(api_router, prefix=settings.API_V1_STR)

# Cambiar la raíz para que muestre el diseño del Dashboard
# Cambiar la raíz para que muestre el diseño del Dashboard con la sintaxis correcta
@app.get("/", response_class=HTMLResponse, tags=["UI"])
def render_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,             # <--- Parámetro explícito primero
        name="index.html"            # <--- Nombre del archivo segundo
    )