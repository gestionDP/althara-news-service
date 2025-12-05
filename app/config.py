"""
Configuración del microservicio usando Pydantic Settings.

Carga las variables de entorno y proporciona una instancia global de configuración.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración del microservicio desde variables de entorno"""
    
    DATABASE_URL: str
    
    # Configuración Idealista API
    IDEALISTA_API_BASE_URL: Optional[str] = None
    IDEALISTA_API_KEY: Optional[str] = None
    IDEALISTA_API_SECRET: Optional[str] = None
    
    # Configuración Idealista API - Consultas de propiedades (gpapeleo)
    # Nota: Esta API es para consultas de propiedades, no para noticias
    IDEALISTA_BASE_URL: Optional[str] = None  # URL para consultas de propiedades
    IDEALISTA_PDF_BASE_URL: Optional[str] = None  # URL para PDFs
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()

