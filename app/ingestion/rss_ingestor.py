"""
Generic news ingestor from RSS sources.

Parses legal RSS feeds and inserts them into the database.
NOTE: Idealista does NOT have a news API, so we use RSS sources.
"""
import re
import html
import feedparser
import httpx
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Optional
from app.models.news import News
from app.utils.html_utils import strip_html_tags
from app.utils.rss_utils import parse_published_date
from app.utils.guardrails import passes_guardrails
from app.constants import (
    AltharaCategoryV2,
    DENY_KEYWORDS,
    ALLOW_KEYWORDS,
    STRICT_REQUIRE_ALLOW,
    CATEGORY_HINTS,
)


RSS_SOURCES = [
    {"name": "Expansion Inmobiliario", "url": "https://e00-expansion.uecdn.es/rss/inmobiliario.xml", "default_category": AltharaCategoryV2.SECTOR_INMOBILIARIO, "source": "Expansion"},
    {"name": "Cinco Días - Economía Inmobiliaria", "url": "https://cincodias.elpais.com/rss/act/economia_inmobiliaria/", "default_category": AltharaCategoryV2.SECTOR_INMOBILIARIO, "source": "Cinco Días"},
    {"name": "El Economista - Vivienda", "url": "https://www.eleconomista.es/rss/rss-vivienda.php", "default_category": AltharaCategoryV2.PRECIOS_VIVIENDA, "source": "El Economista"},
    {"name": "Idealista News", "url": "https://www.idealista.com/news/rss/v2/latest-news.xml", "default_category": AltharaCategoryV2.SECTOR_INMOBILIARIO, "source": "Idealista"},
    {"name": "BOE Subastas", "url": "https://subastas.boe.es/rss.php", "default_category": AltharaCategoryV2.BOE_SUBASTAS, "source": "BOE"},
    {"name": "BOE General", "url": "https://www.boe.es/diario_boe/xml.php?id=BOE-S", "default_category": AltharaCategoryV2.REGULACION_VIVIENDA, "source": "BOE"},
    {"name": "Observatorio Inmobiliario", "url": "https://www.observatorioinmobiliario.es/rss/", "default_category": AltharaCategoryV2.SECTOR_INMOBILIARIO, "source": "Observatorio Inmobiliario"},
    {"name": "Interempresas Construcción", "url": "https://www.interempresas.net/construccion/RSS/", "default_category": AltharaCategoryV2.CONSTRUCCION_Y_COSTES, "source": "Interempresas"},
    # Última Hora removed: general newspaper (bikes, crime, etc.) - not sector-specific
]




async def _extract_article_content(url: str) -> Optional[str]:
    """
    Extracts complete article content from URL using scraping.
    
    Args:
        url: Article URL
        
    Returns:
        Complete article text or None if it fails
    """
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            response.raise_for_status()
            # Decode as UTF-8; if server declares wrong charset, try latin-1 then fix with strip_html_tags/ftfy
            raw = response.content
            try:
                html_text = raw.decode("utf-8")
            except UnicodeDecodeError:
                html_text = raw.decode("latin-1", errors="replace")
            soup = BeautifulSoup(html_text, 'html.parser')
            
            for element in soup(["script", "style", "nav", "header", "footer", "aside", "iframe", "noscript"]):
                element.decompose()
            
            article = None
            
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
            
            if not article:
                for div in soup.find_all('div', class_=re.compile(r'(content|article|post|entry)', re.I)):
                    if len(div.get_text()) > 300:
                        article = div
                        break
            
            if not article:
                article = soup.find('body') or soup
            
            text = article.get_text(separator=' ', strip=True) if article else soup.get_text(separator=' ', strip=True)
            
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            if len(text) > 5000:
                text = text[:5000] + "..."
            
            return text if text and len(text) > 50 else None
            
    except Exception:
        return None


