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
        "url": "https://www.idealista.com/news/rss/v2/latest-news.xml",
        "default_category": NewsCategory.NOTICIAS_INMOBILIARIAS,
        "source": "Idealista",
        "description": "Noticias inmobiliarias generales: mercado, precios, hipotecas, normativa"
    },
    
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
    
    {
        "name": "Observatorio Inmobiliario",
        "url": "https://www.observatorioinmobiliario.es/rss/",
        "default_category": NewsCategory.NOTICIAS_INMOBILIARIAS,
        "source": "Observatorio Inmobiliario",
        "description": "Análisis y noticias del sector inmobiliario"
    },
    
    {
        "name": "Interempresas Construcción",
        "url": "https://www.interempresas.net/construccion/RSS/",
        "default_category": NewsCategory.NOTICIAS_CONSTRUCCION,
        "source": "Interempresas",
        "description": "Noticias sobre construcción"
    },
    
    {
        "name": "Última Hora",
        "url": "https://www.ultimahora.es/feed.rss",
        "default_category": NewsCategory.NOTICIAS_INMOBILIARIAS,
        "source": "Última Hora",
        "description": "Noticias locales de Baleares: alquiler, vivienda, mercado inmobiliario"
    },
]


def _clean_html(text: str) -> str:
    """
    Cleans HTML from text, extracting only pure text content.
    
    Args:
        text: Text that may contain HTML
        
    Returns:
        Clean text without HTML tags or entities
    """
    if not text:
        return ""
    
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


