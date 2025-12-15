"""
Microservice configuration using Pydantic Settings.

Loads environment variables and provides a global configuration instance.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Microservice configuration from environment variables"""
    
    DATABASE_URL: str
    
    IDEALISTA_API_BASE_URL: Optional[str] = None
    IDEALISTA_API_KEY: Optional[str] = None
    IDEALISTA_API_SECRET: Optional[str] = None
    
    IDEALISTA_BASE_URL: Optional[str] = None
    IDEALISTA_PDF_BASE_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

