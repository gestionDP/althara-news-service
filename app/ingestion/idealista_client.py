"""
Client for Idealista API.

IMPORTANT: Idealista does NOT have a public news API.
Their official API only includes property search and market data.

This module maintains a news mock for:
- Testing and development
- Ready structure if Idealista offers a news API in the future
- Or for other uses (market data, etc.)

For real news, use RSS sources (see rss_ingestor.py).
"""
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional
from app.config import settings
from app.constants import NewsCategory


class IdealistaNewsItem(BaseModel):
    """Model for an Idealista news item"""
    title: str
    source: str = "Idealista"
    url: str
    published_at: datetime
    category: str
    raw_summary: Optional[str] = None
    tags: Optional[str] = None


class IdealistaClient:
    """Client for interacting with Idealista API"""
    
    def __init__(self):
        """Initializes the client with configuration"""
        self.base_url = settings.IDEALISTA_API_BASE_URL
        self.api_key = settings.IDEALISTA_API_KEY
        self.api_secret = settings.IDEALISTA_API_SECRET
    
    async def fetch_news(self, limit: int = 20) -> list[IdealistaNewsItem]:
        """
        Gets news from Idealista.
        
        Currently a MOCK that generates test news.
        TODO: Implement real call to Idealista API.
        
        Args:
            limit: Maximum number of news items to get
            
        Returns:
            List of news items
        """
        mock_news = [
            IdealistaNewsItem(
                title="El precio de la vivienda en Madrid sube un 5% en el último trimestre",
                source="Idealista",
                url="https://idealista.com/news/precio-vivienda-madrid-trimestre",
                published_at=datetime.now(timezone.utc),
                category=NewsCategory.PRECIOS_VIVIENDA,
                raw_summary="Los precios de la vivienda en Madrid han experimentado un aumento del 5% durante el último trimestre, según datos de Idealista.",
                tags="vivienda, precios, madrid"
            ),
            IdealistaNewsItem(
                title="Nuevo fondo de inversión inmobiliaria recauda 500 millones",
                source="Idealista",
                url="https://idealista.com/news/fondo-inversion-500-millones",
                published_at=datetime.now(timezone.utc),
                category=NewsCategory.FONDOS_INVERSION_INMOBILIARIA,
                raw_summary="Un nuevo fondo de inversión inmobiliaria ha recaudado 500 millones de euros para inversiones en el sector.",
                tags="fondos, inversión, inmobiliaria"
            ),
            IdealistaNewsItem(
                title="Las hipotecas suben hasta el 3,5% de media en España",
                source="Idealista",
                url="https://idealista.com/news/hipotecas-suben-3-5",
                published_at=datetime.now(timezone.utc),
                category=NewsCategory.NOTICIAS_HIPOTECAS,
                raw_summary="El tipo de interés medio de las hipotecas en España ha subido hasta el 3,5%, afectando a nuevos compradores.",
                tags="hipotecas, interés, financiación"
            ),
            IdealistaNewsItem(
                title="Blackstone adquiere 2.000 viviendas en Barcelona por 600 millones",
                source="Idealista",
                url="https://idealista.com/news/blackstone-barcelona-600-millones",
                published_at=datetime.now(timezone.utc),
                category=NewsCategory.GRANDES_INVERSIONES_INMOBILIARIAS,
                raw_summary="Blackstone ha adquirido un paquete de 2.000 viviendas en Barcelona por un valor de 600 millones de euros.",
                tags="blackstone, inversión, barcelona"
            ),
            IdealistaNewsItem(
                title="Tendencias del mercado inmobiliario para 2025",
                source="Idealista",
                url="https://idealista.com/news/tendencias-mercado-2025",
                published_at=datetime.now(timezone.utc),
                category=NewsCategory.NOTICIAS_INMOBILIARIAS,
                raw_summary="Análisis de las principales tendencias que marcarán el mercado inmobiliario español durante 2025.",
                tags="tendencias, mercado, 2025"
            ),
        ]
        
        return mock_news[:limit]
    
    # TODO: Implement method for OAuth2 authentication with Idealista
    # async def _get_access_token(self) -> str:
    #     """Gets an access token for Idealista API"""
    #     pass
    
    # TODO: Implement method to call real Idealista endpoints
    # async def _call_api(self, endpoint: str, params: dict) -> dict:
    #     """Makes a call to Idealista API"""
    #     pass