def _is_relevant_to_real_estate(title: str, summary: str = None) -> bool:
    """
    Filters news to keep only those relevant to the real estate sector.
    Uses strict filtering: requires specific real estate keywords, not generic terms.
    
    Args:
        title: News title
        summary: News summary (optional)
        
    Returns:
        True if the news is relevant to the real estate sector, False otherwise
    """
    if not title:
        return False
    
    text_to_check = title.lower()
    if summary:
        text_to_check += " " + summary.lower()
    
    # STRICT: Only phrases that clearly indicate real estate context
    # These are high-confidence indicators
    strong_real_estate_phrases = [
        'vivienda', 'viviendas', 
        'inmobiliario', 'inmobiliaria', 'inmobiliarias',
        'mercado inmobiliario', 'sector inmobiliario',
        'mercado residencial', 'mercados residenciales',
        'hipoteca', 'hipotecas', 'hipotecario', 'hipotecaria',
        'alquiler', 'alquileres', 'renta', 'rentas',
        'precio vivienda', 'precios vivienda', 'precio de vivienda', 'precios de vivienda',
        'precio inmobiliario', 'precios inmobiliarios',
        'valor inmobiliario', 'valores inmobiliarios',
        'propiedad', 'propiedades', 'inmueble', 'inmuebles',
        'compraventa', 'compraventas', 'compra vivienda', 'venta vivienda',
        'subasta inmobiliaria', 'subastas inmobiliarias',
        'desahucio', 'desahucios',
        'okupa', 'okupas', 'okupación', 'okupaciones',
        'ley vivienda', 'regulación vivienda', 'normativa vivienda',
        'fondo inversión inmobiliaria', 'fondos inversión inmobiliaria',
        'socimi', 'socimis', 'reit', 'reits',
        'burbuja inmobiliaria', 'crisis vivienda',
        'vpo', 'vivienda protegida', 'vivienda social',
        'alquiler vacacional', 'airbnb', 'vivienda turística',
        'real estate', 'housing market', 'property market',
        'mortgage', 'mortgages',
        'residencial', 'residenciales',  # Agregado para capturar "mercados residenciales"
    ]
    
    # Medium confidence: construction/development but must be in real estate context
    # These need to appear WITH other real estate terms
    medium_keywords = [
        'construcción', 'construcciones', 'obra', 'obras',
        'promoción inmobiliaria', 'promociones inmobiliarias', 
        'desarrollo inmobiliario', 'desarrollos inmobiliarios',
        'urbanismo', 'urbanización', 'urbanizaciones',
        'suelo', 'terreno', 'solar', 'urbanizable',
        'reforma vivienda', 'reformas vivienda', 'rehabilitación vivienda',
        'licencia construcción', 'permiso construcción',
        'construction', 'building', 'development',
    ]
    
    # STRICT EXCLUSIONS: Topics that are NEVER relevant to real estate
    strong_exclusions = [
        # Tourism (not real estate related)
        'países más visitados', 'países visitados', 'turismo', 'viajeros', 
        'destinos turísticos', 'visitantes', 'turistas', 'atracciones turísticas',
        
        # Architecture awards/premiums (not market news)
        'premio', 'premios', 'galardón', 'galardones', 'award', 'awards',
        'gana premio', 'ganan premio', 'premio de', 'premios de',
        'architecture awards', 'premios cerámica', 'premios internacionales',
        'excelencia', 'galardones en arquitectura',
        'obras más destacadas', 'recorrido por', 'estudio de arquitectura',
        'doctor arquitecto', 'máster en arquitectura',
        
        # Events/exhibitions (not market news)
        'feria', 'ferias', 'exposición', 'exposiciones', 'congreso',
        'big 5 global', 'participa en', 'participa exitosamente',
        'convocan', 'se convocan', 'convocatoria',
        
        # Non-real-estate industries
        'calzado', 'zapatos', 'panter', 'marca made in spain',
        'logístico', 'logística', 'macrocentro logístico', 'centro logístico',
        'almacén', 'almacenes', 'distribución logística',
        
        # Technical construction (not market news)
        'teja cerámica', 'cubiertas microventiladas', 'materiales nobles',
        'fachada viva', 'impresión 3d', 'impresa en 3d',
        'diseñar con sombra', 'arquitectura bioclimática', 'arquitectura sostenible',
        'transformación digital', 'building smart', 'tecniberia',
        'formación avanzada', 'gestión comercial', 'distribución profesional',
        
        # Accidents/crimes (not market news)
        'herido', 'heridos', 'accidente', 'accidentes', 'volcar', 'volcó',
        'atropello', 'atropellado', 'choque', 'colisión',
        'muerto', 'muertos', 'fallecido', 'fallecidos',
        'detenido', 'detenidos', 'arresto', 'arrestos',
        'robo', 'robos', 'hurto', 'hurtos',
        
        # Entertainment/culture (not market news)
        'película', 'películas', 'cine', 'actor', 'actriz',
        'música', 'concierto', 'conciertos', 'festival',
        'libro', 'libros', 'escritor', 'escritora',
        'museo', 'museos',
        
        # Sports (not market news)
        'fútbol', 'futbol', 'partido', 'partidos', 'gol', 'goles',
        'equipo', 'equipos', 'jugador', 'jugadores',
        'baloncesto', 'tenis', 'deporte', 'deportes',
        
        # Politics (unless specifically about housing laws)
        'elecciones', 'votación', 'votaciones', 'partido político',
        
        # Weather/natural disasters (not market news)
        'incendio', 'incendios', 'inundación', 'inundaciones',
        'temporal', 'temporales', 'lluvia', 'lluvias',
        
        # Health/education (not market news)
        'hospital', 'hospitales', 'médico', 'médicos', 'enfermedad',
        'colegio', 'colegios', 'universidad', 'universidades', 'estudiante',
        
        # Transportation (not market news)
        'tráfico', 'trafico', 'carretera', 'carreteras', 'autopista',
        'camión', 'camiones', 'coche', 'coches', 'vehículo', 'vehículos',
        'mercedes', 'bmw', 'audi', 'ford', 'renault', 'seat', 'volvo',
        'cabrio', 'todoterreno', 'automóvil', 'automóviles', 'auto',
        
        # Vandalism/culture (not market news)
        'pintadas', 'grafiti', 'vandalismo',
        'homenaje', 'homenajes', 'acto', 'actos culturales',
        
        # Technology (not market news)
        'smartphone', 'tablet', 'iphone', 'android', 'app', 'aplicación',
        
        # Opinion/history/philosophy (not market news)
        'dignidad', 'chándal', 'carlos i', 'carlos i de inglaterra',
        'rey', 'reina', 'monarca', 'monarquía',
        'historia', 'histórico', 'histórica',
        'filosofía', 'filosófico', 'filosófica',
        'opinión', 'editorial', 'tribuna', 'columna',
        'ensayo', 'reflexión', 'reflexiones',
    ]
    
    # Check strong exclusions first (always exclude)
    for keyword in strong_exclusions:
        if keyword in text_to_check:
            return False
    
    # Check for strong real estate phrases (high confidence)
    has_strong_keyword = False
    for phrase in strong_real_estate_phrases:
        if phrase in text_to_check:
            has_strong_keyword = True
            break
    
    # If we have a strong keyword, it's relevant
    if has_strong_keyword:
        return True
    
    # If no strong keyword, check if we have medium keywords
    # BUT only if they appear with context that suggests real estate
    has_medium_keyword = False
    for keyword in medium_keywords:
        if keyword in text_to_check:
            has_medium_keyword = True
            break
    
    # Medium keywords alone are NOT enough - they need real estate context
    # Check if text also contains any real estate indicator
    if has_medium_keyword:
        # Look for any additional real estate context
        real_estate_context = [
            'vivienda', 'inmobiliario', 'inmobiliaria', 'propiedad', 
            'inmueble', 'residencial', 'comercial', 'oficina', 'local'
        ]
        for context_word in real_estate_context:
            if context_word in text_to_check:
                return True
    
    # If we get here, it's not relevant
    return False


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
            
            if response.encoding:
                response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser', from_encoding='utf-8')
            
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