def _categorize_althara_v2(title: str, summary: Optional[str] = None) -> str:
    """Clasifica con CATEGORY_HINTS de constants. Devuelve categoría v2."""
    text = (title + " " + (summary or "")).lower()
    best_cat = AltharaCategoryV2.SECTOR_INMOBILIARIO
    best_score = 0
    for category, keywords in CATEGORY_HINTS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_cat = category
    return best_cat


async def ingest_rss_sources(session: AsyncSession, max_items_per_source: int = 10) -> Dict[str, int]:
    """
    Ingests news from all configured RSS sources.
    
    Args:
        session: Async database session
        max_items_per_source: Maximum number of items to process per source (default 20)
        
    Returns:
        Dictionary with source name -> number of news items inserted
    """
    results = {}
    
    for source_config in RSS_SOURCES:
        source_name = source_config["name"]
        feed_url = source_config["url"]
        default_category = source_config["default_category"]
        source_label = source_config["source"]
        
        inserted_count = 0
        
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(
                    feed_url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                )
                response.raise_for_status()
                feed = feedparser.parse(response.text)
            
            if feed.bozo == 1 and feed.bozo_exception:
                pass
            
            if not hasattr(feed, 'entries') or not feed.entries:
                results[source_name] = 0
                continue
            
            entries_to_process = feed.entries
            relevant_count = 0
            
            for entry in entries_to_process:
                if relevant_count >= max_items_per_source:
                    break
                title = getattr(entry, "title", "Untitled")
                link = getattr(entry, 'link', '')
                
                if not title or not link:
                    continue
                
                temp_summary = None
                if hasattr(entry, 'summary') and entry.summary:
                    temp_summary = entry.summary
                elif hasattr(entry, 'description') and entry.description:
                    temp_summary = entry.description
                
                # Clean HTML from temp_summary before filtering
                if temp_summary:
                    temp_summary_clean = strip_html_tags(temp_summary)
                else:
                    temp_summary_clean = None
                
                if not passes_guardrails(
                    title, DENY_KEYWORDS, ALLOW_KEYWORDS, STRICT_REQUIRE_ALLOW,
                    summary=temp_summary_clean, url=link,
                ):
                    continue
                
                relevant_count += 1
                published_at = parse_published_date(entry)
                full_content = None
                
                if hasattr(entry, 'content') and entry.content:
                    if isinstance(entry.content, list) and len(entry.content) > 0:
                        full_content = entry.content[0].get('value', '')
                    elif isinstance(entry.content, str):
                        full_content = entry.content
                
                if not full_content:
                    for key in entry.keys():
                        if 'content' in key.lower() or 'encoded' in key.lower():
                            full_content = entry[key]
                            break
                
                raw_summary = None
                
                if full_content:
                    raw_summary = strip_html_tags(full_content)
                    if len(raw_summary) < 200:
                        raw_summary = None
                
                if not raw_summary and link:
                    scraped_content = await _extract_article_content(link)
                    if scraped_content:
                        raw_summary = scraped_content
                
                if not raw_summary and temp_summary:
                    raw_summary = strip_html_tags(temp_summary)
                
                if not passes_guardrails(
                    title, DENY_KEYWORDS, ALLOW_KEYWORDS, STRICT_REQUIRE_ALLOW,
                    summary=raw_summary, url=link,
                ):
                    continue

                final_category = _categorize_althara_v2(title, raw_summary) or default_category
                
                stmt = select(News).where(News.url == link)
                result = await session.execute(stmt)
                existing_news = result.scalar_one_or_none()
                
                if existing_news is None:
                    new_news = News(
                        title=title,
                        source=source_label,
                        url=link,
                        published_at=published_at,
                        category=final_category,
                        raw_summary=raw_summary,
                        althara_summary=None,
                        tags=None,
                        used_in_social=False
                    )
                    session.add(new_news)
                    inserted_count += 1
        
        except Exception as e:
            inserted_count = 0
        
        results[source_name] = inserted_count
    
    if any(results.values()):
        await session.commit()
    
    return results
