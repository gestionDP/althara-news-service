"""
Tech admin router: ingest tech RSS, ingest-and-generate.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from app.database import get_db
from app.config import settings
from app.models.news import News
from app.models.ig_draft import IGDraft
from app.ingestion.tech_rss_ingestor import ingest_tech_rss_sources
from app.adapters.ig_adapter import generate_ig_draft

router = APIRouter(prefix="/api/tech/admin", tags=["tech-admin"])


@router.post("/ingest")
async def ingest_tech(db: AsyncSession = Depends(get_db)):
    """Ingest tech news from RSS sources."""
    results = await ingest_tech_rss_sources(
        db, max_items_per_source=settings.TECH_RSS_LIMIT_PER_SOURCE
    )
    return results


@router.post("/ingest-and-generate")
async def ingest_and_generate(db: AsyncSession = Depends(get_db)):
    """
    Ingest tech news and generate IG drafts for new/top-score items.
    """
    results = await ingest_tech_rss_sources(
        db, max_items_per_source=settings.TECH_RSS_LIMIT_PER_SOURCE
    )
    total_inserted = sum(results.values())

    if not settings.AUTO_GENERATE_IG_AFTER_INGEST:
        return {
            "status": "ok",
            "ingested": total_inserted,
            "drafts_generated": 0,
            "message": "Ingestion complete. AUTO_GENERATE_IG_AFTER_INGEST is false.",
        }

    # Get new tech news (no draft yet) ordered by relevance_score
    has_draft = exists().where(IGDraft.news_id == News.id)
    stmt = (
        select(News)
        .where(News.domain == "tech")
        .where(~has_draft)
        .order_by(News.relevance_score.desc().nullslast(), News.published_at.desc())
        .limit(20)
    )
    res = await db.execute(stmt)
    news_without_draft = res.scalars().all()

    drafts_created = 0
    for n in news_without_draft:
        try:
            draft_data = generate_ig_draft(n, tone=settings.IG_DEFAULT_TONE, brand="oxono")
            draft = IGDraft(news_id=n.id, **draft_data)
            db.add(draft)
            drafts_created += 1
        except Exception:
            continue

    if drafts_created > 0:
        await db.commit()

    return {
        "status": "ok",
        "ingested": total_inserted,
        "drafts_generated": drafts_created,
        "message": f"Ingested {total_inserted} tech news, generated {drafts_created} IG drafts.",
    }
