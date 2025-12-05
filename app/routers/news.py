from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models.news import News
from app.schemas.news import NewsCreate, NewsRead

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.post("/news", response_model=NewsRead, status_code=201)
async def create_news(news_data: NewsCreate, db: AsyncSession = Depends(get_db)):
    """Crear una nueva noticia"""
    new_news = News(**news_data.model_dump())
    db.add(new_news)
    await db.commit()
    await db.refresh(new_news)
    return new_news

@router.get("/news", response_model=list[NewsRead])
async def list_news(
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    q: Optional[str] = Query(None, description="Buscar en título"),
    from_date: Optional[datetime] = Query(None, description="Fecha desde (published_at >=)"),
    to_date: Optional[datetime] = Query(None, description="Fecha hasta (published_at <=)"),
    db: AsyncSession = Depends(get_db)
):
    """Listar noticias con filtros opcionales"""
    query = select(News)
    
    conditions = []
    
    if category:
        conditions.append(News.category == category)
    
    if from_date:
        conditions.append(News.published_at >= from_date)
    
    if to_date:
        conditions.append(News.published_at <= to_date)
    
    if q:
        conditions.append(News.title.ilike(f"%{q}%"))
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(News.published_at.desc())
    
    result = await db.execute(query)
    news_list = result.scalars().all()
    return news_list

@router.get("/news/{id}", response_model=NewsRead)
async def get_news(id: UUID, db: AsyncSession = Depends(get_db)):
    """Obtener una noticia por ID"""
    query = select(News).where(News.id == id)
    result = await db.execute(query)
    news = result.scalar_one_or_none()
    
    if not news:
        raise HTTPException(status_code=404, detail="Noticia no encontrada")
    
    return news
