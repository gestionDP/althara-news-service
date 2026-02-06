from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

load_dotenv()

Base = declarative_base()


def normalize_database_url(url: str) -> str:
    """
    Normalize database URL for asyncpg.
    
    - Converts postgresql:// to postgresql+asyncpg://
    - Removes incompatible parameters (like sslmode)
    - asyncpg handles SSL automatically
    """
    if not url:
        return url
    
    if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    parsed = urlparse(url)
    
    if parsed.query:
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        
        incompatible_params = ['sslmode', 'channel_binding']
        for param in incompatible_params:
            query_params.pop(param, None)
        
        if query_params:
            new_query = urlencode(query_params, doseq=True)
        else:
            new_query = ""
        
        url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    
    return url


_raw_database_url = os.getenv("DATABASE_URL")

if _raw_database_url:
    DATABASE_URL = normalize_database_url(_raw_database_url)
else:
    DATABASE_URL = None

if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
    if not DATABASE_URL.startswith("postgresql+asyncpg://"):
        raise ValueError(
            f"ERROR: DATABASE_URL must use asyncpg driver.\n"
            f"Current format: {DATABASE_URL[:50]}...\n"
            f"Correct format: postgresql+asyncpg://user:password@host/database"
        )
    
    _echo = os.getenv("SQL_ECHO", "false").lower() in ("1", "true", "yes")
    engine = create_async_engine(
        DATABASE_URL,
        echo=_echo,
        future=True,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
else:
    engine = None
    AsyncSessionLocal = None


async def get_db():
    if AsyncSessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
