"""
Admin router for managing news ingestion.

NOTE: Idealista does NOT have a news API, so we only use RSS sources.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.database import get_db
from app.ingestion.rss_ingestor import ingest_rss_sources
from app.models.news import News
from app.adapters.news_adapter import build_all_content

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/ingest")
async def ingest_news(db: AsyncSession = Depends(get_db)):
    """
    Main endpoint to trigger news ingestion from RSS sources.
    
    Ingests news from all configured RSS sources:
    - Expansion Inmobiliario
    - Cinco Días
    - El Economista
    - BOE Subastas
    - BOE General
    - Observatorio Inmobiliario
    - Interempresas Construcción
    
    Returns:
        JSON with dictionary of sources and number of news items inserted
    """
    results = await ingest_rss_sources(db)
    return results


@router.post("/ingest/rss")
async def ingest_rss(db: AsyncSession = Depends(get_db)):
    """
    Alternative endpoint to trigger ingestion from RSS sources.
    Alias for the main /ingest endpoint.
    
    Returns:
        JSON with dictionary of sources and number of news items inserted
    """
    results = await ingest_rss_sources(db)
    return results


@router.post("/adapt-pending")
async def adapt_pending_news(db: AsyncSession = Depends(get_db)):
    """
    Adapt pending news items to Althara tone and generate Instagram posts.
    
    Finds all news items without althara_summary or instagram_post and adapts them
    using the Althara adapter. Generates both althara_summary and instagram_post.
    
    Returns:
        JSON with number of adapted news items
    """
    stmt = select(News).where(
        (News.althara_summary.is_(None)) | (News.instagram_post.is_(None))
    )
    result = await db.execute(stmt)
    pending_news = result.scalars().all()
    
    adapted_count = 0
    
    for news in pending_news:
        try:
            althara_summary, instagram_post = build_all_content(
                title=news.title,
                raw_summary=news.raw_summary,
                category=news.category,
                source=news.source,
                url=news.url
            )
            
            if not news.althara_summary:
                news.althara_summary = althara_summary
            if not news.instagram_post:
                news.instagram_post = instagram_post
            
            adapted_count += 1
        except Exception as e:
            print(f"Error adapting news {news.id}: {e}")
            continue
    
    if adapted_count > 0:
        await db.commit()
    
    return {
        "adapted": adapted_count,
        "message": f"Adapted {adapted_count} news items to Althara tone and generated Instagram posts"
    }


@router.post("/ingest-and-adapt")
async def ingest_and_adapt(db: AsyncSession = Depends(get_db)):
    """
    All-in-one endpoint: ingests news and adapts them to Althara tone.
    
    Useful for external automation (cloud services, remote cron jobs, etc.).
    Executes the full pipeline: ingest → adapt → ready to use.
    
    Returns:
        Compact JSON with process summary (optimized for cron jobs)
    """
    ingest_results = await ingest_rss_sources(db, max_items_per_source=10)
    total_inserted = sum(ingest_results.values())
    
    stmt = select(News).where(
        (News.althara_summary.is_(None)) | (News.instagram_post.is_(None))
    )
    result = await db.execute(stmt)
    pending_news = result.scalars().all()
    
    adapted_count = 0
    
    for news in pending_news:
        try:
            althara_summary, instagram_post = build_all_content(
                title=news.title,
                raw_summary=news.raw_summary,
                category=news.category,
                source=news.source,
                url=news.url
            )
            
            if not news.althara_summary:
                news.althara_summary = althara_summary
            if not news.instagram_post:
                news.instagram_post = instagram_post
            
            adapted_count += 1
        except Exception as e:
            continue
    
    if adapted_count > 0:
        await db.commit()
    
    return {
        "status": "ok",
        "ingested": total_inserted,
        "adapted": adapted_count,
        "sources_processed": len([v for v in ingest_results.values() if v > 0])
    }


@router.delete("/clean-all")
async def clean_all_news(db: AsyncSession = Depends(get_db)):
    """
    Deletes ALL news items from the database.
    
    WARNING: This operation is irreversible.
    Useful for cleaning and re-ingesting with new improvements.
    
    Returns:
        JSON with number of deleted news items
    """
    count_stmt = select(func.count()).select_from(News)
    count_result = await db.execute(count_stmt)
    total_count = count_result.scalar_one()
    
    delete_stmt = delete(News)
    await db.execute(delete_stmt)
    await db.commit()
    
    return {
        "status": "ok",
        "deleted": total_count,
        "message": f"Deleted {total_count} news items from database"
    }

