from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from datetime import datetime
from uuid import UUID
import logging

from app.database import get_db
from app.models.news import News
from app.schemas.news import NewsCreate, NewsRead, PaginatedResponse
from app.ingestion.rss_ingestor import _is_relevant_to_real_estate

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
    if not _is_relevant_to_real_estate(news_data.title, news_data.raw_summary):
        raise HTTPException(
            status_code=400,
            detail="La noticia no es relevante para el sector inmobiliario. Solo se permiten noticias relacionadas con vivienda, inmobiliaria, hipotecas, alquiler, construcción inmobiliaria, etc."
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
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        query = query.order_by(News.published_at.desc())
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
