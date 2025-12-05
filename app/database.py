from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

load_dotenv()

# Base para modelos - puede importarse sin crear el engine
Base = declarative_base()


def normalize_database_url(url: str) -> str:
    """
    Normalizar la URL de base de datos para asyncpg.
    
    - Convierte postgresql:// a postgresql+asyncpg://
    - Elimina parámetros incompatibles con asyncpg (como sslmode)
    - asyncpg maneja SSL automáticamente, no necesita sslmode
    """
    if not url:
        return url
    
    # Convertir postgresql:// a postgresql+asyncpg://
    if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Parsear la URL para limpiar parámetros incompatibles
    parsed = urlparse(url)
    
    # Si tiene query parameters, limpiarlos
    if parsed.query:
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        
        # asyncpg no acepta sslmode, ssl, channel_binding, etc. como query params
        # Eliminar parámetros incompatibles
        incompatible_params = ['sslmode', 'channel_binding']
        for param in incompatible_params:
            query_params.pop(param, None)
        
        # Reconstruir query string solo si quedan parámetros válidos
        if query_params:
            new_query = urlencode(query_params, doseq=True)
        else:
            new_query = ""
        
        # Reconstruir URL sin los parámetros incompatibles
        url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    
    return url


# Obtener DATABASE_URL y normalizarla
_raw_database_url = os.getenv("DATABASE_URL")

# Normalizar la URL
if _raw_database_url:
    DATABASE_URL = normalize_database_url(_raw_database_url)
else:
    DATABASE_URL = None

# Solo crear engine si DATABASE_URL está disponible
# Esto evita errores cuando Alembic solo necesita importar Base
if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
    # Verificar que ahora use asyncpg
    if not DATABASE_URL.startswith("postgresql+asyncpg://"):
        raise ValueError(
            f"⚠️  ERROR: DATABASE_URL debe usar el driver asyncpg.\n"
            f"   Formato actual: {DATABASE_URL[:50]}...\n"
            f"   Formato correcto: postgresql+asyncpg://usuario:password@host/database"
        )
    
    # Crear engine async con la URL normalizada
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        future=True
    )
    
    # Crear session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
else:
    # Si no hay DATABASE_URL, crear variables None
    # Esto permite que Alembic importe Base sin problemas
    engine = None
    AsyncSessionLocal = None


# Dependency para obtener sesión
async def get_db():
    if AsyncSessionLocal is None:
        raise RuntimeError("DATABASE_URL no está configurada")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
