#!/usr/bin/env python3
"""Test the relevance filter with title and summary from RSS"""
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.ingestion.rss_ingestor import _is_relevant_to_real_estate

# Test cases with title and summary (as they come from RSS)
test_cases = [
    {
        'title': "Giro inesperado en la okupación: Andalucía arrebata a Cataluña el liderazgo tras años de dominio",
        'summary': None
    },
    {
        'title': "Las pistas de esquí animan el inmobiliario con precios récord: así está la oferta por destinos",
        'summary': "Las estaciones de esquí españolas están experimentando un boom inmobiliario sin precedentes..."
    },
    {
        'title': "Las 'branded residences' marcan una nueva era: así son las promociones más exclusivas",
        'summary': "Las branded residences están revolucionando el mercado inmobiliario de lujo..."
    },
]

print("Testing relevance filter with title + summary:\n")
for i, case in enumerate(test_cases, 1):
    result = _is_relevant_to_real_estate(case['title'], case['summary'])
    status = "RELEVANT" if result else "REJECTED"
    print(f"[{status}] {case['title'][:70]}...")
    if case['summary']:
        print(f"        Summary: {case['summary'][:50]}...")
    print()



