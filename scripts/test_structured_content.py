"""
Script para probar la generación de contenido estructurado.
"""
import asyncio
import json
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.models.news import News
from sqlalchemy import select
from app.adapters.news_adapter import build_all_content_structured


async def test_structured_content():
    """Prueba la generación de contenido estructurado"""
    async for session in get_db():
        # Obtener una noticia de prueba
        stmt = select(News).limit(1)
        result = await session.execute(stmt)
        news = result.scalar_one_or_none()
        
        if not news:
            print("❌ No hay noticias en la base de datos para probar")
            return
        
        print(f"📰 Probando con noticia: {news.title[:60]}...")
        print()
        
        try:
            # Generar contenido estructurado
            althara_summary, instagram_post, structured = build_all_content_structured(
                title=news.title,
                raw_summary=news.raw_summary,
                category=news.category,
                source=news.source,
                url=news.url,
                published_at=news.published_at
            )
            
            print("✅ CONTENIDO ESTRUCTURADO GENERADO:")
            print("=" * 80)
            print(json.dumps(structured, indent=2, ensure_ascii=False))
            print("=" * 80)
            print()
            
            # Mostrar estructura web
            print("📄 ESTRUCTURA WEB:")
            print(f"  Título: {structured['web']['title']}")
            print(f"  Deck: {structured['web']['deck']}")
            print(f"  Hecho: {structured['web']['hecho']}")
            print(f"  Lectura: {structured['web']['lectura'][:100]}...")
            print(f"  Implicaciones: {len(structured['web']['implicaciones'])} items")
            print(f"  Señales: {len(structured['web']['senales_a_vigilar'])} items")
            print()
            
            # Mostrar estructura Instagram
            print("📱 ESTRUCTURA INSTAGRAM:")
            print(f"  Hook: {structured['instagram']['hook']}")
            print(f"  Slides: {len(structured['instagram']['carousel_slides'])} slides")
            print(f"  Caption: {len(structured['instagram']['caption'])} caracteres")
            print(f"  CTA: {structured['instagram']['cta']}")
            print()
            
            # Mostrar QA
            print("🔍 QA:")
            print(f"  Facts used: {len(structured['qa']['facts_used'])}")
            print(f"  Unknown/missing: {len(structured['qa']['unknown_or_missing'])}")
            print()
            
            # Guardar en la base de datos
            news.althara_content = structured
            await session.commit()
            
            print("✅ Contenido estructurado guardado en la base de datos")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_structured_content())

