"""
Ingestor genérico de noticias desde fuentes RSS.

Parsea feeds RSS legales y los inserta en la base de datos.
NOTA: Idealista NO tiene API de noticias, por eso usamos fuentes RSS.
"""
import re
import html
import feedparser
import httpx
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Dict, Optional
from app.models.news import News
from app.constants import NewsCategory


RSS_SOURCES = [
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
    {
        "name": "Idealista News",
        "url": "https://www.idealista.com/en/news/rss/v2/latest-news.xml",
        "default_category": NewsCategory.NOTICIAS_INMOBILIARIAS,
        "source": "Idealista",
        "description": "Noticias inmobiliarias generales: mercado, precios, hipotecas, normativa"
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
    # ArchDaily eliminado: es internacional y no garantiza solo España/Europa
    # Si necesitas noticias de arquitectura específicas de España, considerar:
    # - Plataforma Arquitectura (si tiene feed específico de España)
    # - O agregar filtrado por ubicación en el futuro
]


def _clean_html(text: str) -> str:
    """
    Limpia HTML de un texto, extrayendo solo el contenido de texto puro.
    
    Args:
        text: Texto que puede contener HTML
        
    Returns:
        Texto limpio sin tags HTML ni entidades HTML
    """
    if not text:
        return ""
    
    # Convertir entidades HTML a caracteres normales (&amp; -> &, etc.)
    text = html.unescape(text)
    
    # Remover tags HTML (ej: <p>, <a href="...">, etc.)
    text = re.sub(r'<[^>]+>', '', text)
    
    # Limpiar espacios múltiples y saltos de línea
    text = re.sub(r'\s+', ' ', text)
    
    # Limpiar espacios al inicio y final
    text = text.strip()
    
    return text


def _is_relevant_to_spain_europe(title: str, summary: str = None) -> bool:
    """
    Filtra noticias para mantener solo las relevantes a España y Europa.
    
    Args:
        title: Título de la noticia
        summary: Resumen de la noticia (opcional)
        
    Returns:
        True si la noticia es relevante para España/Europa, False en caso contrario
    """
    if not title:
        return False
    
    # Combinar título y resumen para búsqueda
    text_to_check = title.lower()
    if summary:
        text_to_check += " " + summary.lower()
    
    # Palabras clave que indican España/Europa (español e inglés)
    spain_keywords = [
        "españa", "español", "española", "españoles",
        "madrid", "barcelona", "valencia", "sevilla", "bilbao",
        "andalucía", "cataluña", "madrileño", "catalán",
        "boe", "gobierno español", "ministerio",
        # Inglés
        "spain", "spanish", "madrid", "barcelona", "valencia", "seville", "bilbao",
        "andalusia", "catalonia", "catalan"
    ]
    
    europe_keywords = [
        "europa", "europeo", "europea", "europeos",
        "ue", "unión europea", "bruselas",
        "alemania", "francia", "italia", "portugal",
        "países bajos", "bélgica",
        # Inglés
        "europe", "european", "eu", "european union", "brussels",
        "germany", "france", "italy", "portugal",
        "netherlands", "belgium"
    ]
    
    # Excluir palabras que indican otros países/regiones
    exclude_keywords = [
        "méxico", "mexicano", "mexicana", "cdmx",
        "argentina", "argentino", "buenos aires",
        "colombia", "colombiano", "bogotá",
        "chile", "chileno", "santiago",
        "estados unidos", "eeuu", "usa", "nueva york", "los angeles",
        "asia", "china", "japón", "india"
    ]
    
    # Si contiene palabras de exclusión, descartar
    for keyword in exclude_keywords:
        if keyword in text_to_check:
            return False
    
    # Si contiene palabras de España o Europa, incluir
    for keyword in spain_keywords + europe_keywords:
        if keyword in text_to_check:
            return True
    
    # Para fuentes españolas específicas (Expansion, El País, etc.), 
    # asumimos que son relevantes por defecto
    # Esto se puede ajustar según la fuente
    
    # Si no hay indicadores claros, por defecto incluir
    # (las fuentes RSS ya están filtradas por ser españolas)
    return True


async def _extract_article_content(url: str) -> Optional[str]:
    """
    Extrae el contenido completo del artículo desde la URL usando scraping.
    
    Args:
        url: URL del artículo
        
    Returns:
        Texto del artículo completo o None si falla
    """
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            response.raise_for_status()
            
            # Asegurar que el contenido está en UTF-8
            # BeautifulSoup maneja la codificación automáticamente, pero lo forzamos
            if response.encoding:
                response.encoding = 'utf-8'
            
            # Parsear HTML con codificación explícita
            soup = BeautifulSoup(response.text, 'html.parser', from_encoding='utf-8')
            
            # Eliminar scripts, estilos y elementos no deseados
            for element in soup(["script", "style", "nav", "header", "footer", "aside", "iframe", "noscript"]):
                element.decompose()
            
            # Buscar el contenido principal del artículo
            # Intentar encontrar el artículo usando selectores comunes
            article = None
            
            # Selectores comunes para el contenido principal
            article_selectors = [
                'article',
                '.article-body',
                '.article-content',
                '.post-content',
                '.entry-content',
                '[role="article"]',
                'main article',
                '.content article',
                '#main article'
            ]
            
            for selector in article_selectors:
                article = soup.select_one(selector)
                if article:
                    break
            
            # Si no se encuentra article, buscar divs con clase común de contenido
            if not article:
                for div in soup.find_all('div', class_=re.compile(r'(content|article|post|entry)', re.I)):
                    if len(div.get_text()) > 300:  # Si tiene bastante texto, probablemente es el contenido
                        article = div
                        break
            
            # Si aún no se encuentra, usar el body completo (menos ideal pero funcional)
            if not article:
                article = soup.find('body') or soup
            
            # Extraer texto limpio
            text = article.get_text(separator=' ', strip=True) if article else soup.get_text(separator=' ', strip=True)
            
            # Limpiar espacios múltiples
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            # Limitar a 5000 caracteres máximo (para no saturar la BD)
            if len(text) > 5000:
                text = text[:5000] + "..."
            
            return text if text and len(text) > 50 else None  # Mínimo 50 caracteres para considerar válido
            
    except Exception:
        # Si falla el scraping, devolver None (usaremos el resumen del RSS como fallback)
        return None


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
                
                # Extraer resumen temporalmente para el filtro
                temp_summary = None
                if hasattr(entry, 'summary') and entry.summary:
                    temp_summary = entry.summary
                elif hasattr(entry, 'description') and entry.description:
                    temp_summary = entry.description
                
                # Filtrar noticias: solo España y Europa
                if not _is_relevant_to_spain_europe(title, temp_summary):
                    continue  # Saltar esta noticia
                
                # Parsear fecha
                published_at = _parse_published_date(entry)
                
                # Intentar obtener contenido completo del RSS primero
                # Algunos feeds incluyen content:encoded o content con el artículo completo
                full_content = None
                
                # Buscar content o content:encoded en el entry
                if hasattr(entry, 'content') and entry.content:
                    # Algunos feeds tienen content como lista
                    if isinstance(entry.content, list) and len(entry.content) > 0:
                        full_content = entry.content[0].get('value', '')
                    elif isinstance(entry.content, str):
                        full_content = entry.content
                
                # Buscar content:encoded (algunos feeds lo usan)
                if not full_content:
                    for key in entry.keys():
                        if 'content' in key.lower() or 'encoded' in key.lower():
                            full_content = entry[key]
                            break
                
                # Decidir qué contenido usar (prioridad: RSS completo > scraping > resumen RSS)
                raw_summary = None
                
                # Prioridad 1: Contenido completo del RSS (si está disponible)
                if full_content:
                    raw_summary = _clean_html(full_content)
                    # Si el contenido completo del RSS es muy corto (< 200 chars), 
                    # probablemente no es el artículo completo, intentar scraping
                    if len(raw_summary) < 200:
                        raw_summary = None  # Resetear para intentar scraping
                
                # Prioridad 2: Intentar scraping del artículo (solo si no hay contenido completo del RSS)
                if not raw_summary and link:
                    scraped_content = await _extract_article_content(link)
                    if scraped_content:
                        raw_summary = scraped_content
                
                # Prioridad 3: Usar resumen del RSS como fallback
                if not raw_summary and temp_summary:
                    raw_summary = _clean_html(temp_summary)
                
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
