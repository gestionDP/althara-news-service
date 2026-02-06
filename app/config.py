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

    # News Studio / UI
    UI_USER: Optional[str] = None
    UI_PASS: Optional[str] = None
    INGEST_TOKEN: Optional[str] = None

    # RSS ingestion limits per source
    TECH_RSS_LIMIT_PER_SOURCE: int = 5
    REAL_ESTATE_RSS_LIMIT_PER_SOURCE: int = 5

    # IG generation
    AUTO_GENERATE_IG_AFTER_INGEST: bool = True
    IG_DEFAULT_TONE: str = "neutral"
    IG_VARIANTS_COUNT: int = 3

    # Studio default brand (optional)
    STUDIO_BRAND_DEFAULT: Optional[str] = "althara"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

