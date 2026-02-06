from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, exists
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from datetime import datetime
from uuid import UUID
import logging

from app.database import get_db
from app.models.news import News
from app.models.ig_draft import IGDraft
from app.schemas.news import NewsCreate, NewsRead, PaginatedResponse
from app.constants import DENY_KEYWORDS, ALLOW_KEYWORDS, STRICT_REQUIRE_ALLOW
from app.utils.guardrails import passes_guardrails

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.post("/news", response_model=NewsRead, status_code=201)
async def create_news(news_data: NewsCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new news item.
    Validates that the news is relevant to the real estate sector before inserting.
    """
    # Validate relevance to real estate sector
    if not passes_guardrails(
        news_data.title, DENY_KEYWORDS, ALLOW_KEYWORDS, STRICT_REQUIRE_ALLOW,
        summary=news_data.raw_summary, url=getattr(news_data, "url", "") or "",
    ):
        raise HTTPException(
            status_code=400,
            detail="News is not relevant to the real estate sector. Only news related to housing, real estate, mortgages, rentals, construction, etc. are allowed."
        )
    
    new_news = News(**news_data.model_dump())
    db.add(new_news)
    await db.commit()
    await db.refresh(new_news)
    return new_news

@router.get("/news", response_model=PaginatedResponse[NewsRead])
async def list_news(
    category: Optional[str] = Query(None, description="Filter by category"),
    q: Optional[str] = Query(None, description="Search in title"),
    from_date: Optional[datetime] = Query(None, description="Date from (published_at >=)"),
    to_date: Optional[datetime] = Query(None, description="Date to (published_at <=)"),
    used_in_social: Optional[bool] = Query(None, description="Filter by used in social media (true/false)"),
    domain: Optional[str] = Query(None, description="Filter by domain: tech | real_estate | all. Default: real_estate (backward compat Althara web)"),
    only_with_draft: Optional[bool] = Query(None, description="Only news that have at least one IG draft"),
    order_by: Optional[str] = Query("published_at", description="Order by: published_at | relevance_score"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of news items to return (1-200)"),
    offset: int = Query(0, ge=0, description="Number of news items to skip for pagination"),
    db: AsyncSession = Depends(get_db)
):
    """
    List news items with optional filters and pagination.
    
    Returns the latest 50 news items by default (most recent first).
    Uses `limit` and `offset` for pagination.
    """
    try:
        query = select(News)
        count_query = select(func.count()).select_from(News)
        
        conditions = []
        
        if category:
            conditions.append(News.category == category)
        
        if from_date:
            conditions.append(News.published_at >= from_date)
        
        if to_date:
            conditions.append(News.published_at <= to_date)
        
        if q:
            conditions.append(News.title.ilike(f"%{q}%"))
        
        if used_in_social is not None:
            conditions.append(News.used_in_social == used_in_social)

        # domain: None → real_estate (backward compat for Althara web). "all" → no filter
        if domain == "all":
            pass
        elif domain:
            conditions.append(News.domain == domain)
        else:
            conditions.append(News.domain == "real_estate")

        if only_with_draft:
            has_draft = exists().where(IGDraft.news_id == News.id)
            conditions.append(has_draft)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        order_col = News.relevance_score.desc().nullslast() if order_by == "relevance_score" else News.published_at.desc()
        query = query.order_by(order_col)
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        news_list = result.scalars().all()
        
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        has_more = (offset + limit) < total
        
        return PaginatedResponse[NewsRead](
            items=news_list,
            total=total,
            limit=limit,
            offset=offset,
            has_more=has_more
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error listing news: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error accessing database. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error listing news: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )

@router.get("/news/{id}", response_model=NewsRead)
async def get_news(id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a news item by ID"""
    query = select(News).where(News.id == id)
    result = await db.execute(query)
    news = result.scalar_one_or_none()
    
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    
    return news
