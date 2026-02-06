"""Pytest fixtures."""
import pytest
from datetime import datetime, timezone
from uuid import uuid4


@pytest.fixture
def sample_tech_news():
    """Sample News-like object for tech domain."""
    class News:
        id = uuid4()
        title = "OpenAI lanza GPT-5 con mejoras en razonamiento"
        source = "TechCrunch"
        url = "https://example.com/gpt5"
        raw_summary = "OpenAI ha presentado GPT-5 con capacidades mejoradas de razonamiento y menor alucinación."
        category = "AI_ML"
        domain = "tech"
        relevance_score = 85

    return News()


@pytest.fixture
def sample_real_estate_news():
    """Sample News-like object for real_estate domain."""
    class News:
        id = uuid4()
        title = "Los precios de la vivienda suben un 3% en Madrid"
        source = "Expansion"
        url = "https://example.com/precios"
        raw_summary = "El mercado inmobiliario de Madrid registra un aumento del 3% en precios."
        category = "PRECIOS_VIVIENDA"
        domain = "real_estate"
        althara_summary = "Resumen Althara"

    return News()
