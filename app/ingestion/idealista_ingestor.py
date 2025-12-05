"""
Ingestor de noticias desde Idealista API.

Toma los items de IdealistaClient y los inserta en la base de datos,
evitando duplicados.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.ingestion.idealista_client import IdealistaClient, IdealistaNewsItem
from app.models.news import News


async def ingest_idealista_news(session: AsyncSession) -> int:
    """
    Ingesta noticias desde Idealista.
    
    Args:
        session: Sesión de base de datos async
        
    Returns:
        Número de noticias insertadas
    """
    client = IdealistaClient()
    items = await client.fetch_news(limit=20)
    
    inserted_count = 0
    
    for item in items:
        # Verificar si ya existe una noticia con la misma URL
        stmt = select(News).where(News.url == item.url)
        result = await session.execute(stmt)
        existing_news = result.scalar_one_or_none()
        
        if existing_news is None:
            # Crear nuevo registro News
            new_news = News(
                title=item.title,
                source=item.source,
                url=item.url,
                published_at=item.published_at,
                category=item.category,
                raw_summary=item.raw_summary,
                althara_summary=None,
                tags=item.tags,
                used_in_social=False
            )
            session.add(new_news)
            inserted_count += 1
    
    # Commit una sola vez al final
    if inserted_count > 0:
        await session.commit()
    
    return inserted_count