def _categorize_by_keywords(title: str, summary: Optional[str] = None) -> Optional[str]:
    """
    Categorizes news based on keywords from title and summary.
    Uses specific phrases first, then falls back to general terms.
    
    Args:
        title: News title
        summary: News summary (optional)
        
    Returns:
        Detected category or NOTICIAS_INMOBILIARIAS as default
    """
    from app.constants import NewsCategory
    
    text_to_analyze = title.lower()
    if summary:
        text_to_analyze += " " + summary.lower()
    
    # Priority order: specific phrases first, then single words
    # Categories are ordered by specificity (most specific first)
    keyword_mapping = {
        # Very specific categories first
        NewsCategory.FONDOS_INVERSION_INMOBILIARIA: [
            # Multi-word phrases (highest priority)
            'fondo de inversión inmobiliaria', 'fondos de inversión inmobiliaria',
            'fondo inmobiliario', 'fondos inmobiliarios',
            'gestión de activos inmobiliarios', 'vehículo de inversión inmobiliaria',
            'patrimonio inmobiliario', 'grupo inmobiliario',
            'socimi', 'socimis', 'reit', 'reits',
            # Company names (specific to this category)
            'mazabi', 'merlin', 'colonial', 'metrovacesa', 'neinor', 'azora', 'hines', 'silicius',
            # Single words (lower priority)
            'fondo cerrado', 'fondo abierto', 'gestión patrimonial',
        ],
        NewsCategory.GRANDES_INVERSIONES_INMOBILIARIAS: [
            'gran inversión inmobiliaria', 'grandes inversiones inmobiliarias',
            'inversión millonaria inmobiliaria', 'millones de inversión inmobiliaria',
            'mega proyecto inmobiliario', 'macro proyecto inmobiliario',
            'inversión masiva inmobiliaria', 'operación inmobiliaria millonaria',
            'transacción millonaria inmobiliaria', 'adquisición millonaria inmobiliaria',
        ],
        NewsCategory.MOVIMIENTOS_GRANDES_TENEDORES: [
            'gran tenedor', 'grandes tenedores', 'inversor institucional inmobiliario',
            'inversores institucionales inmobiliarios', 'fondo buitre', 'fondos buitre',
            'hedge fund inmobiliario', 'private equity inmobiliario',
            'operador inmobiliario', 'operadores inmobiliarios',
            'rotación de activos inmobiliarios', 'desinversión inmobiliaria',
        ],
        NewsCategory.TOKENIZATION_ACTIVOS: [
            'tokenización inmobiliaria', 'tokenizacion inmobiliaria',
            'blockchain inmobiliario', 'criptoactivo inmobiliario',
            'nft inmobiliario', 'activo tokenizado inmobiliario',
        ],
        
        NewsCategory.NOTICIAS_HIPOTECAS: [
            'hipoteca', 'hipotecas', 'hipotecario', 'hipotecaria',
            'crédito hipotecario', 'euribor', 'tipo de interés hipotecario',
            'tasa hipotecaria', 'préstamo hipotecario',
            'subrogación hipotecaria', 'novación hipotecaria', 'cancelación hipoteca',
        ],
        NewsCategory.NOTICIAS_LEYES_OKUPAS: [
            'okupa', 'okupas', 'okupación', 'okupaciones', 'ocupación ilegal',
            'ley okupas', 'ley antiokupas', 'desalojo okupas', 'desalojos okupas',
        ],
        NewsCategory.NOTICIAS_BOE_SUBASTAS: [
            'subasta inmobiliaria', 'subastas inmobiliarias',
            'subasta judicial inmobiliaria', 'boe subasta',
            'subasta pública inmobiliaria',
        ],
        NewsCategory.NOTICIAS_DESAHUCIOS: [
            'desahucio', 'desahucios', 'lanzamiento inmobiliario',
            'ejecución hipotecaria', 'embargo inmobiliario',
            'expulsión vivienda', 'desalojo forzoso',
        ],
        NewsCategory.FALTA_VIVIENDA: [
            'falta de vivienda', 'escasez de vivienda', 'déficit habitacional',
            'crisis de vivienda', 'problema de vivienda', 'acceso a vivienda',
            'vivienda asequible', 'vivienda social', 'vpo', 'vivienda protegida',
        ],
        
        NewsCategory.PRECIOS_VIVIENDA: [
            'precio de vivienda', 'precios de vivienda', 'precio vivienda', 'precios vivienda',
            'precio por m²', 'precio por metro cuadrado', 'evolución precios vivienda',
            'precio medio vivienda', 'coste vivienda', 'valor vivienda', 'revalorización vivienda',
        ],
        NewsCategory.PRECIOS_MATERIALES: [
            'precio materiales construcción', 'precios materiales construcción',
            'coste materiales construcción', 'costes materiales construcción',
            'precio construcción', 'coste construcción',
            'precio cemento', 'precio acero', 'precio ladrillo',
        ],
        NewsCategory.PRECIOS_SUELO: [
            'precio suelo', 'precios suelo', 'precio del suelo', 'precios del suelo',
            'valor suelo', 'coste suelo', 'suelo urbanizable',
        ],
        
        NewsCategory.NOTICIAS_CONSTRUCCION: [
            'promoción inmobiliaria', 'promociones inmobiliarias',
            'desarrollo inmobiliario', 'obra nueva vivienda',
            'vivienda nueva', 'nueva construcción vivienda',
        ],
        NewsCategory.NOTICIAS_URBANIZACION: [
            'urbanización', 'urbanizaciones', 'urbanismo',
            'plan general urbanístico', 'pgou', 'licencia urbanística',
            'ordenación territorial',
        ],
        NewsCategory.NOVEDADES_CONSTRUCCION: [
            'nueva construcción', 'nuevas construcciones', 'innovación construcción',
            'tecnología construcción', 'tendencias construcción',
        ],
        NewsCategory.CONSTRUCCION_MODULAR: [
            'construcción modular', 'vivienda modular', 'prefabricada',
            'prefabricadas', 'construcción industrializada',
        ],
        
        NewsCategory.ALQUILER_VACACIONAL: [
            'alquiler vacacional', 'alquileres vacacionales', 'airbnb',
            'turismo residencial', 'vivienda turística', 'apartamento turístico',
        ],
        NewsCategory.NORMATIVAS_VIVIENDAS: [
            'ley vivienda', 'ley de vivienda', 'normativa vivienda',
            'regulación vivienda', 'decreto vivienda', 'real decreto vivienda',
            'legislación inmobiliaria', 'ley urbanística',
        ],
        
        NewsCategory.FUTURO_SECTOR_INMOBILIARIO: [
            'futuro sector inmobiliario', 'tendencias inmobiliarias',
            'perspectivas sector inmobiliario', 'evolución sector inmobiliario',
            'previsión sector inmobiliario', 'proyección sector inmobiliario',
        ],
        NewsCategory.BURBUJA_INMOBILIARIA: [
            'burbuja inmobiliaria', 'sobrevaloración inmobiliaria',
            'corrección mercado inmobiliario', 'ajuste precios vivienda',
            'caída precios vivienda',
        ],
        
        # General category (lowest priority, used as fallback)
        NewsCategory.NOTICIAS_INMOBILIARIAS: [
            'inmobiliario', 'inmobiliaria', 'inmobiliarias',
            'vivienda', 'viviendas', 'propiedad', 'propiedades',
            'inmueble', 'inmuebles', 'mercado inmobiliario',
        ],
    }
    
    # Separate specific categories from general
    specific_categories = {k: v for k, v in keyword_mapping.items() 
                          if k != NewsCategory.NOTICIAS_INMOBILIARIAS}
    general_category = {NewsCategory.NOTICIAS_INMOBILIARIAS: keyword_mapping[NewsCategory.NOTICIAS_INMOBILIARIAS]}
    
    # First pass: check multi-word phrases (most specific)
    for category, keywords in specific_categories.items():
        for keyword in keywords:
            if ' ' in keyword and keyword in text_to_analyze:
                return category
    
    # Second pass: check single words in specific categories
    for category, keywords in specific_categories.items():
        for keyword in keywords:
            if ' ' not in keyword and keyword in text_to_analyze:
                return category
    
    # Third pass: check general category (fallback)
    for category, keywords in general_category.items():
        for keyword in keywords:
            if keyword in text_to_analyze:
                return category
    
    # Default fallback
    return NewsCategory.NOTICIAS_INMOBILIARIAS


