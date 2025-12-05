"""
Cliente para la API de Idealista.

IMPORTANTE: Idealista NO tiene una API pública de noticias.
Su API oficial solo incluye búsqueda de propiedades y datos de mercado.

Este módulo mantiene un mock de noticias para:
- Testing y desarrollo
- Estructura lista si en el futuro Idealista ofrece API de noticias
- O para otros usos (datos de mercado, etc.)

Para noticias reales, usar fuentes RSS (ver rss_ingestor.py).
"""
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional
from app.config import settings
from app.constants import NewsCategory


class IdealistaNewsItem(BaseModel):
    """Modelo para un item de noticia de Idealista"""
    title: str
    source: str = "Idealista"
    url: str
    published_at: datetime
    category: str
    raw_summary: Optional[str] = None
    tags: Optional[str] = None


class IdealistaClient:
    """Cliente para interactuar con la API de Idealista"""
    
    def __init__(self):
        """Inicializa el cliente con la configuración"""
        self.base_url = settings.IDEALISTA_API_BASE_URL
        self.api_key = settings.IDEALISTA_API_KEY
        self.api_secret = settings.IDEALISTA_API_SECRET
    
    async def fetch_news(self, limit: int = 20) -> list[IdealistaNewsItem]:
        """
        Obtiene noticias de Idealista.
        
        Por ahora es un MOCK que genera noticias de prueba.
        TODO: Implementar llamada real a la API de Idealista.
        
        Args:
            limit: Número máximo de noticias a obtener
            
        Returns:
            Lista de items de noticias
        """
        # MOCK: Generar noticias de prueba
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
        
        # Limitar al número solicitado
        return mock_news[:limit]
    
    # TODO: Implementar método para autenticación con OAuth2 de Idealista
    # async def _get_access_token(self) -> str:
    #     """Obtiene un token de acceso para la API de Idealista"""
    #     pass
    
    # TODO: Implementar método para llamar a endpoints reales de Idealista
    # async def _call_api(self, endpoint: str, params: dict) -> dict:
    #     """Realiza una llamada a la API de Idealista"""
    #     pass

