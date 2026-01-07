#!/usr/bin/env python3
"""Test the relevance filter with real titles"""
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.ingestion.rss_ingestor import _is_relevant_to_real_estate

test_titles = [
    'Giro inesperado en la okupación: Andalucía arrebata a Cataluña el liderazgo tras años de dominio',
    'Las pistas de esquí animan el inmobiliario con precios récord: así está la oferta por destinos',
    'Las branded residences marcan una nueva era: así son las promociones más exclusivas',
    'El precio de la vivienda acelera su crecimiento en 2025',
    'Marbella, uno de los mercados residenciales más cotizados de España',
    'La compra de vivienda crece un 5% en septiembre: ¿dónde sube más?',
    'Los municipios donde más sube la vivienda: todos están fuera de Madrid'
]

print("Testing relevance filter:\n")
for title in test_titles:
    result = _is_relevant_to_real_estate(title, None)
    status = "RELEVANT" if result else "REJECTED"
    print(f"[{status}] {title}")

