from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

# Cargar variables de entorno
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.database import Base
from app.models.news import News  # Importar todos los modelos

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def normalize_database_url(url: str) -> str:
    """
    Normalizar la URL de base de datos para asyncpg.
    
    - Convierte postgresql:// a postgresql+asyncpg://
    - Elimina parámetros incompatibles con asyncpg (como sslmode, channel_binding)
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
        
        # asyncpg no acepta sslmode, channel_binding, etc. como query params
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


def get_url():
    """Obtener y normalizar DATABASE_URL desde variables de entorno"""
    raw_url = os.getenv("DATABASE_URL", "")
    return normalize_database_url(raw_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_async_migrations())
