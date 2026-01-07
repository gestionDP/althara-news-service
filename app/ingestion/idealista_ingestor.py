"""
News ingestor from Idealista API.

Takes items from IdealistaClient and inserts them into the database,
avoiding duplicates.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.ingestion.idealista_client import IdealistaClient, IdealistaNewsItem
from app.ingestion.rss_ingestor import _is_relevant_to_real_estate
from app.models.news import News


async def ingest_idealista_news(session: AsyncSession) -> int:
    """
    Ingests news from Idealista.
    Applies relevance filter to ensure only real estate news is inserted.
    
    Args:
        session: Async database session
        
    Returns:
        Number of news items inserted
    """
    client = IdealistaClient()
    items = await client.fetch_news(limit=20)
    
    inserted_count = 0
    
    for item in items:
        # Apply relevance filter - only insert real estate relevant news
        if not _is_relevant_to_real_estate(item.title, item.raw_summary):
            continue
        
        stmt = select(News).where(News.url == item.url)
        result = await session.execute(stmt)
        existing_news = result.scalar_one_or_none()
        
        if existing_news is None:
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
    
    if inserted_count > 0:
        await session.commit()
    
    return inserted_count





