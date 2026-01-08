#!/usr/bin/env python3
"""
Script para probar la generación de posts de Instagram.
Genera posts para las noticias existentes y muestra ejemplos.
"""
import asyncio
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.news import News
from app.adapters.news_adapter import build_all_content
from sqlalchemy import select
import json


async def test_instagram_posts():
    """Prueba la generación de posts de Instagram"""
    async with AsyncSessionLocal() as session:
        # Obtener algunas noticias para probar
        stmt = select(News).limit(5)
        result = await session.execute(stmt)
        news_list = result.scalars().all()
        
        if not news_list:
            print("❌ No hay noticias en la base de datos.")
            print("   Primero ejecuta la ingesta: python scripts/ingest_news.py")
            return
        
        print("=" * 80)
        print("🧪 PRUEBA DE GENERACIÓN DE POSTS DE INSTAGRAM")
        print("=" * 80)
        print()
        print(f"📊 Encontradas {len(news_list)} noticias para probar")
        print()
        
        for i, news in enumerate(news_list, 1):
            print(f"\n{'='*80}")
            print(f"📰 NOTICIA {i}/{len(news_list)}")
            print(f"{'='*80}")
            print(f"Título: {news.title[:80]}...")
            print(f"Categoría: {news.category}")
            print(f"Fuente: {news.source}")
            print()
            
            try:
                # Generar post de Instagram
                althara_summary, instagram_post = build_all_content(
                    title=news.title,
                    raw_summary=news.raw_summary,
                    category=news.category,
                    source=news.source,
                    url=news.url
                )
                
                print("✅ POST DE INSTAGRAM GENERADO:")
                print("-" * 80)
                print(instagram_post)
                print("-" * 80)
                print()
                print(f"📏 Longitud: {len(instagram_post)} caracteres")
                print()
                
                # Guardar en la base de datos
                news.instagram_post = instagram_post
                if not news.althara_summary:
                    news.althara_summary = althara_summary
                
            except Exception as e:
                print(f"❌ Error generando post: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Guardar cambios
        await session.commit()
        print("\n" + "=" * 80)
        print("✅ Posts generados y guardados en la base de datos")
        print("=" * 80)
        print()
        print("💡 Puedes consultar los posts usando:")
        print("   GET /api/news - Ver todas las noticias con sus posts")
        print("   GET /api/news/{id} - Ver una noticia específica con su post")


if __name__ == "__main__":
    try:
        asyncio.run(test_instagram_posts())
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)