def _parse_published_date(entry) -> datetime:
    """
    Attempts to parse the publication date of an RSS entry.
    
    Args:
        entry: Feed entry parsed by feedparser
        
    Returns:
        datetime in UTC, or current datetime if parsing fails
    """
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pass
    
    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        try:
            return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pass
    
    return datetime.now(timezone.utc)


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
                title = getattr(entry, 'title', 'Sin título')
                link = getattr(entry, 'link', '')
                
                if not title or not link:
                    continue
                
                temp_summary = None
                if hasattr(entry, 'summary') and entry.summary:
                    temp_summary = entry.summary
                elif hasattr(entry, 'description') and entry.description:
                    temp_summary = entry.description
                
                if not _is_relevant_to_real_estate(title, temp_summary):
                    continue
                
                relevant_count += 1
                published_at = _parse_published_date(entry)
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
                    raw_summary = _clean_html(full_content)
                    if len(raw_summary) < 200:
                        raw_summary = None
                
                if not raw_summary and link:
                    scraped_content = await _extract_article_content(link)
                    if scraped_content:
                        raw_summary = scraped_content
                
                if not raw_summary and temp_summary:
                    raw_summary = _clean_html(temp_summary)
                
                if not _is_relevant_to_real_estate(title, raw_summary):
                    continue
                
                detected_category = _categorize_by_keywords(title, raw_summary)
                final_category = detected_category if detected_category else default_category
                
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
