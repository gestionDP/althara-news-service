"""
Admin router for managing news ingestion.

NOTE: Idealista does NOT have a news API, so we only use RSS sources.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, exists
from app.database import get_db
from app.config import settings
from app.ingestion.rss_ingestor import ingest_rss_sources
from app.models.news import News
from app.models.ig_draft import IGDraft
from app.adapters.news_adapter import build_all_content_structured
from app.adapters.ig_adapter import generate_ig_draft

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/ingest")
async def ingest_news(db: AsyncSession = Depends(get_db)):
    """
    Main endpoint to trigger news ingestion from RSS sources.
    
    Ingests news from all configured RSS sources.
    Uses REAL_ESTATE_RSS_LIMIT_PER_SOURCE from config.
    
    Returns:
        JSON with dictionary of sources and number of news items inserted
    """
    limit = settings.REAL_ESTATE_RSS_LIMIT_PER_SOURCE
    results = await ingest_rss_sources(db, max_items_per_source=limit)
    return results


@router.post("/ingest/rss")
async def ingest_rss(db: AsyncSession = Depends(get_db)):
    """
    Alternative endpoint to trigger ingestion from RSS sources.
    Alias for the main /ingest endpoint.
    """
    limit = settings.REAL_ESTATE_RSS_LIMIT_PER_SOURCE
    results = await ingest_rss_sources(db, max_items_per_source=limit)
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
        (News.althara_summary.is_(None)) | 
        (News.instagram_post.is_(None)) | 
        (News.althara_content.is_(None))
    )
    result = await db.execute(stmt)
    pending_news = result.scalars().all()
    
    adapted_count = 0
    
    for news in pending_news:
        try:
            althara_summary, instagram_post, structured_content = build_all_content_structured(
                title=news.title,
                raw_summary=news.raw_summary,
                category=news.category,
                source=news.source,
                url=news.url,
                published_at=news.published_at
            )
            
            if not news.althara_summary:
                news.althara_summary = althara_summary
            if not news.instagram_post:
                news.instagram_post = instagram_post
            if not news.althara_content:
                news.althara_content = structured_content
            
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
async def ingest_and_adapt(
    db: AsyncSession = Depends(get_db),
    generate_ig: bool = Query(False, description="Generate IG drafts for new news"),
):
    """
    All-in-one endpoint: ingests news and adapts them to Althara tone.
    
    Useful for external automation (cloud services, remote cron jobs, etc.).
    Executes the full pipeline: ingest → adapt → (optional) IG drafts.
    
    Returns:
        Compact JSON with process summary (optimized for cron jobs)
    """
    limit = settings.REAL_ESTATE_RSS_LIMIT_PER_SOURCE
    ingest_results = await ingest_rss_sources(db, max_items_per_source=limit)
    total_inserted = sum(ingest_results.values())
    
    stmt = select(News).where(
        (News.althara_summary.is_(None)) | 
        (News.instagram_post.is_(None)) | 
        (News.althara_content.is_(None))
    )
    result = await db.execute(stmt)
    pending_news = result.scalars().all()
    
    adapted_count = 0
    
    for news in pending_news:
        try:
            althara_summary, instagram_post, structured_content = build_all_content_structured(
                title=news.title,
                raw_summary=news.raw_summary,
                category=news.category,
                source=news.source,
                url=news.url,
                published_at=news.published_at
            )
            
            if not news.althara_summary:
                news.althara_summary = althara_summary
            if not news.instagram_post:
                news.instagram_post = instagram_post
            if not news.althara_content:
                news.althara_content = structured_content
            
            adapted_count += 1
        except Exception as e:
            continue
    
    drafts_generated = 0
    if generate_ig and settings.AUTO_GENERATE_IG_AFTER_INGEST:
        # Generate IG drafts for real_estate news without draft
        has_draft = exists().where(IGDraft.news_id == News.id)
        stmt = (
            select(News)
            .where(News.domain == "real_estate")
            .where(~has_draft)
            .order_by(News.published_at.desc())
            .limit(15)
        )
        res = await db.execute(stmt)
        for news in res.scalars().all():
            try:
                draft_data = generate_ig_draft(news, brand="althara")
                draft = IGDraft(news_id=news.id, **draft_data)
                db.add(draft)
                drafts_generated += 1
            except Exception:
                continue

    if adapted_count > 0 or drafts_generated > 0:
        await db.commit()

    return {
        "status": "ok",
        "ingested": total_inserted,
        "adapted": adapted_count,
        "drafts_generated": drafts_generated,
        "sources_processed": len([v for v in ingest_results.values() if v > 0]),
    }


@router.delete("/clean")
async def clean_news_by_domain(
    db: AsyncSession = Depends(get_db),
    domain: str = Query("real_estate", description="Domain to delete: real_estate (Althara) or tech (Oxono). Use 'all' to delete everything."),
):
    """
    Deletes news by domain. Use domain=real_estate for Althara, domain=tech for Oxono.
    Use domain=all to delete ALL news (irreversible).
    Drafts cascade-delete with their news.
    """
    if domain == "all":
        delete_stmt = delete(News)
    else:
        delete_stmt = delete(News).where(News.domain == domain)

    count_stmt = select(func.count()).select_from(News).where(News.domain == domain) if domain != "all" else select(func.count()).select_from(News)
    count_result = await db.execute(count_stmt)
    total_count = count_result.scalar_one()

    await db.execute(delete_stmt)
    await db.commit()

    return {
        "status": "ok",
        "deleted": total_count,
        "domain": domain,
        "message": f"Deleted {total_count} news items (domain={domain})",
    }


@router.delete("/clean-all")
async def clean_all_news(db: AsyncSession = Depends(get_db)):
    """Alias for DELETE /clean?domain=all - deletes ALL news. WARNING: irreversible."""
    return await clean_news_by_domain(db=db, domain="all")

