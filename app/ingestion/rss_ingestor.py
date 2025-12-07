"""
Ingestor genérico de noticias desde fuentes RSS.

Parsea feeds RSS legales y los inserta en la base de datos.
NOTA: Idealista NO tiene API de noticias, por eso usamos fuentes RSS.
"""
import feedparser
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Dict
from app.models.news import News
from app.constants import NewsCategory


# Configuración de fuentes RSS reales y legales
RSS_SOURCES = [
    # Fuentes de noticias inmobiliarias generales
    {
        "name": "Expansion Inmobiliario",
        "url": "https://e00-expansion.uecdn.es/rss/inmobiliario.xml",
        "default_category": NewsCategory.NOTICIAS_INMOBILIARIAS,
        "source": "Expansion",
        "description": "Noticias de mercado, hipotecas, inversión, big deals"
    },
    {
        "name": "Cinco Días - Economía Inmobiliaria",
        "url": "https://cincodias.elpais.com/rss/act/economia_inmobiliaria/",
        "default_category": NewsCategory.NOTICIAS_INMOBILIARIAS,
        "source": "Cinco Días",
        "description": "Noticias de economía inmobiliaria"
    },
    {
        "name": "El Economista - Vivienda",
        "url": "https://www.eleconomista.es/rss/rss-vivienda.php",
        "default_category": NewsCategory.PRECIOS_VIVIENDA,
        "source": "El Economista",
        "description": "Noticias sobre vivienda y mercado inmobiliario"
    },
    
    # BOE - Subastas y normativas
    {
        "name": "BOE Subastas",
        "url": "https://subastas.boe.es/rss.php",
        "default_category": NewsCategory.NOTICIAS_BOE_SUBASTAS,
        "source": "BOE",
        "description": "Subastas inmobiliarias del BOE"
    },
    {
        "name": "BOE General",
        "url": "https://www.boe.es/diario_boe/xml.php?id=BOE-S",
        "default_category": NewsCategory.NORMATIVAS_VIVIENDAS,
        "source": "BOE",
        "description": "Leyes y normativas (puede incluir temas de vivienda)"
    },
    
    # Observatorios y análisis
    {
        "name": "Observatorio Inmobiliario",
        "url": "https://www.observatorioinmobiliario.es/rss/",
        "default_category": NewsCategory.NOTICIAS_INMOBILIARIAS,
        "source": "Observatorio Inmobiliario",
        "description": "Análisis y noticias del sector inmobiliario"
    },
    
    # Construcción y urbanismo
    {
        "name": "Interempresas Construcción",
        "url": "https://www.interempresas.net/construccion/RSS/",
        "default_category": NewsCategory.NOTICIAS_CONSTRUCCION,
        "source": "Interempresas",
        "description": "Noticias sobre construcción"
    },
    {
        "name": "Plataforma Arquitectura",
        "url": "https://www.archdaily.mx/mx/rss",
        "default_category": NewsCategory.NOVEDADES_CONSTRUCCION,
        "source": "ArchDaily",
        "description": "Noticias de arquitectura y construcción"
    },
]


def _parse_published_date(entry) -> datetime:
    """
    Intenta parsear la fecha de publicación de una entrada RSS.
    
    Args:
        entry: Entrada del feed parseado por feedparser
        
    Returns:
        datetime en UTC, o datetime actual si no se puede parsear
    """
    # Intentar usar published_parsed si está disponible
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        try:
            # published_parsed es una struct_time
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pass
    
    # Si hay updated_parsed, usarlo
    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        try:
            return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pass
    
    # Fallback: usar fecha actual
    return datetime.now(timezone.utc)


async def ingest_rss_sources(session: AsyncSession, max_items_per_source: int = 5) -> Dict[str, int]:
    """
    Ingesta noticias desde todas las fuentes RSS configuradas.
    
    Args:
        session: Sesión de base de datos async
        max_items_per_source: Máximo número de items a procesar por fuente (por defecto 20)
        
    Returns:
        Diccionario con nombre de fuente -> número de noticias insertadas
    """
    results = {}
    
    for source_config in RSS_SOURCES:
        source_name = source_config["name"]
        feed_url = source_config["url"]
        default_category = source_config["default_category"]
        source_label = source_config["source"]
        
        inserted_count = 0
        
        try:
            # Parsear el feed RSS
            # Nota: feedparser es síncrono, pero para feeds pequeños está bien
            # Si necesitas async en el futuro, puedes usar httpx + feedparser
            feed = feedparser.parse(feed_url)
            
            # Verificar que el feed se parseó correctamente
            if feed.bozo == 1 and feed.bozo_exception:
                # Hay algún error en el parseo (silencioso para evitar output largo)
                pass
            
            # Verificar que el feed tiene entradas
            if not hasattr(feed, 'entries') or not feed.entries:
                # Feed vacío (silencioso para evitar output largo)
                results[source_name] = 0
                continue
            
            # Limitar el número de entradas a procesar (para evitar demasiadas noticias)
            entries_to_process = feed.entries[:max_items_per_source]
            
            # Procesar cada entrada del feed
            for entry in entries_to_process:
                # Extraer datos básicos
                title = getattr(entry, 'title', 'Sin título')
                link = getattr(entry, 'link', '')
                
                # Saltar si no hay título o URL
                if not title or not link:
                    continue
                
                # Parsear fecha
                published_at = _parse_published_date(entry)
                
                # Extraer resumen si existe
                raw_summary = None
                if hasattr(entry, 'summary'):
                    raw_summary = entry.summary
                elif hasattr(entry, 'description'):
                    raw_summary = entry.description
                
                # Verificar si ya existe una noticia con la misma URL
                stmt = select(News).where(News.url == link)
                result = await session.execute(stmt)
                existing_news = result.scalar_one_or_none()
                
                if existing_news is None:
                    # Crear nuevo registro News
                    new_news = News(
                        title=title,
                        source=source_label,
                        url=link,
                        published_at=published_at,
                        category=default_category,
                        raw_summary=raw_summary,
                        althara_summary=None,
                        tags=None,
                        used_in_social=False
                    )
                    session.add(new_news)
                    inserted_count += 1
        
        except Exception as e:
            # Manejar errores de manera elegante (silencioso para evitar output largo)
            inserted_count = 0
        
        results[source_name] = inserted_count
    
    # Commit todos los cambios
    if any(results.values()):
        await session.commit()
    
    return results
