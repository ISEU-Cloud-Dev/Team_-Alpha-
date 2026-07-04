from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn

class Settings(BaseSettings):
    # Configuración de la API
    PROJECT_NAME: str = "URL Shortener API"
    PROJECT_VERSION: str = "1.0.0"  # <--- ¡Asegúrate de agregar esta línea!
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"

    # Configuración de Base de Datos (PostgreSQL)
    # Se usa PostgresDsn para validar que la URL tenga el formato correcto
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/shortener_db"

    # Configuración de Caché (Redis)
    REDIS_URL: str = "redis://redis:6379/0"

    # Configuración para leer el archivo .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instancia global para importar en todo el proyecto
settings = Settings()