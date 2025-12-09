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

logger = logging.getLogger(__name__)

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

@router.get("/news", response_model=PaginatedResponse[NewsRead])
async def list_news(
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    q: Optional[str] = Query(None, description="Buscar en título"),
    from_date: Optional[datetime] = Query(None, description="Fecha desde (published_at >=)"),
    to_date: Optional[datetime] = Query(None, description="Fecha hasta (published_at <=)"),
    used_in_social: Optional[bool] = Query(None, description="Filtrar por usado en redes (true/false)"),
    limit: int = Query(50, ge=1, le=200, description="Número máximo de noticias a devolver (1-200)"),
    offset: int = Query(0, ge=0, description="Número de noticias a saltar para paginación"),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar noticias con filtros opcionales y paginación.
    
    Por defecto devuelve las últimas 50 noticias (las más recientes primero).
    Usa `limit` y `offset` para paginación.
    """
    try:
        # Query base
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
        
        # Filtro por used_in_social si se especifica
        if used_in_social is not None:
            conditions.append(News.used_in_social == used_in_social)
        
        # Aplicar condiciones a ambas queries
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Ordenar por fecha (más recientes primero)
        query = query.order_by(News.published_at.desc())
        
        # Aplicar paginación
        query = query.limit(limit).offset(offset)
        
        # Ejecutar queries
        result = await db.execute(query)
        news_list = result.scalars().all()
        
        # Obtener total
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # Calcular si hay más resultados
        has_more = (offset + limit) < total
        
        return PaginatedResponse[NewsRead](
            items=news_list,
            total=total,
            limit=limit,
            offset=offset,
            has_more=has_more
        )
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al listar noticias: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error al acceder a la base de datos. Por favor, inténtalo de nuevo más tarde."
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar noticias: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor. Por favor, inténtalo de nuevo más tarde."
        )

@router.get("/news/{id}", response_model=NewsRead)
async def get_news(id: UUID, db: AsyncSession = Depends(get_db)):
    """Obtener una noticia por ID"""
    query = select(News).where(News.id == id)
    result = await db.execute(query)
    news = result.scalar_one_or_none()
    
    if not news:
        raise HTTPException(status_code=404, detail="Noticia no encontrada")
    
    return news
