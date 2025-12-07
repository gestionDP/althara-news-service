"""
Router de administración para gestionar la ingestión de noticias.

NOTA: Idealista NO tiene API de noticias, por eso solo usamos fuentes RSS.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.database import get_db
from app.ingestion.rss_ingestor import ingest_rss_sources
from app.models.news import News
from app.adapters.news_adapter import build_althara_summary

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/ingest")
async def ingest_news(db: AsyncSession = Depends(get_db)):
    """
    Endpoint principal para disparar la ingestión de noticias desde fuentes RSS.
    
    Ingesta noticias desde todas las fuentes RSS configuradas:
    - Expansion Inmobiliario
    - Cinco Días
    - El Economista
    - BOE Subastas
    - BOE General
    - Observatorio Inmobiliario
    - Interempresas Construcción
    - ArchDaily
    
    Returns:
        JSON con el diccionario de fuentes y número de noticias insertadas
    """
    results = await ingest_rss_sources(db)
    return results


@router.post("/ingest/rss")
async def ingest_rss(db: AsyncSession = Depends(get_db)):
    """
    Endpoint alternativo para disparar la ingestión desde fuentes RSS.
    Es un alias del endpoint principal /ingest.
    
    Returns:
        JSON con el diccionario de fuentes y número de noticias insertadas
    """
    results = await ingest_rss_sources(db)
    return results


@router.post("/adapt-pending")
async def adapt_pending_news(db: AsyncSession = Depends(get_db)):
    """
    Adapta noticias pendientes al tono Althara.
    
    Busca todas las noticias que no tienen althara_summary y las adapta
    usando el adapter de Althara. Guarda el resultado en althara_summary.
    
    Returns:
        JSON con el número de noticias adaptadas
    """
    # Buscar noticias con althara_summary IS NULL
    stmt = select(News).where(News.althara_summary.is_(None))
    result = await db.execute(stmt)
    pending_news = result.scalars().all()
    
    adapted_count = 0
    
    for news in pending_news:
        try:
            # Construir el resumen Althara
            althara_summary = build_althara_summary(
                title=news.title,
                raw_summary=news.raw_summary,
                category=news.category
            )
            
            # Actualizar la noticia
            news.althara_summary = althara_summary
            adapted_count += 1
        
        except Exception as e:
            # Si hay un error con una noticia, continuar con las demás
            print(f"Error adaptando noticia {news.id}: {e}")
            continue
    
    # Commit todos los cambios
    if adapted_count > 0:
        await db.commit()
    
    return {
        "adapted": adapted_count,
        "message": f"Se adaptaron {adapted_count} noticias al tono Althara"
    }


@router.post("/ingest-and-adapt")
async def ingest_and_adapt(db: AsyncSession = Depends(get_db)):
    """
    Endpoint todo-en-uno: ingesta noticias y las adapta al tono Althara.
    
    Útil para automatización externa (servicios cloud, cron jobs remotos, etc.).
    Ejecuta todo el pipeline: ingest → adapt → listo para usar.
    
    Returns:
        JSON compacto con resumen del proceso (optimizado para cron jobs)
    """
    # 1. Ingestar noticias (máximo 5 por fuente para evitar demasiadas)
    ingest_results = await ingest_rss_sources(db, max_items_per_source=5)
    total_inserted = sum(ingest_results.values())
    
    # 2. Adaptar noticias pendientes
    stmt = select(News).where(News.althara_summary.is_(None))
    result = await db.execute(stmt)
    pending_news = result.scalars().all()
    
    adapted_count = 0
    
    for news in pending_news:
        try:
            althara_summary = build_althara_summary(
                title=news.title,
                raw_summary=news.raw_summary,
                category=news.category
            )
            news.althara_summary = althara_summary
            adapted_count += 1
        except Exception as e:
            # Solo registrar errores críticos, sin detalles largos
            continue
    
    if adapted_count > 0:
        await db.commit()
    
    # Respuesta compacta para evitar "output too large" en cron jobs
    return {
        "status": "ok",
        "ingested": total_inserted,
        "adapted": adapted_count,
        "sources_processed": len([v for v in ingest_results.values() if v > 0])
    }


@router.delete("/clean-all")
async def clean_all_news(db: AsyncSession = Depends(get_db)):
    """
    Elimina TODAS las noticias de la base de datos.
    
    ⚠️ ADVERTENCIA: Esta operación es irreversible.
    Útil para limpiar y re-ingerir con nuevas mejoras.
    
    Returns:
        JSON con el número de noticias eliminadas
    """
    # Contar noticias antes de eliminar
    count_stmt = select(func.count()).select_from(News)
    count_result = await db.execute(count_stmt)
    total_count = count_result.scalar_one()
    
    # Eliminar todas las noticias
    delete_stmt = delete(News)
    await db.execute(delete_stmt)
    await db.commit()
    
    return {
        "status": "ok",
        "deleted": total_count,
        "message": f"Se eliminaron {total_count} noticias de la base de datos"
    }

